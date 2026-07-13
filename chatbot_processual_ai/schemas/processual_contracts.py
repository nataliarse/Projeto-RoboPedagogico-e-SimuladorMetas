from dataclasses import dataclass, field


@dataclass
class ProcessualChatRequest:
    session_id: str | None
    mensagem: str


@dataclass
class ProcessualChatResponse:
    tipo: str
    intent: str | None
    resposta: str
    processo_ativo: str | None
    collection_status: str | None
    failed_stage: str | None
    rag_status: str | None = None
    fontes: list[dict] = field(default_factory=list)


@dataclass
class ProcessualChatStepResult:
    response: ProcessualChatResponse
    intent_data: dict
    context_data: dict
    analysis: dict
