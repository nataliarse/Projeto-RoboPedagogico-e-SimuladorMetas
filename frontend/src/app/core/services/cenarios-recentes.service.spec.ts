import { TestBed } from '@angular/core/testing';
import { CenariosRecentesService } from './cenarios-recentes.service';

describe('CenariosRecentesService', () => {
  beforeEach(() => { localStorage.clear(); TestBed.resetTestingModule(); });
  it('deduplica, remove zeros e limita cada meta aos três mais recentes', () => {
    const service = TestBed.inject(CenariosRecentesService);
    service.salvarMeta1('A', { '2026-03': { julgados: 0 } });
    service.salvarMeta1('B', { '2026-03': { julgados: 1 } });
    service.salvarMeta1('C', { '2026-03': { julgados: 2 } });
    service.salvarMeta1('D', { '2026-03': { julgados: 3 } });
    service.salvarMeta1('D novamente', { '2026-03': { julgados: 3 } });
    expect(service.meta1()).toHaveLength(3);
    expect(service.meta1()[0].nome).toBe('D novamente');
    expect(service.meta1().some(item => item.nome === 'D')).toBe(false);
  });
  it('restaura, limpa e tolera armazenamento indisponível', () => {
    localStorage.setItem('simulador_recentes_meta2', JSON.stringify([{ nome:'ANT', grupo:'ANT', alteracoes:{}, criadoEm:'x' }]));
    const service = new CenariosRecentesService();
    expect(service.meta2()[0].grupo).toBe('ANT');
    service.limparMeta2(); expect(service.meta2()).toEqual([]);
    const spy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('bloqueado'); });
    expect(() => service.salvarMeta1('offline', {})).not.toThrow(); spy.mockRestore();
  });
});
