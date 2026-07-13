from schemas.meta_contracts import MetaSimulationRequest, MetaSimulationResponse


def simulate_meta(request: MetaSimulationRequest) -> MetaSimulationResponse:
    return MetaSimulationResponse(
        tipo="meta_simulation",
        meta_id=request.meta_id,
        ano=request.ano,
        status="not_integrated",
        resultado=None,
        meta_alvo=None,
        indicadores={
            "unidade": request.unidade,
            "cenario": request.cenario,
        },
        observacoes=[
            "Simulador de metas ainda não integrado ao backend.",
            "Contrato de entrada e saída precisa ser validado com a equipe responsável.",
        ],
    )
