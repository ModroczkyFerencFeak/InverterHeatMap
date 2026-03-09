# Web oldal megtekintesere: bejelentkezesi adatok beallitasa.
# A jelszo csak hash-elt formaban kerul a .env fajlba (.env nincs a gitben).
# Ezutan a start-server.bat inditotta szerver csak ezzel a parossal engedi meg az oldal megtekinteset.

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = (Get-Item $root).Parent.FullName
Set-Location $repoRoot

$envFile = Join-Path $repoRoot ".env"
$envContent = @{}
if (Test-Path $envFile) {
    Get-Content $envFile -Encoding UTF8 | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') { $envContent[$Matches[1].Trim()] = $Matches[2].Trim() }
    }
}

Write-Host "Oldal megtekintese: beallitando felhasznalonev es jelszo (ezt keri a bongeszo az oldal megnyitasakor)." -ForegroundColor Cyan
$user = Read-Host "Felhasznalonev"
$sec  = Read-Host "Jelszo" -AsSecureString
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
$pass = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) | Out-Null

$sha = [System.Security.Cryptography.SHA256]::Create()
$bytes = [System.Text.Encoding]::UTF8.GetBytes($pass)
$hash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-","").ToLowerInvariant()

$envContent["WEB_AUTH_USER"] = $user
$envContent["WEB_AUTH_HASH"] = $hash
$lines = $envContent.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }
$lines | Set-Content -Path $envFile -Encoding UTF8

$authConfigPath = Join-Path $repoRoot "auth-config.js"
$authJs = "// Megtekinteshez szukseges belepes (ugyanaz, mint a .env-ben). Generalva: setup-web-auth.ps1`n"
$authJs += "window.__AUTH_USER__ = '$user';`n"
$authJs += "window.__AUTH_HASH__ = '$hash';`n"
Set-Content -Path $authConfigPath -Value $authJs -Encoding UTF8

Write-Host "Kesz. A .env fajlban elmentve (WEB_AUTH_USER, WEB_AUTH_HASH). Inditsd a start-server.bat-ot, majd a bongeszo megkeri a felhasznalonevet es jelszot." -ForegroundColor Green
Write-Host "Az auth-config.js is frissitve (statikus oldal / GitHub Pages belepeshez)." -ForegroundColor Green
