// Reconstruído localmente a partir do uso em chat.ts, state.ts e local-storage.ts.
// O arquivo original não está no repositório: a regra `models/` do .gitignore da raiz
// ignora esta pasta. Substituir pelo original quando ele for versionado.

export interface ChatMessage {
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export interface ProcessoConsulta {
  numero_processo: string;
  data_consulta: string;
  resposta_resumo: string;
}
