import { Component, inject, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SimuladorService } from '../../core/services/simulador.service';
import { SimuladorApiService } from '../../core/services/simulador-api.service';
import { AlteracoesCenario, ANO_SIM } from '../../core/models/simulador.model';

@Component({
  selector: 'app-cenarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="col">

      @if (meta === 'meta1') {
      <div class="card">
        <div class="card-title">Criar novo cenário</div>

        <div class="row-gap">
          <div class="field-grow">
            <label class="field-label">Nome do cenário</label>
            <input [(ngModel)]="nomeCenario" placeholder="Ex: Força-tarefa Outubro"
              class="input-text" />
          </div>
          <button class="btn-primary" (click)="adicionar()"
            [disabled]="!nomeCenario.trim() || !sim.basePronta() || api.carregando() || entradasInvalidas.size > 0">
            {{ api.carregando() ? 'Calculando...' : 'Adicionar cenário' }}
          </button>
        </div>

        @if (api.erro()) {
          <div class="erro-api">⚠️ {{ api.erro() }}</div>
        }

        <p class="hint">
          Defina valores mensais. Casos novos são <strong>fixos</strong> e não podem ser alterados.
        </p>

        <div class="table-scroll">
          <table class="tabela">
            <thead>
              <tr>
                <th>Mês</th>
                <th class="th-azul">Δ Julgados</th>
                <th class="th-verde">Δ Dessobrestados</th>
                <th class="th-verm">Δ Suspensos</th>
              </tr>
            </thead>
            <tbody>
              @for (mes of sim.mesesDisponiveis(); track mes; let i = $index) {
                <tr [class.par]="i % 2 === 0">
                  <td class="td-mes">{{ mesLabel(mes) }}/{{ anoSim }}</td>
                  @for (v of variaveis; track v.key) {
                    <td>
                      <input type="number" step="1"
                        [value]="getInc(mes, v.key)"
                        (input)="setInc(mes, v.key, $event)"
                        class="input-num" />
                    </td>
                  }
                </tr>
              }
            </tbody>
          </table>
        </div>
      </div>
      }

      <div class="card">
        <div class="card-title">Comparação de cenários</div>
        <div class="table-scroll">
          <table class="tabela">
            <thead>
              <tr>
                <th>Cenário</th>
                <th>{{ meta === 'meta2' ? 'Meta 2 Final' : 'Meta 1 Final' }}</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              @for (c of sim.cenariosCalculados(); track c.id; let i = $index) {
                <tr [class.par]="i % 2 === 0">
                  <td>
                    <span class="dot" [style.background]="c.cor"></span>
                    <strong>{{ c.nome }}</strong>
                  </td>
                  <td [style.color]="sim.corMeta(meta === 'meta2' ? c.meta2Final : c.meta1Final)" class="td-num">
                    {{ sim.fmt(meta === 'meta2' ? c.meta2Final : c.meta1Final) }}
                  </td>
                  <td>
                    <span class="badge" [class]="badgeClass(meta === 'meta2' ? c.meta2Final : c.meta1Final)">
                      {{ badgeLabel(meta === 'meta2' ? c.meta2Final : c.meta1Final) }}
                    </span>
                  </td>
                  <td>
                    @if (c.id !== 1) {
                      <button class="btn-remover" (click)="sim.removerCenario(c.id)">Remover</button>
                    }
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .col { display: flex; flex-direction: column; gap: 20px; }
    .card { background: #fff; border: 1px solid #D1D5DB; border-radius: 10px; padding: 18px 20px; }
    .card-title { font-size: 13px; font-weight: 600; color: #4A4E57; margin-bottom: 14px; }
    .row-gap { display: flex; gap: 12px; align-items: flex-end; margin-bottom: 14px; flex-wrap: wrap; }
    .field-grow { flex: 1; min-width: 200px; }
    .field-label { font-size: 12px; color: #4A4E57; font-weight: 500; display: block; margin-bottom: 4px; }
    .input-text { width: 100%; padding: 8px 12px; border: 1px solid #D1D5DB; border-radius: 6px;
      font-size: 14px; box-sizing: border-box; }
    .hint { font-size: 12px; color: #6B7280; margin-bottom: 14px; line-height: 1.5; }
    .btn-primary { padding: 9px 24px; background: #1B4F8A; color: #fff; border: none;
      border-radius: 7px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; }
    .btn-primary:disabled { opacity: .45; cursor: not-allowed; }
    .erro-api { background: #FEE2E2; color: #B91C1C; border: 1px solid #B91C1C;
      border-radius: 6px; padding: 8px 12px; font-size: 13px; margin-bottom: 12px; }
    .table-scroll { overflow-x: auto; }
    .tabela { width: 100%; border-collapse: collapse; font-size: 13px; }
    .tabela th { padding: 9px 12px; text-align: left; font-weight: 600; color: #4A4E57;
      font-size: 12px; background: #F3F4F6; white-space: nowrap; }
    .tabela td { padding: 7px 10px; border-bottom: 1px solid #E5E7EB; }
    .tabela tr.par td { background: #fff; }
    .tabela tr:not(.par) td { background: #F7F8FA; }
    .th-azul { color: #1B4F8A !important; }
    .th-verde { color: #1F6E3A !important; }
    .th-verm { color: #B91C1C !important; }
    .td-mes { font-weight: 600; white-space: nowrap; }
    .td-num { font-weight: 700; }
    .input-num { width: 100px; padding: 5px 8px; border: 1px solid #D1D5DB;
      border-radius: 5px; font-size: 13px; text-align: center; }
    .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
    .badge { font-size: 11px; font-weight: 600; padding: 2px 9px; border-radius: 20px; }
    .badge.verde   { background: #E6F4EC; color: #1F6E3A; }
    .badge.amarelo { background: #FEF3C7; color: #92400E; }
    .badge.vermelho{ background: #FEE2E2; color: #B91C1C; }
    .btn-remover { border: none; background: #FEE2E2; color: #B91C1C;
      border-radius: 5px; padding: 3px 10px; cursor: pointer; font-size: 12px; }
  `]
})
export class CenariosComponent {
  @Input() meta: 'meta1' | 'meta2' = 'meta1';

  sim = inject(SimuladorService);
  api = inject(SimuladorApiService);

  nomeCenario = '';
  anoSim      = ANO_SIM;

  variaveis = [
    { key: 'julgados'       as const },
    { key: 'dessobrestados' as const },
    { key: 'suspensos'      as const },
  ];

  private inc: Record<string, Record<string, number>> = {};
  entradasInvalidas = new Set<string>();

  getInc(mes: string, variavel: string): number {
    return this.inc[mes]?.[variavel] ?? 0;
  }

  setInc(mes: string, variavel: string, event: Event): void {
    const campo = event.target as HTMLInputElement;
    const chave = `${mes}:${variavel}`;
    const texto = campo.value.trim();
    if (texto === '') {
      this.entradasInvalidas.delete(chave);
      delete this.inc[mes]?.[variavel];
      return;
    }

    const val = Number(texto);
    if (!Number.isFinite(val) || !Number.isInteger(val)) {
      this.entradasInvalidas.add(chave);
      this.api.erro.set('Os valores preenchidos devem ser números inteiros.');
      return;
    }

    this.entradasInvalidas.delete(chave);
    if (!this.inc[mes]) this.inc[mes] = {};
    this.inc[mes][variavel] = val;
  }

  adicionar(): void {
    const nome = this.nomeCenario.trim();
    if (!nome || !this.sim.basePronta() || this.api.carregando() || this.entradasInvalidas.size) return;
    if (this.sim.nomeCenarioExiste(nome)) {
      this.api.erro.set('Já existe um cenário com esse nome.');
      return;
    }

    // Monta as alterações
    const alteracoes: AlteracoesCenario = {};
    Object.entries(this.inc).forEach(([mes, vars]) => {
      const algum = Object.values(vars).some(v => v !== 0);
      if (algum) {
        alteracoes[mes] = {
          julgados: vars['julgados'],
          dessobrestados: vars['dessobrestados'],
          suspensos: vars['suspensos'],
        };
      }
    });

    const alteracoesEnviadas: AlteracoesCenario = Object.fromEntries(
      Object.entries(alteracoes).map(([mes, vars]) => [mes, { ...vars }])
    );

    this.api.simular(alteracoesEnviadas).subscribe({
      next: res => {
        this.sim.adicionarCenario(nome, alteracoesEnviadas, res);
        this.nomeCenario = '';
        this.inc = {};
        this.entradasInvalidas.clear();
      },
      error: () => {}
    });
  }

  mesLabel(d: string): string { return this.sim.mesLabel(d); }

  badgeClass(v: number | null): string {
    if (v == null) return 'amarelo';
    if (v >= 100)  return 'verde';
    if (v >= 95)   return 'amarelo';
    return 'vermelho';
  }

  badgeLabel(v: number | null): string {
    if (v == null)  return 'Não calculável';
    if (v >= 100)   return `Cumprida ${this.sim.fmt(v)}`;
    if (v >= 95)    return `≥95% ${this.sim.fmt(v)}`;
    return `Abaixo ${this.sim.fmt(v)}`;
  }
}
