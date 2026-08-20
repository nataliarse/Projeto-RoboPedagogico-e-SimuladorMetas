"""
Ponto de integração com o chatbot (a "ferramenta de coleta" da proposta técnica).

O chatbot NÃO navega no site nem conhece o PJe: ele chama `obter_processo(numero)`
e recebe de volta a árvore JSON já coletada, limpa e validada (um dict pronto
para `json.dumps`). Toda a complexidade de raspagem/CAPTCHA/normalização fica
escondida aqui.

Uso típico (lado do chatbot):

    from servico import obter_processo
    arvore = obter_processo("0011000-82.1981.5.18.0051")
    # -> {"processo": {...}, "movimentacoes": [...], ..., "coleta": {...}}
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from normalizador import normalizar

RAIZ = Path(__file__).resolve().parent
DIR_BRUTOS = RAIZ / "data" / "brutos"


def _numero_normalizado(numero: str) -> str:
    return re.sub(r"\D", "", str(numero))


def obter_processo(
    numero: str,
    *,
    usar_cache: bool = True,
    coletar: bool = True,
    headless: bool = False,
    status_cnj_planilha: Optional[str] = None,
) -> dict:
    """
    Retorna a árvore JSON (dict) de um processo.

    Estratégia:
      1. Se `usar_cache` e há um bruto salvo COM o detalhe do processo, reaproveita.
      2. Senão, se `coletar`, executa a raspagem (abre navegador + CAPTCHA).
      3. Senão, levanta erro (sem dados disponíveis).

    O resultado é sempre validado pelo esquema Pydantic antes de retornar.
    """
    import coletor_trt18 as coletor  # imports pesados são carregados sob demanda

    numero_norm = _numero_normalizado(numero)
    if len(numero_norm) != 20:
        raise ValueError(f"Número CNJ inválido: '{numero}' ({len(numero_norm)} dígitos, esperado 20).")

    cache = DIR_BRUTOS / f"{numero_norm}.json"
    bruto = None

    if usar_cache and cache.exists():
        candidato = json.loads(cache.read_text(encoding="utf-8"))
        # ignora cache incompleto (sem o detalhe do processo) e recoleta
        if coletor.cache_aproveitavel(candidato):
            bruto = candidato

    if bruto is None:
        if not coletar:
            raise FileNotFoundError(
                f"Sem dados completos para {numero}: cache ausente/incompleto e "
                "coleta desabilitada (coletar=False)."
            )
        bruto = coletor.coletar_processo(
            numero, headless=headless, salvar=True, status_cnj_planilha=status_cnj_planilha
        )

    processo = normalizar(bruto)
    return json.loads(processo.model_dump_json())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Obtém a árvore JSON de um processo.")
    parser.add_argument("numero")
    parser.add_argument("--sem-coleta", action="store_true", help="Usa só o cache em data/brutos.")
    args = parser.parse_args()

    arvore = obter_processo(args.numero, coletar=not args.sem_coleta)
    print(json.dumps(arvore, ensure_ascii=False, indent=2))
