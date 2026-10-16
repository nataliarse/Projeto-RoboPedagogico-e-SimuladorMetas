import { HttpErrorResponse, provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { TimeoutError } from 'rxjs';

import { ProcessualChatHttpResponse } from '../models/chat.model';
import { ChatService, InvalidApiResponseError } from './chat';
import { ChatSessionService } from './chat-session';

describe('ChatService', () => {
  let service: ChatService;
  let httpTesting: HttpTestingController;
  let sessionId: string | null;

  const sessionStub: Pick<ChatSessionService, 'getSessionId'> = {
    getSessionId: () => sessionId
  };

  const validResponse: ProcessualChatHttpResponse = {
    session_id: 'sessao-123',
    resultado: {
      tipo: 'processual_chat', intent: null, resposta: 'Resposta real',
      processo_ativo: null, collection_status: null, failed_stage: null,
      rag_status: 'not_needed', fontes: []
    }
  };

  beforeEach(() => {
    sessionId = null;
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: ChatSessionService, useValue: sessionStub }
      ]
    });
    service = TestBed.inject(ChatService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('envia POST sem session_id quando não há sessão', () => {
    service.enviar('Olá').subscribe();

    const request = httpTesting.expectOne('/api/processos/chat');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ mensagem: 'Olá' });
    expect(request.request.body).not.toHaveProperty('session_id');

    request.flush(validResponse);
  });

  it('preserva session_id e mensagem no POST quando há sessão', () => {
    sessionId = 'sessao-123';

    service.enviar('Qual foi a última movimentação?').subscribe();

    const request = httpTesting.expectOne('/api/processos/chat');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      session_id: 'sessao-123',
      mensagem: 'Qual foi a última movimentação?'
    });

    request.flush(validResponse);
  });

  it('aceita session_id explícito na request tipada', () => {
    sessionId = 'sessao-armazenada';

    service.enviar('Continue', { sessionId: 'sessao-explicita' }).subscribe();

    const request = httpTesting.expectOne('/api/processos/chat');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      session_id: 'sessao-explicita',
      mensagem: 'Continue'
    });
    request.flush(validResponse);
  });

  it('duas perguntas consecutivas reutilizam a sessão devolvida pela primeira', () => {
    service.enviar('Primeira pergunta').subscribe(response => {
      sessionId = response.session_id;
    });
    const first = httpTesting.expectOne('/api/processos/chat');
    expect(first.request.body).toEqual({ mensagem: 'Primeira pergunta' });
    first.flush(validResponse);

    service.enviar('Segunda pergunta').subscribe();
    const second = httpTesting.expectOne('/api/processos/chat');
    expect(second.request.body).toEqual({
      session_id: validResponse.session_id,
      mensagem: 'Segunda pergunta'
    });
    second.flush(validResponse);
  });

  it('emite o envelope HTTP contratual recebido', () => {
    let emitted: ProcessualChatHttpResponse | undefined;

    service.enviar('Olá').subscribe(value => emitted = value);
    const request = httpTesting.expectOne('/api/processos/chat');
    request.flush(validResponse);

    expect(emitted).toEqual(validResponse);
  });

  it('rejeita resposta 2xx inválida sem emitir falso sucesso', () => {
    let emitted: ProcessualChatHttpResponse | undefined;
    let observedError: unknown;

    service.enviar('Olá').subscribe({
      next: value => emitted = value,
      error: error => observedError = error
    });
    httpTesting.expectOne('/api/processos/chat').flush({ session_id: 'sessao-123' });

    expect(emitted).toBeUndefined();
    expect(observedError).toBeInstanceOf(InvalidApiResponseError);
  });

  it('não transforma resposta vazia em sucesso aparente', () => {
    let observedError: unknown;
    service.enviar('Olá').subscribe({ error: error => observedError = error });

    httpTesting.expectOne('/api/processos/chat').flush({
      ...validResponse,
      resultado: { ...validResponse.resultado, resposta: '   ' }
    });

    expect(observedError).toBeInstanceOf(InvalidApiResponseError);
  });

  it('aplica orçamento de 120 segundos ao chat sem espera real', () => {
    let observedError: unknown;

    vi.useFakeTimers();
    try {
      service.enviar('Olá').subscribe({ error: error => observedError = error });
      const request = httpTesting.expectOne('/api/processos/chat');

      vi.advanceTimersByTime(119_999);
      expect(observedError).toBeUndefined();

      vi.advanceTimersByTime(2);
      expect(observedError).toBeInstanceOf(TimeoutError);
      expect(request.cancelled).toBe(true);
    } finally {
      vi.useRealTimers();
    }
  });

  it('propaga erro HTTP ao consumidor sem transformá-lo em sucesso', () => {
    let emitted: ProcessualChatHttpResponse | undefined;
    let observedError: unknown;

    service.enviar('Olá').subscribe({
      next: value => emitted = value,
      error: error => observedError = error
    });
    const request = httpTesting.expectOne('/api/processos/chat');
    request.flush(
      { detail: 'falha técnica' },
      { status: 500, statusText: 'Internal Server Error' }
    );

    expect(emitted).toBeUndefined();
    expect(observedError).toBeInstanceOf(HttpErrorResponse);
    expect((observedError as HttpErrorResponse).status).toBe(500);
  });
});
