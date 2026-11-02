// src/app/core/services/chat-session.service.ts
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ChatSessionService {
  private readonly KEY = 'processual_chat_session_id';

  getSessionId(): string | null {
    return sessionStorage.getItem(this.KEY);
  }

  setSessionId(sessionId: string): void {
    sessionStorage.setItem(this.KEY, sessionId);
  }

  clearSession(): void {
    sessionStorage.removeItem(this.KEY);
  }
}
