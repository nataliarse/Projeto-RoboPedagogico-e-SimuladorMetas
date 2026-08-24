import { Component, inject, ViewChild, ElementRef, AfterViewChecked, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { StateService } from '../../core/services/state';
import { ChatService } from '../../core/services/chat';
import { LocalStorageService } from '../../core/services/local-storage';
import { ChatSessionService } from '../../core/services/chat-session';
import { ApiHealthService } from '../../core/services/api-health';
import { ProcessoConsulta } from '../../core/models/chat.model';
import { finalize, TimeoutError } from 'rxjs';

const TIMEOUT_MESSAGE = 'A solicitação demorou mais que o esperado. Tente novamente.';
const TRANSPORT_MESSAGE = 'Não foi possível conectar ao serviço.';
const HTTP_4XX_MESSAGE = 'Não foi possível enviar a solicitação.';
const TECHNICAL_MESSAGE = 'Não foi possível concluir a solicitação.';

type ApiHealthStatus = 'verificando' | 'disponivel' | 'indisponivel';

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
  session = inject(ChatSessionService);
  apiHealth = inject(ApiHealthService);

  texto       = '';
  darkMode    = signal(false);
  cardAberto  = signal(false);
  historico   = signal<ProcessoConsulta[]>([]);
  apiHealthStatus = signal<ApiHealthStatus>('verificando');

  @ViewChild('fim') fim!: ElementRef;

  ngOnInit() {
    this.historico.set(this.storage.carregar());
    this.apiHealth.check().subscribe({
      next: response => this.apiHealthStatus.set(
        response.status === 'ok' ? 'disponivel' : 'indisponivel'
      ),
      error: () => this.apiHealthStatus.set('indisponivel')
    });
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
    this.state.erro.set(null);

    this.state.adicionarMensagem({
      role: 'user',
      content: pergunta,
      timestamp: new Date()
    });

    this.state.carregando.set(true);

    this.chat.enviar(pergunta)
      .pipe(finalize(() => this.state.carregando.set(false)))
      .subscribe({
        next: response => {
          this.session.setSessionId(response.session_id);
          this.state.adicionarMensagem({
            role: 'bot',
            content: response.resultado.resposta,
            timestamp: new Date()
          });

          const processoAtivo = response.resultado.processo_ativo?.trim();
          if (processoAtivo) {
            this.storage.salvar({
              numero_processo: processoAtivo,
              data_consulta: new Date().toLocaleString('pt-BR'),
              resposta_resumo: response.resultado.resposta.slice(0, 80)
            });
            this.historico.set(this.storage.carregar());
          }

          this.state.erro.set(null);
        },
        error: error => this.state.erro.set(this.classificarErro(error))
      });
  }

  onEnter(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.enviar();
    }
  }

  private classificarErro(error: unknown): string {
    if (error instanceof TimeoutError) {
      return TIMEOUT_MESSAGE;
    }

    if (error instanceof HttpErrorResponse) {
      if (error.status === 0) {
        return TRANSPORT_MESSAGE;
      }

      if (error.status >= 400 && error.status < 500) {
        return HTTP_4XX_MESSAGE;
      }
    }

    return TECHNICAL_MESSAGE;
  }

}
