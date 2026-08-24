// src/app/core/services/chat.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timeout } from 'rxjs';
import {
  ProcessualChatHttpResponse,
  ProcessualChatRequest
} from '../types/processual-chat.types';
import { ChatSessionService } from './chat-session';

const PROCESSUAL_CHAT_TIMEOUT_MS = 135_000;

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
      .post<ProcessualChatHttpResponse>('/api/processos/chat', request)
      .pipe(timeout(PROCESSUAL_CHAT_TIMEOUT_MS));
  }
}
