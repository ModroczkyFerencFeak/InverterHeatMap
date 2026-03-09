# Push elott ellenorzi a megadott felhasznalonev + jelszo hash-et a .push-auth fajlhoz kepest.
# A .git/hooks/pre-push hivja. Kilepeskod: 0 = OK, 1 = elutasitva.

$ErrorActionPreference = "Stop"
# A hook a repo gyokeret hasznalja cwd-kent
$repoRoot = (Get-Location).Path
$authFile = Join-Path $repoRoot ".push-auth"

if (-not (Test-Path $authFile)) {
    Write-Host "Push vedelem: nincs beallitva. Eloszor futtasd: .\scripts\setup-push-auth.ps1" -ForegroundColor Red
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

Write-Host "Push: felhasznalonev es jelszo megadasa (a .push-auth-hoz beallitott)." -ForegroundColor Cyan
$user = Read-Host "Felhasznalonev"
$sec  = Read-Host "Jelszo" -AsSecureString
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
$pass = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) | Out-Null

$sha = [System.Security.Cryptography.SHA256]::Create()
$bytes = [System.Text.Encoding]::UTF8.GetBytes($pass)
$hash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-","").ToLowerInvariant()

if ($user -ne $storedUser -or $hash -ne $storedHash) {
    Write-Host "Hibas felhasznalonev vagy jelszo. A push megtagadva." -ForegroundColor Red
    exit 1
}
exit 0
