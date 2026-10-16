[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repositoryRoot 'chatbot_processual_ai'
$python = Join-Path $backendRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Ambiente ausente: crie chatbot_processual_ai/.venv conforme docs/development.md."
}

Push-Location $backendRoot
try {
    & $python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
