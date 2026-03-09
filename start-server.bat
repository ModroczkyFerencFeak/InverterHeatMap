@echo off
title Geomap Szerver
cd /d "%~dp0"

echo.
echo [Geomap] Szerver inditasa (jelszavas megtekintes) a 8080-as porton...
echo.
echo Eloszor allitsd be a felhasznalot es jelszot:  scripts\setup-web-auth.ps1
echo Ha mar beallitottad, inditsd a szervert, majd a bongeszo megkeri az adatokat.
echo.
echo Ha megjelenik "Geomap szerver (jelszavas)...",
echo   nyisd meg:  http://127.0.0.1:8080/
echo.
echo NE zard be ezt az ablakot, amig hasznalod a terkepet.
echo Kilepes: Ctrl+C, majd egy billentyu.
echo.
pause

where py >nul 2>&1
if %errorlevel% equ 0 (
  py server_with_auth.py
) else (
  python server_with_auth.py
)
if errorlevel 1 (
  echo.
  echo HIBA: A szerver nem indult. Telepitsd a Pythont: https://www.python.org/downloads/
)
echo.
pause
