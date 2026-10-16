import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SimuladorService } from '../../core/services/simulador.service';
import { ResultadoOtimizador, MESES_NOMES, MESES_SIM, ANO_SIM } from '../../core/models/simulador.model';

@Component({
  selector: 'app-otimizador',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="col">

      <div class="card">
        <div class="card-title">Calcular esforço mínimo para atingir a meta</div>
        <p class="desc">
          O otimizador encontra automaticamente o menor ajuste necessário em uma variável
          para que a Meta 1 acumulada do ano atinja o percentual desejado.
        </p>

        <div class="grid-3">
          <div class="field">
            <label class="field-label">Variável a ajustar</label>
            <select [(ngModel)]="variavel" class="select">
              <option value="julgados">Julgados</option>
              <option value="dessobrestados">Dessobrestados</option>
              <option value="suspensos">Suspensos</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">Mês de aplicação</label>
            <select [(ngModel)]="mes" class="select">
              @for (m of mesesSim; track m) {
                <option [value]="m">{{ mesLabel(m) }}/{{ anoSim }}</option>
              }
            </select>
          </div>
          <div class="field">
            <label class="field-label">Meta desejada (%)</label>
            <input type="number" [(ngModel)]="metaAlvo" step="1" min="0" max="200"
              class="input-num" />
          </div>
        </div>

        <button class="btn-primary" (click)="calcular()">
          Calcular esforço mínimo
        </button>

        @if (resultado()) {
          <div class="resultado" [class.ok]="resultado()!.ok" [class.nok]="!resultado()!.ok">
            <div class="resultado-titulo">
              {{ resultado()!.ok ? '✓ Meta atingível' : '✗ Meta não atingível' }}
            </div>
            <div class="resultado-msg">{{ resultado()!.mensagem }}</div>

            @if (resultado()!.metaAtual) {
              <div class="kpis-row">
                <div class="kpi-box">
                  <span class="kpi-label">Meta atual</span>
                  <span class="kpi-val">{{ resultado()!.metaAtual }}%</span>
                </div>
                <span class="seta">→</span>
                <div class="kpi-box">
                  <span class="kpi-label">Meta resultante</span>
                  <span class="kpi-val verde">{{ resultado()!.metaResultante }}%</span>
                </div>
                <span class="seta">·</span>
                <div class="kpi-box">
                  <span class="kpi-label">Ajuste necessário</span>
                  <span class="kpi-val azul">+{{ resultado()!.incremento?.toLocaleString('pt-BR') }}</span>
                </div>
              </div>
            }
          </div>
        }
      </div>

      <div class="card">
        <div class="card-title">Como funciona o otimizador</div>
        <div class="explicacao">
          <p>O algoritmo utiliza <strong>busca binária (bisseção)</strong> para encontrar o menor incremento
          inteiro que, aplicado a uma variável editável em um mês específico, resulta na Meta 1 acumulada
          atingindo o percentual-alvo.</p>
          <p><strong>Variáveis disponíveis:</strong> julgados (↑ aumenta a meta), dessobrestados
          (↑ reduz a meta), suspensos (↑ reduz o denominador, aumentando a meta).</p>
          <p><strong>Casos novos</strong> são sempre fixos e não podem ser alterados, conforme regra do CNJ.</p>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .col { display: flex; flex-direction: column; gap: 20px; }
    .card { background: #fff; border: 1px solid #D1D5DB; border-radius: 10px; padding: 18px 20px; }
    .card-title { font-size: 13px; font-weight: 600; color: #4A4E57; margin-bottom: 10px; }
    .desc { font-size: 13px; color: #6B7280; line-height: 1.6; margin-bottom: 18px; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
    @media (max-width: 640px) { .grid-3 { grid-template-columns: 1fr; } }
    .field { display: flex; flex-direction: column; gap: 4px; }
    .field-label { font-size: 12px; color: #4A4E57; font-weight: 500; }
    .select, .input-num {
      padding: 8px 10px; border: 1px solid #D1D5DB; border-radius: 6px;
      font-size: 13px; width: 100%; box-sizing: border-box;
    }
    .btn-primary { padding: 10px 28px; background: #1B4F8A; color: #fff; border: none;
      border-radius: 7px; font-size: 14px; font-weight: 600; cursor: pointer; }

    .resultado { margin-top: 20px; padding: 16px 20px; border-radius: 8px; border: 1px solid; }
    .resultado.ok  { background: #E6F4EC; border-color: #1F6E3A; }
    .resultado.nok { background: #FEE2E2; border-color: #B91C1C; }
    .resultado-titulo { font-weight: 700; font-size: 15px; margin-bottom: 8px; }
    .ok  .resultado-titulo { color: #1F6E3A; }
    .nok .resultado-titulo { color: #B91C1C; }
    .resultado-msg { font-size: 14px; color: #4A4E57; line-height: 1.7; }

    .kpis-row { display: flex; align-items: center; gap: 20px; margin-top: 14px; flex-wrap: wrap; }
    .kpi-box { display: flex; flex-direction: column; }
    .kpi-label { font-size: 11px; color: #6B7280; }
    .kpi-val { font-size: 20px; font-weight: 700; color: #1a1a2e; }
    .kpi-val.verde { color: #1F6E3A; }
    .kpi-val.azul  { color: #1B4F8A; }
    .seta { font-size: 20px; color: #9CA3AF; }

    .explicacao p { font-size: 13px; color: #4A4E57; line-height: 1.8; margin-bottom: 10px; }
    .explicacao p:last-child { margin-bottom: 0; }
  `]
})
export class OtimizadorComponent {
  sim = inject(SimuladorService);

  variavel: 'julgados' | 'dessobrestados' | 'suspensos' = 'julgados';
  mes    = '2026-06';
  metaAlvo = 100;
  mesesSim = MESES_SIM;
  anoSim = ANO_SIM;

  resultado = signal<ResultadoOtimizador | null>(null);

  calcular() {
    const res = this.sim.encontrarAjusteMinimo(this.variavel, this.mes, this.metaAlvo);
    this.resultado.set(res);
  }

  mesLabel(d: string): string { return this.sim.mesLabel(d); }
}
