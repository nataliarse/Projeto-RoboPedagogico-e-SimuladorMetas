# Comparação e otimizador

Os contratos `POST /api/simulador/comparar` e `POST /api/simulador/otimizador` estão
tipados e testados no cliente Angular. Ambos chegam ao backend do simulador pela porta
8001 por meio do proxy canônico.

Na interface mais recente recebida:

- a comparação visual é calculada a partir das respostas individuais de `/simular`;
  portanto o componente não chama `/comparar`;
- a aba “Otimizador (pendente)” permanece desabilitada e o componente transportado
  ainda não é instanciado pelo shell.

Essa lacuna visual é preservada deliberadamente: habilitar funcionalidades que o
snapshot marcava como pendentes mudaria seu comportamento. O cliente e o backend ficam
cobertos e prontos para uma decisão futura, sem apresentar recursos incompletos ao
usuário.
