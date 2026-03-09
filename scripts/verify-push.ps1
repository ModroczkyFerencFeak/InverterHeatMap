# Push elott ellenorzi a megadott felhasznalonev + jelszo hash-et a .push-auth fajlhoz kepest.
# A .git/hooks/pre-push hivja. Kilepeskod: 0 = OK, 1 = elutasitva.
# Ha a hook nem redirectalja a stdint (pl. exec 0</dev/tty), a Git ref lista kerulne a Read-Host-ba – ezert eldobjuk.
#
# Nem interaktiv kornyezetben (pl. IDE, Cursor): a push akadalyozva lehet.
# Megoldas 1: git push --no-verify  (kihagyja a hookot)
# Megoldas 2: $env:SKIP_PUSH_AUTH='1'; git push  (a hook engedelyez, kerdes nelkul)

$ErrorActionPreference = "Stop"
# Git a ref listat adja a stdinnen; olvassuk ki es dobjuk el, hogy a Read-Host ne azt kapja
try {
    while ($null -ne ($null = [Console]::In.ReadLine())) { }
} catch { }

# A hook a repo gyokeret hasznalja cwd-kent
$repoRoot = (Get-Location).Path
$authFile = Join-Path $repoRoot ".push-auth"

# Opcionalis: kerdes nelkul engedelyez (pl. nem interaktiv push)
if ($env:SKIP_PUSH_AUTH -eq '1') {
    exit 0
}
# Ha nincs interaktiv terminal (pl. IDE-bol push), ne blokkoljuk a push-t
if (-not [Environment]::UserInteractive) {
    exit 0
}

if (-not (Test-Path $authFile)) {
    Write-Host "Push vedelem: nincs beallitva. Eloszor futtasd: .\scripts\setup-push-auth.ps1" -ForegroundColor Red
    Write-Host "  (Megadod egy felhasznalot es jelszot, utana push-kor ugyanazt kell beirni.)" -ForegroundColor Yellow
    exit 1
}

$content = Get-Content -Path $authFile -Raw
$content = ($content -split "`n")[0].Trim()
if (-not $content -or $content -notmatch "^([^:]+):(.+)$") {
    Write-Host "Push vedelem: hibas .push-auth formatum." -ForegroundColor Red
    exit 1
}
$storedUser = $Matches[1]
$storedHash = $Matches[2].Trim().ToLowerInvariant()

Write-Host "Push: felhasznalonev es jelszo (a .push-auth-hoz beallitott)." -ForegroundColor Cyan
# A Git a ref listat a stdinnen kuldi, ezert kozvetlen Read-Host a pipe-bol olvasna.
# Windows: CON-bol olvassuk (billentyűzet), kulon prompt: jelszo maszkolt (SecureString), csak a hash kerul at.
$user = $null
$inputHash = $null
if ($env:OS -eq 'Windows_NT') {
    $userFile = [System.IO.Path]::GetTempFileName()
    $hashFile = [System.IO.Path]::GetTempFileName()
    $env:GEOMAP_PUSH_USER_FILE = $userFile
    $env:GEOMAP_PUSH_HASH_FILE = $hashFile
    try {
        $cmdUser = "(Read-Host 'Felhasznalonev').Trim() | Set-Content -LiteralPath `$env:GEOMAP_PUSH_USER_FILE -Encoding UTF8"
        & cmd /c "powershell -NoProfile -Command `"$cmdUser`" < CON"
        $hashPs1 = [System.IO.Path]::GetTempFileName() + '.ps1'
        @'
$sec = Read-Host 'Jelszo' -AsSecureString
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
$pass = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) | Out-Null
$sha = [System.Security.Cryptography.SHA256]::Create()
$bytes = [System.Text.Encoding]::UTF8.GetBytes($pass)
$h = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-","").ToLowerInvariant()
$h | Set-Content -LiteralPath $env:GEOMAP_PUSH_HASH_FILE -Encoding UTF8
'@ | Set-Content -LiteralPath $hashPs1 -Encoding UTF8
        try {
            & cmd /c "powershell -NoProfile -ExecutionPolicy Bypass -File `"$hashPs1`" < CON"
        } finally {
            if (Test-Path $hashPs1) { Remove-Item -LiteralPath $hashPs1 -Force -ErrorAction SilentlyContinue }
        }
        $user = (Get-Content -LiteralPath $userFile -Raw -ErrorAction SilentlyContinue) -replace "`r`n?",""
        $inputHash = (Get-Content -LiteralPath $hashFile -Raw -ErrorAction SilentlyContinue) -replace "`r`n?",""
    } finally {
        if (Test-Path $userFile) { Remove-Item -LiteralPath $userFile -Force -ErrorAction SilentlyContinue }
        if (Test-Path $hashFile) { Remove-Item -LiteralPath $hashFile -Force -ErrorAction SilentlyContinue }
        $env:GEOMAP_PUSH_USER_FILE = $null
        $env:GEOMAP_PUSH_HASH_FILE = $null
    }
} else {
    $user = Read-Host "Felhasznalonev"
    $sec  = Read-Host "Jelszo" -AsSecureString
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    $pass = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) | Out-Null
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($pass)
    $inputHash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-","").ToLowerInvariant()
}
if (-not $user -or -not $inputHash) {
    Write-Host "Ures felhasznalonev vagy jelszo." -ForegroundColor Red
    exit 1
}

if ($user -ne $storedUser -or ($inputHash.Trim().ToLowerInvariant()) -ne $storedHash) {
    Write-Host "Hibas felhasznalonev vagy jelszo. A push megtagadva." -ForegroundColor Red
    exit 1
}
exit 0
