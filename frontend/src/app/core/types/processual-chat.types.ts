// Compatibilidade temporária: novos consumidores devem importar de chat.model.
export type {
  ApiValidationErrorItem,
  ApiValidationErrorResponse,
  ChatTransportError,
  ChatTransportErrorKind,
  ProcessualChatHttpResponse,
  ProcessualChatRequest,
  ProcessualChatResponse,
} from '../models/chat.model';
