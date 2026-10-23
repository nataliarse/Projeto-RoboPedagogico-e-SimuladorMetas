import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AlteracoesCenario, ANO_SIM, RespostaQuantoFalta } from '../../core/models/simulador.model';
import { SimuladorApiService } from '../../core/services/simulador-api.service';
import { SimuladorService } from '../../core/services/simulador.service';

@Component({
  selector: 'app-quanto-falta',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="calculator" aria-labelledby="quanto-falta-title">
      <header class="calculator-header">
        <h2 id="quanto-falta-title">Quanto falta para a Meta 1?</h2>
        <p>Estime o esforço mensal adicional necessário para atingir a meta desejada em dezembro de {{ anoSim }}.</p>
      </header>

      <div class="card">
        <div class="fields">
          <label>Meta desejada (%)
            <input type="number" min="1" max="200" step="0.5" [(ngModel)]="metaAlvo" />
          </label>
          <label>Distribuir a partir de
            <select [(ngModel)]="mesInicio">
              @for (mes of mesesDoAno(); track mes.data) {
                <option [value]="mes.data">{{ sim.mesLabel(mes.data) }}/{{ anoSim }}{{ mes.real ? ' (real)' : '' }}</option>
              }
            </select>
          </label>
          <label>Partir de
            <select [(ngModel)]="partidaId">
              @for (cenario of sim.cenariosCalculados(); track cenario.id) {
                <option [ngValue]="cenario.id">{{ cenario.id === 1 ? 'Base' : cenario.nome }}</option>
              }
            </select>
          </label>
          <button type="button" (click)="calcular()"
            [disabled]="api.carregando() || !sim.basePronta() || !metaValida()">
            {{ api.carregando() ? 'Calculando...' : 'Calcular' }}
          </button>
        </div>

        @if (!metaValida()) { <p class="warning" role="alert">Informe uma meta entre 1% e 200%.</p> }
        @if (api.erro()) { <p class="error" role="alert">{{ api.erro() }}</p> }

        @if (resultado(); as resposta) {
          <div class="result" aria-live="polite">
            @if (resposta.ja_atingida) {
              <h3>Meta já atingida</h3>
              <p>A projeção atual é {{ fmtPct(resposta.meta_atual) }}. Nenhum esforço adicional é necessário.</p>
            } @else if (!resposta.ok) {
              <h3>Não foi possível calcular</h3><p>{{ resposta.mensagem }}</p>
            } @else {
              <h3>+{{ fmtNum(resposta.incremento_mensal) }} julgamentos por mês</h3>
              <p>De {{ periodo(resposta) }}, totalizando +{{ fmtNum(resposta.total_adicional) }} julgamentos.</p>
              <p>Projeção: {{ fmtPct(resposta.meta_atual) }} → <strong>{{ fmtPct(resposta.meta_resultante) }}</strong>.</p>
              <button type="button" class="secondary" (click)="criarCenario(resposta)">Criar cenário com esse esforço</button>
            }
          </div>
          @if (resposta.meses_reais.length) {
            <p class="warning">O período inclui dados reais; o esforço nesses meses é apenas retroativo.</p>
          }
          <p class="disclaimer">Estimativa de apoio à decisão baseada no cálculo do servidor; não constitui determinação.</p>
        }
      </div>
    </section>
  `,
  styles: [`
    .calculator { display:flex; flex-direction:column; gap:20px; }
    .calculator-header { color:#fff; background:linear-gradient(90deg,#1B4F8A,#0C447C); border-radius:10px; padding:16px 24px; }
    h2 { font-size:16px; margin:0 0 4px; } .calculator-header p { font-size:13px; margin:0; opacity:.85; }
    .card { background:#fff; border:1px solid #D1D5DB; border-radius:10px; padding:20px; }
    .fields { display:grid; grid-template-columns:minmax(130px,.6fr) 1fr 1fr auto; gap:12px; align-items:end; }
    label { display:flex; flex-direction:column; gap:4px; font-size:12px; font-weight:600; }
    input,select { min-height:38px; border:1px solid #9CA3AF; border-radius:6px; padding:6px 10px; background:#fff; }
    button { min-height:38px; border:0; border-radius:7px; padding:8px 18px; background:#1B4F8A; color:#fff; font-weight:600; cursor:pointer; }
    button:disabled { opacity:.5; cursor:not-allowed; } .secondary { margin-top:8px; background:#fff; color:#1B4F8A; border:1px solid #1B4F8A; }
    .result { margin-top:16px; padding:14px 18px; border:1px solid #BFDBFE; border-radius:8px; background:#EFF6FF; }
    .result h3 { margin:0 0 6px; color:#1B4F8A; } .result p { margin:5px 0; }
    .warning,.error { margin:14px 0 0; padding:8px 12px; border-radius:6px; font-size:12px; }
    .warning { color:#92400E; background:#FFFBEB; border:1px solid #FDE68A; } .error { color:#B91C1C; background:#FEE2E2; border:1px solid #B91C1C; }
    .disclaimer { color:#6B7280; font-size:11px; margin:12px 0 0; }
    @media (max-width:800px) { .fields { grid-template-columns:1fr; } }
  `],
})
export class QuantoFaltaComponent {
  readonly sim = inject(SimuladorService);
  readonly api = inject(SimuladorApiService);
  readonly anoSim = ANO_SIM;
  metaAlvo = 100;
  partidaId = 1;
  private readonly mesEscolhido = signal<string | null>(null);
  readonly resultado = signal<RespostaQuantoFalta | null>(null);
  readonly mesesDoAno = computed(() => this.sim.cenariosCalculados()[0]?.anoRows.map(row => ({
    data: row.data, real: row.julgados_tipo !== 'forecast',
  })) ?? []);

  get mesInicio(): string {
    const meses = this.mesesDoAno();
    return this.mesEscolhido() ?? meses.find(mes => !mes.real)?.data ?? meses[0]?.data ?? '';
  }
  set mesInicio(value: string) { this.mesEscolhido.set(value); }

  metaValida(): boolean { return Number.isFinite(this.metaAlvo) && this.metaAlvo >= 1 && this.metaAlvo <= 200; }

  calcular(): void {
    if (!this.metaValida()) return;
    this.api.quantoFalta({ meta_alvo: this.metaAlvo, mes_inicio: this.mesInicio || undefined,
      alteracoes: this.alteracoesPartida() }).subscribe({
      next: resposta => this.resultado.set(resposta), error: () => this.resultado.set(null),
    });
  }

  criarCenario(resposta: RespostaQuantoFalta): void {
    const incremento = resposta.incremento_mensal ?? 0;
    const alteracoes: AlteracoesCenario = Object.fromEntries(
      Object.entries(this.alteracoesPartida()).map(([mes, valor]) => [mes, { ...valor }]),
    );
    resposta.meses.forEach(mes => alteracoes[mes] = {
      ...(alteracoes[mes] ?? {}), julgados: (alteracoes[mes]?.julgados ?? 0) + incremento,
    });
    this.api.simular(alteracoes).subscribe({ next: simulacao => {
      let nome = `Meta ${this.fmtPct(resposta.meta_alvo)} (+${this.fmtNum(incremento)}/mês)`;
      for (let i = 2; this.sim.nomeCenarioExiste(nome); i++) nome = `Meta ${this.fmtPct(resposta.meta_alvo)} (+${this.fmtNum(incremento)}/mês) ${i}`;
      this.sim.adicionarCenario(nome, alteracoes, simulacao);
      this.sim.abaSelecionada.set('meta1');
    }});
  }

  private alteracoesPartida(): AlteracoesCenario {
    return this.sim.cenarios().find(cenario => cenario.id === this.partidaId)?.alteracoes ?? {};
  }
  periodo(resposta: RespostaQuantoFalta): string {
    if (!resposta.meses.length) return '—';
    const inicio = `${this.sim.mesLabel(resposta.meses[0])}/${this.anoSim}`;
    const fim = `${this.sim.mesLabel(resposta.meses.at(-1)! )}/${this.anoSim}`;
    return resposta.meses.length === 1 ? inicio : `${inicio} a ${fim}`;
  }
  fmtNum(valor: number | null | undefined): string { return valor == null ? '—' : valor.toLocaleString('pt-BR'); }
  fmtPct(valor: number | null | undefined): string { return valor == null ? '—' : `${valor.toLocaleString('pt-BR', { maximumFractionDigits: 2 })}%`; }
}
