import { HttpErrorResponse } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Observable, of, Subject, TimeoutError } from 'rxjs';

import { ProcessoConsulta } from '../../core/models/chat.model';
import { ApiHealthService } from '../../core/services/api-health';
import { ChatService, InvalidApiResponseError } from '../../core/services/chat';
import { ChatSessionService } from '../../core/services/chat-session';
import { LocalStorageService } from '../../core/services/local-storage';
import {
  ProcessualChatHttpResponse,
  ProcessualChatResponse,
} from '../../core/models/chat.model';
import { ChatComponent } from './chat';

const TIMEOUT_MESSAGE = 'A solicitação demorou mais que o esperado. Tente novamente.';
const TRANSPORT_MESSAGE = 'Não foi possível conectar ao serviço.';
const HTTP_4XX_MESSAGE = 'Não foi possível enviar a solicitação.';
const TECHNICAL_MESSAGE = 'Não foi possível concluir a solicitação.';

function criarResponse(
  resultado: Partial<ProcessualChatResponse> = {},
): ProcessualChatHttpResponse {
  return {
    session_id: 'sessao-123',
    resultado: {
      tipo: 'processual_chat',
      intent: null,
      resposta: 'Resposta real do backend',
      processo_ativo: 'PROCESSO-X',
      collection_status: null,
      failed_stage: null,
      rag_status: 'not_needed',
      fontes: [],
      ...resultado,
    },
  };
}

describe('ChatComponent', () => {
  let component: ChatComponent;
  let fixture: ComponentFixture<ChatComponent>;
  let enviar: ReturnType<typeof vi.fn<(mensagem: string) => Observable<ProcessualChatHttpResponse>>>;
  let setSessionId: ReturnType<typeof vi.fn<(sessionId: string) => void>>;
  let clearSession: ReturnType<typeof vi.fn<() => void>>;
  let carregar: ReturnType<typeof vi.fn<() => ProcessoConsulta[]>>;
  let salvar: ReturnType<typeof vi.fn<(processo: ProcessoConsulta) => void>>;
  let check: ReturnType<typeof vi.fn<ApiHealthService['check']>>;

  const scrollIntoViewDescriptor = Object.getOwnPropertyDescriptor(
    HTMLElement.prototype,
    'scrollIntoView',
  );

  beforeAll(() => {
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: vi.fn(),
    });
  });

  afterAll(() => {
    if (scrollIntoViewDescriptor) {
      Object.defineProperty(
        HTMLElement.prototype,
        'scrollIntoView',
        scrollIntoViewDescriptor,
      );
    } else {
      delete (HTMLElement.prototype as Partial<HTMLElement>).scrollIntoView;
    }
  });

  beforeEach(async () => {
    enviar = vi.fn();
    setSessionId = vi.fn();
    clearSession = vi.fn();
    carregar = vi.fn(() => []);
    salvar = vi.fn();
    check = vi.fn(() => of({ status: 'ok' as const }));

    await TestBed.configureTestingModule({
      imports: [ChatComponent],
      providers: [
        { provide: ChatService, useValue: { enviar } satisfies Pick<ChatService, 'enviar'> },
        {
          provide: ChatSessionService,
          useValue: { setSessionId, clearSession } satisfies Pick<
            ChatSessionService,
            'setSessionId' | 'clearSession'
          >,
        },
        {
          provide: LocalStorageService,
          useValue: { carregar, salvar } satisfies Pick<
            LocalStorageService,
            'carregar' | 'salvar'
          >,
        },
        { provide: ApiHealthService, useValue: { check } satisfies Pick<ApiHealthService, 'check'> },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ChatComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('envia a mensagem, bloqueia envio duplicado e usa a resposta real no sucesso', () => {
    const request = new Subject<ProcessualChatHttpResponse>();
    const response = criarResponse();
    enviar.mockReturnValue(request);

    component.texto = 'Consulte o processo 123';
    component.enviar();

    expect(enviar).toHaveBeenCalledOnce();
    expect(enviar).toHaveBeenCalledWith('Consulte o processo 123');
    expect(component.state.mensagens()[0]).toMatchObject({
      role: 'user',
      content: 'Consulte o processo 123',
    });
    expect(component.state.carregando()).toBe(true);

    component.texto = 'Segunda mensagem';
    component.enviar();
    expect(enviar).toHaveBeenCalledOnce();

    request.next(response);
    request.complete();
    fixture.detectChanges();

    expect(component.state.carregando()).toBe(false);
    expect(component.state.mensagens()[1]).toMatchObject({
      role: 'bot',
      content: response.resultado.resposta,
    });
    expect(fixture.nativeElement.textContent).toContain(response.resultado.resposta);
    expect(setSessionId).toHaveBeenCalledOnce();
    expect(setSessionId).toHaveBeenCalledWith(response.session_id);
    expect(salvar).toHaveBeenCalledWith(
      expect.objectContaining({ numero_processo: response.resultado.processo_ativo }),
    );
  });

  it('inicia nova conversa sem apagar o histórico local de processos', () => {
    component.state.adicionarMensagem({
      role: 'bot', content: 'Conversa anterior', timestamp: new Date()
    });
    component.state.erro.set('Erro anterior');
    component.texto = 'Rascunho';

    component.novaConversa();

    expect(clearSession).toHaveBeenCalledOnce();
    expect(component.state.mensagens()).toEqual([]);
    expect(component.state.erro()).toBeNull();
    expect(component.texto).toBe('');
    expect(carregar).toHaveBeenCalledOnce();
    expect(salvar).not.toHaveBeenCalled();
  });

  it('cancela a request ativa e ignora qualquer resposta tardia', () => {
    const request = new Subject<ProcessualChatHttpResponse>();
    enviar.mockReturnValue(request);
    component.texto = 'Consulta cancelável';
    component.enviar();

    expect(component.state.carregando()).toBe(true);
    expect(request.observed).toBe(true);
    component.cancelarEnvio();

    expect(request.observed).toBe(false);
    expect(component.state.carregando()).toBe(false);
    expect(component.state.erro()).toBe('Solicitação cancelada.');
    request.next(criarResponse());
    expect(component.state.mensagens()).toHaveLength(1);
    expect(setSessionId).not.toHaveBeenCalled();
  });

  it('salva o processo ativo, e não a pergunta livre, no histórico', () => {
    const pergunta = 'qual foi a última movimentação?';
    enviar.mockReturnValue(of(criarResponse({ processo_ativo: 'PROCESSO-X' })));

    component.texto = pergunta;
    component.enviar();

    expect(salvar).toHaveBeenCalledOnce();
    expect(salvar).toHaveBeenCalledWith(
      expect.objectContaining({ numero_processo: 'PROCESSO-X' }),
    );
    expect(salvar).not.toHaveBeenCalledWith(
      expect.objectContaining({ numero_processo: pergunta }),
    );
  });

  it('não salva histórico quando a resposta não possui processo ativo', () => {
    enviar.mockReturnValue(of(criarResponse({ processo_ativo: null })));

    component.texto = 'Explique o que este assistente faz';
    component.enviar();

    expect(salvar).not.toHaveBeenCalled();
  });

  it.each([
    ['timeout', new TimeoutError(), TIMEOUT_MESSAGE],
    ['transporte', new HttpErrorResponse({ status: 0, statusText: 'segredo-rede' }), TRANSPORT_MESSAGE],
    ['HTTP 4xx', new HttpErrorResponse({ status: 422, statusText: 'segredo-validacao' }), HTTP_4XX_MESSAGE],
    ['HTTP 5xx', new HttpErrorResponse({ status: 500, statusText: 'segredo-servidor' }), TECHNICAL_MESSAGE],
    ['resposta inválida', new InvalidApiResponseError(), 'O serviço retornou uma resposta inválida. Tente novamente.'],
  ])('apresenta erro seguro e finaliza loading para %s', (_cenario, error, mensagemPublica) => {
    const request = new Subject<ProcessualChatHttpResponse>();
    enviar.mockReturnValue(request);

    component.texto = 'Mensagem que falhará';
    component.enviar();

    expect(component.state.carregando()).toBe(true);
    request.error(error);
    fixture.detectChanges();

    expect(component.state.carregando()).toBe(false);
    expect(component.state.erro()).toBe(mensagemPublica);
    expect(component.state.mensagens()).toHaveLength(1);
    expect(component.state.mensagens()[0].role).toBe('user');
    expect(fixture.nativeElement.textContent).toContain(mensagemPublica);
    expect(fixture.nativeElement.textContent).not.toContain(error.message);
    expect(enviar).toHaveBeenCalledOnce();
    expect(salvar).not.toHaveBeenCalled();
  });

  it('permite nova tentativa e limpa o erro anterior sem retry automático', () => {
    const primeiraRequest = new Subject<ProcessualChatHttpResponse>();
    const segundaRequest = new Subject<ProcessualChatHttpResponse>();
    enviar.mockReturnValueOnce(primeiraRequest).mockReturnValueOnce(segundaRequest);

    component.texto = 'Primeira tentativa';
    component.enviar();
    primeiraRequest.error(new HttpErrorResponse({ status: 500 }));

    expect(enviar).toHaveBeenCalledOnce();
    expect(component.state.erro()).toBe(TECHNICAL_MESSAGE);

    component.texto = 'Nova tentativa';
    component.enviar();

    expect(enviar).toHaveBeenCalledTimes(2);
    expect(enviar).toHaveBeenLastCalledWith('Nova tentativa');
    expect(component.state.erro()).toBeNull();
    expect(component.state.carregando()).toBe(true);

    segundaRequest.next(criarResponse());
    segundaRequest.complete();
    expect(component.state.carregando()).toBe(false);
  });

  it('trata falha controlada 2xx como resposta do bot', () => {
    const response = criarResponse({
      failed_stage: 'Agente 2',
      resposta: 'Resposta segura da falha controlada',
    });
    enviar.mockReturnValue(of(response));

    component.texto = 'Consulte o processo';
    component.enviar();

    expect(component.state.mensagens().at(-1)).toMatchObject({
      role: 'bot',
      content: response.resultado.resposta,
    });
    expect(component.state.erro()).toBeNull();
  });
});
