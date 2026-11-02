import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { RespostaQuantoFalta } from '../../core/models/simulador.model';
import { SimuladorApiService } from '../../core/services/simulador-api.service';
import { SimuladorService } from '../../core/services/simulador.service';
import { QuantoFaltaComponent } from './quanto-falta.component';

const resposta: RespostaQuantoFalta = {
  ok: true, ja_atingida: false, meta_alvo: 100, meta_atual: 96.47, meta_resultante: 100.01,
  mes_inicio: '2026-03', meses: ['2026-03', '2026-04'], n_meses: 2, meses_reais: [],
  incremento_mensal: 387, total_adicional: 774, julgados_previstos_periodo: 1000,
  conta: { denominador: 100, julgados_acumulados: 90, julgados_necessarios: 100 }, mensagem: 'ok',
};

describe('QuantoFaltaComponent', () => {
  const abaSelecionada = signal<'meta1' | 'quanto-falta'>('quanto-falta');
  const simMock = {
    basePronta: signal(true),
    cenariosCalculados: signal([{ id: 1, nome: 'Base', anoRows: [
      { data: '2026-02', julgados_tipo: 'real' }, { data: '2026-03', julgados_tipo: 'forecast' },
    ] }]),
    cenarios: signal([{ id: 1, nome: 'Base', alteracoes: {} }]),
    abaSelecionada,
    mesLabel: (mes: string) => ({ '02': 'Fev', '03': 'Mar', '04': 'Abr' })[mes.slice(-2)] ?? mes,
    nomeCenarioExiste: () => false,
    adicionarCenario: vi.fn(),
  };
  const apiMock = {
    carregando: signal(false), erro: signal<string | null>(null),
    quantoFalta: vi.fn(() => of(resposta)), simular: vi.fn(() => of({ registros: [], meta1Final: 100.01, meta2Final: null })),
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    await TestBed.configureTestingModule({
      imports: [QuantoFaltaComponent],
      providers: [
        { provide: SimuladorService, useValue: simMock },
        { provide: SimuladorApiService, useValue: apiMock },
      ],
    }).compileComponents();
  });

  it('usa o primeiro mês projetado e envia o cálculo somente ao backend', () => {
    const fixture = TestBed.createComponent(QuantoFaltaComponent);
    fixture.componentInstance.calcular();
    expect(fixture.componentInstance.mesInicio).toBe('2026-03');
    expect(apiMock.quantoFalta).toHaveBeenCalledWith({ meta_alvo: 100, mes_inicio: '2026-03', alteracoes: {} });
    expect(fixture.componentInstance.resultado()).toEqual(resposta);
  });

  it('valida o intervalo antes de chamar a API', () => {
    const component = TestBed.createComponent(QuantoFaltaComponent).componentInstance;
    component.metaAlvo = 201;
    component.calcular();
    expect(apiMock.quantoFalta).not.toHaveBeenCalled();
  });

  it('limpa resultado quando a API falha', () => {
    apiMock.quantoFalta.mockReturnValueOnce(throwError(() => new Error('falha')) as never);
    const component = TestBed.createComponent(QuantoFaltaComponent).componentInstance;
    component.resultado.set(resposta);
    component.calcular();
    expect(component.resultado()).toBeNull();
  });

  it('cria cenário via API e retorna à aba Meta 1', () => {
    const component = TestBed.createComponent(QuantoFaltaComponent).componentInstance;
    component.criarCenario(resposta);
    expect(apiMock.simular).toHaveBeenCalledWith({
      '2026-03': { julgados: 387 }, '2026-04': { julgados: 387 },
    });
    expect(simMock.adicionarCenario).toHaveBeenCalled();
    expect(abaSelecionada()).toBe('meta1');
  });
});
