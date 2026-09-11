"""
Coletor de dados processuais do TRT18 (PJe Consulta Processual).

Estende o protótipo de raspagem que já existia (acesso + resolução de CAPTCHA)
adicionando a ETAPA QUE FALTAVA: a extração dos dados do processo depois que o
CAPTCHA é validado.

Estratégia de extração (robusta a mudanças de layout):
  1. O portal `consultaprocessual` é uma SPA Angular que carrega os dados via
     chamadas XHR a uma API que devolve JSON. Capturamos essas respostas
     (`page.on("response")`) — é a fonte mais limpa e estável.
  2. Como fallback, guardamos o HTML completo e o texto visível da página,
     para que o normalizador funcione mesmo se a API mudar.

O resultado de cada processo é salvo "bruto" em `data/brutos/<numero>.json`,
permitindo reprocessar a estruturação sem re-raspar (e retomar lotes).

Observação: a coleta abre um navegador real e depende do CAPTCHA, portanto roda
na máquina do usuário (não em ambiente headless sem display). O notebook
`pipeline.ipynb` chama as funções daqui.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# --- torna o pacote de captcha já existente importável -----------------------
RAIZ = Path(__file__).resolve().parent.parent


def _carregar_dependencias_de_coleta():
    """
    Importa Playwright e o decifrador de CAPTCHA *sob demanda*.

    Mantemos esses imports pesados (cv2, ddddocr, playwright) fora do topo do
    módulo para que o pipeline de estruturação possa importar este arquivo sem
    precisar deles instalados — só a coleta de fato exige.
    """
    _corrigir_cv2_para_caminhos_unicode()

    from .captcha.decifra_coleta import decifrar_captcha
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright

    return decifrar_captcha, sync_playwright, PlaywrightTimeoutError


def _corrigir_cv2_para_caminhos_unicode() -> None:
    """
    No Windows, `cv2.imread`/`cv2.imwrite` falham silenciosamente com caminhos que
    contêm acentos (ex.: "Área de Trabalho"): imread devolve None e imwrite não
    grava. Como o pipeline de captcha (DCF_CODE) usa cv2 com paths sob essa pasta,
    substituímos as duas funções por versões unicode-safe (via np.fromfile/tofile).

    Idempotente: só aplica uma vez.
    """
    import os

    import cv2
    import numpy as np

    if getattr(cv2, "_unicode_safe_patch", False):
        return

    _imread_orig = cv2.imread
    _imwrite_orig = cv2.imwrite

    def imread_unicode(filename, flags=cv2.IMREAD_COLOR):
        try:
            dados = np.fromfile(filename, dtype=np.uint8)
            if dados.size == 0:
                return None
            return cv2.imdecode(dados, flags)
        except Exception:
            return _imread_orig(filename, flags)

    def imwrite_unicode(filename, img, params=None):
        try:
            ext = os.path.splitext(str(filename))[1] or ".png"
            ok, buf = cv2.imencode(ext, img, params if params is not None else [])
            if not ok:
                return False
            buf.tofile(filename)
            return True
        except Exception:
            return _imwrite_orig(filename, img, params if params is not None else [])

    cv2.imread = imread_unicode
    cv2.imwrite = imwrite_unicode
    cv2._unicode_safe_patch = True


# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------
VERSAO_COLETOR = "1.1.0"
BASE_URL = "https://pje.trt18.jus.br/consultaprocessual/captcha/detalhe-processo/{numero}/1"
MAX_TENTATIVAS_CAPTCHA = 5
TEMPO_VALIDACAO_CAPTCHA_MS = 5000
# Espera pelo campo do captcha aparecer. Na prática ele surge em ~2s; quando não
# surge, é porque o portal está degradado/limitando o ritmo — nesse caso esperar
# 30s não adianta e só multiplica o custo por 5 tentativas. Medição do lote:
# sucesso ~5s vs. falha ~158s, com as falhas consumindo 78% do tempo total.
TEMPO_ESPERA_CAPTCHA_MS = 12000
# Pausa entre tentativas e entre processos, para não martelar o portal (o excesso
# de requisições em sequência é o que dispara a degradação).
PAUSA_ENTRE_TENTATIVAS_MS = 2000
PAUSA_ENTRE_PROCESSOS_S = 1.5
# Após o captcha ser aceito, o PJe ainda demora para responder o endpoint de
# detalhes (`/api/processos/{id}?tokenDesafio=...`). Esperamos por essa resposta
# específica, e não por um tempo fixo — 8s não bastavam e a página era capturada
# ainda em "Enviando resposta do captcha. Aguarde.".
TEMPO_CARREGAR_DADOS_MS = 45000

DIR_BRUTOS = RAIZ / "data" / "brutos"
DIR_DEBUG = RAIZ / "data" / "debug"
# The image exists only between capture and OCR; it never belongs in source.
CAPTCHA_OUTPUT = DIR_DEBUG / "captcha" / "img_captured.png"

# trechos de URL que indicam respostas de API com dados do processo
PADRAO_API = re.compile(r"/(consultaprocessual|api)/", re.IGNORECASE)

# Chaves que identificam o payload COMPLETO do processo (o que traz o histórico).
# `itensProcesso` é a lista de movimentações; `poloAtivo`/`poloPassivo`, as partes.
CHAVES_PAYLOAD_COMPLETO = ("itensProcesso", "poloAtivo", "poloPassivo")


def _tem_dados_completos(respostas_api: list[dict]) -> bool:
    """True se alguma resposta já trouxe o detalhe do processo (com movimentações)."""
    for item in respostas_api:
        payload = item.get("payload")
        if isinstance(payload, dict) and any(k in payload for k in CHAVES_PAYLOAD_COMPLETO):
            return True
    return False


def _processo_nao_encontrado(respostas_api: list[dict]) -> bool:
    """
    True quando o PJe respondeu `dadosbasicos` com lista vazia.

    O endpoint devolve `[{...}]` para um processo existente e `[]` quando o
    número é válido mas não há processo correspondente no TRT18.
    """
    viu_dadosbasicos = False
    for item in respostas_api:
        if "dadosbasicos" not in (item.get("url") or ""):
            continue
        viu_dadosbasicos = True
        payload = item.get("payload")
        if isinstance(payload, list) and len(payload) > 0:
            return False
    return viu_dadosbasicos


def cache_aproveitavel(bruto: dict) -> bool:
    """
    Um bruto salvo só serve se contiver o detalhe do processo.

    Coletas anteriores à versão 1.1.0 podiam ser marcadas como SUCESSO tendo
    capturado apenas os `dadosbasicos` (a página era lida antes de o PJe
    responder). Esses arquivos são tratados como inválidos e recoletados.
    """
    return _tem_dados_completos(bruto.get("respostas_api") or [])

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
# Estrutura do número CNJ (Resolução CNJ nº 65/2008):
#   NNNNNNN - DD . AAAA . J . TR . OOOO
#   seq(7)   dv(2)  ano(4) seg(1) trib(2) origem(4)
SEGMENTO_JUSTICA_TRABALHO = "5"
TRIBUNAL_TRT18 = "18"


def digito_verificador_cnj(numero_norm: str) -> int:
    """
    Calcula o dígito verificador do número CNJ (módulo 97 base 10, ISO 7064).

    DV = 98 - ((NNNNNNN AAAA J TR OOOO) * 100 mod 97)
    """
    seq, ano = numero_norm[0:7], numero_norm[9:13]
    seg, trib, org = numero_norm[13:14], numero_norm[14:16], numero_norm[16:20]
    base = int(seq + ano + seg + trib + org)
    return 98 - ((base * 100) % 97)


def validar_numero_cnj(numero: str, *, exigir_trt18: bool = True) -> str:
    """
    Valida o número CNJ e devolve os 20 dígitos.

    Verifica, sem acessar a rede: quantidade de dígitos, dígito verificador
    (pega erro de digitação) e, se `exigir_trt18`, se o processo é mesmo da
    Justiça do Trabalho da 18ª Região — este coletor só consulta o TRT18.

    Levanta `ValueError` com mensagem explicativa quando algo não confere.
    Atenção: número válido não significa processo existente; a existência só é
    confirmada na consulta ao portal.
    """
    digitos = re.sub(r"\D", "", str(numero))

    if len(digitos) != 20:
        raise ValueError(
            f"Número inválido: '{numero}' tem {len(digitos)} dígitos; "
            "o padrão CNJ exige 20 (NNNNNNN-DD.AAAA.J.TR.OOOO)."
        )

    esperado = digito_verificador_cnj(digitos)
    informado = int(digitos[7:9])
    if esperado != informado:
        raise ValueError(
            f"Número inválido: dígito verificador não confere "
            f"(informado {informado:02d}, esperado {esperado:02d}). "
            "Provável erro de digitação."
        )

    if exigir_trt18:
        segmento, tribunal = digitos[13:14], digitos[14:16]
        if segmento != SEGMENTO_JUSTICA_TRABALHO:
            raise ValueError(
                f"Número inválido para este coletor: segmento '{segmento}' não é "
                "Justiça do Trabalho (esperado 5)."
            )
        if tribunal != TRIBUNAL_TRT18:
            raise ValueError(
                f"Processo do TRT{tribunal}, não do TRT18. Este coletor consulta "
                "apenas o TRT da 18ª Região."
            )

    return digitos


def normalizar_numero_processo(numero: str) -> str:
    """Valida e devolve os 20 dígitos do número CNJ."""
    return validar_numero_cnj(numero)


def montar_url(numero_normalizado: str) -> str:
    return BASE_URL.format(numero=numero_normalizado)


def salvar_data_url_imagem(data_url: str, output_path: Path) -> None:
    import base64

    match = re.match(r"data:image/[^;]+;base64,(.+)", data_url, re.DOTALL)
    if not match:
        raise ValueError("Imagem do captcha não está no formato data:image/*;base64.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(match.group(1)))


def encontrar_navegador_instalado() -> Optional[Path]:
    """Returns only an explicit override; Playwright Chromium is the default."""
    configured = os.getenv("TRT18_COLLECTOR_BROWSER_EXECUTABLE", "").strip()
    if not configured:
        return None
    browser_path = Path(configured).expanduser()
    if not browser_path.is_file():
        raise FileNotFoundError(
            "TRT18_COLLECTOR_BROWSER_EXECUTABLE does not point to an executable: "
            f"{browser_path}"
        )
    return browser_path


# ---------------------------------------------------------------------------
# Coleta de um processo
# ---------------------------------------------------------------------------
def _captcha_ainda_visivel(page, PlaywrightTimeoutError) -> bool:
    """True se o #captchaInput continua visível (captcha NÃO validado)."""
    try:
        page.locator("#captchaInput").wait_for(state="hidden", timeout=TEMPO_VALIDACAO_CAPTCHA_MS)
        return False
    except PlaywrightTimeoutError:
        return True


def _rodar_sem_event_loop(func, *args, **kwargs):
    """
    Executa `func` (que usa a API síncrona do Playwright) de forma segura mesmo
    dentro do Jupyter.

    São dois obstáculos no Windows + Jupyter:
      1. A API síncrona do Playwright recusa rodar se já houver um event loop
         ativo na thread (o kernel do Jupyter roda um). -> rodamos numa thread.
      2. O Jupyter troca a policy do asyncio para `Selector`, que NÃO suporta
         subprocessos; o Playwright precisa de subprocess para subir o navegador
         e isso causa `NotImplementedError`. -> na thread, forçamos um
         `ProactorEventLoop` (que suporta subprocess no Windows).
    """
    import asyncio
    import sys

    try:
        asyncio.get_running_loop()
        tem_loop = True
    except RuntimeError:
        tem_loop = False

    if not tem_loop:
        return func(*args, **kwargs)

    import concurrent.futures

    def _runner():
        # O Playwright cria o próprio loop via asyncio.new_event_loop(), que
        # respeita a *policy* global. Por isso trocamos a policy para Proactor
        # (e restauramos depois) — só setar um loop na thread não bastaria.
        if sys.platform != "win32":
            return func(*args, **kwargs)

        import warnings

        with warnings.catch_warnings():
            # get/set_event_loop_policy são deprecados no 3.14 (removidos no 3.16),
            # mas continuam funcionando e são a forma de garantir o Proactor aqui.
            warnings.simplefilter("ignore", DeprecationWarning)
            policy_anterior = asyncio.get_event_loop_policy()
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            try:
                return func(*args, **kwargs)
            finally:
                asyncio.set_event_loop_policy(policy_anterior)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(_runner).result()


def coletar_processo(
    numero: str,
    headless: bool = False,
    salvar: bool = True,
    status_cnj_planilha: Optional[str] = None,
) -> dict:
    """Acessa o processo, resolve o CAPTCHA e captura os dados brutos.

    Funciona tanto em script puro quanto dentro do Jupyter (roda em thread
    separada quando há um event loop ativo). Veja `_coletar_processo` para o
    dicionário bruto retornado.
    """
    return _rodar_sem_event_loop(
        _coletar_processo, numero, headless, salvar, status_cnj_planilha
    )


def _coletar_processo(
    numero: str,
    headless: bool = False,
    salvar: bool = True,
    status_cnj_planilha: Optional[str] = None,
) -> dict:
    """
    Implementação síncrona (Playwright) da coleta de um processo.

    Retorna um dicionário "bruto" com:
      numero, numero_normalizado, url, capturado_em, tentativas_captcha,
      status_coleta ("SUCESSO" | "FALHA"), erros,
      respostas_api: [{url, payload}],  html, texto_pagina,
      status_cnj_planilha
    """
    numero_norm = normalizar_numero_processo(numero)
    url = montar_url(numero_norm)

    import time

    inicio = time.perf_counter()
    bruto: dict = {
        "numero": str(numero),
        "numero_normalizado": numero_norm,
        "url": url,
        "capturado_em": datetime.now().isoformat(),
        "versao_coletor": VERSAO_COLETOR,
        "tempo_execucao_seg": None,
        "tentativas_captcha": None,
        "status_coleta": "FALHA",
        "warnings": [],
        "erros": [],
        "respostas_api": [],
        "html": None,
        "texto_pagina": None,
        "status_cnj_planilha": status_cnj_planilha,
    }

    decifrar_captcha, sync_playwright, PlaywrightTimeoutError = _carregar_dependencias_de_coleta()

    with sync_playwright() as p:
        navegador_path = encontrar_navegador_instalado()

        sucesso = False
        for tentativa in range(1, MAX_TENTATIVAS_CAPTCHA + 1):
            bruto["tentativas_captcha"] = tentativa
            ultima = tentativa == MAX_TENTATIVAS_CAPTCHA
            if _executar_tentativa(
                p, navegador_path, url, headless, decifrar_captcha,
                PlaywrightTimeoutError, bruto, ultima,
            ):
                sucesso = True
                break
            if bruto["status_coleta"] in ("NAO_ENCONTRADO", "BLOQUEADO"):
                break  # repetir não resolve: processo inexistente ou acesso barrado
            if not ultima:
                # respira antes de tentar de novo: quando o portal está limitando
                # o ritmo, insistir imediatamente só piora
                time.sleep(PAUSA_ENTRE_TENTATIVAS_MS / 1000)

        if not sucesso and not bruto["erros"]:
            bruto["erros"].append("CAPTCHA não validado após várias tentativas.")

    return _finalizar(bruto, salvar, inicio)


def _executar_tentativa(
    p, navegador_path, url, headless, decifrar_captcha,
    PlaywrightTimeoutError, bruto, ultima,
) -> bool:
    """
    Uma tentativa = um navegador novo (mesma estrutura do protótipo original).

    Em caso de sucesso, preenche `bruto` com respostas_api / html / texto_pagina
    e devolve True. Em falha devolve False (e, na última tentativa, salva o
    diagnóstico de tela/HTML).
    """
    captcha_data_url = {"v": None}
    respostas_api: list[dict] = []
    bloqueio: dict = {}

    def capturar_imagem_da_rede(request):
        if request.url.startswith("data:image/png;base64,"):
            captcha_data_url["v"] = request.url

    def capturar_resposta_api(response):
        try:
            if not PADRAO_API.search(response.url):
                return
            # 403 = o portal recusou o acesso (limite de consultas). Registramos
            # para abortar cedo: insistir nesse estado só prolonga o bloqueio.
            if response.status in (403, 429):
                bloqueio["status"] = response.status
                return
            ctype = (response.headers or {}).get("content-type", "")
            if "application/json" not in ctype.lower():
                return
            respostas_api.append({"url": response.url, "payload": response.json()})
        except Exception:  # corpo não-JSON / resposta já consumida
            pass

    launch_kwargs = {"headless": headless, "slow_mo": 100}
    if navegador_path is not None:
        launch_kwargs["executable_path"] = str(navegador_path)

    browser = p.chromium.launch(**launch_kwargs)
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()
    page.on("request", capturar_imagem_da_rede)
    page.on("response", capturar_resposta_api)

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # O PJe consulta `dadosbasicos` ANTES de exibir o captcha. Se vier vazio,
        # o número é válido mas não existe processo — aborta sem gastar tentativas.
        esperou = 0
        while esperou < 10000:
            if bloqueio or any("dadosbasicos" in (r.get("url") or "") for r in respostas_api):
                break
            page.wait_for_timeout(500)
            esperou += 500

        if bloqueio:
            bruto["status_coleta"] = "BLOQUEADO"
            bruto["erros"].append(
                f"O portal do TRT18 recusou o acesso (HTTP {bloqueio['status']}), "
                "provavelmente por excesso de consultas em sequência. "
                "Aguarde alguns minutos antes de tentar novamente."
            )
            return False

        if _processo_nao_encontrado(respostas_api):
            bruto["status_coleta"] = "NAO_ENCONTRADO"
            bruto["erros"].append(
                "Processo não encontrado no TRT18 (o portal não retornou dados básicos)."
            )
            return False

        captcha_input = page.locator("#captchaInput")
        captcha_input.wait_for(state="visible", timeout=TEMPO_ESPERA_CAPTCHA_MS)

        data_url = captcha_data_url["v"]
        if data_url is None:
            data_url = page.locator("img[src^='data:image/png;base64,']").first.get_attribute(
                "src", timeout=30000
            )

        salvar_data_url_imagem(data_url, CAPTCHA_OUTPUT)
        texto = decifrar_captcha(CAPTCHA_OUTPUT)
        captcha_input.fill(texto or "")
        captcha_input.press("Enter")

        if _captcha_ainda_visivel(page, PlaywrightTimeoutError):
            return False  # OCR errou; tenta de novo com navegador novo

        # --- captcha validado: aguarda o endpoint de detalhes responder ---
        # Espera ativa: o campo do captcha some assim que a resposta é enviada,
        # mas os dados (movimentações/partes) chegam só depois. Fazemos polling
        # até a resposta completa aparecer, em vez de dormir um tempo fixo.
        completo = False
        aguardado = 0
        PASSO_MS = 500
        while aguardado < TEMPO_CARREGAR_DADOS_MS:
            if _tem_dados_completos(respostas_api):
                completo = True
                break
            page.wait_for_timeout(PASSO_MS)
            aguardado += PASSO_MS

        if completo:
            page.wait_for_timeout(1000)  # deixa a SPA terminar de renderizar

        bruto["respostas_api"] = respostas_api
        bruto["html"] = page.content()
        try:
            bruto["texto_pagina"] = page.locator("body").inner_text(timeout=5000)
        except Exception:
            bruto["texto_pagina"] = None

        if completo:
            bruto["status_coleta"] = "SUCESSO"
        else:
            bruto["status_coleta"] = "PARCIAL"
            bruto["warnings"].append(
                "Detalhe do processo (itensProcesso/partes) não chegou no tempo limite; "
                "apenas dados básicos foram capturados."
            )
        return True

    except PlaywrightTimeoutError as exc:
        if ultima:
            bruto["erros"].append(f"Timeout: {exc}")
            _salvar_diagnostico(page, bruto["numero_normalizado"])
        return False
    except Exception as exc:  # ex.: net::ERR_ABORTED no goto
        if ultima:
            bruto["erros"].append(f"Erro: {exc}")
            _salvar_diagnostico(page, bruto["numero_normalizado"])
        return False
    finally:
        browser.close()


def _salvar_diagnostico(page, numero_norm: str) -> None:
    """Salva screenshot + HTML da página no momento da falha (para inspeção)."""
    try:
        DIR_DEBUG.mkdir(parents=True, exist_ok=True)
        try:
            page.screenshot(path=str(DIR_DEBUG / f"{numero_norm}.png"), full_page=True)
        except Exception:
            pass
        try:
            (DIR_DEBUG / f"{numero_norm}.html").write_text(page.content(), encoding="utf-8")
        except Exception:
            pass
    except Exception:
        pass


def _finalizar(bruto: dict, salvar: bool, inicio: float | None = None) -> dict:
    if inicio is not None:
        import time

        bruto["tempo_execucao_seg"] = round(time.perf_counter() - inicio, 3)
    if salvar:
        DIR_BRUTOS.mkdir(parents=True, exist_ok=True)
        destino = DIR_BRUTOS / f"{bruto['numero_normalizado']}.json"
        destino.write_text(json.dumps(bruto, ensure_ascii=False, indent=2), encoding="utf-8")
    return bruto


def coletar_lote(
    processos: list[dict | str],
    headless: bool = False,
    pular_existentes: bool = True,
) -> list[dict]:
    """
    Coleta vários processos.

    `processos` pode ser uma lista de números (str) ou de dicts
    {"numero": ..., "status_cnj_planilha": ...}.

    Se `pular_existentes`, processos já salvos em data/brutos são reaproveitados
    (permite retomar um lote interrompido).

    Roda o lote inteiro em uma única thread quando chamado de dentro do Jupyter
    (evita o erro "Sync API inside the asyncio loop").
    """
    return _rodar_sem_event_loop(_coletar_lote, processos, headless, pular_existentes)


def _coletar_lote(
    processos: list[dict | str],
    headless: bool = False,
    pular_existentes: bool = True,
) -> list[dict]:
    resultados: list[dict] = []
    for item in processos:
        if isinstance(item, str):
            numero, status = item, None
        else:
            numero, status = item.get("numero"), item.get("status_cnj_planilha")

        numero_norm = normalizar_numero_processo(numero)
        cache = DIR_BRUTOS / f"{numero_norm}.json"
        if pular_existentes and cache.exists():
            cacheado = json.loads(cache.read_text(encoding="utf-8"))
            # só reaproveita coletas que realmente trouxeram o detalhe do processo;
            # FALHA e coletas incompletas (sem itensProcesso) são refeitas.
            if cache_aproveitavel(cacheado):
                resultados.append(cacheado)
                print(f"[cache] {numero} já coletado ({cacheado.get('status_coleta')}).")
                continue
            print(f"[retry] {numero} sem dados completos, coletando de novo ...")

        print(f"[coleta] {numero} ...")
        # já estamos numa thread sem event loop: chama a impl direto
        bruto = _coletar_processo(numero, headless=headless, status_cnj_planilha=status)
        print(f"         -> {bruto['status_coleta']} ({len(bruto['respostas_api'])} respostas API)")
        resultados.append(bruto)

    return resultados


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Coleta dados de um processo do TRT18.")
    parser.add_argument("numero", help="Número CNJ (com ou sem pontuação).")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    resultado = coletar_processo(args.numero, headless=args.headless)
    print(json.dumps(resultado, ensure_ascii=False, indent=2)[:2000])
