export interface ProcessualChatRequest {
  session_id?: string | null;
  mensagem: string;
}

export interface ProcessualChatResponse {
  tipo: 'processual_chat';
  intent: string | null;
  resposta: string;
  processo_ativo: string | null;
  collection_status: string | null;
  failed_stage: string | null;
  rag_status: string | null;
  fontes: ReadonlyArray<unknown>;
}

export interface ProcessualChatHttpResponse {
  session_id: string;
  resultado: ProcessualChatResponse;
}

export interface ApiValidationErrorItem {
  loc: ReadonlyArray<string | number>;
  msg: string;
  type: string;
  input?: unknown;
  ctx?: Readonly<Record<string, unknown>>;
}

export interface ApiValidationErrorResponse {
  detail: ReadonlyArray<ApiValidationErrorItem>;
}
