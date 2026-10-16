// src/app/core/models/chat.model.ts
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