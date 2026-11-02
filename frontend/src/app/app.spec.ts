import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { App } from './app';
import { ApiHealthService } from './core/services/api-health';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideRouter([]),
        {
          provide: ApiHealthService,
          useValue: {
            checkProcessual: () => of({ status: 'ok' }),
            checkSimulator: () => of({ status: 'ok', registros: 86 }),
          },
        },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should host routed content', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('router-outlet')).not.toBeNull();
  });

  it('oferece navegação global para chat e simulador', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const links = Array.from(
      (fixture.nativeElement as HTMLElement).querySelectorAll('nav a'),
    ).map(link => ({ text: link.firstChild?.textContent?.trim(), href: link.getAttribute('href') }));

    expect(links).toEqual([
      { text: 'Chat processual', href: '/' },
      { text: 'Simulador de metas', href: '/simulador' },
    ]);
  });

  it('mantém a navegação fora do conteúdo roteado', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    const navigation = root.querySelector('.app-nav');
    const routedContent = root.querySelector('main');

    expect(navigation).not.toBeNull();
    expect(routedContent).not.toBeNull();
    expect(routedContent?.contains(navigation)).toBe(false);
  });
});
