import { HttpErrorResponse, provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { RespostaBaseApi, RespostaSimulacao } from '../models/simulador.model';
import { InvalidSimulatorResponseError, SimuladorApiService } from './simulador-api.service';

const resposta: RespostaBaseApi = {
  registros: [{
    data: '2026-01', ano: 2026, mes: 1,
    novos: 10, julgados: 12, dessobrestados: 1, suspensos: 0,
    novos_tipo: 'real', julgados_tipo: 'previsao_sas',
    novos_acum: 10, julgados_acum: 12,
    dessobrestados_acum: 1, suspensos_acum: 0,
    meta1: 109.09, meta2: 127.66,
  }],
  meta1_final: 109.09,
  meta2_final: 127.66,
};

describe('SimuladorApiService', () => {
  let service: SimuladorApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(SimuladorApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('carrega e converte a base pelo endpoint namespaced', () => {
    let result: RespostaSimulacao | undefined;
    service.carregarBase().subscribe(value => result = value);
    const request = http.expectOne('/api/simulador/base');
    expect(request.request.method).toBe('GET');
    request.flush(resposta);

    expect(result!.registros[0].julgados_tipo).toBe('forecast');
    expect(result!.meta1Final).toBe(109.09);
    expect(service.carregando()).toBe(false);
  });

  it('envia alterações tipadas para simulação', () => {
    service.simular({ '2026-06': { julgados: 25 } }).subscribe();
    const request = http.expectOne('/api/simulador/simular');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ alteracoes: { '2026-06': { julgados: 25 } } });
    request.flush(resposta);
  });

  it('aceita resposta vazia válida sem inventar registros', () => {
    let count = -1;
    service.carregarBase().subscribe(value => count = value.registros.length);
    http.expectOne('/api/simulador/base').flush({ registros: [], meta1_final: null, meta2_final: null });
    expect(count).toBe(0);
    expect(service.erro()).toBeNull();
  });

  it('expõe indisponibilidade sem emitir sucesso', () => {
    let value: unknown;
    let error: unknown;
    service.carregarBase().subscribe({ next: result => value = result, error: cause => error = cause });
    http.expectOne('/api/simulador/base').error(new ProgressEvent('offline'));
    expect(value).toBeUndefined();
    expect(error).toBeInstanceOf(HttpErrorResponse);
    expect(service.erro()).toContain('Não foi possível conectar');
  });

  it('rejeita payload 2xx inválido', () => {
    let error: unknown;
    service.carregarBase().subscribe({ error: cause => error = cause });
    http.expectOne('/api/simulador/base').flush({ meta1_final: 100, meta2_final: 100 });
    expect(error).toBeInstanceOf(InvalidSimulatorResponseError);
    expect(service.erro()).toContain('resposta inválida');
  });

  it('chama comparar com cenários tipados', () => {
    const body = { cenarios: [{ nome: 'Cenário A', alteracoes: { '2026-06': { julgados: 10 } } }] };
    let received: unknown;
    service.comparar(body).subscribe(value => received = value);
    const request = http.expectOne('/api/simulador/comparar');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(body);
    const response = { cenarios: [], meta1_base: 109.09, meta2_base: 127.66 };
    request.flush(response);
    expect(received).toEqual(response);
  });

  it('chama otimizador com variável, mês e meta tipados', () => {
    const body = { variavel: 'julgados' as const, mes: '2026-06', meta_alvo: 100, meta: 'meta1' as const };
    let received: unknown;
    service.otimizador(body).subscribe(value => received = value);
    const request = http.expectOne('/api/simulador/otimizador');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(body);
    const response = {
      variavel: 'julgados', mes: '2026-06', meta_alvo: 100,
      meta_atual: 98, incremento_necessario: 2, meta_resultante: 100,
      mensagem: 'Ajuste calculado.', ok: true,
    };
    request.flush(response);
    expect(received).toEqual(response);
  });

  it('consulta quanto-falta pelo namespace do simulador', () => {
    let received: unknown;
    service.quantoFalta({ meta_alvo: 100 }).subscribe(value => received = value);
    const request = http.expectOne('/api/simulador/meta1/quanto-falta');
    expect(request.request.method).toBe('POST');
    request.flush({
      ok: true, ja_atingida: false, meta_alvo: 100, meta_atual: 96.47,
      meta_resultante: 100.01, mes_inicio: '2026-03', meses: ['2026-03'],
      n_meses: 1, meses_reais: [], incremento_mensal: 387, total_adicional: 387,
      julgados_previstos_periodo: 8991,
      conta: { denominador: 109210, julgados_acumulados: 105350, julgados_necessarios: 109211 },
      mensagem: 'Esforço calculado.',
    });
    expect((received as { incremento_mensal: number }).incremento_mensal).toBe(387);
  });

  it('carrega e simula Meta 2 A/ANT', () => {
    const response = {
      resultado_2025: { A: { meta: 106.22 }, ANT: { meta: 100 } },
      resultado_2026: {
        A: { grupo: 'A', ano: 2026, meta2: 105.32, distribuidos: 27548, descricao: 'A', formula: 'A',
          homologado: false, status_validacao: 'demonstrativo', mensagem_validacao: 'Metodologia oficial CNJ 2026 v3 aplicada a dados não homologados',
          proveniencia: { fonte: 'fixture', versao: 'teste-1', referencia: '2026', homologada: false },
          semantica_temporal: { julgados: 'fluxo_mensal', suspensos: 'carga_consolidada', dessobrestados: 'fluxo_mensal' } },
        ANT: { grupo: 'ANT', ano: 2026, meta2: 111.11, distribuidos: 72, descricao: 'ANT', formula: 'ANT',
          homologado: false, status_validacao: 'demonstrativo', mensagem_validacao: 'Metodologia oficial CNJ 2026 v3 aplicada a dados não homologados',
          proveniencia: { fonte: 'fixture', versao: 'teste-1', referencia: '2026', homologada: false },
          semantica_temporal: { julgados: 'fluxo_mensal', suspensos: 'carga_consolidada', dessobrestados: 'fluxo_mensal' } },
      },
      reproducao_original_2026: {
        A: { grupo: 'A', ano: 2026, meta2: 104.63, distribuidos: 27548, descricao: 'Reprodução', formula: 'A' },
        ANT: { grupo: 'ANT', ano: 2026, meta2: 110, distribuidos: 72, descricao: 'Reprodução', formula: 'ANT' },
      },
      serie_A: [], serie_ANT: [],
    };
    service.carregarMeta2().subscribe();
    const base = http.expectOne('/api/simulador/meta2/base');
    expect(base.request.method).toBe('GET');
    base.flush(response);

    service.simularMeta2({ alteracoes_A: {}, alteracoes_ANT: {} }).subscribe();
    const simulation = http.expectOne('/api/simulador/meta2/simular');
    expect(simulation.request.method).toBe('POST');
    simulation.flush(response);
  });

  it('propaga 422 e 500 com mensagem do backend', () => {
    for (const status of [422, 500]) {
      service.quantoFalta({ meta_alvo: 100 }).subscribe({ error: () => undefined });
      http.expectOne('/api/simulador/meta1/quanto-falta').flush(
        { detail: `falha ${status}` }, { status, statusText: 'Erro' },
      );
      expect(service.erro()).toContain(`falha ${status}`);
    }
  });

  it('rejeita resposta malformada das novas rotas', () => {
    let error: unknown;
    service.carregarMeta2().subscribe({ error: cause => error = cause });
    http.expectOne('/api/simulador/meta2/base').flush({ resultado_2026: {} });
    expect(error).toBeInstanceOf(InvalidSimulatorResponseError);
  });

  it('encerra loading e propaga timeout', () => {
    vi.useFakeTimers();
    try {
      let error: unknown;
      service.quantoFalta({ meta_alvo: 100 }).subscribe({ error: cause => error = cause });
      http.expectOne('/api/simulador/meta1/quanto-falta');
      vi.advanceTimersByTime(20_001);
      expect(error).toBeDefined();
      expect(service.carregando()).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });
});
