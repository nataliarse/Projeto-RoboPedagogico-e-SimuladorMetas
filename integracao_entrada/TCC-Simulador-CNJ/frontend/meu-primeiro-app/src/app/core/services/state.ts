// src/app/core/services/state.service.ts
import { Injectable, signal } from '@angular/core';
import { ChatMessage } from '../models/chat.model';

@Injectable({ providedIn: 'root' })
export class StateService {
  mensagens  = signal<ChatMessage[]>([]);
  carregando = signal<boolean>(false);
  erro       = signal<string | null>(null);

  adicionarMensagem(msg: ChatMessage): void {
    this.mensagens.update(lista => [...lista, msg]);
  }

  limpar(): void {
    this.mensagens.set([]);
    this.erro.set(null);
  }
}