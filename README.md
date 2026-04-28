# Projeto-RoboPedagogico-e-SimuladorMetas
Repositório para colocar os andamentos/arquivos relacionados à criação do robô pedagógico (Letícia/Natália/Simone/Giuliano/Leonardo) e simulador de metas (Letícia/Natália/Simone/Mateus/Nicole).

Para o RoboPedagogico atenção à lógica abaixo:
1. Arquitetura do Sistema (Pipeline de Execução)
O fluxo de trabalho do seu chatbot deve seguir esta ordem lógica:

Input: O usuário fornece o ID (número do processo).
Recuperação (Retrieval): O bot acessa a fonte (PDF no PJe) e extrai o texto do histórico do ID.
Processamento (LLM + Extração): A IA lê o histórico bruto e extrai os "eventos-chave" (ex: "Protocolo realizado em X", "Despacho proferido em Y").
Mapeamento (Matching): O motor de regras compara esses eventos com o seu fluxograma estático.
Output: O bot responde onde o ID parou no fluxo e qual o próximo passo esperado.

2. Passo a Passo Técnico
Passo 1: Estruturar o Fluxograma 
Transforme seu fluxograma em uma estrutura de Dicionário ou Grafo em Python. Cada etapa deve ter critérios claros.
Técnica: Use a biblioteca NetworkX para criar o grafo ou um arquivo JSON simples.
Exemplo:
    Nó 1: "Petição Inicial" -> Se "Distribuído", vá para Nó 2.
    Nó 2: "Citação" -> Se "Mandado Cumprido", vá para Nó 3.

Passo 2: Extração de Dados do Histórico
Como o histórico pode ser uma "parede de texto" suja, você precisará de um modelo de linguagem (LLM) para atuar como Parser.
Técnica: Few-Shot Prompting. Você dá 2 ou 3 exemplos de históricos e como eles devem ser resumidos em eventos.
Prompt Sugerido: "Dado o histórico abaixo do ID {id}, identifique a última fase concluída e a data da última movimentação relevante."

Passo 3: O "Motor de Inferência"
Para evitar que a IA se perca, você pode usar uma técnica chamada Slot Filling.
O chatbot verifica quais "campos" do seu fluxograma foram preenchidos pelo histórico lido.
Se o histórico diz "Sentença proferida", o bot marca automaticamente as etapas anteriores (Petição, Instrução) como concluídas e posiciona o ID na fase de "Recurso" ou "Trânsito em Julgado".

3. Sugestão de Ferramentas (Stack)
LangGraph (Framework): É a melhor ferramenta atual para isso. Ela permite que você desenhe o "fluxograma" dentro do código e defina que o bot deve seguir exatamente aqueles caminhos, impedindo que ele invente respostas.
Streamlit: Para criar uma interface visual rápida e limpa onde o usuário digita o ID e vê o resultado do fluxograma na tela.

4. Exemplo de Lógica de Prompt para o Bot
"Determine em qual passo o processo se encontra e justifique citando o trecho do histórico."

Ponto de Atenção: Performance
Como você vai ler o histórico na hora em que o usuário pedir, a busca deve ser indexada. Se o histórico estiver em arquivos PDF, você precisará de uma etapa de OCR ou leitura de PDF (como o PyMuPDF) integrada antes da análise.
