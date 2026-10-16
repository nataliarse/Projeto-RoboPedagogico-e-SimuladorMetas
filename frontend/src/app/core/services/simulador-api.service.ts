import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, finalize, map, throwError } from 'rxjs';
import {
  AlteracaoMes,
  RegistroApi,
  RegistroCalculado,
  RespostaSimulacao,
  TipoDado,
  TipoDadoApi,
} from '../models/simulador.model';

interface RespostaBaseApi {
  registros: RegistroApi[];
  meta1_final: number | null;
  meta2_final: number | null;
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

export interface OtimizadorRequest {
  variavel: 'julgados' | 'dessobrestados' | 'suspensos';
  mes: string;
  meta_alvo: number;
  meta: 'meta1' | 'meta2';
}

@Injectable({ providedIn: 'root' })
export class SimuladorApiService {
  private readonly http = inject(HttpClient);
  private readonly API = '/api';

  carregando = signal(false);
  erro = signal<string | null>(null);

  carregarBase(): Observable<RespostaSimulacao> {
    this.carregando.set(true);
    this.erro.set(null);
    return this.http.get<RespostaBaseApi>(`${this.API}/base`).pipe(
      map((res) => this.paraApresentacao(res)),
      catchError((err) => {
        this.erro.set(this.msg(err));
        return throwError(() => err);
      }),
      finalize(() => this.carregando.set(false)),
    );
  }

  simular(alteracoes: Record<string, AlteracaoMes>): Observable<RespostaSimulacao> {
    this.carregando.set(true);
    this.erro.set(null);
    return this.http.post<RespostaBaseApi>(`${this.API}/simular`, { alteracoes }).pipe(
      map((res) => this.paraApresentacao(res)),
      catchError((err) => {
        this.erro.set(this.msg(err));
        return throwError(() => err);
      }),
      finalize(() => this.carregando.set(false)),
    );
  }

  private paraApresentacao(res: RespostaBaseApi): RespostaSimulacao {
    return {
      registros: res.registros.map((registro) => this.mapearRegistro(registro)),
      meta1Final: res.meta1_final,
      meta2Final: res.meta2_final,
    };
  }

  private mapearRegistro(registro: RegistroApi): RegistroCalculado {
    return {
      data: registro.data,
      novos: registro.novos,
      julgados: registro.julgados,
      dessobrestados: registro.dessobrestados,
      suspensos: registro.suspensos,
      novos_tipo: this.mapearTipo(registro.novos_tipo),
      julgados_tipo: this.mapearTipo(registro.julgados_tipo),
      novos_acum: registro.novos_acum,
      julgados_acum: registro.julgados_acum,
      dessobrestados_acum: registro.dessobrestados_acum,
      suspensos_acum: registro.suspensos_acum,
      meta1: registro.meta1,
      meta2: registro.meta2,
    };
  }

  private mapearTipo(tipo: TipoDadoApi): TipoDado {
    return tipo === 'previsao_sas' ? 'forecast' : tipo;
  }

  otimizador(req: OtimizadorRequest): Observable<RespostaOtimizador> {
    this.carregando.set(true);
    this.erro.set(null);
    return this.http.post<RespostaOtimizador>(`${this.API}/otimizador`, req).pipe(
      catchError((err) => {
        this.erro.set(this.msg(err));
        return throwError(() => err);
      }),
      finalize(() => this.carregando.set(false)),
    );
  }

  private msg(err: HttpErrorResponse): string {
    if (err.status === 0)
      return 'NÃ£o foi possÃ­vel conectar. Verifique se a API estÃ¡ disponÃ­vel.';
    const detail = err.error?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      const mensagens = detail
        .map((item) => (typeof item?.msg === 'string' ? item.msg : null))
        .filter((item): item is string => item !== null);
      if (mensagens.length) return mensagens.join(' ');
    }
    return `Erro ${err.status}: ${err.statusText || 'solicitaÃ§Ã£o rejeitada'}`;
  }
}
