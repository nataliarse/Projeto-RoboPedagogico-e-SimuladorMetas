import base64
import re
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from decifra_coleta import decifrar_captcha


NUMERO_PROCESSO_PADRAO = "0011000-82.1981.5.18.0051"
MAX_TENTATIVAS_CAPTCHA = 5
TEMPO_VALIDACAO_CAPTCHA_MS = 5000

BASE_URL = "https://pje.trt18.jus.br/consultaprocessual/captcha/detalhe-processo/{numero}/1"
CAPTCHA_OUTPUT = Path(__file__).resolve().parent / "img_captured.png"
NAVEGADORES_INSTALADOS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]


def normalizar_numero_processo(numero: str) -> str:
    numero_normalizado = re.sub(r"\D", "", numero)

    if len(numero_normalizado) != 20:
        raise ValueError(
            f"Numero de processo invalido apos normalizacao: {numero_normalizado} "
            f"({len(numero_normalizado)} digitos). O padrao CNJ esperado tem 20 digitos."
        )

    return numero_normalizado


def montar_url(numero: str) -> str:
    return BASE_URL.format(numero=numero)


def salvar_data_url_imagem(data_url: str, output_path: Path) -> None:
    match = re.match(r"data:image/[^;]+;base64,(.+)", data_url, re.DOTALL)
    if not match:
        raise ValueError("URL da imagem nao esta no formato data:image/*;base64.")

    output_path.write_bytes(base64.b64decode(match.group(1)))


def encontrar_navegador_instalado() -> Path:
    for navegador in NAVEGADORES_INSTALADOS:
        if navegador.exists():
            return navegador

    raise FileNotFoundError(
        "Chrome ou Edge nao encontrado nos caminhos padrao do Windows. "
        "Instale o Chromium do Playwright ou informe o caminho do navegador."
    )


def captcha_ainda_visivel(page) -> bool:
    try:
        page.locator("#captchaInput").wait_for(
            state="hidden",
            timeout=TEMPO_VALIDACAO_CAPTCHA_MS,
        )
        return False
    except PlaywrightTimeoutError:
        return True


def executar_tentativa(p, navegador_path: Path, url: str, tentativa: int) -> bool:
    captcha_data_url = None

    def capturar_imagem_da_rede(request):
        nonlocal captcha_data_url

        request_url = request.url
        if request_url.startswith("data:image/png;base64,"):
            captcha_data_url = request_url

    print(f"[INFO] Tentativa {tentativa}/{MAX_TENTATIVAS_CAPTCHA}")

    browser = p.chromium.launch(
        executable_path=str(navegador_path),
        headless=False,
        slow_mo=100,
    )

    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
    )

    page = context.new_page()
    page.on("request", capturar_imagem_da_rede)

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print("[INFO] Pagina aberta com sucesso.")
        print(f"[INFO] Titulo da pagina: {page.title()}")

        captcha_input = page.locator("#captchaInput")
        captcha_input.wait_for(state="visible", timeout=30000)

        if captcha_data_url is None:
            captcha_data_url = page.locator("img[src^='data:image/png;base64,']").first.get_attribute(
                "src",
                timeout=30000,
            )

        salvar_data_url_imagem(captcha_data_url, CAPTCHA_OUTPUT)
        print(f"[INFO] Imagem do captcha salva em: {CAPTCHA_OUTPUT}")

        texto_decifrado = decifrar_captcha(CAPTCHA_OUTPUT)
        print(f"[INFO] Texto decifrado: {texto_decifrado or '[vazio]'}")

        captcha_input.fill(texto_decifrado)
        print(f"[INFO] Campo do captcha preenchido com: {texto_decifrado or '[vazio]'}")
        captcha_input.press("Enter")
        print("[INFO] Enter pressionado no campo do captcha.")

        if captcha_ainda_visivel(page):
            print("[INFO] Captcha nao validado; fechando navegador para nova tentativa.")
            return False

        print("[INFO] Acesso liberado.")
        try:
            input("\nPressione ENTER para fechar o navegador...")
        except EOFError:
            print("[INFO] Execucao sem entrada interativa; fechando navegador.")
        return True

    except PlaywrightTimeoutError:
        print("[ERRO] A pagina demorou demais para carregar ou validar o captcha.")
        return False

    finally:
        browser.close()


def abrir_processo(numero: str) -> bool:
    normalizar_numero_processo(numero)
    url = montar_url(numero)

    print(f"[INFO] Numero original: {numero}")
    print(f"[INFO] URL final: {url}")

    with sync_playwright() as p:
        navegador_path = encontrar_navegador_instalado()
        print(f"[INFO] Navegador usado: {navegador_path}")

        for tentativa in range(1, MAX_TENTATIVAS_CAPTCHA + 1):
            if executar_tentativa(p, navegador_path, url, tentativa):
                return True

    print("[ERRO] Nao foi possivel acessar apos 5 tentativas.")
    return False


if __name__ == "__main__":
    abrir_processo(NUMERO_PROCESSO_PADRAO)
