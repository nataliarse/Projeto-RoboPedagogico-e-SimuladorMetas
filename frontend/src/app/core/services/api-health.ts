import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface ApiHealthResponse {
  status: 'ok';
}

@Injectable({ providedIn: 'root' })
export class ApiHealthService {
  private http = inject(HttpClient);

  check(): Observable<ApiHealthResponse> {
    return this.http.get<ApiHealthResponse>('/api/health');
  }
}
