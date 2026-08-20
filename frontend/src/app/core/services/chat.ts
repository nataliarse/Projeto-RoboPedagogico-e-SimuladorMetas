// src/app/core/services/chat.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timeout } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private http = inject(HttpClient);

  enviar(mensagem: string): Observable<any> {
    return this.http
      .post('/api/chat', { mensagem })
      .pipe(timeout(60000));
  }
}