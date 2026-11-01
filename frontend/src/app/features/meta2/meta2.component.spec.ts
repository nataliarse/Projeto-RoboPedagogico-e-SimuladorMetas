import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { RespostaMeta2 } from '../../core/models/simulador.model';
import { SimuladorApiService } from '../../core/services/simulador-api.service';
import { SimuladorService } from '../../core/services/simulador.service';
import { Meta2Component } from './meta2.component';

const metadata = {
  homologado: false,
  proveniencia: { fonte: 'fixture', versao: null, referencia: '2026', homologada: false },
  semantica_temporal: { julgados: 'indefinida', suspensos: 'indefinida', dessobrestados: 'indefinida' } as const,
};

const base: RespostaMeta2 = {
  resultado_2025: { A: { meta: 106.22 }, ANT: { meta: 100 } },
  resultado_2026: {
    A: { grupo: 'A', ano: 2026, meta2: 104.63, distribuidos: 27548, descricao: 'Coorte A', formula: 'A',
      ...metadata, status_validacao: 'demonstrativo', mensagem_validacao: 'Simulação com dados não homologados' },
    ANT: { grupo: 'ANT', ano: 2026, meta2: null, distribuidos: 72, descricao: 'Coorte ANT', formula: 'ANT',
      ...metadata, status_validacao: 'pendente_validacao', mensagem_validacao: 'Indicador pendente de validação' },
  },
  serie_A: [
    { data: '2026-01', tipo: 'real', julgados: 180, suspensos: 92, dessobrestados: 2, julgados_acum_2026: 180, dessobrestados_acum_2026: 2, meta2: 101, status_validacao: 'demonstrativo', mensagem_validacao: 'Simulação com dados não homologados' },
    { data: '2026-03', tipo: 'previsao', julgados: 75, suspensos: 89, dessobrestados: 1, julgados_acum_2026: 392, dessobrestados_acum_2026: 3, meta2: 102, status_validacao: 'demonstrativo', mensagem_validacao: 'Simulação com dados não homologados' },
  ],
  serie_ANT: [
    { data: '2026-01', tipo: 'real', julgados: 2, suspensos: 1, dessobrestados: 0, julgados_acum_2026: 2, dessobrestados_acum_2026: 0, meta2: null, status_validacao: 'pendente_validacao', mensagem_validacao: 'Indicador pendente de validação' },
    { data: '2026-03', tipo: 'previsao', julgados: 2, suspensos: 1, dessobrestados: 2, julgados_acum_2026: 4, dessobrestados_acum_2026: 2, meta2: null, status_validacao: 'pendente_validacao', mensagem_validacao: 'Indicador pendente de validação' },
  ],
};

describe('Meta2Component', () => {
  const api = { carregando: signal(false), erro: signal<string | null>(null), carregarMeta2: vi.fn(() => of(base)), simularMeta2: vi.fn(() => of(base)) };
  const sim = { fmt: (v: number | null) => v == null ? '—' : `${v.toFixed(2)}%`, mesLabel: (m: string) => m };

  beforeEach(async () => {
    vi.clearAllMocks();
    await TestBed.configureTestingModule({ imports: [Meta2Component], providers: [
      { provide: SimuladorApiService, useValue: api }, { provide: SimuladorService, useValue: sim },
    ] }).compileComponents();
  });

  it('carrega A e ANT e apresenta nulo sem convertê-lo em zero', () => {
    const fixture = TestBed.createComponent(Meta2Component); fixture.detectChanges();
    expect(api.carregarMeta2).toHaveBeenCalled();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('104.63%');
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('—');
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Histórico');
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Projeção');
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Simulação com dados não homologados');
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Indicador pendente de validação');
  });

  it('mantém alterações A e ANT independentes e envia ambas ao backend', () => {
    const component = TestBed.createComponent(Meta2Component).componentInstance; component.ngOnInit();
    component.alterar('2026-03', 'julgados', 10);
    component.grupoSelecionado = 'ANT'; component.alterar('2026-03', 'suspensos', 2);
    component.nomeCenario = 'Cenário ANT'; component.simular();
    expect(api.simularMeta2).toHaveBeenCalledWith({
      alteracoes_A: { '2026-03': { julgados: 10 } }, alteracoes_ANT: { '2026-03': { suspensos: 2 } },
    });
    expect(component.cenarios()[0].grupo).toBe('ANT');
  });
});
