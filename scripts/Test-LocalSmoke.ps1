[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$processes = [System.Collections.Generic.List[System.Diagnostics.Process]]::new()
$logs = Join-Path $env:TEMP 'robo-metas-smoke'
New-Item -ItemType Directory -Path $logs -Force | Out-Null

function Start-LocalProcess($file, $arguments, $workingDirectory, $name) {
    $process = Start-Process -FilePath $file -ArgumentList $arguments `
        -WorkingDirectory $workingDirectory -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $logs "$name.out.log") `
        -RedirectStandardError (Join-Path $logs "$name.err.log")
    $processes.Add($process)
}

function Wait-Http($uri) {
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try { return Invoke-WebRequest -UseBasicParsing -Uri $uri -TimeoutSec 2 }
        catch { Start-Sleep -Milliseconds 500 }
    }
    throw "Serviço não respondeu: $uri. Logs: $logs"
}

try {
    $chatRoot = Join-Path $root 'chatbot_processual_ai'
    $simRoot = Join-Path $root 'simulador_metas_cnj'
    $frontRoot = Join-Path $root 'frontend'
    $chatPython = Join-Path $chatRoot '.venv\Scripts\python.exe'
    $simPython = Join-Path $simRoot '.venv\Scripts\python.exe'
    $nodeRoot = Join-Path $root '.tools\node-v24.19.0-win-x64'
    $node = Join-Path $nodeRoot 'node.exe'
    $ng = Join-Path $frontRoot 'node_modules\@angular\cli\bin\ng.js'

    $env:OLLAMA_BASE_URL = 'http://127.0.0.1:9'
    $env:OLLAMA_TIMEOUT_SECONDS = '1'
    $env:RAG_ENABLED = 'false'

    Start-LocalProcess $chatPython @('-m','uvicorn','api:app','--host','127.0.0.1','--port','8000') $chatRoot 'chatbot'
    Start-LocalProcess $simPython @('-m','uvicorn','main:app','--host','127.0.0.1','--port','8001') $simRoot 'simulador'
    Start-LocalProcess $node @($ng,'serve','--host','127.0.0.1','--port','4200') $frontRoot 'frontend'

    $chatHealth = (Wait-Http 'http://127.0.0.1:4200/api/processos/health').Content | ConvertFrom-Json
    $simHealth = (Wait-Http 'http://127.0.0.1:4200/api/simulador/health').Content | ConvertFrom-Json
    if ($chatHealth.status -ne 'ok') { throw 'Health do chatbot inválido.' }
    if ($simHealth.status -ne 'ok' -or $simHealth.registros -ne 86) { throw 'Health do simulador inválido.' }

    $chat = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:4200/api/processos/chat' `
        -ContentType 'application/json' -Body '{"mensagem":"oi"}' -TimeoutSec 20
    if (-not $chat.session_id -or -not $chat.resultado.resposta) { throw 'Resposta do chat inválida.' }

    $base = Invoke-RestMethod -Uri 'http://127.0.0.1:4200/api/simulador/base' -TimeoutSec 20
    if ($base.registros.Count -ne 86 -or $base.meta1_final -ne 109.86) { throw 'Base do simulador divergente.' }

    foreach ($route in @('/', '/simulador')) {
        $page = Wait-Http "http://127.0.0.1:4200$route"
        if ($page.StatusCode -ne 200 -or $page.Content -notmatch '<app-root') {
            throw "Rota Angular inválida: $route"
        }
    }

    [pscustomobject]@{
        ChatHealth = $chatHealth.status
        SimulatorRecords = $simHealth.registros
        ChatSession = [bool]$chat.session_id
        ChatResponse = [bool]$chat.resultado.resposta
        Meta1 = $base.meta1_final
        Routes = '/, /simulador'
    } | Format-List
}
finally {
    foreach ($process in $processes) {
        if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
    }
}
