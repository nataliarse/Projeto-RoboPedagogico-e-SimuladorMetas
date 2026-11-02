# Pipeline interno de OCR do CAPTCHA

Este diretório contém apenas as etapas internas de tratamento, segmentação e
leitura OCR reutilizadas por `../decifra_coleta.py`. Ele não é um aplicativo
independente e não possui ponto de entrada, manifesto de dependências ou fluxo
de coleta próprios.

## Fonte de verdade operacional

O fluxo atual de coleta está em `../../coletor_trt18.py` e é exposto por
`../../servico.py` e `../../app.py`. As dependências Python são mantidas em
`../../../chatbot_processual_ai/requirements.txt`; instruções de ambiente e uso
estão em `../../../README.md`, `../../../docs/development.md` e
`../../../docs/data-ingestion.md`.

Não crie um ambiente ou instale navegadores a partir deste diretório. A
instalação e a validação de browsers Playwright pertencem ao setup consolidado
do projeto.

## Componentes

- `decifra.py`: coordena preparação, segmentação e leitura.
- `prepara_leitura.py`: prepara e recorta a imagem.
- `segmenta_chars.py`: separa as posições dos caracteres.
- `remove_ruido.py`: aplica a limpeza dos recortes.
- `leitura_ddddocr.py`: executa o OCR e normaliza o caractere reconhecido.

O processamento depende de autorização institucional e não deve ser usado para
contornar bloqueios, limites ou mecanismos de segurança do portal.
