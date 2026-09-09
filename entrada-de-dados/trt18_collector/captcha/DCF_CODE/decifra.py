from pathlib import Path

from .prepara_leitura import (
    INPUT_IMAGE,
    OUTPUT_BINARY,
    OUTPUT_CROPPED,
    OUTPUT_CROPPED_BINARY,
    OUTPUT_READABLE,
)
from .leitura_ddddocr import executar_pipeline_ddddocr, formatar_texto_slot
from .remove_ruido import DEFAULT_OUTPUT_DIR as CLEAN_SEGMENTS_DIR
from .segmenta_chars import DEFAULT_OUTPUT_DIR as SEGMENTS_DIR


TEMP_FILES = [
    OUTPUT_READABLE,
    OUTPUT_BINARY,
    OUTPUT_CROPPED,
    OUTPUT_CROPPED_BINARY,
]
TEMP_DIRS = [
    SEGMENTS_DIR,
    CLEAN_SEGMENTS_DIR,
]


def limpar_temporarios() -> None:
    """Remove arquivos gerados pelo pipeline apos o OCR."""
    for file_path in TEMP_FILES:
        file_path.unlink(missing_ok=True)

    for dir_path in TEMP_DIRS:
        if not dir_path.exists():
            continue

        for file_path in dir_path.glob("*.png"):
            file_path.unlink(missing_ok=True)

        try:
            dir_path.rmdir()
        except OSError:
            pass


def decifrar_imagem(
    imagem: str | Path,
    limpar_ruido_borda: bool = False,
) -> str:
    """Executa o pipeline e retorna apenas a palavra decifrada."""
    try:
        texto_final, _ = executar_pipeline_ddddocr(
            input_path=Path(imagem),
            limpar_ruido_borda=limpar_ruido_borda,
        )
        return texto_final
    finally:
        limpar_temporarios()


def imprimir_resultado(texto_final: str, resultados: list[tuple[Path, str]]) -> None:
    print("\nPipeline OCR por caractere")
    print("-" * 60)

    for index, (image_path, text) in enumerate(resultados, start=1):
        print(f"Char {index}: {image_path.name} -> {formatar_texto_slot(text)}")

    print("-" * 60)
    print(f"Texto final: {texto_final or '[vazio]'}")


if __name__ == "__main__":
    try:
        texto, leituras = executar_pipeline_ddddocr(INPUT_IMAGE)
        imprimir_resultado(texto, leituras)
    finally:
        limpar_temporarios()
