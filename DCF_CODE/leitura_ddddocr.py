from argparse import ArgumentParser
from pathlib import Path
import re

from DCF_CODE.prepara_leitura import remover_ruido_pixelacao
from remove_ruido import DEFAULT_OUTPUT_DIR as CLEAN_SEGMENTS_DIR
from remove_ruido import limpar_recortes
from segmenta_chars import DEFAULT_OUTPUT_DIR, segmentar_caracteres


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGES = [
    BASE_DIR / "teste_real1.png",
    BASE_DIR / "teste_real1_sem_ruido.png",
    BASE_DIR / "teste_real1_recorte_letras.png",
]
ALLOWED_CHAR_PATTERN = re.compile(r"[a-z0-9]", re.IGNORECASE)


def criar_ocr():
    try:
        import ddddocr
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Biblioteca ddddocr nao instalada. Instale com: pip install ddddocr"
        ) from exc

    return ddddocr.DdddOcr(show_ad=False)


def ler_imagem_com_ddddocr(image_path: Path, ocr=None) -> str:
    image_path = image_path.resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")

    ocr = ocr or criar_ocr()
    with image_path.open("rb") as image_file:
        return ocr.classification(image_file.read()).strip()


def normalizar_texto_ocr(text: str) -> str:
    return "".join(ALLOWED_CHAR_PATTERN.findall(text.lower()))


def normalizar_resultado_slot(text: str) -> str:
    normalized = normalizar_texto_ocr(text)
    if len(normalized) != 1:
        return ""
    return normalized


def testar_imagens(image_paths: list[Path]) -> list[tuple[Path, str]]:
    ocr = criar_ocr()
    return [(image_path, ler_imagem_com_ddddocr(image_path, ocr)) for image_path in image_paths]


def testar_por_caractere(
    image_path: Path = BASE_DIR / "teste_real1_recorte_letras.png",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    limpar_ruido_borda: bool = False,
    clean_output_dir: Path = CLEAN_SEGMENTS_DIR,
) -> tuple[str, list[tuple[Path, str]]]:
    recortes = segmentar_caracteres(image_path, output_dir)
    if limpar_ruido_borda:
        recortes = limpar_recortes(output_dir, clean_output_dir)

    leituras = testar_imagens(recortes)
    resultados = [
        (image_path, normalizar_resultado_slot(text))
        for image_path, text in leituras
    ]
    texto = "".join(text if text else "?" for _, text in resultados)
    return texto, resultados


def formatar_texto_slot(text: str) -> str:
    return text or "[invalido]"


def executar_pipeline_ddddocr(
    input_path: Path = BASE_DIR / "teste_real1.png",
    segments_dir: Path = DEFAULT_OUTPUT_DIR,
    limpar_ruido_borda: bool = False,
    clean_segments_dir: Path = CLEAN_SEGMENTS_DIR,
) -> tuple[str, list[tuple[Path, str]]]:
    _, _, cropped_image, _ = remover_ruido_pixelacao(input_path=input_path)
    return testar_por_caractere(
        cropped_image,
        segments_dir,
        limpar_ruido_borda=limpar_ruido_borda,
        clean_output_dir=clean_segments_dir,
    )


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Testa leitura OCR usando ddddocr.")
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Executa tratamento, segmentacao em 6 chars e OCR em sequencia.",
    )
    parser.add_argument(
        "--por-caractere",
        action="store_true",
        help="Segmenta a imagem em 6 slots e roda OCR em cada caractere.",
    )
    parser.add_argument(
        "--segments-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretorio onde os recortes por caractere serao salvos.",
    )
    parser.add_argument(
        "--limpar-ruido-borda",
        action="store_true",
        help="Remove componentes conectados as bordas antes do OCR.",
    )
    parser.add_argument(
        "--clean-segments-dir",
        type=Path,
        default=CLEAN_SEGMENTS_DIR,
        help="Diretorio dos recortes apos limpeza de borda.",
    )
    parser.add_argument(
        "images",
        nargs="*",
        type=Path,
        default=DEFAULT_IMAGES,
        help="Imagens para testar. Se vazio, usa as imagens principais do pipeline.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        if args.pipeline:
            texto_final, resultados = executar_pipeline_ddddocr(
                input_path=args.images[0],
                segments_dir=args.segments_dir,
                limpar_ruido_borda=args.limpar_ruido_borda,
                clean_segments_dir=args.clean_segments_dir,
            )
        elif args.por_caractere:
            texto_final, resultados = testar_por_caractere(
                image_path=args.images[0],
                output_dir=args.segments_dir,
                limpar_ruido_borda=args.limpar_ruido_borda,
                clean_output_dir=args.clean_segments_dir,
            )
        else:
            texto_final = ""
            resultados = testar_imagens(args.images)
    except ModuleNotFoundError as exc:
        print(exc)
        raise SystemExit(1) from exc

    print("\nResultados ddddocr")
    print("-" * 60)
    if args.pipeline or args.por_caractere:
        print(f"Texto final: {texto_final or '[vazio]'}")
        print("-" * 60)

    for image_path, text in resultados:
        print(f"Imagem: {image_path.name}")
        print(f"Texto: {formatar_texto_slot(text)}")
        print("-" * 60)
