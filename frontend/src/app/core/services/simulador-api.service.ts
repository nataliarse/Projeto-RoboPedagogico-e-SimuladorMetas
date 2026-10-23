import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, finalize, map, throwError, timeout } from 'rxjs';
import {
  AlteracaoMes,
  CompararRequest,
  CompararResponse,
  OtimizadorRequest,
  RegistroApi,
  RegistroCalculado,
  RespostaBaseApi,
  RespostaOtimizador,
  QuantoFaltaRequest,
  RespostaQuantoFalta,
  RespostaMeta2,
  SimularMeta2Request,
  RespostaSimulacao,
  SimularRequest,
  TipoDado,
  TipoDadoApi,
} from '../models/simulador.model';
import { HTTP_TIMEOUT_MS } from '../config/http-timeouts';

export class InvalidSimulatorResponseError extends Error {
  constructor() {
    super('A API do simulador retornou uma resposta inválida.');
    this.name = 'InvalidSimulatorResponseError';
  }
}

@Injectable({ providedIn: 'root' })
export class SimuladorApiService {
  private readonly http = inject(HttpClient);
  private readonly API = '/api/simulador';

  carregando = signal(false);
  erro = signal<string | null>(null);

  carregarBase(): Observable<RespostaSimulacao> {
    this.carregando.set(true);
    this.erro.set(null);
    return this.http.get<RespostaBaseApi>(`${this.API}/base`).pipe(
      timeout(HTTP_TIMEOUT_MS.simulatorBase),
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
    const request: SimularRequest = { alteracoes };
    return this.http.post<RespostaBaseApi>(`${this.API}/simular`, request).pipe(
      timeout(HTTP_TIMEOUT_MS.simulatorScenario),
      map((res) => this.paraApresentacao(res)),
      catchError((err) => {
        this.erro.set(this.msg(err));
        return throwError(() => err);
      }),
      finalize(() => this.carregando.set(false)),
    );
  }

  private paraApresentacao(res: RespostaBaseApi): RespostaSimulacao {
    if (!res || !Array.isArray(res.registros)) {
      throw new InvalidSimulatorResponseError();
    }
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
      timeout(HTTP_TIMEOUT_MS.simulatorOptimizer),
      catchError((err) => {
        this.erro.set(this.msg(err));
        return throwError(() => err);
      }),
      finalize(() => this.carregando.set(false)),
    );
  }

  comparar(req: CompararRequest): Observable<CompararResponse> {
    this.carregando.set(true);
    this.erro.set(null);
    return this.http.post<CompararResponse>(`${this.API}/comparar`, req).pipe(
      timeout(HTTP_TIMEOUT_MS.simulatorComparison),
      catchError((err) => {
        this.erro.set(this.msg(err));
        return throwError(() => err);
      }),
      finalize(() => this.carregando.set(false)),
    );
  }

  quantoFalta(req: QuantoFaltaRequest): Observable<RespostaQuantoFalta> {
    return this.request(
      this.http.post<RespostaQuantoFalta>(`${this.API}/meta1/quanto-falta`, req),
      HTTP_TIMEOUT_MS.simulatorEffort,
      (response) => this.validarQuantoFalta(response),
    );
  }

  carregarMeta2(): Observable<RespostaMeta2> {
    return this.request(
      this.http.get<RespostaMeta2>(`${this.API}/meta2/base`),
      HTTP_TIMEOUT_MS.simulatorMeta2,
      (response) => this.validarMeta2(response),
    );
  }

  simularMeta2(req: SimularMeta2Request): Observable<RespostaMeta2> {
    return this.request(
      this.http.post<RespostaMeta2>(`${this.API}/meta2/simular`, req),
      HTTP_TIMEOUT_MS.simulatorMeta2,
      (response) => this.validarMeta2(response),
    );
  }

  private request<T>(source: Observable<T>, timeoutMs: number, validate: (value: T) => T): Observable<T> {
    this.carregando.set(true);
    this.erro.set(null);
    return source.pipe(
      timeout(timeoutMs),
      map(validate),
      catchError((err) => {
        this.erro.set(this.msg(err));
        return throwError(() => err);
      }),
      finalize(() => this.carregando.set(false)),
    );
  }

  private validarQuantoFalta(response: RespostaQuantoFalta): RespostaQuantoFalta {
    if (!response || typeof response.ok !== 'boolean' || !Array.isArray(response.meses)) {
      throw new InvalidSimulatorResponseError();
    }
    return response;
  }

  private validarMeta2(response: RespostaMeta2): RespostaMeta2 {
    if (!response || !Array.isArray(response.serie_A) || !Array.isArray(response.serie_ANT)
      || !response.resultado_2026?.A || !response.resultado_2026?.ANT) {
      throw new InvalidSimulatorResponseError();
    }
    return response;
  }

  private msg(err: unknown): string {
    if (err instanceof InvalidSimulatorResponseError) return err.message;
    if (!(err instanceof HttpErrorResponse)) return 'Falha inesperada no simulador.';
    if (err.status === 0)
      return 'Não foi possível conectar. Verifique se a API está disponível.';
    const detail = err.error?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      const mensagens = detail
        .map((item) => (typeof item?.msg === 'string' ? item.msg : null))
        .filter((item): item is string => item !== null);
      if (mensagens.length) return mensagens.join(' ');
    }
    return `Erro ${err.status}: ${err.statusText || 'solicitação rejeitada'}`;
  }
}
