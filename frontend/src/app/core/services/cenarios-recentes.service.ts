import { Injectable, signal } from '@angular/core';
import { AlteracoesCenario } from '../models/simulador.model';

export interface CenarioRecente { nome: string; alteracoes: AlteracoesCenario; criadoEm: string; grupo?: 'A' | 'ANT'; }
const MAX = 3;

@Injectable({ providedIn: 'root' })
export class CenariosRecentesService {
  readonly meta1 = signal(this.ler('simulador_recentes_meta1'));
  readonly meta2 = signal(this.ler('simulador_recentes_meta2'));

  salvarMeta1(nome: string, alteracoes: AlteracoesCenario): void { this.salvar(this.meta1, 'simulador_recentes_meta1', { nome, alteracoes: this.limpar(alteracoes), criadoEm: new Date().toISOString() }); }
  salvarMeta2(nome: string, grupo: 'A'|'ANT', alteracoes: AlteracoesCenario): void { this.salvar(this.meta2, 'simulador_recentes_meta2', { nome, grupo, alteracoes: this.limpar(alteracoes), criadoEm: new Date().toISOString() }); }
  limparMeta1(): void { this.meta1.set([]); this.remover('simulador_recentes_meta1'); }
  limparMeta2(): void { this.meta2.set([]); this.remover('simulador_recentes_meta2'); }

  private salvar(estado: typeof this.meta1, chave: string, item: CenarioRecente): void {
    const assinatura = (valor: CenarioRecente) => `${valor.grupo ?? ''}:${JSON.stringify(valor.alteracoes)}`;
    const lista = [item, ...estado().filter(valor => assinatura(valor) !== assinatura(item))].slice(0, MAX);
    estado.set(lista); try { globalThis.localStorage?.setItem(chave, JSON.stringify(lista)); } catch { /* opcional */ }
  }
  private limpar(alteracoes: AlteracoesCenario): AlteracoesCenario { return Object.fromEntries(Object.entries(alteracoes).flatMap(([mes, valores]) => { const limpos = Object.fromEntries(Object.entries(valores).filter(([,v]) => typeof v === 'number' && v !== 0)); return Object.keys(limpos).length ? [[mes, limpos]] : []; })); }
  private ler(chave: string): CenarioRecente[] { try { const lista = JSON.parse(globalThis.localStorage?.getItem(chave) ?? '[]'); return Array.isArray(lista) ? lista.slice(0, MAX) : []; } catch { return []; } }
  private remover(chave: string): void { try { globalThis.localStorage?.removeItem(chave); } catch { /* opcional */ } }
}
