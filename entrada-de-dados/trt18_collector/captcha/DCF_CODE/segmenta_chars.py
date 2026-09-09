from argparse import ArgumentParser
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "teste_real1_recorte_letras.png"
DEFAULT_OUTPUT_DIR = BASE_DIR / "char_recortes"

BASE_WIDTH = 300
CHAR_RANGES_X = [
    (0, 46),
    (46, 100),
    (100, 146),
    (146, 200),
    (200, 250),
    (250, 300),
]


def carregar_cinza(image_path: Path) -> np.ndarray:
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")
    return image


def escalar_faixas(width: int) -> list[tuple[int, int]]:
    scale = width / BASE_WIDTH
    return [
        (round(start * scale), round(end * scale))
        for start, end in CHAR_RANGES_X
    ]


def limpar_bordas_do_slot(slot: np.ndarray) -> np.ndarray:
    """Remove tracos colados nas bordas sem apagar o miolo do caractere."""
    cleaned = slot.copy()
    height, width = cleaned.shape
    border_x = max(2, round(width * 0.08))
    border_y = max(2, round(height * 0.04))

    cleaned[:, :border_x] = 255
    cleaned[:, width - border_x :] = 255
    cleaned[:border_y, :] = 255
    cleaned[height - border_y :, :] = 255

    return cleaned


def centralizar_em_canvas(slot: np.ndarray, canvas_size: tuple[int, int] = (120, 120)) -> np.ndarray:
    """Cria recortes com tamanho estavel para OCR por caractere."""
    canvas_width, canvas_height = canvas_size
    height, width = slot.shape
    scale = min((canvas_width - 16) / width, (canvas_height - 16) / height)
    new_width = max(1, round(width * scale))
    new_height = max(1, round(height * scale))

    resized = cv2.resize(slot, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    canvas = np.full((canvas_height, canvas_width), 255, dtype=np.uint8)

    y = (canvas_height - new_height) // 2
    x = (canvas_width - new_width) // 2
    canvas[y : y + new_height, x : x + new_width] = resized

    return canvas


def segmentar_caracteres(
    input_path: Path = DEFAULT_INPUT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    limpar_bordas: bool = True,
) -> list[Path]:
    image = carregar_cinza(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = []
    for index, (start_x, end_x) in enumerate(escalar_faixas(image.shape[1]), start=1):
        slot = image[:, start_x:end_x]
        if limpar_bordas:
            slot = limpar_bordas_do_slot(slot)

        slot = centralizar_em_canvas(slot)
        output_path = output_dir / f"char_{index}.png"
        cv2.imwrite(str(output_path), slot)
        output_paths.append(output_path)

    return output_paths


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Segmenta a imagem em 6 recortes de caracteres.")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Imagem recortada na faixa das letras.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretorio de saida dos 6 recortes.",
    )
    parser.add_argument(
        "--keep-borders",
        action="store_true",
        help="Nao limpa bordas dos slots.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    outputs = segmentar_caracteres(
        input_path=args.input,
        output_dir=args.output_dir,
        limpar_bordas=not args.keep_borders,
    )

    print("Recortes criados:")
    for output in outputs:
        print(output)
