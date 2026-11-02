export interface ChatMessage {
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export interface ProcessoConsulta {
  numero_processo: string;
  data_consulta: string;
  resposta_resumo: string;
}

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
  fontes: ReadonlyArray<Readonly<Record<string, unknown>>>;
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

export type ChatTransportErrorKind =
  | 'timeout'
  | 'network'
  | 'validation'
  | 'server'
  | 'invalid_response';

export interface ChatTransportError {
  kind: ChatTransportErrorKind;
  status: number | null;
  validation?: ApiValidationErrorResponse;
}
