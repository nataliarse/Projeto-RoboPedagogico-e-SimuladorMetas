import { Component, inject, ViewChild, ElementRef, AfterViewChecked, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { StateService } from '../../core/services/state';
import { ChatService } from '../../core/services/chat';
import { LocalStorageService } from '../../core/services/local-storage';
import { ProcessoConsulta } from '../../core/models/chat.model';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class ChatComponent implements AfterViewChecked {
  state   = inject(StateService);
  chat    = inject(ChatService);
  storage = inject(LocalStorageService);

  texto       = '';
  darkMode    = signal(false);
  cardAberto  = signal(false);
  historico   = signal<ProcessoConsulta[]>([]);

  @ViewChild('fim') fim!: ElementRef;

  ngOnInit() {
    this.historico.set(this.storage.carregar());
  }

  ngAfterViewChecked() {
    this.fim?.nativeElement.scrollIntoView({ behavior: 'smooth' });
  }

  toggleDark() {
    this.darkMode.update(v => !v);
  }

  toggleCard() {
    this.cardAberto.update(v => !v);
  }

  enviar() {
    if (!this.texto.trim() || this.state.carregando()) return;

    const pergunta = this.texto.trim();
    this.texto = '';

    this.state.adicionarMensagem({
      role: 'user',
      content: pergunta,
      timestamp: new Date()
    });

    this.state.carregando.set(true);

    this.chat.enviar(pergunta).subscribe({
      next: () => this.responderMock(pergunta),
      error: () => this.responderMock(pergunta)
    });
  }

  onEnter(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.enviar();
    }
  }

  private responderMock(pergunta: string): void {
    const resposta = 'Olá, infelizmente ainda estamos desenvolvendo o nosso sistema. Muito obrigado pela compreensão.';

    this.state.adicionarMensagem({
      role: 'bot',
      content: resposta,
      timestamp: new Date()
    });

    this.storage.salvar({
      numero_processo: pergunta,
      data_consulta: new Date().toLocaleString('pt-BR'),
      resposta_resumo: resposta.slice(0, 80)
    });

    this.historico.set(this.storage.carregar());
    this.state.erro.set(null);
    this.state.carregando.set(false);
  }
}