[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repositoryRoot 'frontend'

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw 'npm não está disponível no PATH; consulte docs/development.md.'
}

if (-not (Test-Path -LiteralPath (Join-Path $frontendRoot 'node_modules') -PathType Container)) {
    throw 'Dependências ausentes: execute npm ci em frontend/ conforme docs/development.md.'
}

Push-Location $frontendRoot
try {
    & npm start -- --host 127.0.0.1 --port 4200
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
