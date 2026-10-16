[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repositoryRoot 'simulador_metas_cnj'
$python = Join-Path $backendRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Ambiente ausente: crie simulador_metas_cnj/.venv conforme docs/development.md."
}

Push-Location $backendRoot
try {
    & $python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
