from argparse import ArgumentParser

from raspagem_dados import NUMERO_PROCESSO_PADRAO, abrir_processo


def parse_args() -> str:
    parser = ArgumentParser(description="Orquestra a coleta e decifracao do captcha.")
    parser.add_argument(
        "numero_processo",
        nargs="?",
        default=NUMERO_PROCESSO_PADRAO,
        help="Numero do processo no formato CNJ, com ou sem pontuacao.",
    )
    args = parser.parse_args()
    return args.numero_processo


def main() -> None:
    abrir_processo(parse_args())


if __name__ == "__main__":
    main()
