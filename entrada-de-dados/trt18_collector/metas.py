"""
Diagnóstico de um processo frente às Metas Nacionais 1 e 2 do CNJ (Justiça do Trabalho).

O que este módulo responde
--------------------------
Dado o histórico de movimentos de um processo (árvore JSON da camada de dados):

1. o processo consta como pendente na Meta 1 e/ou na Meta 2?
2. qual movimento o colocou no cômputo e qual movimento o retira?
3. há indício de inconsistência de registro (ato praticado sem o movimento
   correspondente)?

Fonte das regras
----------------
CNJ. Glossário das Metas Nacionais do Poder Judiciário 2026 - Justiça do Trabalho,
versão 3 (março/2026). As regras abaixo transcrevem esse glossário:

* As duas metas alcançam apenas processos de CONHECIMENTO.
* Caso novo: situação Pendente (88) iniciada por Distribuído (24), entre outras.
* Julgado (para as metas) é a PRIMEIRA ocorrência, o que ocorrer primeiro, de:
    - primeira sentença: situações das hierarquias 62, 27 e 28, incluída a
      homologatória (29);
    - baixa: situações 2, 10, 23 e 41, ou Pendente (88) finalizada por execução
      iniciada (26), fase processual iniciada (65), liquidação iniciada (91) ou
      remessa em grau de recurso (132).
* Meta 1/2026: julgar mais processos de conhecimento do que os distribuídos de
  20/12/2025 a 19/12/2026, excluídos os suspensos e sobrestados no período.
* Meta 2/2026 (TRTs): julgar até 31/12/2026 pelo menos 94% dos distribuídos até
  31/12/2024 e 99% dos pendentes de julgamento há 5 anos (2021) ou mais,
  desconsiderados os suspensos ao final de 2026 e os dessobrestados em 2026.
* Processo pendente em uma meta (aba Downloads do painel): distribuído = 1,
  suspenso = 0 e julgado = 0.

Limites assumidos (declarados na saída)
---------------------------------------
* O portal de consulta entrega a DENOMINAÇÃO do movimento, não o código da TPU
  nem a Situação do Datamart; a correspondência é feita por regras sobre o texto.
* A fase de conhecimento é inferida pela classe processual, sem a parametrização
  completa do DataJud (id_fase_processual / id_tipo_procedimento).
* Para a Meta 2 adota-se 01/01/2026 como início do período de apuração.
* O resultado da meta é agregado por unidade; aqui se informa apenas se o
  processo pesa no cálculo.

Princípio do artefato: este módulo CALCULA; o modelo de linguagem apenas redige
a orientação a partir do resultado calculado.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Optional

try:  # dentro do package trt18_collector
    from .afd import executar as executar_afd
    from .movimentos_tpu import Categoria, _sem_acento, classificar_movimento, normalizar_denominacao
except ImportError:  # uso direto na pasta do projeto
    from afd import executar as executar_afd
    from movimentos_tpu import Categoria, _sem_acento, classificar_movimento, normalizar_denominacao


FONTE = ("CNJ. Glossário das Metas Nacionais do Poder Judiciário 2026 - Justiça do Trabalho, "
         "versão 3 (março/2026)")

# Parâmetros por ano de apuração (glossário do ano correspondente).
PARAMETROS = {
    2026: {
        "m1_inicio": date(2025, 12, 20),
        "m1_fim": date(2026, 12, 19),
        "m2_inicio": date(2026, 1, 1),
        "m2_fim": date(2026, 12, 31),
        "m2_corte": date(2024, 12, 31),          # faixa geral: distribuídos até
        "m2_corte_antigos": date(2021, 12, 31),  # pendentes há 5 anos ou mais
        "m2_percentual": 94,
        "m2_percentual_antigos": 99,
    },
}

# Tipos de evento relevantes para as metas
CASO_NOVO = "CASO_NOVO"
JULGAMENTO = "JULGAMENTO"
BAIXA = "BAIXA"
FASE_INICIADA = "FASE_INICIADA"
REMESSA_RECURSO = "REMESSA_RECURSO"
SUSPENSAO = "SUSPENSAO"
DESSOBRESTAMENTO = "DESSOBRESTAMENTO"
CONCLUSAO_SENTENCA = "CONCLUSAO_SENTENCA"

# eventos que contam como "julgado" na apuração das Metas 1 e 2
EVENTOS_QUE_JULGAM = (JULGAMENTO, BAIXA, FASE_INICIADA, REMESSA_RECURSO)

# Classes que não são de conhecimento (execução, cumprimento, cartas)
_CLASSES_FORA = ("exfis", "extiex", "cumsen", "cumprse", "exprovas", "cartprec", "cartord",
                 "execucao", "cumprimento", "carta precatoria", "carta de ordem")
_INDICIOS_EXECUCAO = ("execucao", "penhora", "bndt", "liquidacao", "agravo de peticao",
                      "precatorio", "rpv", "hasta", "leilao", "sisbajud", "renajud")

O_QUE_RETIRA = [
    "sentença proferida (julgamento com ou sem resolução de mérito)",
    "homologação de acordo",
    "arquivamento definitivo ou baixa definitiva",
    "remessa dos autos em grau de recurso",
    "início da liquidação ou da execução",
]


@dataclass
class EventoMeta:
    tipo: str
    data: Optional[date]
    denominacao: str
    situacao_datamart: str
    ordem: int = 0

    def resumo(self) -> str:
        quando = self.data.strftime("%d/%m/%Y") if self.data else "sem data"
        return f'"{self.denominacao}", em {quando}'


@dataclass
class ResultadoMeta:
    meta: str
    status: str          # PENDENTE | CUMPRIDA | SUSPENSO | FORA | NAO_SE_APLICA | INCONCLUSIVO
    resumo: str
    motivo: str
    faixa: Optional[str] = None
    movimento_determinante: Optional[str] = None
    o_que_retira: list[str] = field(default_factory=list)


@dataclass
class DiagnosticoMetas:
    numero: str
    ano: int
    classe: Optional[str]
    escopo: str                       # CONHECIMENTO | FORA | INDEFINIDO
    data_caso_novo: Optional[date]
    origem_data_caso_novo: str
    primeiro_julgado: Optional[EventoMeta]
    suspenso_atualmente: bool
    estado_automato: str
    situacao_automato: str
    metas: list[ResultadoMeta]
    ultimo_ato_relevante: Optional[EventoMeta] = None
    inconsistencias: list[str] = field(default_factory=list)
    alertas: list[str] = field(default_factory=list)
    fonte: str = FONTE

    @property
    def consta_em_alguma_meta(self) -> bool:
        return any(m.status == "PENDENTE" for m in self.metas)

    def to_dict(self) -> dict:
        return _serializar(asdict(self))

    def texto(self) -> str:
        """Texto determinístico do diagnóstico (base factual da orientação)."""
        linhas = [f"Metas Nacionais do CNJ ({self.ano}):"]
        for m in self.metas:
            linhas.append(f"- {m.meta}: {m.resumo} {m.motivo}".rstrip())
            if m.movimento_determinante:
                linhas.append(f"  Movimento determinante: {m.movimento_determinante}.")
        pendentes = [m for m in self.metas if m.status == "PENDENTE"]
        if pendentes:
            linhas.append("Para deixar de constar, o processo precisa receber o primeiro destes "
                          "registros, desde que o ato tenha sido de fato praticado: "
                          + "; ".join(O_QUE_RETIRA) + ".")
        for inc in self.inconsistencias:
            linhas.append(f"Possível inconsistência de registro: {inc}")
        for al in self.alertas:
            linhas.append(f"Atenção: {al}")
        linhas.append(f"Situação pelo autômato: {self.situacao_automato} "
                      f"(estado {self.estado_automato}).")
        return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Leitura tolerante da árvore JSON
# ---------------------------------------------------------------------------
def _serializar(valor):
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, dict):
        return {k: _serializar(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [_serializar(v) for v in valor]
    return valor


def _para_data(valor) -> Optional[date]:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if not isinstance(valor, str) or not valor.strip():
        return None
    texto = valor.strip()
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if m:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    return None


def _descricao(mov: dict) -> str:
    for chave in ("descricao", "titulo", "movimento", "nome"):
        valor = mov.get(chave)
        if isinstance(valor, str) and valor.strip():
            return valor.strip()
    return ""


def _data_mov(mov: dict) -> Optional[date]:
    for chave in ("data", "data_hora", "data_movimento"):
        d = _para_data(mov.get(chave))
        if d:
            return d
    return None


def _movimentos_ordenados(arvore: dict) -> list[dict]:
    movs = [m for m in (arvore.get("movimentacoes") or []) if isinstance(m, dict)]
    # ordem cronológica; a ordem original desempata movimentos do mesmo dia
    indexados = list(enumerate(movs))
    indexados.sort(key=lambda par: (_data_mov(par[1]) or date.min,
                                    par[1].get("ordem") if isinstance(par[1].get("ordem"), int)
                                    else par[0]))
    return [m for _, m in indexados]


# ---------------------------------------------------------------------------
# Classificação do movimento para fins das metas
# ---------------------------------------------------------------------------
def _eh_incidente(denominacao: str) -> bool:
    """Julgamento de incidente traz "( / Nome do incidente)"; o principal traz "(Classe / )"."""
    return bool(re.search(r"\(\s*[^()]*?/\s*[^)\s]", re.sub(r"\(\d+\)", "", denominacao)))


def classificar_para_metas(denominacao: str) -> Optional[tuple[str, str]]:
    """Devolve (tipo_do_evento, situacao_datamart) ou None se o movimento não afeta as metas."""
    t = _sem_acento(normalizar_denominacao(denominacao))
    if not t or t.startswith("juntada"):
        return None  # petição ou documento da parte: não é ato do juízo

    if t.startswith("conclusos os autos para julgamento"):
        if "proferir sentenca" in t or "generica" in t:
            return CONCLUSAO_SENTENCA, "68 (Concluso para julgamento)"
        return None  # conclusão para julgar incidente

    incidente = _eh_incidente(denominacao) or " o incidente" in t

    # julgamento (primeira sentença): hierarquias 62, 27 e 28, incluída a homologatória (29)
    if not incidente:
        if t.startswith("julgado"):
            return JULGAMENTO, "27 (Julgamento com resolução de mérito)"
        if t.startswith("homologad") and any(k in t for k in ("transacao", "acordo", "conciliacao")):
            return JULGAMENTO, "29 (Julgamento homologatório proferido)"
        if t.startswith("homologada a desistencia") or t.startswith("homologada a renuncia"):
            return JULGAMENTO, "28 (Julgamento sem resolução de mérito)"
        if t.startswith("extinto o processo") or t.startswith("extinto sem resolucao"):
            return JULGAMENTO, "28 (Julgamento sem resolução de mérito)"
        if t.startswith("indeferida a peticao inicial"):
            return JULGAMENTO, "28 (Julgamento sem resolução de mérito)"
        if re.match(r"arquivad[oa] (o processo|a reclamacao)", t) and "ausencia" in t:
            return JULGAMENTO, "28 (Julgamento sem resolução de mérito)"
        if t.startswith("pronunciada a decadencia") or t.startswith("pronunciada a prescricao"):
            return JULGAMENTO, "27 (Julgamento com resolução de mérito)"
        if t.startswith("proferida sentenca"):
            return JULGAMENTO, "62 (Julgamento)"

    # baixa da fase de conhecimento
    if "arquivados os autos definitivamente" in t or "arquivamento definitivo" in t:
        return BAIXA, "2 (Arquivado definitivamente)"
    if not incidente and (t.startswith("baixa definitiva") or t.startswith("baixado definitivamente")):
        return BAIXA, "10 (Baixado definitivamente)"
    if "cancelada a distribuicao" in t or "distribuicao cancelada" in t:
        return BAIXA, "23 (Distribuição cancelada)"
    if t.startswith("remetidos os autos"):
        if "processar recurso" in t:
            return REMESSA_RECURSO, "132 (Remetido em grau de recurso)"
        if any(k in t for k in ("incompetencia", "declinio", "outra justica", "outro tribunal")):
            return BAIXA, "41 (Remetido)"
        return None
    if t.startswith("iniciada a liquidacao"):
        return FASE_INICIADA, "91 (Liquidação iniciada)"
    if t.startswith("iniciada a execucao"):
        return FASE_INICIADA, "26 (Execução não criminal iniciada)"

    # suspensão e retomada (definem o Pendente Líquido, situação 25)
    if (t.startswith("encerrada a suspensao") or t.startswith("revogada a suspensao")
            or t.startswith("levantada a suspensao") or t.startswith("dessobrestad")):
        return DESSOBRESTAMENTO, "25 (Pendente líquido reaberto)"
    categoria, _ = classificar_movimento(denominacao)
    if categoria == Categoria.SUSPENSAO:
        return SUSPENSAO, "45-49 (Suspenso/sobrestado)"
    if categoria == Categoria.DISTRIBUICAO and t.startswith("distribuido"):
        return CASO_NOVO, "24 (Distribuído)"
    return None


def _denominacao_limpa(denominacao: str) -> str:
    """Denominação sem as partes variáveis: nomes, documentos e códigos entre parênteses."""
    s = normalizar_denominacao(denominacao)
    s = re.sub(r"\s+(de|a|em)\s+<(NOME|DATA)>.*$", "", s)
    s = re.sub(r"\s*\(\d+\)", "", s)
    s = s.replace("<NOME>", "").replace("<DATA>", "").replace("<HORA>", "")
    s = re.sub(r"\s*/\s*\)", ")", s)  # "(Classe / )" -> "(Classe)"
    return re.sub(r"\s+", " ", s).strip(" .-")[:140]


def extrair_eventos(arvore: dict) -> list[EventoMeta]:
    eventos = []
    for i, mov in enumerate(_movimentos_ordenados(arvore), start=1):
        denominacao = _descricao(mov)
        classificado = classificar_para_metas(denominacao)
        if classificado is None:
            continue
        tipo, situacao = classificado
        eventos.append(EventoMeta(tipo=tipo, data=_data_mov(mov),
                                  denominacao=_denominacao_limpa(denominacao),
                                  situacao_datamart=situacao, ordem=i))
    return eventos


# ---------------------------------------------------------------------------
# Avaliação
# ---------------------------------------------------------------------------
def _escopo(classe: Optional[str]) -> str:
    if not classe:
        return "INDEFINIDO"
    c = _sem_acento(classe)
    if any(k in c for k in _CLASSES_FORA):
        return "FORA"
    return "CONHECIMENTO"


def _dentro(d: Optional[date], inicio: date, fim: date) -> bool:
    return d is not None and inicio <= d <= fim


def _fmt(d: Optional[date]) -> str:
    return d.strftime("%d/%m/%Y") if d else "data não identificada"


def avaliar(arvore: dict, ano: int = 2026, hoje: Optional[date] = None) -> DiagnosticoMetas:
    """Avalia o processo frente às Metas 1 e 2 do ano informado."""
    if ano not in PARAMETROS:
        raise ValueError(f"Sem parâmetros das metas para o ano {ano}.")
    par = PARAMETROS[ano]
    hoje = hoje or date.today()

    processo = arvore.get("processo") if isinstance(arvore.get("processo"), dict) else {}
    numero = str(processo.get("numero") or processo.get("numero_normalizado") or "")
    classe = processo.get("classe_judicial") or processo.get("classe")
    escopo = _escopo(classe)

    movimentos = _movimentos_ordenados(arvore)
    eventos = extrair_eventos(arvore)
    afd = executar_afd([{"ordem": m.get("ordem", i), "data": m.get("data"),
                         "descricao": _descricao(m)} for i, m in enumerate(movimentos, 1)])

    # data do caso novo: distribuição registrada; na falta, autuação
    distribuicoes = [e for e in eventos if e.tipo == CASO_NOVO and e.data]
    data_caso_novo = _para_data(processo.get("data_distribuicao"))
    origem = "campo data de distribuição"
    evento_entrada = distribuicoes[0] if distribuicoes else None
    if data_caso_novo is None and distribuicoes:
        data_caso_novo, origem = distribuicoes[0].data, "movimento de distribuição"
    if data_caso_novo is None:
        data_caso_novo, origem = _para_data(processo.get("data_autuacao")), "campo data de autuação"
    if data_caso_novo is None:
        origem = "não identificada"
    # processo antigo recadastrado: a distribuição registrada pode ser posterior à autuação;
    # o caso novo é a entrada mais antiga
    autuacao = _para_data(processo.get("data_autuacao"))
    if autuacao is not None and data_caso_novo is not None and autuacao < data_caso_novo:
        data_caso_novo, origem = autuacao, "campo data de autuação"

    julgados = [e for e in eventos if e.tipo in EVENTOS_QUE_JULGAM]
    primeiro_julgado = julgados[0] if julgados else None

    # suspensão vigente: o último evento de suspensão/retomada é uma suspensão
    susp = [e for e in eventos if e.tipo in (SUSPENSAO, DESSOBRESTAMENTO)]
    suspenso = bool(susp) and susp[-1].tipo == SUSPENSAO and primeiro_julgado is None
    ultima_suspensao = next((e for e in reversed(susp) if e.tipo == SUSPENSAO), None)
    ultimo_dessobrestamento = next((e for e in reversed(susp) if e.tipo == DESSOBRESTAMENTO), None)
    conclusoes = [e for e in eventos if e.tipo == CONCLUSAO_SENTENCA]
    ultima_conclusao = conclusoes[-1] if conclusoes else None

    inconsistencias: list[str] = []
    alertas: list[str] = []

    # histórico possivelmente incompleto (processo físico convertido) ou fase posterior
    textos = [_sem_acento(_descricao(m)) for m in movimentos]
    convertido = any("convertida a tramitacao do processo do meio fisico" in t for t in textos[:5])
    em_execucao = any(any(k in t for k in _INDICIOS_EXECUCAO) for t in textos)
    historico_incompleto = primeiro_julgado is None and (convertido or em_execucao)
    if primeiro_julgado is not None:
        # sinais de fase posterior ANTES do primeiro evento localizado: o julgamento real é
        # anterior ao histórico digital, e o evento localizado não é o primeiro do processo
        anteriores = textos[:max(primeiro_julgado.ordem - 1, 0)]
        if convertido or any(any(k in t for k in _INDICIOS_EXECUCAO) for t in anteriores):
            historico_incompleto = True
    julgado_para_metas = None if historico_incompleto else primeiro_julgado

    # documento de sentença sem o movimento de julgamento correspondente
    docs_sentenca = []
    for doc in (arvore.get("documentos") or []):
        if not isinstance(doc, dict):
            continue
        titulo = _sem_acento(str(doc.get("titulo") or doc.get("tipo") or ""))
        if titulo.startswith("sentenca") or "homologacao de acordo" in titulo:
            docs_sentenca.append((_para_data(doc.get("data")), str(doc.get("titulo") or "")))
    tem_julgamento_mov = any(e.tipo == JULGAMENTO for e in eventos)
    if docs_sentenca and not tem_julgamento_mov and escopo != "FORA" and not historico_incompleto:
        d0, t0 = sorted(docs_sentenca, key=lambda x: x[0] or date.min)[0]
        inconsistencias.append(
            f'há documento "{t0}" juntado em {_fmt(d0)}, mas nenhum movimento de julgamento '
            "foi localizado no histórico. Verifique se o movimento da sentença foi lançado.")
    if (primeiro_julgado is not None and primeiro_julgado.tipo == FASE_INICIADA
            and not tem_julgamento_mov):
        inconsistencias.append(
            "a liquidação ou a execução foi iniciada sem movimento de julgamento anterior "
            "no histórico consultado.")

    if escopo == "INDEFINIDO":
        alertas.append("a classe processual não foi identificada; assumiu-se processo de "
                       "conhecimento.")
    if data_caso_novo is None:
        alertas.append("a data de distribuição não foi identificada.")
    if historico_incompleto and escopo != "FORA":
        alertas.append("há sinais de fase posterior ou de processo físico digitalizado antes de "
                       "qualquer julgamento localizado; o julgamento pode ter ocorrido antes do "
                       "período coberto pelos movimentos consultados.")

    situacao_coleta = str(processo.get("situacao") or "").upper()
    if situacao_coleta in ("PENDENTE", "BAIXADO") and situacao_coleta != afd.situacao:
        alertas.append(f"a situação registrada na coleta ({situacao_coleta}) difere da "
                       f"classificação do autômato ({afd.situacao}), que segue as Situações do "
                       "Datamart do CNJ.")

    ultimo_ato = ultima_suspensao if suspenso else (ultima_conclusao or evento_entrada)

    metas = [
        _avaliar_meta1(par, escopo, data_caso_novo, evento_entrada, julgado_para_metas, suspenso,
                       ultima_suspensao, ultimo_dessobrestamento, ultima_conclusao,
                       historico_incompleto),
        _avaliar_meta2(par, escopo, data_caso_novo, evento_entrada, julgado_para_metas, suspenso,
                       ultima_suspensao, ultimo_dessobrestamento, ultima_conclusao,
                       historico_incompleto),
    ]

    return DiagnosticoMetas(
        numero=numero, ano=ano, classe=classe, escopo=escopo,
        data_caso_novo=data_caso_novo, origem_data_caso_novo=origem,
        primeiro_julgado=primeiro_julgado, suspenso_atualmente=suspenso,
        estado_automato=afd.estado_final.value, situacao_automato=afd.situacao,
        metas=metas, ultimo_ato_relevante=ultimo_ato,
        inconsistencias=inconsistencias, alertas=alertas,
    )


def _nao_se_aplica(meta: str) -> ResultadoMeta:
    return ResultadoMeta(
        meta=meta, status="NAO_SE_APLICA", resumo="não se aplica.",
        motivo="A meta alcança apenas processos de conhecimento, e a classe deste processo é "
               "de execução, cumprimento ou carta.")


def _inconclusivo(meta: str) -> ResultadoMeta:
    return ResultadoMeta(
        meta=meta, status="INCONCLUSIVO", resumo="não foi possível concluir.",
        motivo="O histórico consultado não permite afirmar se houve julgamento na fase de "
               "conhecimento.")


def _determinante_pendencia(entrada, conclusao, data_caso_novo) -> str:
    if conclusao is not None:
        return (f"{conclusao.resumo()} (concluso para sentença, sem movimento de julgamento "
                "posterior)")
    if entrada is not None:
        return f"{entrada.resumo()} (entrada do processo, sem movimento de julgamento posterior)"
    return f"distribuição em {_fmt(data_caso_novo)}, sem movimento de julgamento posterior"


def _avaliar_meta1(par, escopo, data_caso_novo, entrada, julgado, suspenso, suspensao,
                   dessobrestamento, conclusao, historico_incompleto) -> ResultadoMeta:
    meta = "Meta 1 (julgar mais processos que os distribuídos)"
    ini, fim = par["m1_inicio"], par["m1_fim"]
    periodo = f"{_fmt(ini)} a {_fmt(fim)}"
    if escopo == "FORA":
        return _nao_se_aplica(meta)

    if julgado is not None:
        if _dentro(julgado.data, ini, fim):
            return ResultadoMeta(
                meta=meta, status="CUMPRIDA", resumo="o processo conta como julgado no período.",
                motivo=f"O primeiro julgamento ou baixa ocorreu dentro do período de {periodo} "
                       f"(situação {julgado.situacao_datamart}).",
                movimento_determinante=julgado.resumo())
        return ResultadoMeta(
            meta=meta, status="FORA", resumo="o processo não pesa na meta deste ano.",
            motivo=f"O primeiro julgamento ou baixa ocorreu fora do período de {periodo} "
                   f"(situação {julgado.situacao_datamart}).",
            movimento_determinante=julgado.resumo())

    if historico_incompleto:
        return _inconclusivo(meta)

    caso_novo_no_periodo = _dentro(data_caso_novo, ini, fim)
    dessobrestado_no_periodo = (dessobrestamento is not None
                                and _dentro(dessobrestamento.data, ini, fim) and not suspenso)
    if not caso_novo_no_periodo and not dessobrestado_no_periodo:
        return ResultadoMeta(
            meta=meta, status="FORA", resumo="o processo não entra no cálculo deste ano.",
            motivo=f"Foi distribuído em {_fmt(data_caso_novo)}, fora do período de {periodo}, e "
                   "não foi dessobrestado no período. Processos antigos sem julgamento são "
                   "acompanhados pela Meta 2.")
    if suspenso:
        return ResultadoMeta(
            meta=meta, status="SUSPENSO", resumo="o processo está excluído do cálculo.",
            motivo="Ele está suspenso ou sobrestado, e os suspensos no período são "
                   "descontados dos casos novos.",
            movimento_determinante=suspensao.resumo() if suspensao else None)
    origem = ("foi dessobrestado no período" if dessobrestado_no_periodo and not caso_novo_no_periodo
              else f"é caso novo do período ({periodo})")
    determinante = (dessobrestamento.resumo() + " (retomada da tramitação, sem julgamento posterior)"
                    if dessobrestado_no_periodo and not caso_novo_no_periodo
                    else _determinante_pendencia(entrada, conclusao, data_caso_novo))
    return ResultadoMeta(
        meta=meta, status="PENDENTE", resumo="o processo consta como pendente e pesa contra a meta.",
        motivo=f"Ele {origem} e ainda não tem julgamento nem baixa registrados.",
        movimento_determinante=determinante, o_que_retira=list(O_QUE_RETIRA))


def _avaliar_meta2(par, escopo, data_caso_novo, entrada, julgado, suspenso, suspensao,
                   dessobrestamento, conclusao, historico_incompleto) -> ResultadoMeta:
    meta = "Meta 2 (julgar processos mais antigos)"
    ini, fim = par["m2_inicio"], par["m2_fim"]
    if escopo == "FORA":
        return _nao_se_aplica(meta)
    if data_caso_novo is None:
        return _inconclusivo(meta)

    if data_caso_novo > par["m2_corte"]:
        return ResultadoMeta(
            meta=meta, status="FORA", resumo="o processo não entra no cálculo deste ano.",
            motivo=f"Foi distribuído em {_fmt(data_caso_novo)}, depois da data de corte de "
                   f"{_fmt(par['m2_corte'])}.")
    antigo = data_caso_novo <= par["m2_corte_antigos"]
    faixa = (f"pendentes há 5 anos ou mais (distribuídos até {_fmt(par['m2_corte_antigos'])}; "
             f"alvo de {par['m2_percentual_antigos']}%)" if antigo
             else f"distribuídos até {_fmt(par['m2_corte'])} (alvo de {par['m2_percentual']}%)")

    if julgado is not None:
        if julgado.data is not None and julgado.data < ini:
            return ResultadoMeta(
                meta=meta, status="FORA", faixa=faixa,
                resumo="o processo não entra no cálculo deste ano.",
                motivo=f"Já havia julgamento ou baixa antes de {_fmt(ini)} "
                       f"(situação {julgado.situacao_datamart}).",
                movimento_determinante=julgado.resumo())
        return ResultadoMeta(
            meta=meta, status="CUMPRIDA", faixa=faixa,
            resumo="o processo conta como julgado na meta.",
            motivo=f"Estava no passivo da faixa de {faixa} e recebeu julgamento ou baixa em "
                   f"{julgado.data.year if julgado.data else 'data não identificada'} "
                   f"(situação {julgado.situacao_datamart}).",
            movimento_determinante=julgado.resumo())

    if historico_incompleto:
        return _inconclusivo(meta)
    if suspenso:
        return ResultadoMeta(
            meta=meta, status="SUSPENSO", faixa=faixa,
            resumo="o processo será desconsiderado se continuar suspenso.",
            motivo=f"Ele pertence à faixa de {faixa}, mas está suspenso ou sobrestado; os "
                   f"processos suspensos ao final de {fim.year} são desconsiderados.",
            movimento_determinante=suspensao.resumo() if suspensao else None)
    if dessobrestamento is not None and _dentro(dessobrestamento.data, ini, fim):
        return ResultadoMeta(
            meta=meta, status="FORA", faixa=faixa,
            resumo="o processo é desconsiderado no cálculo deste ano.",
            motivo=f"Ele foi dessobrestado em {fim.year}, e os dessobrestados durante o ano não "
                   "entram no cômputo.",
            movimento_determinante=dessobrestamento.resumo())
    return ResultadoMeta(
        meta=meta, status="PENDENTE", faixa=faixa,
        resumo="o processo consta como pendente e pesa contra a meta.",
        motivo=f"Ele pertence à faixa de {faixa} e ainda não tem julgamento nem baixa "
               "registrados.",
        movimento_determinante=_determinante_pendencia(entrada, conclusao, data_caso_novo),
        o_que_retira=list(O_QUE_RETIRA))


__all__ = ["avaliar", "extrair_eventos", "classificar_para_metas", "DiagnosticoMetas",
           "ResultadoMeta", "EventoMeta", "PARAMETROS", "FONTE", "O_QUE_RETIRA"]
