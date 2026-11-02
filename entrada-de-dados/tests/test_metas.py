from __future__ import annotations

from datetime import date

from trt18_collector import metas


def _arvore(movimentos, *, classe="ATOrd", autuacao="2026-04-17", documentos=None, situacao=None):
    return {
        "processo": {
            "numero": "0000001-00.2026.5.18.0001",
            "classe_judicial": classe,
            "data_autuacao": autuacao,
            "data_distribuicao": autuacao,
            "situacao": situacao,
        },
        "movimentacoes": [
            {"ordem": i, "data": f"{data}T10:00:00", "descricao": descricao}
            for i, (data, descricao) in enumerate(movimentos, start=1)
        ],
        "documentos": documentos or [],
    }


def _status(diagnostico):
    return [meta.status for meta in diagnostico.metas]


def test_caso_novo_sem_julgamento_consta_na_meta_1():
    arvore = _arvore([
        ("2026-04-17", "Distribuído por sorteio"),
        ("2026-06-01", "Conclusos os autos para julgamento Proferir sentença a JUIZ DA VARA"),
    ])

    diagnostico = metas.avaliar(arvore, hoje=date(2026, 10, 1))

    assert _status(diagnostico) == ["PENDENTE", "FORA"]
    assert "Conclusos os autos para julgamento" in diagnostico.metas[0].movimento_determinante
    assert diagnostico.metas[0].o_que_retira
    assert diagnostico.consta_em_alguma_meta


def test_sentenca_no_periodo_conta_como_julgado_na_meta_1():
    arvore = _arvore([
        ("2026-01-10", "Distribuído por sorteio"),
        ("2026-05-20", "Julgado(s) procedente(s) em parte o(s) pedido(s) "
                       "(Ação Trabalhista - Rito Ordinário (985) / ) de FULANO DE TAL"),
    ], autuacao="2026-01-10")

    diagnostico = metas.avaliar(arvore)

    assert diagnostico.metas[0].status == "CUMPRIDA"
    assert diagnostico.primeiro_julgado.tipo == metas.JULGAMENTO
    assert "FULANO" not in diagnostico.metas[0].movimento_determinante


def test_julgamento_de_incidente_nao_conta_como_sentenca():
    arvore = _arvore([
        ("2026-01-10", "Distribuído por sorteio"),
        ("2026-05-20", "Julgado(s) improcedente(s) o(s) pedido(s) ( / Exceção de Incompetência) "
                       "de FULANO DE TAL"),
    ], autuacao="2026-01-10")

    assert metas.avaliar(arvore).metas[0].status == "PENDENTE"


def test_processo_antigo_sem_julgamento_consta_na_meta_2_faixa_dos_antigos():
    arvore = _arvore([("2020-03-02", "Distribuído por sorteio")], autuacao="2020-03-02")

    diagnostico = metas.avaliar(arvore)

    assert _status(diagnostico) == ["FORA", "PENDENTE"]
    assert "5 anos" in diagnostico.metas[1].faixa


def test_remessa_em_grau_de_recurso_encerra_a_pendencia():
    arvore = _arvore([
        ("2025-04-23", "Distribuído por sorteio"),
        ("2025-11-14", "Remetidos os autos para Órgão jurisdicional competente para processar recurso"),
    ], autuacao="2025-04-23", situacao="PENDENTE")

    diagnostico = metas.avaliar(arvore)

    assert diagnostico.primeiro_julgado.tipo == metas.REMESSA_RECURSO
    assert _status(diagnostico) == ["FORA", "FORA"]
    assert diagnostico.situacao_automato == "BAIXADO"
    assert any("difere" in alerta for alerta in diagnostico.alertas)


def test_processo_suspenso_fica_excluido_do_calculo():
    arvore = _arvore([
        ("2026-02-02", "Distribuído por sorteio"),
        ("2026-03-10", "Suspenso ou sobrestado o processo por decisão judicial"),
    ], autuacao="2026-02-02")

    assert metas.avaliar(arvore).metas[0].status == "SUSPENSO"


def test_classe_de_execucao_esta_fora_do_universo_das_metas():
    arvore = _arvore([("2026-02-02", "Distribuído por sorteio")], classe="ExFis")

    assert _status(metas.avaliar(arvore)) == ["NAO_SE_APLICA", "NAO_SE_APLICA"]


def test_processo_fisico_digitalizado_e_inconclusivo():
    arvore = _arvore([
        ("2018-07-02", "Convertida a tramitação do processo do meio físico para o eletrônico"),
        ("2025-12-05", "Arquivados os autos definitivamente"),
    ], autuacao="1997-02-04")

    diagnostico = metas.avaliar(arvore)

    assert _status(diagnostico) == ["INCONCLUSIVO", "INCONCLUSIVO"]
    assert diagnostico.inconsistencias == []


def test_documento_de_sentenca_sem_movimento_gera_alerta_de_inconsistencia():
    arvore = _arvore(
        [("2026-02-02", "Distribuído por sorteio")],
        autuacao="2026-02-02",
        documentos=[{"data": "2026-06-10T09:00:00", "titulo": "Sentença"}],
    )

    diagnostico = metas.avaliar(arvore)

    assert diagnostico.metas[0].status == "PENDENTE"
    assert len(diagnostico.inconsistencias) == 1


def test_texto_do_diagnostico_cita_o_que_retira_da_meta():
    arvore = _arvore([("2026-04-17", "Distribuído por sorteio")])

    texto = metas.avaliar(arvore).texto()

    assert "Meta 1" in texto and "Meta 2" in texto
    assert "desde que o ato tenha sido de fato praticado" in texto
