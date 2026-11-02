[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

Push-Location (Join-Path $root 'chatbot_processual_ai')
try {
    & '.\.venv\Scripts\python.exe' -m pytest tests\test_api_processual_chat.py tests\test_meta_simulator_adapter.py -q -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }

Push-Location (Join-Path $root 'simulador_metas_cnj')
try {
    & '.\.venv\Scripts\python.exe' -m unittest tests.test_contracts -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }

$portableNode = Join-Path $root '.tools\node-v24.19.0-win-x64'
if (Test-Path $portableNode) { $env:Path = "$portableNode;$env:Path" }
Push-Location (Join-Path $root 'frontend')
try {
    npm test -- --watch=false --include='**/chat.spec.ts' --include='**/simulador-api.service.spec.ts'
    exit $LASTEXITCODE
} finally { Pop-Location }
