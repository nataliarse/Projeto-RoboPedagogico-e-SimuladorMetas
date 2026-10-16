// ============================================================
// MODELOS DO SIMULADOR DE METAS CNJ
// ============================================================

export type TipoDado = 'real' | 'forecast';

export interface RegistroBase {
  data: string; // 'YYYY-MM'
  novos: number;
  julgados: number;
  dessobrestados: number;
  suspensos: number;
  novos_tipo: TipoDado;
  julgados_tipo: TipoDado;
}

export interface RegistroCalculado extends RegistroBase {
  novos_acum: number;
  julgados_acum: number;
  dessobrestados_acum: number;
  suspensos_acum: number;
  meta1: number | null;
  meta2: number | null;
}

export interface AlteracaoMes {
  julgados?: number;
  dessobrestados?: number;
  suspensos?: number;
}

export type AlteracoesCenario = Record<string, AlteracaoMes>;

export interface Cenario {
  id: number;
  nome: string;
  alteracoes: AlteracoesCenario;
  cor: string;
}

export interface CenarioCalculado extends Cenario {
  resultado: RegistroCalculado[];
  anoRows: RegistroCalculado[];
  meta1Final: number | null;
  meta2Final: number | null;
}

export interface ResultadoOtimizador {
  ok: boolean;
  mensagem: string;
  incremento?: number;
  metaAtual?: string;
  metaResultante?: string;
}

export interface PontoGrafico {
  mes: string;
  [cenario: string]: number | string | null;
}

export interface PontoBarra {
  nome: string;
  meta1: number;
  meta2: number;
  cor: string;
}

export const MESES_NOMES = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
export const ANO_SIM = 2026;
export const MESES_SIM = Array.from({ length: 12 }, (_, i) =>
  `${ANO_SIM}-${String(i + 1).padStart(2, '0')}`
);
export const CORES_CENARIOS = ['#1B4F8A','#1F6E3A','#9333EA','#EA580C','#0891B2','#BE185D'];
