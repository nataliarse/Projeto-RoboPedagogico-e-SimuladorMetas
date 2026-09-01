from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent
DCF_CODE_DIR = ROOT_DIR / "DCF_CODE"
IMG_CAPTURED = Path(__file__).resolve().parent / "img_captured.png"

sys.path.insert(0, str(DCF_CODE_DIR))

from decifra import decifrar_imagem  # noqa: E402


def decifrar_captcha(image_path: str | Path = IMG_CAPTURED) -> str:
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Imagem do captcha nao encontrada: {image_path}")

    try:
        return decifrar_imagem(image_path)
    finally:
        if image_path.resolve() == IMG_CAPTURED.resolve():
            image_path.unlink(missing_ok=True)


def main() -> None:
    print("Resultados do decifrador")
    print("-" * 60)
    texto = decifrar_captcha()
    print(f"Imagem: {IMG_CAPTURED.name}")
    print(f"Texto final: {texto or '[vazio]'}")
    print("-" * 60)


if __name__ == "__main__":
    main()
