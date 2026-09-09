from argparse import ArgumentParser
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
INPUT_IMAGE = BASE_DIR / "teste_real1.png"
OUTPUT_READABLE = BASE_DIR / "teste_real1_sem_ruido.png"
OUTPUT_BINARY = BASE_DIR / "teste_real1_sem_ruido_binaria.png"
OUTPUT_CROPPED = BASE_DIR / "teste_real1_recorte_letras.png"
OUTPUT_CROPPED_BINARY = BASE_DIR / "teste_real1_recorte_letras_binaria.png"


def carregar_imagem(input_path: Path) -> np.ndarray:
    image = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Imagem nao encontrada: {input_path}")
    return image


def preparar_para_leitura(image: np.ndarray, scale: int = 4) -> np.ndarray:
    """Reduz pixelacao/ruido mantendo contornos uteis para leitura."""
    enlarged = cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC,
    )

    denoised = cv2.fastNlMeansDenoisingColored(
        enlarged,
        None,
        h=10,
        hColor=10,
        templateWindowSize=7,
        searchWindowSize=21,
    )

    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    readable = clahe.apply(gray)

    sharpen_kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0],
        ]
    )
    return cv2.filter2D(readable, -1, sharpen_kernel)


def binarizar_para_texto(readable: np.ndarray) -> np.ndarray:
    """Cria uma versao preto/branco que costuma ajudar OCR e leitura de texto."""
    return cv2.adaptiveThreshold(
        readable,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        8,
    )


def recortar_faixa_das_letras(
    image: np.ndarray,
    top_ratio: float = 0.26,
    bottom_ratio: float = 0.78,
) -> np.ndarray:
    """Recorta a faixa onde as letras aparecem, descartando ruido acima/abaixo."""
    height = image.shape[0]
    top = int(height * top_ratio)
    bottom = int(height * bottom_ratio)

    if top < 0 or bottom > height or top >= bottom:
        raise ValueError(
            f"Recorte invalido: top={top_ratio}, bottom={bottom_ratio}, height={height}"
        )

    return image[top:bottom, :]


def remover_ruido_pixelacao(
    input_path: Path = INPUT_IMAGE,
    output_readable: Path = OUTPUT_READABLE,
    output_binary: Path = OUTPUT_BINARY,
    output_cropped: Path = OUTPUT_CROPPED,
    output_cropped_binary: Path = OUTPUT_CROPPED_BINARY,
    scale: int = 4,
    crop_top: float = 0.26,
    crop_bottom: float = 0.78,
) -> tuple[Path, Path, Path, Path]:
    image = carregar_imagem(input_path)
    readable = preparar_para_leitura(image, scale=scale)
    binary = binarizar_para_texto(readable)
    cropped = recortar_faixa_das_letras(readable, crop_top, crop_bottom)
    cropped_binary = binarizar_para_texto(cropped)

    cv2.imwrite(str(output_readable), readable)
    cv2.imwrite(str(output_binary), binary)
    cv2.imwrite(str(output_cropped), cropped)
    cv2.imwrite(str(output_cropped_binary), cropped_binary)

    return output_readable, output_binary, output_cropped, output_cropped_binary


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(
        description="Remove ruido de pixelacao e gera imagens mais legiveis."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=INPUT_IMAGE,
        help="Imagem de entrada.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_READABLE,
        help="Imagem de saida em tons de cinza tratada.",
    )
    parser.add_argument(
        "--binary-output",
        type=Path,
        default=OUTPUT_BINARY,
        help="Imagem de saida preto/branco para texto.",
    )
    parser.add_argument(
        "--cropped-output",
        type=Path,
        default=OUTPUT_CROPPED,
        help="Imagem tratada recortada na faixa das letras.",
    )
    parser.add_argument(
        "--cropped-binary-output",
        type=Path,
        default=OUTPUT_CROPPED_BINARY,
        help="Imagem recortada preto/branco para texto.",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=4,
        help="Fator de ampliacao antes da limpeza.",
    )
    parser.add_argument(
        "--crop-top",
        type=float,
        default=0.26,
        help="Inicio vertical do recorte, em proporcao da altura.",
    )
    parser.add_argument(
        "--crop-bottom",
        type=float,
        default=0.78,
        help="Fim vertical do recorte, em proporcao da altura.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    outputs = remover_ruido_pixelacao(
        input_path=args.input,
        output_readable=args.output,
        output_binary=args.binary_output,
        output_cropped=args.cropped_output,
        output_cropped_binary=args.cropped_binary_output,
        scale=args.scale,
        crop_top=args.crop_top,
        crop_bottom=args.crop_bottom,
    )
    print(f"Imagem tratada criada: {outputs[0]}")
    print(f"Imagem binaria criada: {outputs[1]}")
    print(f"Imagem recortada criada: {outputs[2]}")
    print(f"Imagem recortada binaria criada: {outputs[3]}")
