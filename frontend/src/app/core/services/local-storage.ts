// src/app/core/services/local-storage.service.ts
import { Injectable } from '@angular/core';
import { ProcessoConsulta } from '../models/chat.model';

@Injectable({ providedIn: 'root' })
export class LocalStorageService {
  private readonly KEY = 'chatbot_historico';
  private readonly MAX = 3;

  salvar(processo: ProcessoConsulta): void {
    const lista = this.carregar().filter(
      item => item.numero_processo !== processo.numero_processo
    );
    lista.unshift(processo);
    localStorage.setItem(this.KEY, JSON.stringify(lista.slice(0, this.MAX)));
  }

  carregar(): ProcessoConsulta[] {
    const raw = localStorage.getItem(this.KEY);
    return raw ? JSON.parse(raw) : [];
  }

  limpar(): void {
    localStorage.removeItem(this.KEY);
  }
}
