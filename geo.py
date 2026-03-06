import requests
import pandas as pd
import time
import sys
from functools import lru_cache
from unidecode import unidecode

print("geo.py indul...", flush=True)

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
    time.sleep(WAIT_BEFORE_START)

def _str_cell(v):
    """CSV cella loghoz: nan/None -> üres string."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).strip()
    return "" if s.lower() == "nan" else s

df = pd.read_csv(
    "IccExport20260217.csv",
    sep=";",
    encoding="latin1",
    dtype=str
)

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
            
            response = requests.get(url, params=params, timeout=30, headers=headers)
            if response.status_code == 429:
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
            return None, None, None
        except Exception as e:
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
            
            response = requests.get(url, params=params, timeout=30, headers=headers)
            if response.status_code == 429:
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
            return None, None, None
        except Exception as e:
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
    street_type = str(row.get("StreetType", "")).strip()
    street_no = str(row.get("StreetNo", "")).strip()
    building = str(row.get("Building", "")).strip()

    if "," in city_str:
        city_name = city_str.split(",")[0].strip()
    else:
        city_name = city_str

    city_name_clean = unidecode(city_name)
    street_clean = unidecode(street)
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

latitudes = []
longitudes = []
search_types = []  # Track whether this was city or address level
zip_corrected_list = []  # Nominatimból lekérült irányítószám, ha az eredeti 0000/üres

start_time = time.time()

def elapsed():
    t = time.time() - start_time
    return f"[{int(t // 60):02d}:{int(t % 60):02d}]"

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
            time.sleep(1)
        if (lat is None or lon is None) and search_str:
            lat, lon, _ = geocode_city(cname)
            time.sleep(1)
        if lat is not None and lon is not None:
            print(f"{elapsed()} - Első sor címe megvan: {lat:.4f}, {lon:.4f} (Debrecen, Károli Gáspár u. 414…)", flush=True)
            break
        geocode_address.cache_clear()
        geocode_city.cache_clear()
        print(f"{elapsed()} - Nem található, 60 mp múlva újrapróbálkozás…", flush=True)
        time.sleep(60)
else:
    print(f"{elapsed()} - Első sornak nincs kereshető címe, folytatás.", flush=True)

# A ciklus előtt még 1 mp szünet (Nominatim limit)
time.sleep(1)

limit = 5 if TEST_MODE else len(df)
if TEST_MODE:
    print(f"{elapsed()} - [TESZT MÓD] Csak az első {limit} sor feldolgozása, a küldött cím és válasz kiírva.\n", flush=True)

for index, row in df.iterrows():
    if index >= limit:
        break
    n = index + 1

    search_type, search_string, city_name, effective_zip = build_search_info(row)
    
    if not search_string:
        latitudes.append(None)
        longitudes.append(None)
        search_types.append(None)
        zip_corrected_list.append(effective_zip or "")
        if TEST_MODE:
            print(f"{elapsed()} - [{n}] CSV City: {row.get('City', '')[:70]}", flush=True)
            print(f"{elapsed()} -        -> sikertelen (adat hiányzik)\n", flush=True)
        else:
            print(f"{elapsed()} - {n}/{len(df)} - sikertelen (adat hiányzik)  |  {row_address_summary(row)}", flush=True)
        if n % 100 == 0 and not TEST_MODE:
            success_count = sum(1 for t in search_types[-100:] if t is not None)
            print(f"{elapsed()} - --- {n}/{len(df)}: {success_count}/100 sikeres ---", flush=True)
        continue

    lat = None
    lon = None
    
    try:
        if search_type == "address":
            lat, lon, postcode_from_api = geocode_address(search_string)
            if lat is None or lon is None:
                time.sleep(1)  # 1 kérés/mp a fallback előtt
                lat, lon, postcode_from_api = geocode_city(city_name)
                search_type = "city"

        else:
            lat, lon, postcode_from_api = geocode_city(search_string)

        if lat is not None and lon is not None:
            latitudes.append(lat)
            longitudes.append(lon)
            search_types.append(search_type)
            original_zip = effective_zip or ""
            if (not original_zip or original_zip == "0000") and postcode_from_api:
                zip_corrected_list.append(str(postcode_from_api))
            else:
                zip_corrected_list.append(original_zip if original_zip else "")
            if search_type == "address":
                label = (search_string[:50] + "…") if len(search_string) > 50 else search_string
            else:
                label = city_name
            extra = ""
            if (not original_zip or original_zip == "0000") and postcode_from_api:
                extra = f"  |  irányítószám korrigálva: {original_zip or '(üres)'} → {postcode_from_api}"
            if TEST_MODE:
                print(f"{elapsed()} - [{n}] CSV City: {str(row.get('City', ''))[:70]}", flush=True)
                print(f"{elapsed()} -        Küldött ({search_type}): {search_string[:80]}{'…' if len(search_string) > 80 else ''}", flush=True)
                print(f"{elapsed()} -        Válasz: {lat:.5f}, {lon:.5f} (sikeres)\n", flush=True)
            else:
                print(f"{elapsed()} - {n}/{len(df)} - sikeres ({search_type}): {label}  |  {row_address_summary(row)}{extra}", flush=True)
        else:
            latitudes.append(None)
            longitudes.append(None)
            search_types.append(None)
            zip_corrected_list.append(effective_zip or "")
            if TEST_MODE:
                print(f"{elapsed()} - [{n}] CSV City: {str(row.get('City', ''))[:70]}", flush=True)
                print(f"{elapsed()} -        Küldött ({search_type}): {search_string[:80]}{'…' if len(search_string) > 80 else ''}", flush=True)
                print(f"{elapsed()} -        Válasz: nem található\n", flush=True)
            else:
                print(f"{elapsed()} - {n}/{len(df)} - sikertelen (nem található): {city_name}  |  {row_address_summary(row)}", flush=True)

    except Exception as e:
        latitudes.append(None)
        longitudes.append(None)
        search_types.append(None)
        zip_corrected_list.append(effective_zip or "")
        if TEST_MODE:
            print(f"{elapsed()} - [{n}] CSV City: {str(row.get('City', ''))[:70]}", flush=True)
            print(f"{elapsed()} -        Hiba: {e}\n", flush=True)
        else:
            print(f"{elapsed()} - {n}/{len(df)} - sikertelen (hiba): {e}  |  {row_address_summary(row)}", flush=True)
    
    if n % 100 == 0 and not TEST_MODE:
        success_count = sum(1 for t in search_types[-100:] if t is not None)
        print(f"{elapsed()} - --- {n}/{len(df)}: {success_count}/100 sikeres ---", flush=True)
    
    # Nominatim: max 1 kérés/másodperc – minden API hívást tartalmazó sor után 1 mp szünet
    if search_string:
        time.sleep(1)

# DataFrame csak a feldolgozott sorokkal (tesztmódban kevesebb)
df_out = df.iloc[:len(latitudes)].copy()
df_out["latitude"] = latitudes
df_out["longitude"] = longitudes
df_out["search_type"] = search_types
df_out["Zip_corrected"] = zip_corrected_list

if not TEST_MODE:
    df_out.to_csv("geocoded_output.csv", sep=";", index=False)
    print(f"\n{elapsed()} - ✓ Feldolgozás kész!")
    print(f"{elapsed()} - Eredmények mentve: geocoded_output.csv")
    print(f"{elapsed()} - Város szintű: {sum(1 for t in search_types if t == 'city')}")
    print(f"{elapsed()} - Utca szintű: {sum(1 for t in search_types if t == 'address')}")
    print(f"{elapsed()} - Sikertelen: {sum(1 for t in search_types if t is None)}")
else:
    print(f"\n{elapsed()} - [TESZT KÉSZ] {len(latitudes)} sor feldolgozva. Nem írtunk geocoded_output.csv-t.")