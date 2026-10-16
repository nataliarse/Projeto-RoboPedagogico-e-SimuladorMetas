import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SimuladorService } from '../../core/services/simulador.service';
import { ANO_SIM } from '../../core/models/simulador.model';

@Component({
  selector: 'app-tabela',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card">
      <div class="card-title">Evolução mensal acumulada — {{ anoSim }} (cenário Base)</div>
      <div class="table-scroll">
        <table class="tabela">
          <thead>
            <tr>
              <th>Mês</th>
              <th>Novos Acum.</th>
              <th>Julgados Acum.</th>
              <th>Dessobr. Acum.</th>
              <th>Suspensos</th>
              <th>Meta 1</th>
              <th>Meta 2</th>
              <th>Status M2</th>
            </tr>
          </thead>
          <tbody>
            @for (r of linhas; track r.data; let i = $index) {
              <tr [class.par]="i % 2 === 0">
                <td class="td-mes">
                  {{ sim.mesLabel(r.data) }}/{{ anoSim }}
                  @if (r.novos_tipo === 'forecast') {
                    <span class="tag-prev">prev.</span>
                  }
                </td>
                <td>{{ sim.fmtN(r.novos_acum) }}</td>
                <td>{{ sim.fmtN(r.julgados_acum) }}</td>
                <td>{{ sim.fmtN(r.dessobrestados_acum) }}</td>
                <td>{{ sim.fmtN(r.suspensos) }}</td>
                <td class="td-num" [style.color]="sim.corMeta(r.meta1)">{{ sim.fmt(r.meta1) }}</td>
                <td class="td-num" [style.color]="sim.corMeta(r.meta2)">{{ sim.fmt(r.meta2) }}</td>
                <td>
                  <span class="badge" [class]="badgeClass(r.meta2)">{{ badgeLabel(r.meta2) }}</span>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .card { background: #fff; border: 1px solid #D1D5DB; border-radius: 10px; padding: 18px 20px; }
    .card-title { font-size: 13px; font-weight: 600; color: #4A4E57; margin-bottom: 14px; }
    .table-scroll { overflow-x: auto; }
    .tabela { width: 100%; border-collapse: collapse; font-size: 13px; }
    .tabela th { padding: 9px 12px; text-align: left; font-weight: 600; color: #fff;
      font-size: 12px; background: #1B4F8A; white-space: nowrap; }
    .tabela td { padding: 8px 12px; border-bottom: 1px solid #E5E7EB; }
    .tabela tr.par td { background: #fff; }
    .tabela tr:not(.par) td { background: #F7F8FA; }
    .td-mes { font-weight: 600; white-space: nowrap; }
    .td-num { font-weight: 700; }
    .tag-prev { font-size: 10px; color: #6B7280; margin-left: 5px; }
    .badge { font-size: 11px; font-weight: 600; padding: 2px 9px; border-radius: 20px; }
    .badge.verde   { background: #E6F4EC; color: #1F6E3A; }
    .badge.amarelo { background: #FEF3C7; color: #92400E; }
    .badge.vermelho{ background: #FEE2E2; color: #B91C1C; }
  `]
})
export class TabelaComponent {
  sim = inject(SimuladorService);
  anoSim = ANO_SIM;

  get linhas() {
    return this.sim.cenariosCalculados()[0]?.resultado
      .filter(r => r.data.startsWith(String(ANO_SIM))) ?? [];
  }

  badgeClass(v: number | null): string {
    if (v == null) return 'amarelo';
    if (v >= 100)  return 'verde';
    if (v >= 95)   return 'amarelo';
    return 'vermelho';
  }

  badgeLabel(v: number | null): string {
    if (v == null) return 'Não calculável';
    if (v >= 100)  return 'Cumprida';
    if (v >= 95)   return '≥ 95%';
    return 'Abaixo de 95%';
  }
}
