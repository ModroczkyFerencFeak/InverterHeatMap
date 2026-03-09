# GitHub Pages – térkép megtekintése (privát repó)

## Először: Pages beállítása (egyszer)

A **"Get Pages site failed"** elkerüléséhez a repóban:

1. Nyisd meg: **Settings** → **Pages**
2. **Build and deployment** → **Source**: válaszd a **GitHub Actions** lehetőséget (ne Branch).
3. Mentsd a beállítást.

Ezután a `main` branchre pusholáskor a **Deploy to GitHub Pages** workflow lefut és feltölti a térképet.

## Privát repó + belépés

- A repó **privát**, ezért a Pages URL-t csak olyan felhasználók érik el, akiknek **van hozzáférése** a repóhoz (pl. te vagy közreműködők).
- A térkép oldal betöltésekor megjelenik a **bejelentkezési ablak** (auth gate). Add meg a felhasználónevet és a jelszót (ugyanaz, amit a lokális oldalhoz használsz, pl. az `auth-config.js` / `setup-web-auth.ps1` alapján).
- Ha nincs repo hozzáférésed, a böngésző nem tudja megnyitni a Pages URL-t (404 / Not Found). Ha van hozzáférésed, a lap betöltődik, és a térkép csak a helyes belépés után látszik.

**Összefoglalva:** GitHub bejelentkezés (repo hozzáférés) → Pages URL megnyitása → térkép oldal belépő (felhasználónév + jelszó) → térkép megtekintése.
