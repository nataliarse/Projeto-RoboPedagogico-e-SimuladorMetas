"""
Normalização e estruturação dos dados brutos -> esquema Pydantic.

Cobre as etapas 3 (análise/extração), 5 (limpeza/padronização) e parte da 6
(validação) do tarefas.md.

Como o portal do PJe pode mudar nomes de campos, o mapeamento é *tolerante*:
procuramos campos por uma lista de nomes candidatos, em qualquer nível do JSON
capturado da API. Se a API não trouxer algo, caímos no texto da página.

Funções principais:
  - limpar_texto / parse_data / parse_valor : utilitários de limpeza
  - extrair_campos(bruto) -> dict cru já achatado
  - normalizar(bruto) -> Processo  (objeto Pydantic validado)
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any, Iterable, Optional

from .models import (
    Coleta,
    DadosProcesso,
    Documento,
    Movimentacao,
    Parte,
    Polo,
    Processo,
    SituacaoProcesso,
    StatusColeta,
)


# ---------------------------------------------------------------------------
# Limpeza / padronização
# ---------------------------------------------------------------------------
def limpar_texto(valor: Any) -> Optional[str]:
    """Remove espaços extras, quebras de linha e normaliza para None se vazio."""
    if valor is None:
        return None
    texto = str(valor).replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto or None


def _sem_acento(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    ).lower()


_FORMATOS_DATA = (
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
)


def parse_data(valor: Any) -> Optional[datetime]:
    """Converte datas em vários formatos (BR e ISO) para datetime."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime(valor.year, valor.month, valor.day)

    texto = limpar_texto(valor)
    if not texto:
        return None

    # tenta extrair só a parte de data/hora se vier com texto em volta
    m = re.search(r"\d{2}/\d{2}/\d{4}(?:\s+\d{2}:\d{2}(?::\d{2})?)?", texto)
    candidato = m.group(0) if m else texto.replace("Z", "")

    for fmt in _FORMATOS_DATA:
        try:
            return datetime.strptime(candidato, fmt)
        except ValueError:
            continue
    # ISO genérico
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_valor(valor: Any) -> Optional[float]:
    """Converte 'R$ 1.234,56' ou '1234.56' em float."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = re.sub(r"[^\d,.-]", "", str(valor))
    if not texto:
        return None
    # formato BR: 1.234,56 -> 1234.56
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Busca tolerante dentro do JSON capturado
# ---------------------------------------------------------------------------
def _iter_dicts(obj: Any) -> Iterable[dict]:
    """Percorre recursivamente todos os dicts de uma estrutura aninhada."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _iter_dicts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_dicts(v)


def _buscar_chave(obj: Any, candidatos: Iterable[str]) -> Any:
    """
    Primeiro valor (escalar) cuja chave bate com algum candidato (sem acento).

    A ordem de `candidatos` é uma ordem de PRIORIDADE: percorremos todos os dicts
    procurando o primeiro candidato antes de tentar o segundo. Sem isso, a ordem
    das chaves no JSON decidiria o resultado — o que fazia, por exemplo,
    `distribuidoEm` (2025) sobrepor `autuadoEm` (1981) na data de autuação.
    """
    dicts = list(_iter_dicts(obj))
    for candidato in candidatos:
        alvo = _sem_acento(candidato)
        for d in dicts:
            for k, v in d.items():
                if _sem_acento(str(k)) == alvo and not isinstance(v, (dict, list)):
                    if v not in (None, "", []):
                        return v
    return None


def _buscar_lista(obj: Any, candidatos: Iterable[str]) -> list:
    """Primeira lista não-vazia cuja chave bate com algum candidato."""
    alvos = {_sem_acento(c) for c in candidatos}
    for d in _iter_dicts(obj):
        for k, v in d.items():
            if _sem_acento(str(k)) in alvos and isinstance(v, list) and v:
                return v
    return []


def _payloads(bruto: dict) -> list[Any]:
    return [r.get("payload") for r in bruto.get("respostas_api", []) if r.get("payload")]


# ---------------------------------------------------------------------------
# Extração por seção
# ---------------------------------------------------------------------------
def _extrair_partes(payloads: list[Any]) -> list[Parte]:
    partes: list[Parte] = []
    mapa_polo = {
        ("poloativo", "polo_ativo", "ativos", "reqte", "reclamantes"): Polo.ATIVO,
        ("polopassivo", "polo_passivo", "passivos", "reqdo", "reclamados"): Polo.PASSIVO,
    }
    for payload in payloads:
        for chaves, polo in mapa_polo.items():
            for lista in (_buscar_lista(payload, chaves),):
                for item in lista:
                    parte = _parte_de_item(item, polo)
                    if parte:
                        partes.append(parte)

        # formato alternativo: lista única "partes" com campo de polo embutido
        for item in _buscar_lista(payload, ("partes", "partesProcesso", "interessados")):
            if not isinstance(item, dict):
                continue
            polo_txt = _sem_acento(str(_buscar_chave(item, ("polo", "tipoParte", "papel")) or ""))
            polo = Polo.ATIVO if "ativ" in polo_txt else Polo.PASSIVO if "passiv" in polo_txt else Polo.OUTROS
            parte = _parte_de_item(item, polo)
            if parte:
                partes.append(parte)

    # remove duplicatas (mesmo nome + polo)
    vistos, unicas = set(), []
    for p in partes:
        chave = (p.polo, (p.nome or "").lower())
        if chave not in vistos:
            vistos.add(chave)
            unicas.append(p)
    return unicas


def _parte_de_item(item: Any, polo: Polo) -> Optional[Parte]:
    if isinstance(item, str):
        nome = limpar_texto(item)
        return Parte(polo=polo, nome=nome) if nome else None
    if not isinstance(item, dict):
        return None
    nome = limpar_texto(_buscar_chave(item, ("nome", "name", "nomeParte", "razaoSocial")))
    if not nome:
        return None
    representantes = [
        limpar_texto(_buscar_chave(r, ("nome", "name")) if isinstance(r, dict) else r)
        for r in _buscar_lista(item, ("representantes", "advogados", "procuradores"))
    ]
    return Parte(
        polo=polo,
        nome=nome,
        tipo=limpar_texto(_buscar_chave(item, ("tipo", "papel", "tipoParte", "qualificacao"))),
        documento=_so_digitos(_buscar_chave(item, ("documento", "cpf", "cnpj", "cpfCnpj"))),
        representantes=[r for r in representantes if r],
    )


def _so_digitos(valor: Any) -> Optional[str]:
    if valor is None:
        return None
    d = re.sub(r"\D", "", str(valor))
    return d or None


def _itens_processo(payloads: list[Any]) -> list[dict]:
    """
    Retorna a lista `itensProcesso` do PJe (endpoint /api/processos/{id}).

    É a fonte real do histórico: cada item tem `titulo`, `data` e o booleano
    `documento`, que distingue uma peça juntada de um movimento comum.
    """
    for payload in payloads:
        if isinstance(payload, dict) and isinstance(payload.get("itensProcesso"), list):
            return [i for i in payload["itensProcesso"] if isinstance(i, dict)]
    return []


def _extrair_movimentacoes(payloads: list[Any], texto_pagina: Optional[str]) -> list[Movimentacao]:
    brutas: list[dict] = []

    # formato real do PJe Consulta: itensProcesso (documento=False => movimento)
    itens = _itens_processo(payloads)
    if itens:
        brutas = [i for i in itens if not i.get("documento")]

    for payload in payloads if not brutas else []:
        lista = _buscar_lista(
            payload, ("movimentos", "movimentacoes", "movimentacao", "andamentos", "fases")
        )
        for item in lista:
            if isinstance(item, dict):
                brutas.append(item)
            elif isinstance(item, str):
                brutas.append({"descricao": item})

    movs: list[Movimentacao] = []
    if brutas:
        for i, item in enumerate(brutas, start=1):
            descricao = limpar_texto(
                _buscar_chave(item, ("descricao", "movimento", "nome", "titulo", "evento"))
            )
            if not descricao:
                continue
            movs.append(
                Movimentacao(
                    ordem=i,
                    data=parse_data(_buscar_chave(item, ("data", "dataHora", "dataMovimento", "dataHoraMovimento"))),
                    descricao=descricao,
                    complemento=limpar_texto(_buscar_chave(item, ("complemento", "observacao", "detalhe"))),
                    referencia=limpar_texto(_buscar_chave(item, ("link", "url", "href", "referencia"))),
                )
            )
    elif texto_pagina:
        # fallback: linhas do tipo "12/03/1999  Descrição..."
        for i, linha in enumerate(_linhas_movimento_do_texto(texto_pagina), start=1):
            data_txt, desc = linha
            movs.append(Movimentacao(ordem=i, data=parse_data(data_txt), descricao=desc))

    # ordena por data quando houver; mantém ordem original como desempate
    movs.sort(key=lambda m: (m.data or datetime.min, m.ordem))
    for i, m in enumerate(movs, start=1):
        m.ordem = i
    return movs


def _linhas_movimento_do_texto(texto: str) -> list[tuple[str, str]]:
    padrao = re.compile(r"(\d{2}/\d{2}/\d{4}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)\s+(.+)")
    resultado = []
    for linha in texto.splitlines():
        m = padrao.match(linha.strip())
        if m:
            desc = limpar_texto(m.group(2))
            if desc:
                resultado.append((m.group(1), desc))
    return resultado


def _extrair_documentos(payloads: list[Any]) -> list[Documento]:
    docs: list[Documento] = []

    # formato real do PJe: itens de `itensProcesso` marcados com documento=True
    for item in _itens_processo(payloads):
        if not item.get("documento"):
            continue
        titulo = limpar_texto(item.get("titulo"))
        if not titulo:
            continue
        docs.append(
            Documento(
                data=parse_data(item.get("data")),
                titulo=titulo,
                tipo=limpar_texto(item.get("tipoConteudo")),
                id_documento=limpar_texto(item.get("idUnicoDocumento") or item.get("id")),
            )
        )
    if docs:
        return docs

    for payload in payloads:
        for item in _buscar_lista(payload, ("documentos", "anexos", "pecas")):
            if not isinstance(item, dict):
                continue
            titulo = limpar_texto(_buscar_chave(item, ("titulo", "nome", "descricao", "tipo")))
            if not titulo:
                continue
            docs.append(
                Documento(
                    data=parse_data(_buscar_chave(item, ("data", "dataHora", "dataJuntada"))),
                    titulo=titulo,
                    tipo=limpar_texto(_buscar_chave(item, ("tipo", "tipoDocumento"))),
                    id_documento=limpar_texto(_buscar_chave(item, ("id", "idDocumento", "codigo"))),
                )
            )
    return docs


# ---------------------------------------------------------------------------
# Heurística de situação (PENDENTE x BAIXADO)
# ---------------------------------------------------------------------------
TERMOS_BAIXADO = (
    "baixa definitiva",
    "arquivado definitivamente",
    "arquivamento definitivo",
    "transitado em julgado",
    "transito em julgado",
    "extinta a execucao",
    "extincao da execucao",
    "definitivamente arquivado",
)

# Movimentos que indicam que o processo VOLTOU a tramitar depois de uma baixa.
# "arquivados os autos provisoriamente" não entra em TERMOS_BAIXADO justamente
# por ser provisório.
TERMOS_REATIVACAO = (
    "desarquivados os autos",
    "desarquivamento",
    "desarquivado",
    "reativado",
    "reativacao",
    "suspenso o processo",
    "retomada da execucao",
    "prosseguimento do feito",
)


def inferir_situacao(movimentacoes: list[Movimentacao]) -> SituacaoProcesso:
    """
    Heurística baseada no movimento relevante MAIS RECENTE.

    Vale quem veio por último: um processo pode ser baixado e depois voltar a
    tramitar (desarquivamento, suspensão por falência, retomada da execução).
    Por isso a varredura é de trás para frente e para no primeiro movimento que
    seja de baixa OU de reativação — o que aparecer antes decide.

    Atenção: o mapeamento "oficial" contra o fluxograma (códigos TPU/Situações
    do Datamart) é responsabilidade do motor de regras. Aqui entregamos apenas
    um palpite auxiliar.
    """
    if not movimentacoes:
        return SituacaoProcesso.INDEFINIDO

    for mov in reversed(movimentacoes):
        alvo = _sem_acento(f"{mov.descricao} {mov.complemento or ''}")
        if any(termo in alvo for termo in TERMOS_BAIXADO):
            return SituacaoProcesso.BAIXADO
        if any(termo in alvo for termo in TERMOS_REATIVACAO):
            return SituacaoProcesso.PENDENTE
    return SituacaoProcesso.PENDENTE


# ---------------------------------------------------------------------------
# Montagem do cabeçalho
# ---------------------------------------------------------------------------
def _numero_formatado(numero_norm: str) -> str:
    n = numero_norm
    if len(n) != 20:
        return numero_norm
    return f"{n[0:7]}-{n[7:9]}.{n[9:13]}.{n[13:14]}.{n[14:16]}.{n[16:20]}"


def extrair_campos(bruto: dict) -> dict:
    """Achata os principais campos do bruto (útil para a etapa de análise/EDA)."""
    payloads = _payloads(bruto)
    assunto = _buscar_chave(payloads, ("assunto", "assuntoPrincipal"))
    if not assunto:
        lst = _buscar_lista(payloads, ("assuntos",))
        if lst:
            primeiro = lst[0]
            assunto = primeiro if isinstance(primeiro, str) else _buscar_chave(primeiro, ("nome", "descricao"))
    return {
        "numero_normalizado": bruto.get("numero_normalizado"),
        "classe_judicial": limpar_texto(_buscar_chave(payloads, ("classeJudicial", "classe", "classeProcessual"))),
        "assunto": limpar_texto(assunto),
        "orgao_julgador": limpar_texto(_buscar_chave(payloads, ("orgaoJulgador", "orgao", "vara"))),
        "unidade": limpar_texto(_buscar_chave(payloads, ("unidade", "unidadeJudiciaria", "lotacao", "serventia"))),
        "jurisdicao": limpar_texto(_buscar_chave(payloads, ("jurisdicao", "comarca", "municipio"))),
        "data_autuacao": _buscar_chave(payloads, ("autuadoEm", "dataAutuacao", "autuacao")),
        "data_distribuicao": _buscar_chave(
            payloads, ("distribuidoEm", "dataDistribuicao", "distribuicao")
        ),
        "valor_causa": _buscar_chave(payloads, ("valorDaCausa", "valorCausa", "valor")),
        "qtd_respostas_api": len(payloads),
        "qtd_movimentos_texto": len(_linhas_movimento_do_texto(bruto.get("texto_pagina") or "")),
    }


def normalizar(bruto: dict) -> Processo:
    """Converte o dicionário bruto da coleta em um `Processo` validado."""
    payloads = _payloads(bruto)
    numero_norm = bruto.get("numero_normalizado") or re.sub(r"\D", "", bruto.get("numero", ""))
    campos = extrair_campos(bruto)

    movimentacoes = _extrair_movimentacoes(payloads, bruto.get("texto_pagina"))
    partes = _extrair_partes(payloads)
    documentos = _extrair_documentos(payloads)

    data_aut = parse_data(campos["data_autuacao"])
    data_dist = parse_data(campos["data_distribuicao"])
    dados = DadosProcesso(
        numero=_numero_formatado(numero_norm),
        numero_normalizado=numero_norm,
        classe_judicial=campos["classe_judicial"],
        assunto=campos["assunto"],
        orgao_julgador=campos["orgao_julgador"],
        unidade=campos["unidade"],
        jurisdicao=campos["jurisdicao"],
        data_autuacao=data_aut.date() if data_aut else None,
        data_distribuicao=data_dist.date() if data_dist else None,
        valor_causa=parse_valor(campos["valor_causa"]),
        situacao=inferir_situacao(movimentacoes),
    )

    # pendências: expedientes ainda em aberto + heurística sobre o último movimento
    pendencias = _expedientes_em_aberto(payloads)
    pendencias += _inferir_pendencias(movimentacoes, dados.situacao)

    status_map = {
        "SUCESSO": StatusColeta.SUCESSO,
        "PARCIAL": StatusColeta.PARCIAL,
        "FALHA": StatusColeta.FALHA,
        "NAO_ENCONTRADO": StatusColeta.NAO_ENCONTRADO,
        "BLOQUEADO": StatusColeta.BLOQUEADO,
    }
    coleta = Coleta(
        fonte="https://pje.trt18.jus.br/consultaprocessual/",
        coletado_em=parse_data(bruto.get("capturado_em")) or datetime.now(),
        versao_coletor=limpar_texto(bruto.get("versao_coletor")),
        tempo_execucao_seg=bruto.get("tempo_execucao_seg"),
        status_coleta=status_map.get(bruto.get("status_coleta", "SUCESSO"), StatusColeta.SUCESSO),
        tentativas_captcha=bruto.get("tentativas_captcha"),
        status_cnj_planilha=limpar_texto(bruto.get("status_cnj_planilha")),
        warnings=[w for w in bruto.get("warnings", []) if w],
        erros=[e for e in bruto.get("erros", []) if e],
    )

    return Processo(
        processo=dados,
        partes_interessadas=partes,
        movimentacoes=movimentacoes,
        documentos=documentos,
        pendencias=pendencias,
        coleta=coleta,
    )


def _expedientes_em_aberto(payloads: list[Any]) -> list[str]:
    """Expedientes do PJe ainda não fechados representam pendências concretas."""
    pendencias: list[str] = []
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for exp in payload.get("expedientes") or []:
            if not isinstance(exp, dict) or exp.get("fechado"):
                continue
            tipo = limpar_texto(exp.get("tipo")) or "Expediente"
            destinatario = limpar_texto(exp.get("destinatario"))
            texto = f"Expediente em aberto: {tipo}"
            if destinatario:
                texto += f" para {destinatario}"
            pendencias.append(texto)
    return pendencias


def _inferir_pendencias(movimentacoes: list[Movimentacao], situacao: SituacaoProcesso) -> list[str]:
    if situacao == SituacaoProcesso.BAIXADO or not movimentacoes:
        return []
    ultimo = movimentacoes[-1]
    return [f"Última movimentação: {ultimo.descricao}"]


__all__ = [
    "limpar_texto",
    "parse_data",
    "parse_valor",
    "extrair_campos",
    "inferir_situacao",
    "normalizar",
]
