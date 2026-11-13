import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ApiHealthService } from './api-health';

describe('ApiHealthService', () => {
  it('consulta o healthcheck do backend processual', () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const service = TestBed.inject(ApiHealthService);
    const http = TestBed.inject(HttpTestingController);
    let status: string | undefined;

    service.checkProcessual().subscribe(value => status = value.status);
    http.expectOne('/api/processos/health').flush({ status: 'ok' });

    expect(status).toBe('ok');
    http.verify();
  });

  it('propaga a falha quando o backend processual cai', () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const service = TestBed.inject(ApiHealthService);
    const http = TestBed.inject(HttpTestingController);
    let failed = false;

    service.checkProcessual().subscribe({ error: () => failed = true });
    http.expectOne('/api/processos/health').flush(
      { detail: 'offline' }, { status: 503, statusText: 'Unavailable' },
    );

    expect(failed).toBe(true);
    http.verify();
  });
});
