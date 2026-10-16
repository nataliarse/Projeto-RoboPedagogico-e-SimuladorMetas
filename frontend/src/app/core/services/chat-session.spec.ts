import { TestBed } from '@angular/core/testing';

import { ChatSessionService } from './chat-session';

describe('ChatSessionService', () => {
  let service: ChatSessionService;

  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({});
    service = TestBed.inject(ChatSessionService);
  });

  afterEach(() => sessionStorage.clear());

  it('guarda, recupera e remove o session_id somente na sessão do navegador', () => {
    expect(service.getSessionId()).toBeNull();
    service.setSessionId('sessao-backend-123');
    expect(service.getSessionId()).toBe('sessao-backend-123');
    expect(localStorage.getItem('processual_chat_session_id')).toBeNull();

    service.clearSession();
    expect(service.getSessionId()).toBeNull();
  });
});
