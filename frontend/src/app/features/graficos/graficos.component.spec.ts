import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { SimuladorService } from '../../core/services/simulador.service';
import { GraficosComponent } from './graficos.component';

const chartMock = vi.hoisted(() => ({ criar: vi.fn(), destruir: vi.fn() }));
vi.mock('chart.js', () => {
  class ChartFake {
    static register() {}
    constructor(...args: unknown[]) { chartMock.criar(...args); }
    destroy() { chartMock.destruir(); }
  }
  return {
    Chart: ChartFake,
    CategoryScale: {}, LinearScale: {}, LineController: {}, LineElement: {}, PointElement: {}, Tooltip: {},
  };
});

describe('GraficosComponent', () => {
  const cenarios = signal([
    { id: 1, nome: 'Base', cor: '#1B4F8A' },
    { id: 2, nome: 'Esforço outubro', cor: '#1F6E3A' },
  ]);
  const barras = signal([
    { nome: 'Base', meta1: 96.47, meta2: null, cor: '#1B4F8A' },
    { nome: 'Esforço outubro', meta1: 100.01, meta2: null, cor: '#1F6E3A' },
  ]);
  const service = {
    cenariosCalculados: cenarios,
    dadosBarras: barras,
    dadosGrafico: signal([
      { mes: 'Out', Base: 95, 'Esforço outubro': 99 },
      { mes: 'Dez', Base: 96.47, 'Esforço outubro': 100.01 },
    ]),
  };

  beforeEach(async () => {
    chartMock.criar.mockClear();
    chartMock.destruir.mockClear();
    cenarios.set([
      { id: 1, nome: 'Base', cor: '#1B4F8A' },
      { id: 2, nome: 'Esforço outubro', cor: '#1F6E3A' },
    ]);
    barras.set([
      { nome: 'Base', meta1: 96.47, meta2: null, cor: '#1B4F8A' },
      { nome: 'Esforço outubro', meta1: 100.01, meta2: null, cor: '#1F6E3A' },
    ]);
    service.dadosGrafico.set([
      { mes: 'Out', Base: 95, 'Esforço outubro': 99 },
      { mes: 'Dez', Base: 96.47, 'Esforço outubro': 100.01 },
    ]);
    await TestBed.configureTestingModule({
      imports: [GraficosComponent],
      providers: [{ provide: SimuladorService, useValue: service }],
    }).compileComponents();
  });

  it('identifica cenários e exibe exatamente os valores recebidos da API', () => {
    const fixture = TestBed.createComponent(GraficosComponent);
    fixture.detectChanges();
    const text = (fixture.nativeElement as HTMLElement).textContent;
    expect(text).toContain('Base');
    expect(text).toContain('Esforço outubro');
    expect(text).toContain('96.47%');
    expect(text).toContain('100.01%');
  });

  it('mantém barras limitadas e representa nulo sem inventar zero', () => {
    const component = TestBed.createComponent(GraficosComponent).componentInstance;
    expect(component.barraWidth(100.01)).toMatch(/%$/);
    expect(component.barraWidth(null)).toBe('0%');
    expect(component.barraColor(null)).toBe('#6B7280');
  });

  it('renderiza o gráfico quando há séries válidas', async () => {
    vi.useFakeTimers();
    try {
      const fixture = TestBed.createComponent(GraficosComponent);
      fixture.detectChanges();
      await vi.runAllTimersAsync();
      expect(chartMock.criar).toHaveBeenCalledOnce();
      expect(fixture.componentInstance.graficoIndisponivel()).toBe(false);
      fixture.destroy();
    } finally {
      vi.useRealTimers();
    }
  });

  it('informa indisponibilidade quando os dados estão ausentes', async () => {
    service.dadosGrafico.set([]);
    vi.useFakeTimers();
    try {
      const fixture = TestBed.createComponent(GraficosComponent);
      fixture.detectChanges();
      await vi.runAllTimersAsync();
      expect(chartMock.criar).not.toHaveBeenCalled();
      expect(fixture.componentInstance.graficoIndisponivel()).toBe(true);
      fixture.destroy();
    } finally {
      vi.useRealTimers();
    }
  });

  it('rejeita valores mensais inválidos sem tentar renderizá-los', async () => {
    service.dadosGrafico.set([{ mes: 'Dez', Base: Number.NaN, 'Esforço outubro': 100.01 }]);
    vi.useFakeTimers();
    try {
      const fixture = TestBed.createComponent(GraficosComponent);
      fixture.detectChanges();
      await vi.runAllTimersAsync();
      expect(chartMock.criar).not.toHaveBeenCalled();
      expect(fixture.componentInstance.graficoIndisponivel()).toBe(true);
      fixture.destroy();
    } finally {
      vi.useRealTimers();
    }
  });
});
