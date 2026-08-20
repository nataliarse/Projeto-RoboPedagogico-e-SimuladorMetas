# Integração entre o frontend Angular e o backend FastAPI

## Objetivo e escopo positivo

Esta integração existe para conectar duas aplicações existentes por meio de uma
fronteira HTTP estável:

```text
Browser / Angular
        ↓
      HTTP
        ↓
     FastAPI
```

Seu objetivo é permitir que o usuário consuma, pelo frontend existente, as
funcionalidades já existentes e autorizadas do backend. Os detalhes do contrato
HTTP, da estratégia de sessão, de CORS, proxy, DTOs e da topologia alvo serão
definidos na fase P1 e não são antecipados neste documento.

## Princípio de integração conservadora

Esta integração existe para conectar duas aplicações existentes através de uma
fronteira HTTP estável. Ela não constitui autorização para refatoração ampla,
redesign, modernização, expansão de produto ou conclusão de funcionalidades
independentes.

Devem ser preservados ao máximo o comportamento, o layout, as funcionalidades e
a arquitetura existentes. Uma alteração só entra no escopo quando pelo menos
uma das respostas abaixo for positiva:

1. É necessária para Angular e FastAPI funcionarem corretamente?
2. É necessária para evitar erro, regressão, risco de segurança ou comportamento
   incorreto diretamente causado pela integração?
3. É necessária para testar ou documentar de forma confiável a própria
   integração?

Se a resposta for não para todas as perguntas, a alteração está **fora do
escopo**.

## Escopo e não objetivos

As restrições abaixo admitem somente a exceção por dependência comprovada
definida neste documento.

### Frontend

Não fazem parte desta integração:

- alterar layout, redesenhar componentes ou modificar a identidade visual;
- reorganizar CSS por estética, criar animações ou corrigir warnings puramente
  estéticos, como o budget CSS, apenas porque foram encontrados;
- adicionar loading sofisticado apenas por UX, toast, modal ou feedback visual
  que não seja necessário à integração;
- mudar a navegação existente, criar telas ou adicionar funcionalidades;
- completar features ou TODOs preexistentes sem relação direta com a
  integração;
- remodelar o histórico apenas por preferência;
- renomear em massa componentes, arquivos ou o projeto Angular;
- reorganizar services ou components apenas por preferência arquitetural;
- trocar bibliotecas ou frameworks, ou atualizar o Angular sem necessidade
  comprovada.

### Backend

Não fazem parte desta integração:

- refatorar agentes do chatbot ou modificar seu comportamento interno apenas
  por qualidade percebida, sem necessidade da fronteira HTTP;
- reorganizar orquestradores, mudar regras de negócio ou alterar a lógica
  processual existente sem necessidade da integração;
- trocar ou migrar SQLite, Qdrant ou Ollama;
- mudar o modelo de IA apenas para facilitar o frontend;
- reestruturar o RAG ou otimizar um pipeline que já satisfaz o contrato;
- alterar semanticamente respostas sem necessidade do contrato;
- introduzir nova persistência apenas por robustez futura.

### Simulador de metas

Não fazem parte desta integração:

- implementar novas regras do simulador;
- concluir funcionalidades parcialmente desenvolvidas;
- alterar modelos ARIMA ou revisar previsões por oportunidade;
- mudar a lógica de metas sem requisito específico;
- refatorar o simulador como efeito colateral da integração do chat.

O diretório `simulador-de-metas/` só deve ser alterado diante de uma dependência
concreta e demonstrável da integração.

### Infraestrutura e produto

Não devem ser introduzidos automaticamente nesta integração:

- autenticação, autorização ou sistema de usuários;
- deploy ou um novo CI/CD;
- containerização apenas por conveniência;
- infraestrutura ou persistência distribuída de sessão;
- Redis apenas por robustez futura ou qualquer novo banco;
- cloud;
- observabilidade ampla, telemetria, analytics ou monitoramento externo;
- redesign da arquitetura de produção.

Esses assuntos podem ser avaliados futuramente, mediante decisão específica,
mas não pertencem automaticamente à integração atual.

## Dívida técnica encontrada

> Descobrir um problema não constitui autorização para corrigi-lo.

Warnings, TODOs, código antigo, nomes ruins, testes preexistentes quebrados,
dependências desatualizadas, vulnerabilidades npm, refatorações desejáveis e
features parcialmente prontas devem seguir este fluxo:

1. registrar o achado quando relevante;
2. classificar seu impacto sobre a integração;
3. corrigir somente se necessário para concluir a integração com segurança;
4. caso contrário, preservar o comportamento e manter o achado fora do escopo.

Dívida preexistente não deve ser classificada como regressão causada pela
integração.

## Exceção por dependência comprovada

O escopo negativo não impede uma alteração indispensável ao funcionamento da
fronteira HTTP, à segurança da integração, ao isolamento correto de sessão, à
compatibilidade Angular/FastAPI, ao tratamento correto de request e response, à
prevenção de regressão introduzida pela integração, aos testes da integração ou
à sua execução reproduzível.

Toda exceção deve:

1. registrar o motivo;
2. apontar a dependência concreta;
3. aplicar a menor alteração coerente;
4. não expandir o escopo além da necessidade comprovada.

## Exemplos normativos

- O frontend ignora `resultado.resposta` e sempre mostra um mock: deve ser
  alterado, pois impede o uso real do backend.
- Clientes web sem `session_id` compartilham a sessão `default`: pode exigir
  alteração, pois afeta diretamente a correção da integração multiusuário.
- O CSS possui warning de budget: registrar se relevante; não corrigir apenas
  por oportunidade.
- Uma feature frontend está 80% pronta: não completar somente porque o arquivo
  será tocado.
- Um agente Python poderia ser arquiteturalmente mais elegante: não refatorar
  se a API já funciona corretamente.
