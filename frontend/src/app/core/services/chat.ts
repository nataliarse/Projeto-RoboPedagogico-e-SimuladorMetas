// src/app/core/services/chat.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable, timeout } from 'rxjs';
import {
  ProcessualChatHttpResponse,
  ProcessualChatRequest
} from '../models/chat.model';
import { ChatSessionService } from './chat-session';
import { HTTP_TIMEOUT_MS } from '../config/http-timeouts';

export class InvalidApiResponseError extends Error {
  constructor() {
    super('Resposta inválida do serviço processual.');
    this.name = 'InvalidApiResponseError';
  }
}

export interface ChatSendOptions {
  sessionId?: string | null;
}

function isProcessualChatResponse(value: unknown): value is ProcessualChatHttpResponse {
  if (typeof value !== 'object' || value === null) return false;
  const envelope = value as Partial<ProcessualChatHttpResponse>;
  return typeof envelope.session_id === 'string'
    && envelope.session_id.trim().length > 0
    && typeof envelope.resultado === 'object'
    && envelope.resultado !== null
    && envelope.resultado.tipo === 'processual_chat'
    && typeof envelope.resultado.resposta === 'string'
    && envelope.resultado.resposta.trim().length > 0;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private http = inject(HttpClient);
  private session = inject(ChatSessionService);

  enviar(
    mensagem: string,
    options: ChatSendOptions = {},
  ): Observable<ProcessualChatHttpResponse> {
    const sessionId = options.sessionId === undefined
      ? this.session.getSessionId()
      : options.sessionId;
    const request: ProcessualChatRequest = sessionId === null
      ? { mensagem }
      : { session_id: sessionId, mensagem };

    return this.http
      .post<unknown>('/api/processos/chat', request)
      .pipe(
        timeout(HTTP_TIMEOUT_MS.processualChat),
        map(response => {
          if (!isProcessualChatResponse(response)) throw new InvalidApiResponseError();
          return response;
        })
      );
  }
}
