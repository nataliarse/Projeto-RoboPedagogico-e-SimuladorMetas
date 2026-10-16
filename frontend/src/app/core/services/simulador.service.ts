import { Injectable, computed, signal } from '@angular/core';
import {
  AlteracoesCenario,
  Cenario,
  CenarioCalculado,
  CORES_CENARIOS,
  MESES_NOMES,
  ANO_SIM,
  PontoGrafico,
  PontoBarra,
  RegistroBase,
  RegistroCalculado,
  RespostaSimulacao,
  ResultadoOtimizador,
} from '../models/simulador.model';
import { DadosService } from './dados.service';
import { SimuladorApiService } from './simulador-api.service';

@Injectable({ providedIn: 'root' })
export class SimuladorService {
  // â”€â”€ Estado reativo â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  cenarios = signal<Cenario[]>([
    { id: 1, nome: 'Base', alteracoes: {}, cor: CORES_CENARIOS[0], resposta: null },
  ]);
  private cargaBaseIniciada = false;

  abaSelecionada = signal<'meta1' | 'meta2' | 'graficos' | 'otimizador'>('meta1');

  // â”€â”€ Base consolidada (montada uma vez) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  readonly baseGlobal: RegistroBase[];

  constructor(
    private dados: DadosService,
    private api: SimuladorApiService,
  ) {
    this.baseGlobal = this.montarBase();
  }

  carregarBase(): void {
    if (this.cargaBaseIniciada) return;
    this.cargaBaseIniciada = true;

    this.api.carregarBase().subscribe({
      next: (resposta) =>
        this.cenarios.update((cenarios) =>
          cenarios.map((cenario) => (cenario.id === 1 ? { ...cenario, resposta } : cenario)),
        ),
      error: () => {},
    });
  }

  // ============================================================
  // ETL â€” consolida as sÃ©ries em uma base Ãºnica
  // ============================================================
  private montarBase(): RegistroBase[] {
    const idx: Record<string, Partial<RegistroBase>> = {};

    this.dados.novos.forEach((r) => {
      idx[r.d] = { data: r.d, novos: r.v, novos_tipo: r.t };
    });

    this.dados.julgados.forEach((r) => {
      if (!idx[r.d]) idx[r.d] = { data: r.d };
      idx[r.d].julgados = r.v;
      idx[r.d].julgados_tipo = r.t;
    });

    this.dados.suspensos.forEach((r) => {
      if (!idx[r.d]) idx[r.d] = { data: r.d };
      idx[r.d].suspensos = r.v;
      // dessobrestados â‰ˆ 8% dos novos (estimativa baseada nos dados histÃ³ricos)
      const nov = idx[r.d].novos ?? 0;
      idx[r.d].dessobrestados = Math.round(nov * 0.08);
    });

    return (Object.values(idx) as RegistroBase[])
      .filter((r) => r.novos && r.julgados && r.suspensos != null && r.dessobrestados != null)
      .sort((a, b) => a.data.localeCompare(b.data));
  }

  // ============================================================
  // FÃ“RMULAS OFICIAIS CNJ
  // Meta 1 = julgados / max(novos + dessobr - suspensos, novos + dessobr) * 100
  // Meta 2 = julgados / (novos_acum - suspensos) * (1000/9.4)
  // ============================================================
  private calcMeta1(jAcum: number, nAcum: number, dAcum: number, sAcum: number): number | null {
    const den = nAcum + dAcum - sAcum;
    if (!den || den <= 0) return null;
    const piso = Math.max(nAcum + dAcum, 1);
    return (jAcum / Math.max(den, piso)) * 100;
  }

  private calcMeta2(jAcum: number, distAcum: number, sus: number): number | null {
    const den = distAcum - sus;
    if (!den || den <= 0) return null;
    return (jAcum / den) * (1000 / 9.4);
  }

  // ============================================================
  // calcular_meta_acumulada() â€” acumula por ano e calcula metas
  // ============================================================
  calcularMetas(base: RegistroBase[]): RegistroCalculado[] {
    const resultado: RegistroCalculado[] = [];
    const acum: Record<
      string,
      { novos: number; julgados: number; dessobrestados: number; suspensos: number }
    > = {};

    base.forEach((row) => {
      const ano = row.data.slice(0, 4);
      if (!acum[ano]) acum[ano] = { novos: 0, julgados: 0, dessobrestados: 0, suspensos: 0 };

      acum[ano].novos += row.novos;
      acum[ano].julgados += row.julgados;
      acum[ano].dessobrestados += row.dessobrestados;
      acum[ano].suspensos += row.suspensos;

      const a = acum[ano];

      resultado.push({
        ...row,
        novos_acum: a.novos,
        julgados_acum: a.julgados,
        dessobrestados_acum: a.dessobrestados,
        suspensos_acum: a.suspensos,
        meta1: this.calcMeta1(a.julgados, a.novos, a.dessobrestados, a.suspensos),
        meta2: this.calcMeta2(a.julgados, a.novos, row.suspensos),
      });
    });

    return resultado;
  }

  // ============================================================
  // simular_cenario() â€” aplica incrementos e recalcula
  // ============================================================
  simularCenario(alteracoes: AlteracoesCenario): RegistroCalculado[] {
    const sim = this.baseGlobal.map((row) => {
      const alt = alteracoes[row.data];
      if (!alt) return { ...row };
      return {
        ...row,
        julgados: Math.max(0, row.julgados + (alt.julgados ?? 0)),
        dessobrestados: Math.max(0, row.dessobrestados + (alt.dessobrestados ?? 0)),
        suspensos: Math.max(0, row.suspensos + (alt.suspensos ?? 0)),
      };
    });
    return this.calcularMetas(sim);
  }

  // ============================================================
  // Computed: cenÃ¡rios calculados com meta final
  // ============================================================
  readonly cenariosCalculados = computed<CenarioCalculado[]>(() =>
    this.cenarios().flatMap((c) => {
      if (!c.resposta) return [];
      const resultado = c.resposta.registros;
      const anoRows = resultado.filter((r) => r.data.startsWith(String(ANO_SIM)));
      return [
        {
          ...c,
          resultado,
          anoRows,
          meta1Final: c.resposta.meta1Final,
          meta2Final: c.resposta.meta2Final,
        },
      ];
    }),
  );

  readonly basePronta = computed(() =>
    this.cenarios().some((c) => c.id === 1 && c.resposta !== null),
  );

  readonly mesesDisponiveis = computed(() => {
    const base = this.cenarios().find((c) => c.id === 1)?.resposta;
    return base?.registros.filter((r) => r.data.startsWith(`${ANO_SIM}-`)).map((r) => r.data) ?? [];
  });

  // Computed: dados para o grÃ¡fico de linhas
  readonly dadosGrafico = computed<PontoGrafico[]>(() =>
    this.mesesDisponiveis().map((mes) => {
      const ponto: PontoGrafico = { mes: this.mesLabel(mes) };
      this.cenariosCalculados().forEach((c) => {
        const row = c.resultado.find((r) => r.data === mes);
        ponto[c.nome] = row?.meta1 != null ? parseFloat(row.meta1.toFixed(2)) : null;
      });
      return ponto;
    }),
  );

  // Computed: dados para o grÃ¡fico de barras
  readonly dadosBarras = computed<PontoBarra[]>(() =>
    this.cenariosCalculados().map((c) => ({
      nome: c.nome,
      meta1: c.meta1Final != null ? parseFloat(c.meta1Final.toFixed(2)) : null,
      meta2: c.meta2Final != null ? parseFloat(c.meta2Final.toFixed(2)) : null,
      cor: c.cor,
    })),
  );

  // ============================================================
  // OperaÃ§Ãµes sobre cenÃ¡rios
  // ============================================================
  adicionarCenario(nome: string, alteracoes: AlteracoesCenario, resposta: RespostaSimulacao): void {
    const id = Date.now();
    const cor = CORES_CENARIOS[this.cenarios().length % CORES_CENARIOS.length];
    this.cenarios.update((list) => [...list, { id, nome, alteracoes, cor, resposta }]);
  }
  nomeCenarioExiste(nome: string): boolean {
    const normalizado = nome.trim().toLocaleLowerCase('pt-BR');
    return this.cenarios().some((c) => c.nome.trim().toLocaleLowerCase('pt-BR') === normalizado);
  }

  removerCenario(id: number): void {
    this.cenarios.update((list) => list.filter((c) => c.id !== id));
  }

  // ============================================================
  // encontrar_ajuste_minimo() â€” busca binÃ¡ria
  // ============================================================
  encontrarAjusteMinimo(
    variavel: 'julgados' | 'dessobrestados' | 'suspensos',
    mes: string,
    metaAlvo: number,
    meta: 'meta1' | 'meta2' = 'meta1',
  ): ResultadoOtimizador {
    const testar = (inc: number): number => {
      const res = this.simularCenario({ [mes]: { [variavel]: inc } });
      const rows = res.filter((r) => r.data.startsWith(String(ANO_SIM)));
      const ultimo = rows[rows.length - 1];
      return meta === 'meta2' ? (ultimo?.meta2 ?? 0) : (ultimo?.meta1 ?? 0);
    };
    // resto do mÃ©todo permanece igual...

    const metaAtual = testar(0);

    if (metaAtual >= metaAlvo) {
      return {
        ok: true,
        mensagem: `Meta de ${metaAlvo}% jÃ¡ atingida (${metaAtual.toFixed(2)}%). Nenhum ajuste necessÃ¡rio.`,
        metaAtual: metaAtual.toFixed(2),
        metaResultante: metaAtual.toFixed(2),
        incremento: 0,
      };
    }

    let lo = 0,
      hi = 100000;
    while (testar(hi) < metaAlvo && hi < 10_000_000) hi *= 2;

    for (let i = 0; i < 60; i++) {
      const meio = Math.floor((lo + hi) / 2);
      if (testar(meio) >= metaAlvo) hi = meio;
      else lo = meio;
      if (hi - lo <= 1) break;
    }

    const incNec = hi;
    const metaResult = testar(incNec);
    const varLabel: Record<string, string> = {
      julgados: 'julgamentos',
      dessobrestados: 'dessobrestamentos',
      suspensos: 'suspensÃµes',
    };

    return {
      ok: metaResult >= metaAlvo,
      incremento: incNec,
      metaAtual: metaAtual.toFixed(2),
      metaResultante: metaResult.toFixed(2),
      mensagem: `Para atingir ${metaAlvo}% em ${ANO_SIM}, sÃ£o necessÃ¡rios ${incNec.toLocaleString('pt-BR')} ${varLabel[variavel]} adicionais em ${this.mesLabel(mes)}/${ANO_SIM}.`,
    };
  }

  // ============================================================
  // UtilitÃ¡rios
  // ============================================================
  mesLabel(data: string): string {
    const [, m] = data.split('-');
    return MESES_NOMES[parseInt(m) - 1];
  }

  fmt(v: number | null, dec = 2): string {
    return v == null ? 'â€”' : v.toFixed(dec).replace('.', ',') + '%';
  }

  fmtN(v: number | null): string {
    return v?.toLocaleString('pt-BR') ?? 'â€”';
  }

  corMeta(v: number | null): string {
    if (v == null) return '#92400E';
    if (v >= 100) return '#1F6E3A';
    if (v >= 95) return '#92400E';
    return '#B91C1C';
  }
}
