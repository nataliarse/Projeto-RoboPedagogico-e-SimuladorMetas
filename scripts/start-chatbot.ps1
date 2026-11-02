[CmdletBinding()]
param(
    [string]$HostName = $(if ($env:CHATBOT_HOST) { $env:CHATBOT_HOST } else { '127.0.0.1' }),
    [int]$Port = $(if ($env:CHATBOT_PORT) { [int]$env:CHATBOT_PORT } else { 8000 })
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repositoryRoot 'chatbot_processual_ai'
$python = Join-Path $backendRoot '.venv\Scripts\python.exe'

if ($Port -lt 1 -or $Port -gt 65535) {
    throw "Porta inválida para o chatbot: $Port"
}

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Ambiente ausente: crie chatbot_processual_ai/.venv conforme docs/development.md."
}

Push-Location $backendRoot
try {
    & $python -m uvicorn api:app --reload --host $HostName --port $Port
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
