[CmdletBinding()]
param(
    [string]$HostName = $(if ($env:FRONTEND_HOST) { $env:FRONTEND_HOST } else { '127.0.0.1' }),
    [int]$Port = $(if ($env:FRONTEND_PORT) { [int]$env:FRONTEND_PORT } else { 4200 })
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repositoryRoot 'frontend'

if ($Port -lt 1 -or $Port -gt 65535) {
    throw "Porta inválida para o frontend: $Port"
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw 'npm não está disponível no PATH; consulte docs/development.md.'
}

if (-not (Test-Path -LiteralPath (Join-Path $frontendRoot 'node_modules') -PathType Container)) {
    throw 'Dependências ausentes: execute npm ci em frontend/ conforme docs/development.md.'
}

Push-Location $frontendRoot
try {
    & npm start -- --host $HostName --port $Port
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
