import { Component, inject, AfterViewInit, ElementRef, ViewChild, effect, Injector, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SimuladorService } from '../../core/services/simulador.service';
import { ANO_SIM } from '../../core/models/simulador.model';

@Component({
  selector: 'app-graficos',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="col">

      <!-- Gráfico de linhas -->
      <div class="card">
        <div class="card-title">Meta 1 — evolução mensal por cenário ({{ anoSim }})</div>
        <div class="legenda">
          @for (c of sim.cenariosCalculados(); track c.id) {
            <span class="leg-item">
              <span class="leg-dot" [style.background]="c.cor"></span>{{ c.nome }}
            </span>
          }
        </div>
        <div class="canvas-wrap" role="img" aria-label="Evolução mensal da Meta 1 por cenário">
          <canvas #linhaCanvas aria-hidden="true"></canvas>
          @if (graficoIndisponivel()) {
            <div class="grafico-indisponivel">Gráfico indisponível. Consulte os resultados por cenário abaixo.</div>
          }
        </div>
      </div>

      <!-- Gráfico de barras -->
      <div class="card">
        <div class="card-title">Meta 1 final por cenário</div>
        <div class="barras-wrap" aria-label="Comparação da Meta 1 final por cenário">
          @for (b of sim.dadosBarras(); track b.nome) {
            <div class="barra-row" [attr.aria-label]="b.nome + ': ' + (b.meta1 == null ? 'não calculável' : b.meta1.toFixed(2) + '%')">
              <span class="barra-label">{{ b.nome }}</span>
              <div class="barra-track">
                <div class="barra-fill"
                  [style.width]="barraWidth(b.meta1)"
                  [style.background]="barraColor(b.meta1)">
                </div>
                <span class="barra-val" [style.color]="barraColor(b.meta1)">
                  {{ b.meta1 == null ? '—' : b.meta1.toFixed(2) + '%' }}
                </span>
              </div>
            </div>
          }
          <!-- Linhas de referência -->
          <div class="refs">
            <span class="ref-tag ref-100">100%</span>
            <span class="ref-tag ref-95">95%</span>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .col { display: flex; flex-direction: column; gap: 20px; }
    .card { background: #fff; border: 1px solid #D1D5DB; border-radius: 10px; padding: 18px 20px; }
    .card-title { font-size: 13px; font-weight: 600; color: #4A4E57; margin-bottom: 12px; }
    .legenda { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 14px; }
    .leg-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #4A4E57; }
    .leg-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
    .canvas-wrap { position: relative; height: 320px; }
    canvas { width: 100% !important; }
    .grafico-indisponivel { position: absolute; inset: 0; display: grid; place-items: center;
      color: #6B7280; background: #F7F8FA; border-radius: 6px; font-size: 13px; }

    /* Barras manuais */
    .barras-wrap { display: flex; flex-direction: column; gap: 12px; position: relative; }
    .barra-row { display: flex; align-items: center; gap: 12px; }
    .barra-label { width: 160px; font-size: 12px; font-weight: 600; color: #4A4E57;
      text-align: right; flex-shrink: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .barra-track { flex: 1; background: #F3F4F6; border-radius: 4px; height: 28px;
      position: relative; display: flex; align-items: center; }
    .barra-fill { height: 100%; border-radius: 4px; transition: width .4s ease; min-width: 4px; }
    .barra-val { position: absolute; right: 8px; font-size: 12px; font-weight: 700; }
    .refs { display: flex; justify-content: space-between; padding: 0 0 0 172px; margin-top: -4px; }
    .ref-tag { font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; }
    .ref-100 { background: #FEE2E2; color: #B91C1C; }
    .ref-95  { background: #FEF3C7; color: #92400E; }
  `]
})
export class GraficosComponent implements AfterViewInit, OnDestroy {
  sim = inject(SimuladorService);
  private injector = inject(Injector);
  anoSim = ANO_SIM;
  graficoIndisponivel = signal(false);

  @ViewChild('linhaCanvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  private chart: any;

  ngAfterViewInit() {
    effect((onCleanup) => {
      // reage a mudanças nos cenários
      this.sim.dadosGrafico();
      const timer = setTimeout(() => this.desenharGrafico(), 50);
      onCleanup(() => clearTimeout(timer));
    }, { injector: this.injector });
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
    this.chart = null;
  }

  private async desenharGrafico() {
    if (!this.canvasRef) return;
    const dados   = this.sim.dadosGrafico();
    const cenarios = this.sim.cenariosCalculados();

    // Chart.js via CDN (carregado no index.html)
    const Chart = (window as any).Chart;
    if (!Chart) {
      this.graficoIndisponivel.set(true);
      return;
    }

    if (this.chart) { this.chart.destroy(); this.chart = null; }

    const ctx = this.canvasRef.nativeElement.getContext('2d');
    if (!ctx) {
      this.graficoIndisponivel.set(true);
      return;
    }
    const labels = dados.map(p => p['mes'] as string);

    const datasets = cenarios.map(c => ({
      label: c.nome,
      data: dados.map(p => p[c.nome] as number | null),
      borderColor: c.cor,
      backgroundColor: c.cor + '22',
      borderWidth: 2,
      pointRadius: 3,
      tension: 0.3,
      spanGaps: true,
    }));

    try {
      this.chart = new Chart(ctx, {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          annotation: {
            annotations: {
              meta100: { type: 'line', yMin: 100, yMax: 100, borderColor: '#B91C1C',
                borderDash: [4, 2], borderWidth: 1 },
              meta95:  { type: 'line', yMin: 95,  yMax: 95,  borderColor: '#92400E',
                borderDash: [4, 2], borderWidth: 1 },
            }
          }
        },
        scales: {
          x: { grid: { color: '#E5E7EB' } },
          y: { grid: { color: '#E5E7EB' }, ticks: { callback: (v: any) => v + '%' } }
        }
      }
      });
      this.graficoIndisponivel.set(false);
    } catch {
      this.chart = null;
      this.graficoIndisponivel.set(true);
    }
  }

  barraWidth(val: number | null): string {
    if (val == null) return '0%';
    const valores = this.sim.dadosBarras()
      .map(b => b.meta1)
      .filter((meta): meta is number => meta != null);
    const max = Math.max(...valores, 110);
    return Math.min((val / max) * 100, 100) + '%';
  }

  barraColor(val: number | null): string {
    if (val == null) return '#6B7280';
    if (val >= 100) return '#1F6E3A';
    if (val >= 95)  return '#92400E';
    return '#B91C1C';
  }
}
