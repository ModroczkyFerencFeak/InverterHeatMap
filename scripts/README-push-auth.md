# Push védelem (felhasználónév + jelszó)

A `git push` csak akkor megy végbe, ha megadod a beállított felhasználónevet és jelszót.

---

## Gyors lépések: hogyan tölts fel jelszóval

**1. Beállítás (csak egyszer)**  
A projekt mappájában (Geomap) nyiss PowerShell-t, és futtasd:

```powershell
.\scripts\setup-push-auth.ps1
```

- Beírod a **felhasználónevet** (pl. `admin`), Enter.
- Beírod a **jelszót** (nem látszik, amikor gépeled), Enter.
- Ettől kezdve ez a pár lesz a push jelszava.

**2. Feltöltés (minden push-nál)**  
Ugyanebben a mappában:

```powershell
git add .
git commit -m "üzenet"
git push origin main
```

- A **push** után a terminál megkéri: **Felhasználónév:** → add meg ugyanazt, amit a beállításnál megadtál.
- Aztán: **Jelszó:** → add meg ugyanazt a jelszót.
- Ha jó, a feltöltés végigmegy. Ha rossz, „Hibás felhasználónév vagy jelszó”, és a push megáll.

---

## Részletesen

### Beállítás (egyszer)

```powershell
.\scripts\setup-push-auth.ps1
```

Meg kell adnod egy felhasználónevet és egy jelszót. Ezek kerülnek eltárolásra (a jelszó SHA-256 hash-ként). A `.push-auth` fájl a `.gitignore` miatt nem kerül fel a távoli repóba.

### Push

Amikor `git push`-t futtatsz, a hook megkéri a felhasználónevet és a jelszót. Ha egyezik a beállított értékkel, a push folytatódik; különben megtagadásra kerül.

---

# Oldal megtekintése (böngésző): jelszó + felhasználónév

Az oldal (heatmap) megtekintéséhez a szerver csak akkor adja ki a tartalmat, ha a böngészőben megadod a beállított felhasználónevet és jelszót (HTTP Basic Auth).

## Beállítás (egyszer)

A repo gyökeréből futtasd (PowerShell):

```powershell
.\scripts\setup-web-auth.ps1
```

Megadod a **felhasználónevet** és a **jelszót**, amit később a böngésző kér az oldal megnyitásakor. A jelszó SHA-256 hash-ként kerül a **`.env`** fájlba (`WEB_AUTH_USER`, `WEB_AUTH_HASH`). A `.env` a `.gitignore` miatt nem kerül a gitbe.

## Használat

1. Indítsd a szervert: **start-server.bat**
2. Böngészőben nyisd meg: **http://127.0.0.1:8080/**
3. A böngésző megjeleníti a bejelentkezési ablakot (felhasználónév + jelszó). Add meg a **setup-web-auth.ps1**-ben beállított adatokat; csak ezután jelenik meg a térkép.

---

## Fájlok (push)

- `scripts/setup-push-auth.ps1` – egyszeri beállítás
- `scripts/verify-push.ps1` – push előtti ellenőrzés (a hook hívja)
- `.git/hooks/pre-push` – hook, amely a verify scriptet futtatja
- `.push-auth` – tárolt `felhasznalo:jelszo_hash` (ne commitold)

## Fájlok (oldal megtekintése)

- `scripts/setup-web-auth.ps1` – egyszeri beállítás (böngészős belépés)
- `server_with_auth.py` – jelszavas HTTP szerver; a `.env`-ből olvassa a `WEB_AUTH_USER` és `WEB_AUTH_HASH` értékeket
- `.env` – `WEB_AUTH_USER` és `WEB_AUTH_HASH` (ne commitold)
