import requests
import re
import pandas as pd
import time
import sys
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import lru_cache
from unidecode import unidecode

# Log fájl: futás során keletkezett hibák és figyelmeztetések
LOG_FILE = "geo.log"
_file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
_file_handler.setLevel(logging.INFO)
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
log = logging.getLogger("geo")
log.setLevel(logging.DEBUG)
log.addHandler(_file_handler)

print("geo.py indul...", flush=True)
log.info("=== geo.py futás indul (%s) ===", datetime.now().isoformat(timespec="seconds"))

def _print_parameters():
    """Paraméterek kiírása a konzolra (--parameters vagy --help)."""
    msg = """
geo.py - Nominatim geokodolas magyar cimekre (IccExport -> geocoded_output.csv)

Hasznalat:
  python geo.py                    Teljes CSV feldolgozasa
  python geo.py --limit N          Csak az elso N sor (pl. --limit 30)
  python geo.py --row N            Csak az N. sor (1-tol, pl. --row 30)
  python geo.py --threads N         Parhuzamos szalak szama (alapertelmezett: 20)
  python geo.py --test             Teszt mod: elso 5 sor, reszletes log
  python geo.py --wait MP          Kezdes elott MP mp varakozas (rate limit miatt)
  python geo.py --parameters      Ez az uzenet (--help, -h)

Peldak:
  python geo.py --limit 30
  python geo.py --row 30
  python geo.py --wait 60 --limit 100
"""
    print(msg.strip(), flush=True)

if "--parameters" in sys.argv or "--help" in sys.argv or "-h" in sys.argv:
    _print_parameters()
    sys.exit(0)

TEST_MODE = "--test" in sys.argv

# Opcionális: python geo.py --wait 300 = 300 mp várakozás a rate limit (429) miatt
def _get_wait_seconds():
    for i, a in enumerate(sys.argv):
        if a == "--wait" and i + 1 < len(sys.argv):
            try:
                return max(0, int(sys.argv[i + 1]))
            except ValueError:
                pass
    return 0

WAIT_BEFORE_START = _get_wait_seconds()
if WAIT_BEFORE_START > 0:
    print(f"  Rate limit miatt {WAIT_BEFORE_START} mp várakozás...", flush=True)
    log.warning("Rate limit miatt %s mp várakozás a futás elején", WAIT_BEFORE_START)
    time.sleep(WAIT_BEFORE_START)

def _get_limit():
    """Opcionális: python geo.py --limit 30 = csak az első N sor (pl. 30)."""
    for i, a in enumerate(sys.argv):
        if a == "--limit" and i + 1 < len(sys.argv):
            try:
                return int(sys.argv[i + 1])
            except ValueError:
                pass
    return None

def _get_row_filter():
    """Opcionális: python geo.py --row 30 = csak az N. sor (1-től). Vissza: (start_idx, end_idx) 0-based vagy None."""
    for i, a in enumerate(sys.argv):
        if a == "--row" and i + 1 < len(sys.argv):
            try:
                n = int(sys.argv[i + 1])
                if n >= 1:
                    return (n - 1, n)
            except ValueError:
                pass
    return None

def _get_threads():
    """Opcionális: python geo.py --threads 20 = 20 szál (alapertelmezett 20)."""
    for i, a in enumerate(sys.argv):
        if a == "--threads" and i + 1 < len(sys.argv):
            try:
                return max(1, min(100, int(sys.argv[i + 1])))
            except ValueError:
                pass
    return 20

# Nominatim: max 1 kérés/másodperc – közös lock minden szálon
_nominatim_lock = threading.Lock()
_nominatim_last_ts = [0.0]
_print_lock = threading.Lock()  # terminal kiírás sorról sorra, ne keveredjenek a szálak

def _nominatim_request(fn):
    """1 kérés/mp megengedés, majd fn() végrehajtása a lock alatt. Vissza: fn() eredménye."""
    with _nominatim_lock:
        now = time.time()
        elapsed = now - _nominatim_last_ts[0]
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        _nominatim_last_ts[0] = time.time()
        return fn()

def _str_cell(v):
    """CSV cella loghoz: nan/None -> üres string."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).strip()
    return "" if s.lower() == "nan" else s

def _strip_nan(s):
    """Eltávolítja a 'nan' szót a string végéről vagy közepéről (Nominatim ne kapjon ilyet)."""
    if not s or not isinstance(s, str):
        return s
    s = re.sub(r"\s+nan\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+nan\s+", " ", s, flags=re.IGNORECASE)
    return s.strip()

def _normalize_street_for_output(s):
    """Street mező normalizálása a geocoded_output.csv-be: ? -> ő, nan kiszűrés, u. -> utca; az ékezetek megmaradnak."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    s = str(s).strip()
    if not s or s.lower() in ("nan", "unknow"):
        return s
    s = _fix_wrong_accents(s)
    s = _fix_encoding_placeholder(s)
    s = _strip_nan(s)
    s = s.replace(" u. ", " utca ").replace(" u ", " utca ")
    return " ".join(s.split()) if s else s

def _normalize_city_for_output(s):
    """City mező normalizálása a geocoded_output.csv-be; ékezetek megmaradnak."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    s = str(s).strip()
    if not s or s.lower() in ("nan", "unknow"):
        return s
    s = _fix_encoding_placeholder(s)
    s = _strip_nan(s)
    return " ".join(s.split()) if s else s

# Beolvasás: először UTF-8, ha nem az (pl. régi export latin1/cp1250), akkor fallback
try:
    df = pd.read_csv("IccExport20260217.csv", sep=";", encoding="utf-8", dtype=str)
except UnicodeDecodeError:
    df = pd.read_csv("IccExport20260217.csv", sep=";", encoding="latin1", dtype=str)

# Cache város szintű geokodaláshoz
@lru_cache(maxsize=10000)
def geocode_city(city_name):
    """Város szintű geokódolás Nominatim-el."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": f"{city_name}, Hungary",
                "format": "json",
                "limit": 1,
                "countrycodes": "hu",
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "InverterHeatMap-Geocoding/1.0 (Hungary)"
            }
            # UTF-8 kódolás, hogy az ékezetes formák (pl. Vésztő) helyesen menjenek
            response = _nominatim_request(
                lambda: requests.get(url, params=params, timeout=30, headers=headers)
            )
            if response.status_code == 429:
                log.warning("Nominatim 429 (rate limit) - geocode_city: %s", city_name)
                time.sleep(60)  # Rate limit: 60 mp várakozás
                continue
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                addr = data[0].get("address") or {}
                postcode = addr.get("postcode")
                if isinstance(postcode, (list, dict)):
                    postcode = postcode[0] if postcode else None
                return lat, lon, postcode
            return None, None, None
            
        except requests.Timeout:
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)
                time.sleep(wait_time)
                continue
            log.warning("geocode_city timeout után %s próba: %s", max_retries, city_name)
            return None, None, None
        except Exception as e:
            log.exception("geocode_city hiba: %s - %s", city_name, e)
            return None, None, None
    
    return None, None, None

@lru_cache(maxsize=10000)
def geocode_address(address):
    """Cím szintű geokódolás Nominatim-el."""
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "countrycodes": "hu",
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "InverterHeatMap-Geocoding/1.0 (Hungary)"
            }

            response = _nominatim_request(
                lambda: requests.get(url, params=params, timeout=30, headers=headers)
            )
            if response.status_code == 429:
                log.warning("Nominatim 429 (rate limit) - geocode_address: %s", address[:80])
                time.sleep(60)  # Rate limit: 60 mp várakozás
                continue
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                addr = data[0].get("address") or {}
                postcode = addr.get("postcode")
                if isinstance(postcode, (list, dict)):
                    postcode = postcode[0] if postcode else None
                return lat, lon, postcode
            return None, None, None
            
        except requests.Timeout:
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)
                time.sleep(wait_time)
                continue
            log.warning("geocode_address timeout után %s próba: %s", max_retries, address[:80])
            return None, None, None
        except Exception as e:
            log.exception("geocode_address hiba: %s - %s", address[:80], e)
            return None, None, None
    
    return None, None, None

def extract_zip_from_city(city_str):
    """
    A City mezőből kinyeri a 4 jegyű magyar irányítószámot.
    Pl. 'Debrecen, Károli Gáspár utca 414, 4032, Hajdú-Bihar...' -> '4032'
    """
    if not city_str:
        return None
    for part in city_str.split(","):
        token = part.strip()
        if len(token) == 4 and token.isdigit() and 1000 <= int(token) <= 9999:
            return token
    return None

def _fix_encoding_placeholder(s):
    """Kódolási hiba: szó végi '?' (pl. Veszt?, Ern?) -> 'ő', hogy a cím és város ne maradjon ?-es a Nominatimnek."""
    if not s or "?" not in s:
        return s
    # Betű + ? + szóvég (szóköz, vessző, string vége) -> betű + ő (pl. Veszt? -> Vesztő, Ern? -> Ernő)
    s = re.sub(r"([A-Za-záéíóöőúüűÁÉÍÓÖŐÚÜŰ])\?(?=\s|$|,)", r"\1ő", s)
    return s

# Gyakori rossz ékezet (pl. è helyett é) -> helyes; dinamikus, bármely szóban
WRONG_ACCENT_TO_CORRECT = {"è": "é", "à": "á", "ì": "í", "ò": "ó", "ù": "ú"}

def _fix_wrong_accents(s):
    """Rossz ékezetes karakterek cseréje a helyesre (pl. è->é, à->á)."""
    if not s or not isinstance(s, str):
        return s
    for wrong, right in WRONG_ACCENT_TO_CORRECT.items():
        s = s.replace(wrong, right)
    return s

# Magyar ékezetes karakterek, amiket a "?" helyére próbálunk (dinamikus találat)
HUNGARIAN_ACCENTS = "öüóőúéáűí"

def _variants_for_placeholder(s):
    """Ha van '?' a stringben, visszaadja a változatokat: az első ? helyére mind a 9 ékezetes betű;
    ha a ? előtt van magánhangzó, az első magánhangzó ékezetes formáját is kipróbáljuk (pl. Veszt? -> Vésztő).
    Az ékezetes (pl. Vésztő) változatok előrébb kerülnek, mert a településneveknél ezek gyakran a helyes formák."""
    if "?" not in s:
        return [s]
    base = [s.replace("?", c, 1) for c in HUNGARIAN_ACCENTS]
    idx = s.index("?")
    pre = s[:idx]
    first_vowel_i = next((i for i, ch in enumerate(pre) if ch.lower() in "aeiou"), None)
    if first_vowel_i is None:
        return base
    accented_vowel = {"e": "é", "a": "á", "i": "í", "o": "ó", "u": "ú"}.get(pre[first_vowel_i].lower())
    if not accented_vowel:
        return base
    # Először azok, ahol az első magánhangzó is ékezetes (pl. Vésztő) – ezek gyakran találnak
    extra_first = []
    for v in base:
        extra = v[:first_vowel_i] + accented_vowel + v[first_vowel_i + 1:]
        if extra not in extra_first:
            extra_first.append(extra)
    return extra_first + base

def _ascii_city_variants(word):
    """Ha a szó csak ASCII (pl. Veszto), visszaad ékezetes változatokat városként – dinamikus, nem csak ? esetén."""
    if not word or len(word) < 3 or not word.isascii():
        return []
    w = word
    # Magyar gyakori: utolsó 'o' -> 'ő' (Veszto -> Vesztő), első 'e' -> 'é' (Veszto -> Vésztő)
    out = []
    if "o" in w.lower():
        last_o = w.lower().rindex("o")
        v = w[:last_o] + ("ő" if w[last_o] == "o" else "Ő") + w[last_o + 1:]
        if v not in out:
            out.append(v)
    for i, c in enumerate(w):
        if c.lower() == "e" and (i == 0 or not w[i - 1].isalpha()):
            v = w[:i] + ("é" if c == "e" else "É") + w[i + 1:]
            if v not in out:
                out.append(v)
            break
    return out

def _alternative_address_forms(s):
    """
    Ha a cím "Város, utca rész, 1234 Hungary" vagy "1234 Budapest, utca, Hungary" formátumú
    és nem találta a Nominatim, visszaad alternatív formákat.
    """
    if not s or "Hungary" not in s:
        return []
    s = s.strip()
    # Budapest, utca, 1203 Hungary -> 1203 Budapest, utca + utca, 1203 Budapest
    m = re.match(r"^(Budapest),\s*(.+?)(?:,\s*|\s+)(\d{4})\s*,?\s*Hungary\s*$", s, re.IGNORECASE | re.DOTALL)
    if m:
        city, middle, zip_code = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        return [
            f"{zip_code} {city}, {middle}, Hungary",
            f"{middle}, {zip_code} {city}, Hungary",
        ]
    # Már "1203 Budapest, utca, Hungary" formátum -> próbáljuk "utca, 1203 Budapest, Hungary"
    m2 = re.match(r"^(\d{4})\s+(Budapest),\s*(.+?),?\s*Hungary\s*$", s, re.IGNORECASE | re.DOTALL)
    if m2:
        zip_code, city, middle = m2.group(1).strip(), m2.group(2).strip(), m2.group(3).strip()
        return [f"{middle}, {zip_code} {city}, Hungary"]
    return []

def _normalize_street_string(s):
    """Összeragadt és rossz formátumok javítása: irányítószám+város, utca45, út19, .Város."""
    if not s or len(s) < 3:
        return s
    # 4 jegyű irányítószám összeragadva várossal: 4327Pocspetr -> 4327 Pocspetr
    s = re.sub(r"(\d{4})([A-Za-zÁÉÍÓÖŐÚÜŰa-záéíóöőúüű])", r"\1 \2", s)
    # utca/út + szám összeragadva: utca45, út19, ut19 -> utca 45, út 19
    s = re.sub(r"\butca\s*(\d)", r"utca \1", s, flags=re.IGNORECASE)
    s = re.sub(r"\b(ut|út)\s*(\d)", r"\1 \2", s, flags=re.IGNORECASE)
    # pont + nagybetűs szó (város): "utca45.Adony" -> "utca 45, Adony"
    s = re.sub(r"\.([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüűA-ZÁÉÍÓÖŐÚÜŰ\s\-]+?)(?=\s|$|,)", r", \1", s)
    s = " ".join(s.split())
    return s

def build_search_info(row):
    """
    Meghatározza, milyen specificitáson kell keresni.

    Prioritás:
    1. ZIP + City + Street + StreetNo - pontosan (utca szint)
    2. Ha a City teljes címet tartalmaz (utca, szám) -> cím szintű próba
    3. City - település szint

    Return: (search_type, search_string, city_name, effective_zip)
    """
    city_str = str(row.get("City", "")).strip()
    zip_from_city = extract_zip_from_city(city_str)  # Elsődleges: mindig a település/cím mezőből
    effective_zip = zip_from_city  # Csak a City mezőből, a CSV Zip oszlopát nem használjuk
    street = str(row.get("Street", "")).strip()
    street = _fix_wrong_accents(street)
    street_type = _str_cell(row.get("StreetType", ""))
    street_no = _str_cell(row.get("StreetNo", ""))
    building = _str_cell(row.get("Building", ""))

    if "," in city_str:
        city_name = city_str.split(",")[0].strip()
    else:
        city_name = city_str

    city_name_clean = unidecode(city_name)
    street_clean = _fix_encoding_placeholder(unidecode(street))
    street_type_clean = unidecode(street_type)

    # 1) Klasszikus utca szint: van ZIP, város, külön utca és házszám
    has_valid_zip = effective_zip and effective_zip != "0000"
    has_valid_city = city_name and city_name.lower() != "unknow"
    has_valid_street = street and street.lower() != "unknow"
    has_street_no = (street_no or building) and (street_no or building).lower() not in ("unknow", "")
    num_part = (street_no or building).strip()

    if has_valid_zip and has_valid_city and has_valid_street and has_street_no:
        address = f"{street_clean} {street_type_clean} {num_part} {city_name_clean} {effective_zip} Hungary"
        address = " ".join(address.split())
        return ("address", address, city_name_clean, effective_zip)

    # 2) Új: City mező teljes címnek tűnik (utca + szám) -> cím szintű próba
    city_lower = city_str.lower()
    has_address_hint = (
        any(x in city_lower for x in ("utca", " u.", " út", "tér", " köz", " sor", " sugár", " park")) or
        ("," in city_str and any(c.isdigit() for c in city_str))
    )
    if has_valid_city and has_address_hint and len(city_str) > len(city_name) + 3:
        # Teljes City string geokódolása (Nominatim sokszor megérti)
        full_address = unidecode(city_str)
        # Mindig adjuk hozzá "Hungary"-t a végére (Nominatim jobban talál)
        if "hungary" not in full_address.lower():
            full_address = f"{full_address}, Hungary"
        full_address = " ".join(full_address.split())
        return ("address", full_address, city_name_clean, effective_zip)

    # 3) Fallback: város szint
    if has_valid_city:
        return ("city", city_name_clean, city_name_clean, effective_zip)

    # 4) Ha a City "unknow"/üres, de a Street tartalmaz címet (város, utca, Hungary) -> először címként, ha az nem talál, városként fallback
    street_only = (street_clean + " " + street_type_clean).strip() or street_clean
    street_only = _strip_nan(street_only)
    # Ha a Street vesszőre végződik és van StreetNo/Building (pl. "1203 Hungary"), az része legyen a kereső stringnek (nan ne)
    num_part = (street_no or building).strip()
    if num_part and num_part.lower() == "nan":
        num_part = ""
    if num_part and street_only.rstrip().endswith(",") and ("hungary" in num_part.lower() or (len(num_part) == 4 and num_part.isdigit())):
        street_only = (street_only.rstrip() + " " + num_part).strip()
    elif num_part and "hungary" not in street_only.lower() and re.match(r"^\d{4}\s*,?\s*Hungary\s*$", num_part, re.IGNORECASE):
        street_only = (street_only + " " + num_part).strip()
    street_only = _strip_nan(street_only)
    if street_only and street_only.lower() != "unknow" and len(street_only) > 2:
        search = _normalize_street_string(street_only)
        # Ha a string elején van 4 jegyű irányítószám (pl. "2030 Érd Zólyomi utca 31"), átrendezzük: "Érd, Zólyomi utca 31, 2030 Hungary"
        parts = search.split(None, 2)  # max 3 rész: [zip, city, street_rest]
        city_part = None
        if len(parts) >= 2 and len(parts[0]) == 4 and parts[0].isdigit() and 1000 <= int(parts[0]) <= 9999:
            zip_first = parts[0]
            rest = parts[1] if len(parts) == 2 else (parts[1] + " " + parts[2])
            rest_parts = rest.split()
            if len(rest_parts) >= 2:
                city_part = rest_parts[0]
                street_rest = " ".join(rest_parts[1:])
                search = f"{city_part}, {street_rest}, {zip_first}"
        # Középen lévő irányítószám (pl. "Alsózsolca 3571 Rákóczi út 37") -> "Alsózsolca, Rákóczi út 37, 3571"
        if not city_part and " " in search:
            tokens = search.split()
            for i, t in enumerate(tokens):
                if len(t) == 4 and t.isdigit() and 1000 <= int(t) <= 9999 and i > 0 and i < len(tokens) - 1:
                    city_part = " ".join(tokens[:i])
                    street_rest = " ".join(tokens[i + 1:])
                    search = f"{city_part}, {street_rest}, {t}"
                    break
        if "hungary" not in search.lower():
            search = f"{search}, Hungary"
        search = " ".join(search.split())
        search = _strip_nan(search)
        # "Város, megye, Hungary" -> egyszerűsítve "Város, Hungary" (Nominatim jobban találja)
        if search.count(",") >= 2 and search.strip().lower().endswith("hungary"):
            pre_h = search.rsplit(",", 1)[0].strip()
            parts_comma = [p.strip() for p in pre_h.split(",")]
            if len(parts_comma) >= 2 and "-" in parts_comma[1]:
                search = f"{parts_comma[0]}, Hungary"
        # Nominatim jobban talál magyar címeket, ha " u." -> " utca", " út" megmarad
        for abbr, full in [(" u. ", " utca "), (" u ", " utca ")]:
            if abbr in search and full not in search:
                search = search.replace(abbr, full)
        # Budapest, utca, 1203 Hungary -> 1203 Budapest, utca, Hungary (első kérésre, Nominatim jobban találja)
        budapest_m = re.match(r"^(Budapest),\s*(.+?)(?:,\s*|\s+)(\d{4})\s*,?\s*Hungary\s*$", search.strip(), re.IGNORECASE | re.DOTALL)
        if budapest_m:
            _city, _middle, _zip = budapest_m.group(1).strip(), budapest_m.group(2).strip(), budapest_m.group(3).strip()
            search = f"{_zip} {_city}, {_middle}, Hungary"
        fallback_city = street_only.split(",")[0].strip() if "," in street_only else street_only
        if city_part:
            fallback_city = city_part
        elif not fallback_city or fallback_city.isdigit():
            fallback_city = (search.split(",")[0].strip() if "," in search else (search.split()[0] if search.split() else street_only))
        # Címként próbáljuk, ha van vessző és hosszú, VAGY ha "utca"/"út" van benne (pl. "Szoregi Janos utca 12.")
        looks_like_address = "," in search and len(street_only) > 15
        if not looks_like_address and len(street_only) > 10 and ("utca" in search or " ut " in search or " u. " in search):
            looks_like_address = True
            if not fallback_city or fallback_city == street_only:
                fallback_city = search.split()[0] if search.split() else fallback_city
        if looks_like_address:
            return ("address", search, unidecode(fallback_city), effective_zip)
        return ("city", search, unidecode(fallback_city), effective_zip)

    return (None, None, None, effective_zip)

def row_address_summary(row):
    """Egy sor címelemeiből rövid összefoglaló a loghoz. Irányítószám csak a City (település) mezőből."""
    city = _str_cell(row.get("City", ""))
    zip_val = extract_zip_from_city(city)
    street = _str_cell(row.get("Street", ""))
    street_type = _str_cell(row.get("StreetType", ""))
    street_no = _str_cell(row.get("StreetNo", ""))
    building = _str_cell(row.get("Building", ""))
    no = (street_no or building).strip()
    parts = []
    if zip_val and zip_val != "0000":
        parts.append(f"irányítószám: {zip_val}")
    if city:
        c_short = city.split(",")[0].strip() if "," in city else city
        parts.append(f"város: {c_short[:50]}")
    if street and street.lower() != "unknow":
        addr = f"{street} {street_type} {no}".strip()
        if addr:
            parts.append(f"cím: {addr[:60]}")
    return " | ".join(parts) if parts else "(nincs adat)"

def _log_row_context(row):
    """Sor nyers mezői a loghoz (mindig kiírja City, Street, Zip), hogy beszédes legyen a hiba."""
    city = _str_cell(row.get("City", ""))
    street = _str_cell(row.get("Street", ""))
    zip_val = extract_zip_from_city(city) or _str_cell(row.get("Zip", "")) or "-"
    city_show = (city[:50] + "…") if len(city) > 50 else (city or "(üres)")
    street_show = (street[:60] + "…") if len(street) > 60 else (street or "(üres)")
    return "City=%s, Street=%s, Zip=%s" % (city_show, street_show, zip_val)

latitudes = []
longitudes = []
search_types = []  # Track whether this was city or address level
zip_corrected_list = []  # Nominatimból lekérült irányítószám, ha az eredeti 0000/üres
resolved_city_list = []  # Sikeres geokódolásnál a felhasznált városnév (City oszlopba írjuk, ha eredetileg unknow)

start_time = time.time()

def elapsed():
    t = time.time() - start_time
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    return f"[{h}:{m:02d}:{s:02d}]"

print(f"{elapsed()} - Feldolgozás indul... {len(df)} rekord", flush=True)
# Nominatim: max 1 kérés/mp; kezdés előtt késleltetés
time.sleep(5)

# Addig próbáljuk az első sor címét (Debrecen, Károli Gáspár utca 414…), amíg a Nominatim meg nem találja
first_row = df.iloc[0]
st, search_str, cname, _ = build_search_info(first_row)
if search_str:
    while True:
        lat, lon, _ = None, None, None
        if st == "address":
            lat, lon, _ = geocode_address(search_str)
        if (lat is None or lon is None) and search_str:
            lat, lon, _ = geocode_city(cname)
        if lat is not None and lon is not None:
            print(f"{elapsed()} - Első sor címe megvan: {lat:.4f}, {lon:.4f} (Debrecen, Károli Gáspár u. 414…)", flush=True)
            break
        geocode_address.cache_clear()
        geocode_city.cache_clear()
        print(f"{elapsed()} - Nem található, 60 mp múlva újrapróbálkozás…", flush=True)
        log.warning("Első sor címe nem található, 60 mp múlva újrapróbálkozás")
        time.sleep(60)
else:
    print(f"{elapsed()} - Első sornak nincs kereshető címe, folytatás.", flush=True)
    log.warning("Első sornak nincs kereshető címe")

# A ciklus előtt még 1 mp szünet (Nominatim limit)
# A ciklus előtt még 1 mp szünet (Nominatim limit)
time.sleep(1)

_limit_arg = _get_limit()
row_filter = _get_row_filter()
if row_filter:
    row_start, row_end = row_filter
    row_end = min(row_end, len(df))
    row_start = min(row_start, row_end)
    limit = row_end
    print(f"{elapsed()} - Csak a(z) {row_start + 1}. sor feldolgozása (--row {row_start + 1}).\n", flush=True)
else:
    limit = min(_limit_arg, len(df)) if _limit_arg is not None else (5 if TEST_MODE else len(df))
    if _limit_arg is not None:
        print(f"{elapsed()} - Csak az első {limit} sor feldolgozása (--limit {_limit_arg}).\n", flush=True)
if TEST_MODE and not row_filter:
    print(f"{elapsed()} - [TESZT MÓD] Csak az első {limit} sor feldolgozása, a küldött cím és válasz kiírva.\n", flush=True)

if row_filter:
    row_start, row_end = row_filter
    row_end = min(row_end, len(df))
    indices_to_process = list(range(row_start, row_end))
else:
    indices_to_process = list(range(0, limit))

NUM_THREADS = _get_threads()
print(f"{elapsed()} - {NUM_THREADS} szal, {len(indices_to_process)} sor.", flush=True)
print(f"{elapsed()} - Feldolgozas folyamatban (Nominatim: 1 kereses/mp), elso eredmenyek hamarosan...", flush=True)

def process_one_row(index):
    """Egy sor feldolgozása; vissza: (index, lat, lon, search_type, zip_corrected, resolved_city)."""
    row = df.iloc[index]
    n = index + 1
    search_type, search_string, city_name, effective_zip = build_search_info(row)
    if not search_string:
        log.error("sor %s/%s - sikertelen (adat hianyzik): %s", n, len(df), _log_row_context(row))
        return (index, None, None, None, effective_zip or "", None)
    lat = None
    lon = None
    resolved_city = None
    postcode_from_api = None
    try:
        if search_type == "address":
            if "?" in search_string:
                for variant in _variants_for_placeholder(search_string):
                    lat, lon, postcode_from_api = geocode_address(variant)
                    if lat is not None and lon is not None:
                        search_string = variant
                        break
            if lat is None or lon is None:
                lat, lon, postcode_from_api = geocode_address(search_string)
            if lat is None or lon is None:
                for alt in _alternative_address_forms(search_string):
                    lat, lon, postcode_from_api = geocode_address(alt)
                    if lat is not None and lon is not None:
                        search_string = alt
                        break
            if lat is None or lon is None:
                # Ha a city_name vesszőt tartalmaz (pl. "Budapest, Kende Kanuth u. 4, "), csak az első részt próbáljuk városként
                city_for_fallback = city_name.split(",")[0].strip() if "," in city_name else city_name
                city_for_fallback = _strip_nan(city_for_fallback)
                # Eredeti cím első szava (CSV) – ha benne van "?", ezt használjuk variánsokhoz (a search_string már lehet unidecode)
                street_raw = _str_cell(row.get("Street", ""))
                first_word_original = street_raw.split()[0] if street_raw and street_raw.strip() else None
                # A search_string ékezetes lehet (pl. Vesztő), a city_name viszont unidecode – próbáljuk a search_string első szavát városként
                first_word_search = search_string.split()[0] if search_string and search_string.strip() else None
                if (lat is None or lon is None) and first_word_search and len(first_word_search) > 2:
                    lat, lon, postcode_from_api = geocode_city(first_word_search)
                    if lat is not None and lon is not None:
                        resolved_city = first_word_search
                    else:
                        log.debug("city fallback first_word_search nem talalt: %s", first_word_search)
                # Variánsok: az eredeti CSV első szavát használjuk ha van benne "?" (pl. Vészt?), különben search első szava – dinamikus
                first_word_for_variants = first_word_original if (first_word_original and "?" in first_word_original) else first_word_search
                if (lat is None or lon is None) and first_word_for_variants and "?" in first_word_for_variants:
                    for variant in _variants_for_placeholder(first_word_for_variants):
                        lat, lon, postcode_from_api = geocode_city(variant)
                        if lat is not None and lon is not None:
                            resolved_city = variant
                            break
                # Első szó + megye (pl. Vésztő, Békés), ha még mindig nincs – akkor is ha city_for_fallback "unknow"
                if (lat is None or lon is None) and first_word_for_variants and "?" in first_word_for_variants:
                    fw_fixed = first_word_for_variants.replace("?", "ő")
                    fw_ascii = unidecode(first_word_for_variants)
                    for q in (fw_fixed, fw_ascii):
                        if lat is not None and lon is not None:
                            break
                        for suffix in ("", ", Békés"):
                            if lat is not None and lon is not None:
                                break
                            lat, lon, postcode_from_api = geocode_city(q + suffix)
                            if lat is not None and lon is not None:
                                resolved_city = (q + suffix) if suffix else q
                # Ha még mindig nincs: első szó ASCII (pl. Veszto) -> ékezetes változatok próbálása – dinamikus
                if (lat is None or lon is None) and first_word_search and first_word_search.isascii() and len(first_word_search) >= 4:
                    for variant in _ascii_city_variants(first_word_search):
                        lat, lon, postcode_from_api = geocode_city(variant)
                        if lat is not None and lon is not None:
                            resolved_city = variant
                            break
                # Utolsó próba: első szó egyszerű o->ő, e->é (pl. Veszto->Vesztő) – cache/API miatti hiba esetén is
                if (lat is None or lon is None) and first_word_search and len(first_word_search) >= 4:
                    trials = []
                    if "o" in first_word_search.lower():
                        idx = first_word_search.lower().rindex("o")
                        t = first_word_search[:idx] + ("ő" if first_word_search[idx] == "o" else "Ő") + first_word_search[idx + 1:]
                        if t != first_word_search:
                            trials.append(t)
                    if "e" in first_word_search.lower():
                        idx = first_word_search.lower().index("e")
                        t = first_word_search[:idx] + ("é" if first_word_search[idx] == "e" else "É") + first_word_search[idx + 1:]
                        if t != first_word_search and t not in trials:
                            trials.append(t)
                    for trial in trials:
                        if lat is not None and lon is not None:
                            break
                        lat, lon, postcode_from_api = geocode_city(trial)
                        if lat is not None and lon is not None:
                            resolved_city = trial
                if (lat is None or lon is None) and "?" in city_for_fallback:
                    for variant in _variants_for_placeholder(city_for_fallback):
                        lat, lon, postcode_from_api = geocode_city(variant)
                        if lat is not None and lon is not None:
                            resolved_city = variant
                            break
                if lat is None or lon is None:
                    lat, lon, postcode_from_api = geocode_city(city_for_fallback)
                    if lat is not None and lon is not None:
                        resolved_city = city_for_fallback
                # Ha még mindig nincs találat és a string több szóból áll + van benne "?", próbáljuk csak az első szót (település) városként
                if (lat is None or lon is None) and " " in city_for_fallback and "?" in city_for_fallback:
                    first_word = city_for_fallback.split()[0]
                    # Nominatim: kipróbáljuk az ékezet nélküli (Veszto) és az ékezetes (Vésztő) formát is
                    lat, lon, postcode_from_api = geocode_city(unidecode(first_word))
                    if lat is not None and lon is not None:
                        resolved_city = unidecode(first_word)
                    if lat is None or lon is None:
                        for variant in _variants_for_placeholder(first_word):
                            lat, lon, postcode_from_api = geocode_city(variant)
                            if lat is not None and lon is not None:
                                resolved_city = variant
                                break
                    # Ha még mindig nincs: próba megyével (pl. Vésztő, Békés) – a Nominatim néha ezt találja meg
                    if lat is None or lon is None:
                        uw = unidecode(first_word)
                        for q in (f"{first_word.replace('?', 'ő')}, Békés", f"{uw}, Békés"):
                            lat, lon, postcode_from_api = geocode_city(q)
                            if lat is not None and lon is not None:
                                resolved_city = q
                                break
                search_type = "city"

        else:
            if "?" in search_string:
                for variant in _variants_for_placeholder(search_string):
                    lat, lon, postcode_from_api = geocode_city(variant)
                    if lat is not None and lon is not None:
                        search_string = variant
                        break
            if lat is None or lon is None:
                lat, lon, postcode_from_api = geocode_city(search_string)
            if lat is not None and lon is not None:
                resolved_city = search_string
            # City ág: ha a teljes string nem talált, próbáljuk az első szót és variánsait (dinamikus)
            if (lat is None or lon is None) and search_string:
                street_raw = _str_cell(row.get("Street", ""))
                first_word_orig = street_raw.split()[0] if street_raw and street_raw.strip() else None
                first_word = search_string.split()[0] if search_string.strip() else None
                if first_word and len(first_word) > 2:
                    lat, lon, postcode_from_api = geocode_city(first_word)
                    if lat is not None and lon is not None:
                        resolved_city = first_word
                if (lat is None or lon is None) and first_word_orig and "?" in first_word_orig:
                    for variant in _variants_for_placeholder(first_word_orig):
                        lat, lon, postcode_from_api = geocode_city(variant)
                        if lat is not None and lon is not None:
                            resolved_city = variant
                            break
                if (lat is None or lon is None) and first_word and first_word.isascii() and len(first_word) >= 4:
                    for variant in _ascii_city_variants(first_word):
                        lat, lon, postcode_from_api = geocode_city(variant)
                        if lat is not None and lon is not None:
                            resolved_city = variant
                            break
                # Utolsó próba: első szó o->ő, e->é (pl. Veszto->Vesztő) – mindig kipróbáljuk
                if (lat is None or lon is None) and first_word and len(first_word) >= 4:
                    trials = []
                    if "o" in first_word.lower():
                        idx = first_word.lower().rindex("o")
                        t = first_word[:idx] + ("ő" if first_word[idx] == "o" else "Ő") + first_word[idx + 1:]
                        if t != first_word:
                            trials.append(t)
                    if "e" in first_word.lower():
                        idx = first_word.lower().index("e")
                        t = first_word[:idx] + ("é" if first_word[idx] == "e" else "É") + first_word[idx + 1:]
                        if t != first_word and t not in trials:
                            trials.append(t)
                    for trial in trials:
                        if lat is not None and lon is not None:
                            break
                        lat, lon, postcode_from_api = geocode_city(trial)
                        if lat is not None and lon is not None:
                            resolved_city = trial
        if lat is not None and lon is not None:
            if search_type == "address" and resolved_city is None:
                resolved_city = city_name
            original_zip = effective_zip or ""
            if (not original_zip or original_zip == "0000") and postcode_from_api:
                zip_corrected = str(postcode_from_api)
            else:
                zip_corrected = original_zip if original_zip else ""
            return (index, lat, lon, search_type, zip_corrected, resolved_city)
        else:
            log.warning("sor %s/%s - sikertelen (nem talalhato): kereses=%s | %s", n, len(df), (search_string[:100] + "…") if search_string and len(search_string) > 100 else (search_string or "-"), _log_row_context(row))
            return (index, None, None, None, effective_zip or "", None)
    except Exception as e:
        log.exception("sor %s/%s - sikertelen (hiba): %s | %s", n, len(df), e, _log_row_context(row))
        return (index, None, None, None, effective_zip or "", None)

# Parhuzamos feldolgozas ThreadPoolExecutor-ral
results = {}
executor = ThreadPoolExecutor(max_workers=NUM_THREADS)
futures_dict = {executor.submit(process_one_row, idx): idx for idx in indices_to_process}
_interrupted = False
try:
    done = 0
    for future in as_completed(futures_dict):
        idx = futures_dict[future]
        try:
            res = future.result()
            results[res[0]] = res
        except Exception as e:
            log.exception("sor %s feldolgozasi hiba: %s | %s", idx + 1, e, _log_row_context(row))
            row = df.iloc[idx]
            _, _, _, eff_zip = build_search_info(row)
            results[idx] = (idx, None, None, None, eff_zip or "", None)
            res = results[idx]
        done += 1
        if not TEST_MODE:
            with _print_lock:
                i, lat, lon, st, zip_corr, res_city = res
                n = i + 1
                status = "sikeres" if lat is not None else "sikertelen"
                typ = st if st else "-"
                row = df.iloc[i]
                city_raw = _str_cell(row.get("City", ""))
                street_raw = _str_cell(row.get("Street", ""))
                city_show = (res_city if (lat is not None and res_city) else city_raw) or "-"
                street_show = street_raw or "-"
                W_N = 12  # n/total (pl. 12345/30636)
                W_ST = 18 # status (typ)
                W_CITY = 36
                W_CIM = 50
                W_IRSZ = 6
                W_COORD = 18
                n_str = f"{n}/{len(df)}".ljust(W_N)
                st_str = f"{status} ({typ})".ljust(W_ST)
                city_str = (city_show[:W_CITY - 1] + "…") if len(city_show) > W_CITY else city_show.ljust(W_CITY)
                cim_str = (street_show[:W_CIM - 1] + "…") if len(street_show) > W_CIM else street_show.ljust(W_CIM)
                irsz_str = (str(zip_corr) if (lat is not None and zip_corr) else "-").ljust(W_IRSZ)
                coord_str = (f"{lat:.4f}, {lon:.4f}" if lat is not None else "-").ljust(W_COORD)
                print(f"{elapsed()} - {n_str} - {st_str}  |  varos: {city_str}  |  cim: {cim_str}  |  irsz: {irsz_str}  |  {coord_str}", flush=True)
        elif done == 1 or done % 20 == 0 or done == len(indices_to_process):
            print(f"{elapsed()} - Feldolgozva: {done}/{len(indices_to_process)}", flush=True)
except KeyboardInterrupt:
    _interrupted = True
    print(f"\n{elapsed()} - Megszakitas (Ctrl+C), szalak leallitasa...", flush=True)
    for f in futures_dict:
        f.cancel()
    try:
        executor.shutdown(wait=False, cancel_futures=True)
    except TypeError:
        executor.shutdown(wait=False)
    sys.exit(1)
finally:
    if not _interrupted:
        executor.shutdown(wait=True)

for index in indices_to_process:
    r = results.get(index)
    if r is None:
        row = df.iloc[index]
        _, _, _, eff_zip = build_search_info(row)
        r = (index, None, None, None, eff_zip or "", None)
    _, lat, lon, st, zip_corr, res_city = r
    latitudes.append(lat)
    longitudes.append(lon)
    search_types.append(st)
    zip_corrected_list.append(zip_corr)
    resolved_city_list.append(res_city)

# DataFrame csak a feldolgozott sorokkal (tesztmódban kevesebb, --row N esetén csak az N. sor)
if row_filter:
    row_start, row_end = row_filter
    row_end = min(row_end, len(df))
    df_out = df.iloc[row_start:row_end].copy()
else:
    df_out = df.iloc[:len(latitudes)].copy()
df_out["latitude"] = latitudes
df_out["longitude"] = longitudes
df_out["search_type"] = search_types
df_out["Zip_corrected"] = zip_corrected_list
# Street és City normalizált (javított) formában a kimenetbe: ? -> ő, nan kiszűrés, u. -> utca, stb.
for i in range(len(df_out)):
    idx = df_out.index[i]
    if "Street" in df_out.columns:
        val = df_out.at[idx, "Street"]
        if val is not None and str(val).strip():
            df_out.at[idx, "Street"] = _normalize_street_for_output(val)
    if "City" in df_out.columns:
        val = df_out.at[idx, "City"]
        if val is not None and str(val).strip():
            df_out.at[idx, "City"] = _normalize_city_for_output(val)

# Sikeres geokódolásnál: ha az eredeti City üres/unknow vagy Zip 0000/üres, felülírjuk a feloldott értékekkel
for i in range(len(df_out)):
    idx = df_out.index[i]
    if resolved_city_list[i] is not None and "City" in df_out.columns:
        cur = df_out.at[idx, "City"]
        if cur is None or not str(cur).strip() or str(cur).strip().lower() == "unknow":
            city_val = resolved_city_list[i]
            if "," in str(city_val):
                city_val = str(city_val).split(",")[0].strip()
            df_out.at[idx, "City"] = city_val
    if zip_corrected_list[i] and "Zip" in df_out.columns:
        cur = df_out.at[idx, "Zip"]
        if cur is None or not str(cur).strip() or str(cur).strip() == "0000":
            df_out.at[idx, "Zip"] = zip_corrected_list[i]

if not TEST_MODE:
    df_out.to_csv("geocoded_output.csv", sep=";", index=False, encoding="utf-8")
    print(f"\n{elapsed()} - [OK] Feldolgozas kesz!")
    print(f"{elapsed()} - Eredmények mentve: geocoded_output.csv")
    print(f"{elapsed()} - Város szintű: {sum(1 for t in search_types if t == 'city')}")
    print(f"{elapsed()} - Utca szintű: {sum(1 for t in search_types if t == 'address')}")
    print(f"{elapsed()} - Sikertelen: {sum(1 for t in search_types if t is None)}")
    failed = sum(1 for t in search_types if t is None)
    log.info("=== geo.py futás vége - város: %s, utca: %s, sikertelen: %s, fájl: geocoded_output.csv",
             sum(1 for t in search_types if t == "city"),
             sum(1 for t in search_types if t == "address"),
             failed)
else:
    print(f"\n{elapsed()} - [TESZT KÉSZ] {len(latitudes)} sor feldolgozva. Nem írtunk geocoded_output.csv-t.")
    log.info("=== geo.py teszt futás vége (%s sor)", len(latitudes))