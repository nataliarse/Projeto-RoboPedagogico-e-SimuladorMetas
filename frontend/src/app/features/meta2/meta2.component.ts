import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AlteracoesCenario, RegistroMeta2, RespostaMeta2 } from '../../core/models/simulador.model';
import { SimuladorApiService } from '../../core/services/simulador-api.service';
import { SimuladorService } from '../../core/services/simulador.service';
import { CenariosRecentesService } from '../../core/services/cenarios-recentes.service';

type Grupo = 'A' | 'ANT';
interface CenarioMeta2 { nome: string; grupo: Grupo; resposta: RespostaMeta2; }

@Component({
  selector: 'app-meta2',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="meta2" aria-labelledby="meta2-title">
      <header class="header">
        <div><h2 id="meta2-title">Meta 2 por grupo processual</h2>
          <p>Metodologia CNJ 2026 v3 e reprodução histórica não homologada são exibidas separadamente.</p></div>
        <span class="projection-label">Projeção estática · referência 2026</span>
      </header>

      @if (api.erro()) { <p class="error" role="alert">{{ api.erro() }}</p> }
      @if (base(); as data) {
        <div class="kpis">
          @for (grupo of grupos; track grupo) {
            <article class="kpi"><span>Meta 2-{{ grupo }} · metodologia CNJ 2026 v3</span>
              <strong>{{ fmt(resultadoAtual().resultado_2026[grupo].meta2) }}</strong>
              <small>{{ data.resultado_2026[grupo].descricao }}</small>
              <small class="validation" [class.pending]="resultadoAtual().resultado_2026[grupo].status_validacao === 'pendente_validacao'">
                {{ resultadoAtual().resultado_2026[grupo].mensagem_validacao }}
              </small>
              <small>Reprodução da equipe (não homologada):
                {{ fmt(resultadoAtual().reproducao_original_2026[grupo].meta2) }}
              </small>
            </article>
          }
        </div>

        <div class="tabs" role="tablist" aria-label="Grupo da Meta 2">
          @for (grupo of grupos; track grupo) {
            <button type="button" role="tab" [attr.aria-selected]="grupoSelecionado === grupo"
              [class.active]="grupoSelecionado === grupo" (click)="grupoSelecionado = grupo">Grupo {{ grupo }}</button>
          }
        </div>

        <div class="card">
          <div class="scenario-head"><label>Nome do cenário
            <input maxlength="60" [(ngModel)]="nomeCenario" placeholder="Ex.: esforço adicional" /></label>
            <button type="button" (click)="simular()" [disabled]="!nomeCenario.trim() || api.carregando()">Simular {{ grupoSelecionado }}</button>
          </div>
          <p class="explanation">Os valores são incrementos sobre a base. A e ANT mantêm formulários independentes; campos vazios preservam a projeção.</p>
          @if (recentes.meta2().length) { <p class="explanation">Recentes:
            @for (item of recentes.meta2(); track item.criadoEm) { <button type="button" (click)="restaurar(item)">{{ item.nome }}</button> }
            <button type="button" (click)="recentes.limparMeta2()">Limpar</button></p> }
          <div class="table-wrap"><table>
            <thead><tr><th>Mês</th><th>Natureza</th><th>Julgados ±</th><th>Suspensos ±</th><th>Dessobrestados ±</th></tr></thead>
            <tbody>@for (registro of serieBase(); track registro.data) {
              <tr><td>{{ mesLabel(registro.data) }}/2026</td><td><span [class]="registro.tipo">{{ registro.tipo === 'real' ? 'Histórico' : 'Projeção' }}</span></td>
                <td><input type="number" [ngModel]="valor(registro.data, 'julgados')" (ngModelChange)="alterar(registro.data, 'julgados', $event)" /></td>
                <td><input type="number" [ngModel]="valor(registro.data, 'suspensos')" (ngModelChange)="alterar(registro.data, 'suspensos', $event)" /></td>
                <td><input type="number" [ngModel]="valor(registro.data, 'dessobrestados')" (ngModelChange)="alterar(registro.data, 'dessobrestados', $event)" /></td></tr>
            }</tbody>
          </table></div>
        </div>

        <div class="card"><h3>Comparação de cenários</h3>
          <div class="table-wrap"><table><thead><tr><th>Cenário</th><th>Grupo alterado</th><th>Meta 2-A oficial v3</th><th>Meta 2-ANT oficial v3</th></tr></thead>
            <tbody><tr [class.selected]="selecionado() === -1" (click)="selecionado.set(-1)"><td>Base</td><td>—</td><td>{{ fmt(data.resultado_2026.A.meta2) }}</td><td>{{ fmt(data.resultado_2026.ANT.meta2) }}</td></tr>
              @for (cenario of cenarios(); track $index; let i = $index) {
                <tr [class.selected]="selecionado() === i" (click)="selecionado.set(i)"><td>{{ cenario.nome }}</td><td>{{ cenario.grupo }}</td><td>{{ fmt(cenario.resposta.resultado_2026.A.meta2) }}</td><td>{{ fmt(cenario.resposta.resultado_2026.ANT.meta2) }}</td></tr>
              }
            </tbody></table></div>
        </div>

        <div class="card"><h3>Evolução mensal · Grupo {{ grupoSelecionado }}</h3>
          <div class="table-wrap"><table><thead><tr><th>Mês</th><th>Natureza</th><th>Julgados</th><th>Suspensos</th><th>Dessobrestados</th><th>Oficial v3</th><th>Reprodução</th></tr></thead>
            <tbody>@for (registro of serieAtual(); track registro.data) {<tr><td>{{ mesLabel(registro.data) }}/2026</td><td>{{ registro.tipo === 'real' ? 'Histórico' : 'Projeção' }}</td><td>{{ registro.julgados }}</td><td>{{ registro.suspensos }}</td><td>{{ registro.dessobrestados }}</td><td>{{ fmt(registro.meta2) }}</td><td>{{ fmt(registro.meta2_original ?? null) }}</td></tr>}</tbody>
          </table></div>
        </div>
      } @else { <p class="loading">Carregando Meta 2...</p> }
    </section>
  `,
  styles: [`
    .meta2{display:flex;flex-direction:column;gap:18px}.header{display:flex;justify-content:space-between;gap:12px;align-items:center;background:linear-gradient(90deg,#1F6E3A,#145228);color:#fff;border-radius:10px;padding:16px 24px}.header h2{font-size:16px;margin:0 0 4px}.header p{font-size:12px;margin:0;opacity:.85}.projection-label{font-size:11px;background:rgba(0,0,0,.2);padding:6px 10px;border-radius:6px}.kpis{display:grid;grid-template-columns:1fr 1fr;gap:12px}.kpi,.card{background:#fff;border:1px solid #D1D5DB;border-radius:9px;padding:16px}.kpi{border-left:4px solid #1F6E3A;display:flex;flex-direction:column;gap:5px}.kpi span,.kpi small{color:#6B7280;font-size:11px}.kpi .validation{color:#92400E;font-weight:600}.kpi .validation.pending{color:#B91C1C}.kpi strong{font-size:26px;color:#1F6E3A}.tabs{display:flex;gap:6px}.tabs button{background:#fff;color:#374151;border:1px solid #9CA3AF}.tabs .active{background:#1F6E3A;color:#fff;border-color:#1F6E3A}.scenario-head{display:flex;gap:12px;align-items:end}.scenario-head label{display:flex;flex:1;flex-direction:column;font-size:12px;gap:4px}.scenario-head input{padding:8px}.scenario-head button,.tabs button{border-radius:7px;padding:9px 18px;font-weight:600;cursor:pointer}.scenario-head button{border:0;background:#1F6E3A;color:#fff}.scenario-head button:disabled{opacity:.5}.explanation{font-size:12px;color:#14532D;background:#F0FDF4;padding:9px;border-radius:6px}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:12px}th,td{text-align:left;padding:8px;border-bottom:1px solid #E5E7EB}th{background:#F3F4F6}td input{width:85px;padding:5px}.real,.previsao{border-radius:10px;padding:2px 7px}.real{background:#E6F4EC;color:#1F6E3A}.previsao{background:#FEF3C7;color:#92400E}.selected td{background:#EFF6FF}.error{background:#FEE2E2;color:#B91C1C;padding:9px;border-radius:6px}.loading{background:#fff;padding:20px}.card h3{font-size:13px;margin:0 0 12px}@media(max-width:700px){.header,.scenario-head{align-items:stretch;flex-direction:column}.kpis{grid-template-columns:1fr}}
  `],
})
export class Meta2Component implements OnInit {
  readonly api = inject(SimuladorApiService);
  private readonly sim = inject(SimuladorService);
  readonly recentes = inject(CenariosRecentesService);
  readonly grupos: Grupo[] = ['A', 'ANT'];
  readonly base = signal<RespostaMeta2 | null>(null);
  readonly cenarios = signal<CenarioMeta2[]>([]);
  readonly selecionado = signal(-1);
  grupoSelecionado: Grupo = 'A';
  nomeCenario = '';
  readonly alteracoes: Record<Grupo, AlteracoesCenario> = { A: {}, ANT: {} };
  readonly resultadoAtual = computed(() => this.selecionado() < 0 ? this.base()! : this.cenarios()[this.selecionado()].resposta);

  ngOnInit(): void { this.api.carregarMeta2().subscribe({ next: resposta => this.base.set(resposta) }); }
  valor(mes: string, campo: 'julgados'|'suspensos'|'dessobrestados'): number { return this.alteracoes[this.grupoSelecionado][mes]?.[campo] ?? 0; }
  alterar(mes: string, campo: 'julgados'|'suspensos'|'dessobrestados', valor: number | null): void {
    const numero = Number(valor) || 0; const atual = this.alteracoes[this.grupoSelecionado][mes] ?? {};
    this.alteracoes[this.grupoSelecionado][mes] = { ...atual, [campo]: numero };
  }
  simular(): void {
    const nome = this.nomeCenario.trim(); if (!nome) return;
    this.api.simularMeta2({ alteracoes_A: this.limpar(this.alteracoes.A), alteracoes_ANT: this.limpar(this.alteracoes.ANT) }).subscribe({ next: resposta => {
      this.cenarios.update(lista => [...lista, { nome, grupo: this.grupoSelecionado, resposta }]);
      this.recentes.salvarMeta2(nome, this.grupoSelecionado, this.alteracoes[this.grupoSelecionado]);
      this.selecionado.set(this.cenarios().length - 1); this.nomeCenario = '';
    }});
  }
  restaurar(item: import('../../core/services/cenarios-recentes.service').CenarioRecente): void {
    this.grupoSelecionado = item.grupo ?? 'A'; this.nomeCenario = item.nome;
    this.alteracoes[this.grupoSelecionado] = Object.fromEntries(Object.entries(item.alteracoes).map(([mes,v]) => [mes,{...v}]));
  }
  serieBase(): RegistroMeta2[] { return this.serie(this.base(), this.grupoSelecionado); }
  serieAtual(): RegistroMeta2[] { return this.serie(this.resultadoAtual(), this.grupoSelecionado); }
  private limpar(alteracoes: AlteracoesCenario): AlteracoesCenario { return Object.fromEntries(Object.entries(alteracoes).filter(([,v]) => Object.values(v).some(Boolean))); }
  private serie(resposta: RespostaMeta2 | null, grupo: Grupo): RegistroMeta2[] { return (grupo === 'A' ? resposta?.serie_A : resposta?.serie_ANT)?.filter(r => r.data.startsWith('2026')) ?? []; }
  fmt(valor: number | null): string { return this.sim.fmt(valor); }
  mesLabel(mes: string): string { return this.sim.mesLabel(mes); }
}
