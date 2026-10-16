# Simulador de Metas CNJ — Angular 17+

## Estrutura de arquivos

```
src/app/
  core/
    models/
      simulador.model.ts        ← interfaces, constantes, tipos
    services/
      dados.service.ts          ← dados históricos das planilhas xlsx
      simulador.service.ts      ← toda a lógica ETL + fórmulas CNJ (Signals)
  features/
    cenarios/
      cenarios.component.ts     ← aba "Cenários" (criação + comparação)
    graficos/
      graficos.component.ts     ← aba "Gráficos" (linha + barras)
    tabela/
      tabela.component.ts       ← aba "Evolução Mensal"
    otimizador/
      otimizador.component.ts   ← aba "Otimizador" (busca binária)
  app.component.ts              ← shell: header + abas + roteamento
  app.config.ts
src/
  main.ts
  index.html
  styles.css
```

## Instalação no projeto existente (meu-primeiro-app)

### 1. Copie os arquivos para o seu projeto
Copie cada arquivo para o caminho correspondente dentro de `src/`.

### 2. Instale o Chart.js (para o gráfico de linhas)
O `index.html` já carrega via CDN. Não é necessário instalar via npm.

### 3. Atualize o app.routes.ts
```typescript
import { Routes } from '@angular/router';
import { AppComponent as SimuladorComponent } from './simulador/app.component'; // ajuste o path

export const routes: Routes = [
  { path: 'simulador', loadComponent: () =>
      import('./features/simulador/app.component').then(m => m.AppComponent) },
  // ... suas rotas existentes
];
```

### 4. Rode o projeto
```cmd
ng serve --port 4200 --open
```

## Mapeamento Python → Angular

| Python (robo_cnj_meta2.py)     | Angular (simulador.service.ts)        |
|-------------------------------|---------------------------------------|
| `calcular_meta1()`            | `calcMeta1()`                         |
| `formula_meta2_ano()`         | `calcMeta2()`                         |
| `calcular_acumulados()`       | Dentro de `calcularMetas()`           |
| `simular_cenario()`           | `simularCenario()`                    |
| `comparar_cenarios()`         | Tabela na aba Cenários                |
| `encontrar_ajuste_minimo()`   | `encontrarAjusteMinimo()` — bisseção  |
| `plotar_meta1_por_cenario()`  | Gráfico de linhas (Chart.js)          |
| `plotar_comparacao_cenarios()`| Gráfico de barras manual              |

## Variáveis editáveis (conforme script Python)
- ✅ julgados
- ✅ dessobrestados  
- ✅ suspensos
- 🔒 novos (fixo — não pode ser alterado)
