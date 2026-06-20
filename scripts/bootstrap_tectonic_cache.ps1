# Popula arquivos/tectonic-cache/ no Windows (com internet).
# Depois rode: tar -czf tectonic-cache.tgz -C arquivos tectonic-cache
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$CacheDir = if ($env:TECTONIC_CACHE_DIR) { $env:TECTONIC_CACHE_DIR } else { Join-Path $Root "arquivos\tectonic-cache" }
$Bin = if ($env:TECTONIC_BIN_DIR) { Join-Path $env:TECTONIC_BIN_DIR "tectonic.exe" } else { Join-Path $Root "bin\tectonic.exe" }
$TemplateDir = Join-Path $Root "arquivos\ieee-template"
$Tex = "conference_101719.tex"

New-Item -ItemType Directory -Force -Path $CacheDir | Out-Null
$env:TECTONIC_CACHE_DIR = $CacheDir

if (-not (Test-Path $Bin)) {
    Write-Error "Tectonic não encontrado: $Bin"
}

if (-not (Test-Path (Join-Path $TemplateDir $Tex))) {
    Push-Location $Root
    python -c "from app import create_app; from app.articles.ieee_latex_assets import ensure_template_dir; app=create_app(); app.app_context().push(); ensure_template_dir(app.config['BRAND_ASSETS_FOLDER'])"
    Pop-Location
}

Push-Location $TemplateDir
& $Bin -X compile --outdir $TemplateDir $Tex
Pop-Location

Write-Host ""
Write-Host "Cache pronto em: $CacheDir"
Get-ChildItem -Recurse $CacheDir | Measure-Object -Property Length -Sum | ForEach-Object {
    Write-Host ("Tamanho: {0:N2} MB" -f ($_.Sum / 1MB))
}
Write-Host "Empacote: tar -czf tectonic-cache.tgz -C arquivos tectonic-cache"
