import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SimuladorService } from './core/services/simulador.service';
import { CenariosComponent } from './features/cenarios/cenarios.component';
import { GraficosComponent } from './features/graficos/graficos.component';
import { TabelaComponent } from './features/tabela/tabela.component';
import { OtimizadorComponent } from './features/otimizador/otimizador.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, CenariosComponent, GraficosComponent, TabelaComponent, OtimizadorComponent],
  template: `
    <!-- ── HEADER ── -->
    <header class="header">
      <div class="header-left">
        <span class="header-eyebrow">CNJ · Justiça em Números · {{ anoSim }}</span>
        <h1 class="header-title">Simulador de Metas 1 e 2</h1>
      </div>
      <div class="header-kpis">
        @for (kpi of kpis; track kpi.label) {
          <div class="kpi">
            <span class="kpi-label">{{ kpi.label }}</span>
            <span class="kpi-valor" [style.color]="corMeta(kpi.valor)">
              {{ sim.fmt(kpi.valor) }}
            </span>
          </div>
        }
      </div>
    </header>

    <!-- ── ABAS ── -->
    <nav class="nav-abas">
      @for (aba of abas; track aba.id) {
        <button class="aba-btn"
          [class.ativa]="sim.abaSelecionada() === aba.id"
          (click)="sim.abaSelecionada.set(aba.id)">
          {{ aba.label }}
        </button>
      }
    </nav>

    <!-- ── CONTEÚDO ── -->
    <main class="main-content">
      @switch (sim.abaSelecionada()) {
        @case ('cenarios')   { <app-cenarios /> }
        @case ('graficos')   { <app-graficos /> }
        @case ('tabela')     { <app-tabela /> }
        @case ('otimizador') { <app-otimizador /> }
      }
    </main>
  `,
  styles: [`
    :host { display: block; font-family: 'Inter', 'Segoe UI', sans-serif; background: #F7F8FA; min-height: 100vh; }

    .header {
      background: #1B4F8A;
      padding: 20px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }
    .header-eyebrow { font-size: 11px; color: #93C5FD; font-weight: 500; display: block; margin-bottom: 4px; }
    .header-title   { font-size: 20px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.3px; }
    .header-kpis    { display: flex; gap: 28px; }
    .kpi            { text-align: right; }
    .kpi-label      { font-size: 11px; color: #93C5FD; display: block; }
    .kpi-valor      { font-size: 22px; font-weight: 700; }

    .nav-abas {
      background: #fff;
      padding: 12px 32px 0;
      display: flex;
      gap: 4px;
      border-bottom: 1px solid #D1D5DB;
    }
    .aba-btn {
      padding: 9px 18px;
      font-size: 13px;
      font-weight: 600;
      border: none;
      border-radius: 7px 7px 0 0;
      cursor: pointer;
      background: transparent;
      color: #4A4E57;
      transition: background .15s, color .15s;
    }
    .aba-btn.ativa { background: #1B4F8A; color: #fff; }
    .aba-btn:not(.ativa):hover { background: #F3F4F6; }

    .main-content { padding: 24px 32px; max-width: 1200px; margin: 0 auto; }
  `]
})
export class AppComponent {
  sim = inject(SimuladorService);
  anoSim = 2026;

  abas = [
    { id: 'cenarios'   as const, label: 'Cenários' },
    { id: 'graficos'   as const, label: 'Gráficos' },
    { id: 'tabela'     as const, label: 'Evolução Mensal' },
    { id: 'otimizador' as const, label: 'Otimizador' },
  ];

  get kpis() {
    const base = this.sim.cenariosCalculados()[0];
    return [
      { label: 'Meta 1 Base', valor: base?.meta1Final ?? null },
      { label: 'Meta 2 Base', valor: base?.meta2Final ?? null },
    ];
  }

  corMeta(v: number | null): string {
    if (v == null) return '#FCD34D';
    if (v >= 100) return '#86EFAC';
    if (v >= 95)  return '#FCD34D';
    return '#FCA5A5';
  }
}
