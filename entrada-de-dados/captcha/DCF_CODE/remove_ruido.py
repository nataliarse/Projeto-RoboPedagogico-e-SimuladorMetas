import cv2
import numpy as np
from argparse import ArgumentParser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = BASE_DIR / "char_recortes"
DEFAULT_OUTPUT_DIR = BASE_DIR / "char_recortes_sem_ruido"

def remover_fragmentos_circulo(img_segmento):
    """
    Remove fragmentos de círculo sem deletar letras,
    mesmo quando se tocam.
    """
    cinza = cv2.cvtColor(img_segmento, cv2.COLOR_BGR2GRAY) if len(img_segmento.shape) == 3 else img_segmento.copy()
    _, binaria = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    h, w = binaria.shape
    resultado = binaria.copy()

    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contornos:
        x, y, cw, ch = cv2.boundingRect(cnt)

        toca_borda = (x <= 25 or y <= 25 or (x + cw) >= (w - 25) or (y + ch) >= (h - 25))

        if not toca_borda:
            continue  # provavelmente é letra, ignora

        # --- análise de forma do contorno ---
        area       = cv2.contourArea(cnt)
        perimetro  = cv2.arcLength(cnt, closed=False)
        n_pontos   = len(cnt)

        if area < 5 or perimetro < 10:
            # minúsculo, apaga sem dó
            cv2.drawContours(resultado, [cnt], -1, 0, -1)
            continue

        # Curvatura média: fragmento de círculo tem curvatura CONSISTENTE
        # Letra tem curvatura muito variada (cantos, retas, curvas)
        curvatura = _curvatura_media(cnt)

        # Razão comprimento/largura: fragmento é alongado, letra é mais compacta
        aspecto = max(cw, ch) / (min(cw, ch) + 1e-5)

        # Convexidade: fragmento de arco é pouco convexo
        hull   = cv2.convexHull(cnt)
        a_hull = cv2.contourArea(hull)
        convexidade = area / (a_hull + 1e-5)

        eh_fragmento = (
            curvatura > 0.08        # curvatura consistente de arco
            or aspecto > 3.5        # muito alongado
            or convexidade < 0.35   # pouco preenchido (arco aberto)
        )

        if eh_fragmento:
            # Apaga SÓ os pixels desse contorno, não o bounding box inteiro
            mascara = np.zeros_like(binaria)
            cv2.drawContours(mascara, [cnt], -1, 255, thickness=cv2.FILLED)

            # Dilata levemente a máscara para pegar pixels de 1-2px ao redor
            kernel = np.ones((3, 3), np.uint8)
            mascara = cv2.dilate(mascara, kernel, iterations=1)

            resultado[mascara == 255] = 0  # apaga só esses pixels

    # Inverte de volta para fundo branco
    return cv2.bitwise_not(resultado)


def limpar_recortes(
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    threshold: int = 235,
    border_margin: int = 25,
) -> list[Path]:
    """Aplica a limpeza experimental em todos os recortes por caractere."""
    del threshold, border_margin

    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = []

    for image_path in sorted(input_dir.glob("*.png")):
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")

        cleaned = remover_fragmentos_circulo(image)
        output_path = output_dir / image_path.name
        cv2.imwrite(str(output_path), cleaned)
        output_paths.append(output_path)

    return output_paths


def _curvatura_media(cnt):
    """Estima curvatura média do contorno via variação angular."""
    pts = cnt[:, 0, :]
    if len(pts) < 5:
        return 0.0

    angulos = []
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i-1], pts[i], pts[i+1]
        v1 = p0 - p1
        v2 = p2 - p1
        norma = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norma < 1e-5:
            continue
        cos_a = np.clip(np.dot(v1, v2) / norma, -1, 1)
        angulos.append(np.arccos(cos_a))

    return np.std(angulos) if angulos else 0.0


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(
        description="Remove fragmentos de circulo dos recortes por caractere."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Diretorio com recortes por caractere.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretorio de saida dos recortes limpos.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    outputs = limpar_recortes(args.input_dir, args.output_dir)

    print("Recortes limpos criados:")
    for output in outputs:
        print(output)
