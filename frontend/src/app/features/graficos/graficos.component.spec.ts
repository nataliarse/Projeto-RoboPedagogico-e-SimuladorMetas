import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { SimuladorService } from '../../core/services/simulador.service';
import { GraficosComponent } from './graficos.component';

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
});
