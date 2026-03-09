# Geomap helyi szerver - futtasd a Cursor/VS Code termináljában (PowerShell)
Set-Location $PSScriptRoot
Write-Host ""
Write-Host "[Geomap] Szerver inditasa a mappaban: $PSScriptRoot" -ForegroundColor Cyan
Write-Host "Nyisd meg a bongeszoben: http://127.0.0.1:8080/" -ForegroundColor Green
Write-Host "Leallas: Ctrl+C" -ForegroundColor Yellow
Write-Host ""
try {
  py -m http.server 8080
} catch {
  python -m http.server 8080
}
