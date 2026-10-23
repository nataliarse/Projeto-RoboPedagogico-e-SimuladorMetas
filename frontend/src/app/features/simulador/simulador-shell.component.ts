import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SimuladorService } from '../../core/services/simulador.service';
import { CenariosComponent } from '../cenarios/cenarios.component';
import { GraficosComponent } from '../graficos/graficos.component';
import { SimuladorApiService } from '../../core/services/simulador-api.service';
import { QuantoFaltaComponent } from '../quanto-falta/quanto-falta.component';
import { Meta2Component } from '../meta2/meta2.component';

@Component({
  selector: 'app-simulador-shell',
  standalone: true,
  imports: [CommonModule, CenariosComponent, GraficosComponent, QuantoFaltaComponent, Meta2Component],
  template: `
    <!-- HEADER -->
    <header class="header">
      <div class="header-left">
        <h1 class="header-title">Simulador das Metas 1 e 2 do Poder Judiciário</h1>
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

    <!-- ABAS -->
    <nav class="nav-abas">
      @for (aba of abas; track aba.id) {
        <button class="aba-btn"
          [class.ativa]="sim.abaSelecionada() === aba.id"
          [disabled]="aba.desabilitada"
          [attr.title]="aba.desabilitada ? 'Funcionalidade pendente' : null"
          (click)="sim.abaSelecionada.set(aba.id)">
          {{ aba.label }}
        </button>
      }
    </nav>

    <!-- CONTEÚDO -->
    <main class="main-content">
  @if (api.carregando() && sim.cenariosCalculados().length === 0) {
    <div class="estado-api">Carregando dados do simulador...</div>
  } @else if (api.erro() && sim.cenariosCalculados().length === 0) {
    <div class="estado-api erro-api">{{ api.erro() }}</div>
  } @else {
  @switch (sim.abaSelecionada()) {
  @case ('meta1') {
    <div class="meta-painel">
      <div class="meta-header meta1">
        <div class="meta-titulo">Meta 1: Julgar mais Processos do que os Distribuídos</div>
        <div class="meta-formula">
          Julgados ÷ max(Novos + Dessobrestados − Suspensos) × 100
        </div>
      </div>
      <app-cenarios />
    </div>
  }
  @case ('quanto-falta') { <app-quanto-falta /> }
  @case ('meta2') {
    <app-meta2 />
  }
  @case ('graficos')   { <app-graficos /> }
}
  }
    </main>
  `,
  styles: [`
 :host {
  display: block;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  background: #F7F8FA;
  height: calc(100vh - 52px);
  overflow-y: auto;
  color: #4A4E57;
}

.header {
  background: #1B4F8A;
  padding: 12px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 0;
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
    .aba-btn:disabled { cursor: not-allowed; opacity: .55; }

    .main-content { padding: 24px 32px; max-width: 1200px; margin: 0 auto; }
    .estado-api { background: #fff; border: 1px solid #D1D5DB; border-radius: 10px; padding: 24px; }
    .erro-api { background: #FEE2E2; border-color: #B91C1C; color: #B91C1C; }

    .meta-painel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.meta-header {
  border-radius: 10px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-header.meta1 {
  background: linear-gradient(90deg, #1B4F8A, #0C447C);
}

.meta-header.meta2 {
  background: linear-gradient(90deg, #1F6E3A, #145228);
}

.meta-titulo {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.meta-formula {
  font-size: 12px;
  color: rgba(255,255,255,0.75);
  font-family: 'Courier New', monospace;
  background: rgba(0,0,0,0.2);
  padding: 6px 12px;
  border-radius: 6px;
}
    .meta2-aviso { background: #FFFBEB; border: 1px solid #F59E0B; color: #92400E;
      border-radius: 8px; padding: 10px 14px; font-size: 12px; }

 `]
})
export class SimuladorShellComponent implements OnInit {
  sim = inject(SimuladorService);
  api = inject(SimuladorApiService);
  anoSim = 2026;

  abas = [
    { id: 'meta1' as const, label: '📋 Meta 1', desabilitada: false },
    { id: 'quanto-falta' as const, label: '🎯 Quanto falta', desabilitada: false },
    { id: 'meta2' as const, label: '📋 Meta 2', desabilitada: false },
    { id: 'graficos' as const, label: 'Gráficos', desabilitada: false },
    { id: 'otimizador' as const, label: 'Otimizador (pendente)', desabilitada: true },
  ];

  ngOnInit(): void {
    this.sim.carregarBase();
  }

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
    if (v >= 95) return '#FCD34D';
    return '#FCA5A5';
  }
}
