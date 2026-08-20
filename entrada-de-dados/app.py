"""
Ponto de entrada do módulo de entrada de dados.

Consulta qualquer processo do TRT18 informado pelo usuário e devolve a árvore
JSON padronizada e validada.

Uso:
    python app.py                                    # modo interativo
    python app.py 0011000-82.1981.5.18.0051          # um processo
    python app.py 0011000-82.1981.5.18.0051 --json   # imprime só o JSON

A lógica de verdade mora nos módulos (`coletor_trt18`, `normalizador`,
`modelos`, `servico`); este arquivo é apenas a interface de linha de comando.

Consulta em lote (a partir de planilha) vive no `pipeline.ipynb`, usado na etapa
de pesquisa; aqui o foco é a consulta sob demanda de um processo por vez.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from servico import obter_processo

RAIZ = Path(__file__).resolve().parent
DIR_SAIDA = RAIZ / "data" / "saida"


def _digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def checar_numero(texto: str) -> str | None:
    """Devolve a mensagem de erro do número CNJ, ou None se estiver válido."""
    from coletor_trt18 import validar_numero_cnj

    try:
        validar_numero_cnj(texto)
        return None
    except ValueError as exc:
        return str(exc)


def resumir(arvore: dict) -> str:
    """Resumo legível de um processo — o que o usuário vê no terminal."""
    p = arvore["processo"]
    movs = arvore["movimentacoes"]
    linhas = [
        f"Processo   : {p['numero']}",
        f"Classe     : {p.get('classe_judicial') or '-'}",
        f"Assunto    : {p.get('assunto') or '-'}",
        f"Órgão      : {p.get('orgao_julgador') or '-'}",
        f"Autuação   : {p.get('data_autuacao') or '-'}",
        f"Situação   : {p['situacao']}",
        f"Partes     : {len(arvore['partes_interessadas'])}"
        f" | Movimentações: {len(movs)}"
        f" | Documentos: {len(arvore['documentos'])}",
    ]
    if movs:
        ultimo = movs[-1]
        data = (ultimo.get("data") or "")[:10]
        linhas.append(f"Último mov.: {data} — {ultimo['descricao']}")
    if arvore["pendencias"]:
        linhas.append(f"Pendências : {'; '.join(arvore['pendencias'])}")
    return "\n".join(linhas)


def consultar_e_salvar(numero: str, *, headless: bool, so_cache: bool) -> dict | None:
    """Consulta um processo, salva a árvore JSON e devolve o dicionário."""
    try:
        arvore = obter_processo(numero, coletar=not so_cache, headless=headless)
    except Exception as exc:  # noqa: BLE001 — a mensagem é para o usuário final
        print(f"[erro] {numero}: {exc}", file=sys.stderr)
        return None

    status = arvore["coleta"]["status_coleta"]
    if status == "BLOQUEADO":
        print(
            f"[bloqueado] {numero}: o portal do TRT18 recusou o acesso por excesso de "
            "consultas. Aguarde alguns minutos e tente de novo.",
            file=sys.stderr,
        )
        return None
    if status == "FALHA":
        print(f"[erro] {numero}: {'; '.join(arvore['coleta']['erros']) or 'coleta falhou'}",
              file=sys.stderr)
        return None
    if status == "NAO_ENCONTRADO":
        print(
            f"[aviso] {numero}: número válido, mas não há processo com esse número "
            "no TRT18 (verifique se é de outro tribunal ou se está em segredo de justiça).",
            file=sys.stderr,
        )
        return None
    if status == "PARCIAL":
        print(f"[aviso] {numero}: coleta parcial — {'; '.join(arvore['coleta']['warnings'])}",
              file=sys.stderr)

    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    destino = DIR_SAIDA / f"processo_{_digitos(numero)}.json"
    destino.write_text(json.dumps(arvore, ensure_ascii=False, indent=2), encoding="utf-8")
    return arvore


def modo_interativo(headless: bool, so_cache: bool) -> None:
    print("Consulta de processos do TRT18 — digite o número (ou 'sair').\n")
    while True:
        try:
            entrada = input("Número do processo> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not entrada or entrada.lower() in {"sair", "exit", "quit"}:
            break
        erro = checar_numero(entrada)
        if erro:
            print(f"  {erro}\n")
            continue

        print("  Consultando (pode abrir o navegador e resolver o captcha)...")
        arvore = consultar_e_salvar(entrada, headless=headless, so_cache=so_cache)
        if arvore:
            print()
            print(resumir(arvore))
            print(f"\n  JSON salvo em: data/saida/processo_{_digitos(entrada)}.json\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consulta processos do TRT18 e devolve a árvore JSON padronizada."
    )
    parser.add_argument("numero", nargs="?", help="Número CNJ (com ou sem pontuação).")
    parser.add_argument("--json", action="store_true", help="Imprime apenas o JSON.")
    parser.add_argument("--headless", action="store_true", help="Não abre a janela do navegador.")
    parser.add_argument(
        "--so-cache", action="store_true", help="Usa apenas dados já coletados (não raspa)."
    )
    args = parser.parse_args()

    if args.numero:
        erro = checar_numero(args.numero)
        if erro:
            parser.error(erro)
        arvore = consultar_e_salvar(args.numero, headless=args.headless, so_cache=args.so_cache)
        if arvore is None:
            raise SystemExit(1)
        if args.json:
            print(json.dumps(arvore, ensure_ascii=False, indent=2))
        else:
            print()
            print(resumir(arvore))
            print(f"\nJSON salvo em: data/saida/processo_{_digitos(args.numero)}.json")
    else:
        modo_interativo(args.headless, args.so_cache)


if __name__ == "__main__":
    main()
