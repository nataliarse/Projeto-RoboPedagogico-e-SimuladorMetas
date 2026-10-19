import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface ApiHealthResponse {
  status: 'ok';
}

export interface SimulatorHealthResponse extends ApiHealthResponse {
  registros: number;
}

@Injectable({ providedIn: 'root' })
export class ApiHealthService {
  private http = inject(HttpClient);

  check(): Observable<ApiHealthResponse> {
    return this.checkProcessual();
  }

  checkProcessual(): Observable<ApiHealthResponse> {
    return this.http.get<ApiHealthResponse>('/api/processos/health');
  }

  checkSimulator(): Observable<SimulatorHealthResponse> {
    return this.http.get<SimulatorHealthResponse>('/api/simulador/health');
  }
}
