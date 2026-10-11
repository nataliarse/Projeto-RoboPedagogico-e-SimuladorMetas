"""Diagnóstico das Metas Nacionais 1 e 2 para o processo ativo da conversa.

As regras são calculadas pelo package ``trt18_collector`` (autômato e módulo
``metas``). O modelo de linguagem só redige a orientação a partir do resultado
calculado e dos trechos da norma recuperados (RAG); se ele falhar, ou citar data
que não está nos fatos nem na norma, vale o texto determinístico.
"""

from __future__ import annotations

import re
import unicodedata

from ollama_client import OllamaError, generate_text
from services.norma_rag import GLOSSARIO_FONTE, search_normas

META_IMPACT_INTENT = "meta_impact"

_CNJ_NUMBER = re.compile(r"\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}")
_DATE = re.compile(r"\d{2}/\d{2}/\d{4}")
_MAX_ORIENTATION_CHARS = 1400

META_SYSTEM_PROMPT = (
    "Você orienta servidores da Justiça do Trabalho sobre as Metas Nacionais 1 e 2 do CNJ. "
    "Responda em português do Brasil, em linguagem simples, em no máximo cinco frases, sem "
    "listas e sem títulos. Use somente os FATOS e os TRECHOS DA NORMA fornecidos: não invente "
    "datas, movimentos, percentuais nem normas. Nunca sugira registrar um movimento que não "
    "corresponda a um ato realmente praticado no processo."
)

NO_PROCESS_RESPONSE = (
    "Para avaliar o impacto nas Metas 1 e 2, informe primeiro o número do processo."
)
UNAVAILABLE_RESPONSE = (
    "Não foi possível avaliar o impacto deste processo nas Metas 1 e 2 com os dados disponíveis."
)


def is_meta_question(message: str) -> bool:
    tokens = set(re.findall(r"[a-z0-9]+", _normalize(message)))
    return bool(tokens & {"meta", "metas"})


def has_process_number(message: str) -> bool:
    return bool(_CNJ_NUMBER.search(str(message)))


def diagnose_process(process: dict | None):
    """Devolve o diagnóstico (``DiagnosticoMetas``) ou ``None`` se não for possível calcular."""
    if not isinstance(process, dict) or not process.get("movimentacoes"):
        return None
    try:
        from trt18_collector.metas import avaliar

        return avaliar(process)
    except Exception:  # módulo ausente ou dado fora do formato: o chat segue sem o diagnóstico
        return None


def build_meta_block(process: dict | None) -> str | None:
    diagnosis = diagnose_process(process)
    if diagnosis is None:
        return None
    return diagnosis.texto()


def answer_meta_question(message: str, process: dict | None) -> str:
    if not isinstance(process, dict) or not process:
        return NO_PROCESS_RESPONSE

    diagnosis = diagnose_process(process)
    if diagnosis is None:
        return UNAVAILABLE_RESPONSE

    facts = diagnosis.texto()
    passages = _norm_passages(message, diagnosis)
    orientation = _llm_orientation(message, _facts_for_llm(diagnosis), passages)
    if orientation and not _consistent_with(orientation, diagnosis):
        orientation = None
    citation = _citation(passages)
    if not orientation:
        return f"{facts}{citation}"
    return (
        f"{orientation}\n\nBase da análise (regras do Glossário das Metas {diagnosis.ano}):\n"
        f"{facts}{citation}"
    )


def _norm_passages(message: str, diagnosis) -> list[dict]:
    """Trechos do glossário das metas mais próximos da pergunta (RAG sobre a norma)."""
    metas = sorted({
        "Meta 1" if m.meta.startswith("Meta 1") else "Meta 2"
        for m in diagnosis.metas
        if m.status != "NAO_SE_APLICA"
    })
    if not metas:
        return []
    pending_metas = sorted({
        "Meta 1" if m.meta.startswith("Meta 1") else "Meta 2"
        for m in diagnosis.metas
        if m.status == "PENDENTE"
    })
    pending = bool(pending_metas)
    if pending:
        metas = pending_metas  # a norma buscada é a da meta em que o processo consta
    focus = (
        "processos pendentes na meta; o que é considerado julgado; critério de julgamento"
        if pending
        else "critério de julgamento; período de referência; processos considerados na meta"
    )
    return search_normas(f"{message.strip()} {focus}", metas=metas, top_k=2)


_STATUS_LABELS = {
    "PENDENTE": "PESA CONTRA A META (consta como pendente)",
    "CUMPRIDA": "CONTA A FAVOR DA META (julgado no período)",
    "FORA": "NÃO ENTRA NO CÁLCULO",
    "SUSPENSO": "EXCLUÍDO DO CÁLCULO (suspenso)",
    "NAO_SE_APLICA": "NÃO SE APLICA",
    "INCONCLUSIVO": "INCONCLUSIVO",
}


def _facts_for_llm(diagnosis) -> str:
    """Fatos em forma explícita, para o modelo repetir a conclusão em vez de deduzi-la."""
    lines = []
    for m in diagnosis.metas:
        number = "Meta 1" if m.meta.startswith("Meta 1") else "Meta 2"
        lines.append(f"- {number}: {_STATUS_LABELS.get(m.status, m.status)}. Motivo: {m.motivo}")
        if m.movimento_determinante:
            lines.append(f"  Movimento determinante na {number}: {m.movimento_determinante}.")
    if diagnosis.consta_em_alguma_meta:
        retira = "; ".join(next(m.o_que_retira for m in diagnosis.metas if m.o_que_retira))
        lines.append(f"- Para deixar de constar, é preciso o primeiro destes registros, se o ato "
                     f"foi de fato praticado: {retira}.")
    else:
        lines.append("- O processo não consta como pendente em nenhuma das duas metas.")
    for item in diagnosis.inconsistencias:
        lines.append(f"- Possível inconsistência de registro: {item}")
    return "\n".join(lines)


def _consistent_with(text: str, diagnosis) -> bool:
    """Descarta a redação que afirma peso nas duas metas quando o cálculo diz o contrário."""
    pending = [m for m in diagnosis.metas if m.status == "PENDENTE"]
    if len(pending) == len(diagnosis.metas):
        return True
    normalized = _normalize(text)
    return not re.search(r"(pesa|impacta|consta)[^.]{0,40}metas 1 e 2", normalized)


def _citation(passages: list[dict]) -> str:
    refs: list[str] = []
    for passage in passages:
        ref = f"{passage.get('meta')}, {passage.get('secao')} (p. {passage.get('pagina')})"
        if ref not in refs:
            refs.append(ref)
    if not refs:
        return ""
    return f"\nNorma consultada: {GLOSSARIO_FONTE}: " + "; ".join(refs) + "."


def _llm_orientation(message: str, facts: str, passages: list[dict] | None = None) -> str | None:
    norm_text = "\n".join(f"- {p['texto']}" for p in (passages or []))
    norm_block = f"TRECHOS DA NORMA (Glossário das Metas):\n{norm_text}\n\n" if norm_text else ""
    prompt = (
        f"PERGUNTA DO SERVIDOR: {message.strip()}\n\n"
        f"FATOS:\n{facts}\n\n"
        f"{norm_block}"
        "Escreva três frases curtas. Na primeira, diga em qual meta o processo pesa e em qual "
        "não pesa, repetindo a conclusão dos FATOS, sem comparar datas por conta própria. Na "
        "segunda, cite o movimento determinante. Na terceira, diga o que precisa acontecer para "
        "ele deixar de constar.\n\nRESPOSTA:"
    )
    try:
        text = generate_text(prompt, system_prompt=META_SYSTEM_PROMPT)
    except OllamaError:
        return None
    except Exception:
        return None

    text = re.sub(r"\n{3,}", "\n\n", str(text)).strip()
    if len(text) < 40:
        return None
    if len(text) > _MAX_ORIENTATION_CHARS:
        text = text[:_MAX_ORIENTATION_CHARS].rsplit(".", 1)[0] + "."
    # barreira contra invenção: toda data citada precisa constar nos fatos ou na norma
    if not set(_DATE.findall(text)) <= set(_DATE.findall(facts + norm_text)):
        return None
    return text


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", str(text).lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
