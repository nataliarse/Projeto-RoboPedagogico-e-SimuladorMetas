# Implantação na AWS

Scripts usados para colocar o Robô Orientador em uma instância EC2 (Ubuntu 22.04,
`t3.medium`). Foram executados nessa ordem e deixam tudo como serviço, de modo que o
sistema volta sozinho quando a instância é ligada.

| Script | O que faz |
|---|---|
| `instalar_robo.sh` | Ambiente Python, coletor (Chromium do Playwright com tela virtual), backend como serviço e nginx servindo a interface na porta 7860 |
| `instalar_ollama.sh` | Ollama, modelos `llama3.2:1b`, `llama3.2:3b` e `nomic-embed-text`, e 2 GB de swap |
| `instalar_qdrant.sh` | Qdrant como serviço e indexação do Glossário das Metas (RAG das normas) |
| `configurar_bedrock_pgvector.sh` | Passa a redação para o Amazon Bedrock (Claude Haiku 4.5) e a busca nas normas para o pgvector do banco da IESB; retira o Simulador de Metas da instância |

O Ollama e o Qdrant continuam instalados como reserva: com `LLM_FALLBACK_OLLAMA=true`, uma falha
do Bedrock recorre ao modelo local; com `NORMAS_BACKEND=qdrant`, a busca volta ao Qdrant.

## Como o código chega à instância

O repositório é privado, então o código é enviado da máquina de desenvolvimento. Os
scripts esperam esta estrutura em `/home/ubuntu/robo`:

```
robo/
├── chatbot_processual_ai/   # backend
├── entrada-de-dados/        # package trt18_collector
└── web/                     # interface compilada (conteúdo de frontend/dist/.../browser)
```

A interface é compilada antes do envio, com `npm run build` na pasta `frontend`.

## Arquitetura na instância

- **nginx (porta 7860):** serve a interface e encaminha `/api/` para o backend, reescrevendo
  `/api/processos/health` para `/api/health`, como o proxy do Angular.
- **chatbot (127.0.0.1:8000):** serviço `robo-backend`, executado com `xvfb-run`, porque o
  coletor abre o navegador com janela e o servidor não tem tela.
- **Amazon Bedrock:** redige as respostas (API Converse, `us.anthropic.claude-haiku-4-5-20251001-v1:0`,
  temperatura 0,2) e gera os embeddings do glossário (`amazon.titan-embed-text-v2:0`, 1024
  dimensões). As regras determinísticas calculam os fatos; o modelo só redige. Cada chamada é
  registrada em `chatbot_processual_ai/data/logs/llm_auditoria.jsonl` (modelo, latência, tokens e
  hash do prompt e da resposta, sem o texto, que pode conter dados pessoais).
- **PostgreSQL com pgvector (`bigdata.dataiesb.com`, banco `iesb`, schema `tcc_leonardo_a_pereira`):**
  tabela `normas` com os trechos do Glossário das Metas 2026 e índice HNSW por cosseno. A senha
  vem do secret `tcc/leonardo-a-pereira/db`, lido com a role da instância.
- **Ollama (127.0.0.1:11434)** e **Qdrant (127.0.0.1:6333):** reserva local, acessíveis só de
  dentro da instância.

## Acesso

A porta 7860 depende de liberação no security group. Sem ela, o acesso é por túnel SSH:

```bash
ssh -i <chave.pem> -N -L 7860:127.0.0.1:7860 ubuntu@<ip-publico>
```

Depois, abrir `http://localhost:7860`. O IP público muda a cada vez que a instância é
ligada.

## Observações

- Com o Bedrock, a redação de uma orientação leva de 1 a 3 segundos; com o modelo local de
  reserva (`llama3.2:3b` em CPU), cerca de um minuto. As respostas calculadas por regras são
  imediatas.
- O Simulador de Metas não faz parte desta implantação.
- O banco SQLite da instância guarda os processos consultados, com nomes e documentos das
  partes. Ele não é versionado.
- Nenhuma credencial faz parte destes scripts. O acesso a S3, Secrets Manager e banco de
  dados, quando usado, vem da *instance role*.
- O egress da instância libera apenas 443, 80, 53 e 5432; por isso o código não é clonado
  por SSH.
