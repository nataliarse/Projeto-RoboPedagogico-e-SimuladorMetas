import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ApiHealthService } from './api-health';

describe('ApiHealthService', () => {
  it('mantém healthchecks independentes quando um backend cai', () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const service = TestBed.inject(ApiHealthService);
    const http = TestBed.inject(HttpTestingController);
    let processualFailed = false;
    let simulatorRecords: number | undefined;

    service.checkProcessual().subscribe({ error: () => processualFailed = true });
    service.checkSimulator().subscribe(value => simulatorRecords = value.registros);
    http.expectOne('/api/processos/health').flush(
      { detail: 'offline' }, { status: 503, statusText: 'Unavailable' },
    );
    http.expectOne('/api/simulador/health').flush({ status: 'ok', registros: 86 });

    expect(processualFailed).toBe(true);
    expect(simulatorRecords).toBe(86);
    http.verify();
  });
});
