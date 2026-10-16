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
});
