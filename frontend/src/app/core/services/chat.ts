// src/app/core/services/chat.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable, timeout } from 'rxjs';
import {
  ProcessualChatHttpResponse,
  ProcessualChatRequest
} from '../types/processual-chat.types';
import { ChatSessionService } from './chat-session';

const PROCESSUAL_CHAT_TIMEOUT_MS = 135_000;

export class InvalidApiResponseError extends Error {
  constructor() {
    super('Resposta inválida do serviço processual.');
    this.name = 'InvalidApiResponseError';
  }
}

function isProcessualChatResponse(value: unknown): value is ProcessualChatHttpResponse {
  if (typeof value !== 'object' || value === null) return false;
  const envelope = value as Partial<ProcessualChatHttpResponse>;
  return typeof envelope.session_id === 'string'
    && envelope.session_id.trim().length > 0
    && typeof envelope.resultado === 'object'
    && envelope.resultado !== null
    && envelope.resultado.tipo === 'processual_chat'
    && typeof envelope.resultado.resposta === 'string';
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private http = inject(HttpClient);
  private session = inject(ChatSessionService);

  enviar(mensagem: string): Observable<ProcessualChatHttpResponse> {
    const sessionId = this.session.getSessionId();
    const request: ProcessualChatRequest = sessionId === null
      ? { mensagem }
      : { session_id: sessionId, mensagem };

    return this.http
      .post<unknown>('/api/processos/chat', request)
      .pipe(
        timeout(PROCESSUAL_CHAT_TIMEOUT_MS),
        map(response => {
          if (!isProcessualChatResponse(response)) throw new InvalidApiResponseError();
          return response;
        })
      );
  }
}
