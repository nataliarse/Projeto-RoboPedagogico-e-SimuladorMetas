[CmdletBinding()]
param(
    [string]$HostName = $(if ($env:SIMULADOR_HOST) { $env:SIMULADOR_HOST } else { '127.0.0.1' }),
    [int]$Port = $(if ($env:SIMULADOR_PORT) { [int]$env:SIMULADOR_PORT } else { 8001 })
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repositoryRoot 'simulador_metas_cnj'
$python = Join-Path $backendRoot '.venv\Scripts\python.exe'

if ($Port -lt 1 -or $Port -gt 65535) {
    throw "Porta inválida para o simulador: $Port"
}

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Ambiente ausente: crie simulador_metas_cnj/.venv conforme docs/development.md."
}

Push-Location $backendRoot
try {
    & $python -m uvicorn main:app --reload --host $HostName --port $Port
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
