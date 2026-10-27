from __future__ import annotations

from trt18_collector import afd
from trt18_collector.movimentos_tpu import Categoria, classificar_movimento


def _movs(*descricoes):
    return [
        {"ordem": i, "data": f"2026-01-{i:02d}T10:00:00", "descricao": d}
        for i, d in enumerate(descricoes, start=1)
    ]


def test_transito_em_julgado_nao_e_baixa():
    categoria, motivo = classificar_movimento("Transitado em julgado em 31/03/2026")

    assert categoria is None
    assert "não é baixa" in motivo


def test_processo_transitado_em_julgado_segue_pendente_na_execucao():
    # caso real da amostra de set/2026: o CNJ conta o processo como pendente
    resultado = afd.executar(_movs(
        "Distribuído por sorteio",
        "Julgado(s) procedente(s) o(s) pedido(s) (Ação Trabalhista - Rito Sumaríssimo (1125) / ) de FULANO",
        "Transitado em julgado em 31/03/2026",
        "Suspenso o processo por execução frustrada",
    ))

    assert resultado.situacao == "PENDENTE"
    assert resultado.estado_final == afd.Estado.SUSPENSO


def test_remessa_em_grau_de_recurso_e_baixa_no_primeiro_grau():
    resultado = afd.executar(_movs(
        "Distribuído por sorteio",
        "Julgado(s) improcedente(s) o(s) pedido(s) (Ação Trabalhista - Rito Sumaríssimo (1125) / ) de FULANO",
        "Remetidos os autos para Órgão jurisdicional competente para processar recurso",
    ))

    assert resultado.situacao == "BAIXADO"


def test_arquivamento_definitivo_e_baixa():
    categoria, _ = classificar_movimento("Arquivados os autos definitivamente")

    assert categoria == Categoria.BAIXA


def test_conclusao_para_julgamento_nao_e_julgamento():
    resultado = afd.executar(_movs(
        "Distribuído por sorteio",
        "Conclusos os autos para julgamento Proferir sentença a JUIZ DA VARA",
    ))

    assert resultado.estado_final == afd.Estado.EM_TRAMITACAO


def test_peticao_da_parte_nao_altera_a_situacao():
    categoria, motivo = classificar_movimento("Juntada a petição de Manifestação (Requer suspensão)")

    assert categoria is None
    assert "petição" in motivo


def test_desarquivamento_reabre_processo_baixado():
    resultado = afd.executar(_movs(
        "Distribuído por sorteio",
        "Arquivados os autos definitivamente",
        "Desarquivados os autos",
    ))

    assert resultado.situacao == "PENDENTE"
