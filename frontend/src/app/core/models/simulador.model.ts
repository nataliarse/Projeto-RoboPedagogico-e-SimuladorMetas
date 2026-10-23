// ============================================================
// MODELOS DO SIMULADOR DE METAS CNJ
// ============================================================

export type TipoDado = 'real' | 'forecast';
export type TipoDadoApi = 'real' | 'previsao_sas';

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

/** Registro tal como serializado pelo backend. */
export interface RegistroApi {
  data: string;
  ano: number;
  mes: number;
  novos: number;
  julgados: number;
  dessobrestados: number;
  suspensos: number;
  novos_tipo: TipoDadoApi;
  julgados_tipo: TipoDadoApi;
  novos_acum: number;
  julgados_acum: number;
  dessobrestados_acum: number;
  suspensos_acum: number;
  meta1: number | null;
  meta2: number | null;
}

export interface RespostaSimulacao {
  registros: RegistroCalculado[];
  meta1Final: number | null;
  meta2Final: number | null;
}

export interface RespostaBaseApi {
  registros: RegistroApi[];
  meta1_final: number | null;
  meta2_final: number | null;
}

export interface AlteracaoMes {
  julgados?: number;
  dessobrestados?: number;
  suspensos?: number;
}

export type AlteracoesCenario = Record<string, AlteracaoMes>;

export interface SimularRequest { alteracoes: AlteracoesCenario; }
export interface CompararCenarioRequest { nome: string; alteracoes: AlteracoesCenario; }
export interface CompararRequest { cenarios: CompararCenarioRequest[]; }
export interface CenarioComparadoApi {
  nome: string;
  meta1_final: number | null;
  meta2_final: number | null;
  dif_meta1: number | null;
  dif_meta2: number | null;
  mensal: RegistroApi[];
}
export interface CompararResponse {
  cenarios: CenarioComparadoApi[];
  meta1_base: number | null;
  meta2_base: number | null;
}
export interface OtimizadorRequest {
  variavel: 'julgados' | 'dessobrestados' | 'suspensos';
  mes: string;
  meta_alvo: number;
  meta: 'meta1' | 'meta2';
}
export interface RespostaOtimizador {
  variavel: string;
  mes: string;
  meta_alvo: number;
  meta_atual: number | null;
  incremento_necessario: number | null;
  meta_resultante: number | null;
  mensagem: string;
  ok: boolean;
}

export interface QuantoFaltaRequest {
  meta_alvo: number;
  mes_inicio?: string;
  alteracoes?: AlteracoesCenario;
}

export interface RespostaQuantoFalta {
  ok: boolean;
  ja_atingida: boolean;
  meta_alvo: number;
  meta_atual: number | null;
  meta_resultante: number | null;
  mes_inicio: string;
  meses: string[];
  n_meses: number;
  meses_reais: string[];
  incremento_mensal: number | null;
  total_adicional: number | null;
  julgados_previstos_periodo: number;
  conta: {
    denominador: number | null;
    julgados_acumulados: number;
    julgados_necessarios: number | null;
  };
  mensagem: string;
}

export type TipoRegistroMeta2 = 'real' | 'previsao';
export interface RegistroMeta2 {
  data: string;
  tipo: TipoRegistroMeta2;
  julgados: number;
  suspensos: number;
  dessobrestados: number;
  julgados_acum_2026: number | null;
  dessobrestados_acum_2026: number | null;
  meta2: number | null;
}
export interface ResultadoGrupoMeta2 {
  grupo: 'A' | 'ANT';
  ano: number;
  meta2: number | null;
  distribuidos: number;
  descricao: string;
  formula: string;
}
export interface RespostaMeta2 {
  resultado_2025: Record<'A' | 'ANT', Record<string, number>>;
  resultado_2026: Record<'A' | 'ANT', ResultadoGrupoMeta2>;
  serie_A: RegistroMeta2[];
  serie_ANT: RegistroMeta2[];
}
export interface SimularMeta2Request {
  alteracoes_A: AlteracoesCenario;
  alteracoes_ANT: AlteracoesCenario;
}

export interface Cenario {
  id: number;
  nome: string;
  alteracoes: AlteracoesCenario;
  cor: string;
  resposta: RespostaSimulacao | null;
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
  meta1: number | null;
  meta2: number | null;
  cor: string;
}

export const MESES_NOMES = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
export const ANO_SIM = 2026;
export const MESES_SIM = Array.from({ length: 12 }, (_, i) =>
  `${ANO_SIM}-${String(i + 1).padStart(2, '0')}`
);
export const CORES_CENARIOS = ['#1B4F8A','#1F6E3A','#9333EA','#EA580C','#0891B2','#BE185D'];
