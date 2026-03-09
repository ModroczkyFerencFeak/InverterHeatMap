# Push védelem beállítása: egy felhasználónév és jelszó (hash-elt tárolás).
# Egyszer futtasd, majd git push-kor ezt a párost kell megadni.
# A jelszó csak hash-elt formában kerül a .push-auth fájlba (.push-auth nincs a gitben).

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = (Get-Item $root).Parent.FullName
Set-Location $repoRoot

$authFile = Join-Path $repoRoot ".push-auth"
if (Test-Path $authFile) {
    $over = Read-Host "A .push-auth mar letezik. Felulirod? (i/n)"
    if ($over -ne "i" -and $over -ne "I") { exit 0 }
}

Write-Host "Push vedelem: beallitando felhasznalonev es jelszo (ezt kell majd push-kor megadni)." -ForegroundColor Cyan
$user = Read-Host "Felhasznalonev"
$sec  = Read-Host "Jelszo" -AsSecureString
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
$pass = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) | Out-Null

$sha = [System.Security.Cryptography.SHA256]::Create()
$bytes = [System.Text.Encoding]::UTF8.GetBytes($pass)
$hash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-","").ToLowerInvariant()
$line = "$user`:$hash"
$line | Set-Content -Path $authFile -Encoding UTF8 -NoNewline
Write-Host "Kesz. A .push-auth letrejott (hash-elt jelszo). Push-kor ezt a felhasznalot es jelszot kell megadni." -ForegroundColor Green
