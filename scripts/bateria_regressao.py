"""Bateria de regressão das respostas do Robô Orientador (com o modelo de linguagem real).

Envia perguntas reais ao chat e confere o que pode ser conferido sem depender da redação
exata do modelo: a rota escolhida, os fatos calculados pelas regras e as barreiras contra
invenção. Rode antes de cada atualização da instância; se algum caso falhar, a mudança
piorou algo que funcionava.

Uso (só biblioteca padrão do Python):

    # na instância
    python3 scripts/bateria_regressao.py
    # no PC, com o túnel aberto pelo kit ("Iniciar Robo.cmd")
    python scripts/bateria_regressao.py --url http://localhost:7860

Código de saída 0 quando todos os casos passam e 1 quando algum falha.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass, field

# processos públicos do TRT18 usados nos testes do TCC
PENDENTE_META1 = "0000713-35.2026.5.18.0002"       # caso novo de 2026 sem sentença
JULGADO_NO_PERIODO = "0001583-78.2025.5.18.0111"   # acordo homologado em 2026, em liquidação
TRANSITADO = "0002006-59.2025.5.18.0201"           # julgado em 2026, transitado, em execução
REMESSA_RECURSO = "0000683-95.2025.5.18.0014"      # remessa para recurso: baixado no 1º grau

PERGUNTA_META = "Qual movimento está impactando na meta? O que preciso fazer para parar de constar lá?"
TEMPO_MAXIMO_S = 60.0

# hipóteses do glossário que as regras não modelam: não podem aparecer na redação do modelo
NAO_MODELADO = ("medida protetiva", "medidas protetivas", "procedimento resolvido")
_DATA = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")


@dataclass
class Passo:
    mensagem: str
    intent: str | None = None              # intent esperada (None: não confere)
    contem: list[str] = field(default_factory=list)
    nao_contem: list[str] = field(default_factory=list)
    sem_deixar_de_constar: bool = False    # processo sem meta pendente


@dataclass
class Caso:
    nome: str
    passos: list[Passo]


CASOS = [
    Caso("Processo pendente na Meta 1", [
        Passo(PENDENTE_META1, intent="process_lookup",
              contem=["Meta 1", "pesa contra a meta", "Distribuído por sorteio"]),
        Passo(PERGUNTA_META, intent="meta_impact",
              contem=["Base da análise", "Distribuído por sorteio", "desde que o ato"]),
        Passo("Esse processo pesa na Meta 2?", intent="meta_impact",
              contem=["não entra no cálculo"]),
    ]),
    Caso("Processo julgado no período (sem meta pendente)", [
        Passo(JULGADO_NO_PERIODO, intent="process_lookup",
              contem=["conta como julgado no período", "Homologada a transação"]),
        Passo("quais são os movimentos deste processo?",
              contem=["Movimentacao 1:", "Movimentacao 10:", "mais recentes"]),
        Passo("Quais são os movimentos dele até hoje?",
              contem=["Movimentacao 11:"]),
        Passo("algum deles impacta negativamente em alguma das metas?", intent="meta_impact",
              contem=["Base da análise"], sem_deixar_de_constar=True),
    ]),
    Caso("Trânsito em julgado não é baixa", [
        Passo(TRANSITADO, intent="process_lookup",
              contem=["Situação pelo autômato: PENDENTE"]),
        Passo(PERGUNTA_META, intent="meta_impact",
              contem=["Base da análise"], sem_deixar_de_constar=True),
    ]),
    Caso("Remessa para recurso é baixa no 1º grau", [
        Passo(REMESSA_RECURSO, intent="process_lookup",
              contem=["Situação pelo autômato: BAIXADO"]),
    ]),
    Caso("Pergunta sobre a meta sem processo informado", [
        Passo(PERGUNTA_META, contem=["número do processo"], nao_contem=["Base da análise"]),
    ]),
    Caso("Pergunta fora do escopo", [
        Passo("Qual é a receita de bolo de cenoura?", intent="out_of_scope",
              nao_contem=["Meta 1", "Movimentacao"]),
    ]),
]


def _sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def _enviar(url: str, mensagem: str, sessao: str | None) -> tuple[dict, float]:
    corpo = json.dumps({"session_id": sessao, "mensagem": mensagem}).encode()
    pedido = urllib.request.Request(f"{url}/api/processos/chat", data=corpo,
                                    headers={"Content-Type": "application/json"})
    inicio = time.perf_counter()
    with urllib.request.urlopen(pedido, timeout=300) as resposta:
        dados = json.loads(resposta.read())
    return dados, time.perf_counter() - inicio


def _conferir(passo: Passo, resultado: dict, segundos: float) -> list[str]:
    falhas = []
    resposta = resultado.get("resposta") or ""
    if passo.intent and resultado.get("intent") != passo.intent:
        falhas.append(f"intent {resultado.get('intent')!r}, esperada {passo.intent!r}")
    for trecho in passo.contem:
        if _sem_acento(trecho) not in _sem_acento(resposta):
            falhas.append(f"faltou {trecho!r}")
    for trecho in passo.nao_contem:
        if _sem_acento(trecho) in _sem_acento(resposta):
            falhas.append(f"não devia conter {trecho!r}")

    # parte redigida pelo modelo (antes do bloco calculado pelas regras)
    if "\n\nBase da análise" in resposta:
        redacao, base = resposta.split("\n\nBase da análise", 1)
        redacao_norm = _sem_acento(redacao)
        for termo in NAO_MODELADO:
            if termo in redacao_norm:
                falhas.append(f"modelo citou hipótese não modelada: {termo!r}")
        if passo.sem_deixar_de_constar and re.search(r"deix(ar|e|a) de constar", redacao_norm):
            falhas.append("modelo falou em 'deixar de constar' sem meta pendente")
        datas_inventadas = set(_DATA.findall(redacao)) - set(_DATA.findall(base))
        if datas_inventadas:
            falhas.append(f"modelo citou datas fora do cálculo: {sorted(datas_inventadas)}")
    if segundos > TEMPO_MAXIMO_S:
        falhas.append(f"demorou {segundos:.0f} s (limite {TEMPO_MAXIMO_S:.0f} s)")
    return falhas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--url", default="http://127.0.0.1:7860",
                        help="endereço da interface (padrão: a própria instância)")
    parser.add_argument("--detalhes", action="store_true", help="mostra as respostas completas")
    args = parser.parse_args()
    url = args.url.rstrip("/")

    total = aprovados = 0
    inicio_geral = time.perf_counter()
    for caso in CASOS:
        print(f"\n== {caso.nome}")
        sessao = None
        for passo in caso.passos:
            total += 1
            try:
                dados, segundos = _enviar(url, passo.mensagem, sessao)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                print(f"   FALHOU  {passo.mensagem[:60]!r}: sem resposta ({exc})")
                continue
            sessao = dados.get("session_id")
            resultado = dados.get("resultado") or {}
            falhas = _conferir(passo, resultado, segundos)
            situacao = "ok     " if not falhas else "FALHOU "
            print(f"   {situacao} {segundos:5.1f} s  {passo.mensagem[:60]!r}")
            for falha in falhas:
                print(f"            - {falha}")
            if args.detalhes or falhas:
                for linha in (resultado.get("resposta") or "").splitlines()[:12]:
                    print(f"            | {linha}")
            aprovados += not falhas

    print(f"\n{aprovados} de {total} passos aprovados em {time.perf_counter() - inicio_geral:.0f} s.")
    return 0 if aprovados == total else 1


if __name__ == "__main__":
    sys.exit(main())
