# GitHub Pages – térkép megtekintése (privát repó)

## Kötelező első lépés: Pages forrás beállítása (egyszer)

A **"Create Pages site failed" / "Resource not accessible by integration"** elkerüléséhez a workflow **nem** tudja automatikusan bekapcsolni a Pages-t – ezt neked kell megtenned a repó beállításaiban:

1. Nyisd meg a repót a GitHubon → **Settings** → **Pages**
2. **Build and deployment** → **Source**: válaszd a **GitHub Actions** lehetőséget (ne „Deploy from a branch”).
3. Mentsd a beállítást.

Ha ezt nem állítod be, a deploy workflow mindig hibázni fog. Beállítás után pusholj a `main`-re (vagy futtasd a workflowot kézzel), és a deploy lefut.

## Privát repó + belépés

- A repó **privát**, ezért a Pages URL-t csak olyan felhasználók érik el, akiknek **van hozzáférése** a repóhoz (pl. te vagy közreműködők).
- A térkép oldal betöltésekor megjelenik a **bejelentkezési ablak** (auth gate). Add meg a felhasználónevet és a jelszót (ugyanaz, amit a lokális oldalhoz használsz, pl. az `auth-config.js` / `setup-web-auth.ps1` alapján).
- Ha nincs repo hozzáférésed, a böngésző nem tudja megnyitni a Pages URL-t (404 / Not Found). Ha van hozzáférésed, a lap betöltődik, és a térkép csak a helyes belépés után látszik.

**Összefoglalva:** GitHub bejelentkezés (repo hozzáférés) → Pages URL megnyitása → térkép oldal belépő (felhasználónév + jelszó) → térkép megtekintése.

---

## Vercel (privát repó, titkok .env helyett)

Ha Vercelre deployolsz, a belépő **ne legyen a repóban**, hanem a **Vercel Environment Variables**-ban:

1. **Vercel** → projekt → **Settings** → **Environment Variables**
2. Add hozzá (ne a nyers jelszót, hanem a **hash**-t):
   - **AUTH_USER** = `FEAK-ADMIN` (vagy a felhasználónév)
   - **AUTH_HASH** = a jelszó SHA-256 hash-e, kisbetűs hex (pl. `c1ca4c33...`)
3. A build (`node scripts/build-auth.js`) ezekből generálja az `auth-config.js`-t, a repóban nincs titkos adat.

Hash készítése helyben (PowerShell):  
`[BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes('Jelszó'))).Replace('-','').ToLowerInvariant()`

