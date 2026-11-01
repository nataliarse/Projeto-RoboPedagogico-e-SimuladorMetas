import { CenarioCalculado, RespostaMeta2 } from '../../core/models/simulador.model';
import { formatarPercentual } from '../../core/services/simulador.service';
import { montarKpisCabecalho } from './simulador-shell.component';

describe('cabeçalho do simulador', () => {
  const meta2: RespostaMeta2 = {
    resultado_2025: { A: { meta: 106.22 }, ANT: { meta: 100 } },
    resultado_2026: {
      A: { grupo: 'A', ano: 2026, meta2: 105.32, distribuidos: 27548, descricao: 'A', formula: 'A' },
      ANT: { grupo: 'ANT', ano: 2026, meta2: 111.11, distribuidos: 72, descricao: 'ANT', formula: 'ANT' },
    },
    reproducao_original_2026: {
      A: { grupo: 'A', ano: 2026, meta2: 104.63, distribuidos: 27548, descricao: 'A', formula: 'A' },
      ANT: { grupo: 'ANT', ano: 2026, meta2: 110, distribuidos: 72, descricao: 'ANT', formula: 'ANT' },
    },
    serie_A: [],
    serie_ANT: [],
  };

  it('mantém Meta 2 A e Meta 2 ANT separadas da Meta 2 agregada', () => {
    const base = { meta1Final: 96.47, meta2Final: 169.68 } as CenarioCalculado;
    expect(montarKpisCabecalho(base, meta2)).toEqual([
      { label: 'Meta 1 Base', valor: 96.47 },
      { label: 'Meta 2 A (CNJ v3 demo.)', valor: 105.32 },
      { label: 'Meta 2 ANT (CNJ v3 demo.)', valor: 111.11 },
    ]);
  });

  it('formata o valor ausente com travessão UTF-8', () => {
    const texto = formatarPercentual(null);
    expect(texto).toBe('—');
    expect(texto).not.toContain('â€');
  });
});
