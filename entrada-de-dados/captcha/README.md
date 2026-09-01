# Módulo de resolução de CAPTCHA — código reaproveitado

**Autoria original: Filipe Campos** (`feat/captcha-ocr-pipeline`).

Os arquivos desta pasta (`decifra_coleta.py` e `DCF_CODE/`) são uma **cópia** do
pipeline de OCR de CAPTCHA desenvolvido pelo Filipe e disponível na branch
`feat/captcha-ocr-pipeline` deste mesmo repositório, onde vivem na raiz do
projeto.

A cópia existe apenas para que o módulo de entrada de dados rode de forma
autônoma durante o desenvolvimento. **Na integração das branches, esta pasta
deve ser removida** e o import passa a apontar para a versão única do pipeline
de CAPTCHA, evitando duplicação de código.

Nenhuma alteração de lógica foi feita nos arquivos originais. O único ajuste
aplicado está **fora** desta pasta, em `coletor_trt18.py`
(`_corrigir_cv2_para_caminhos_unicode`), que corrige em tempo de execução a
leitura/escrita de imagens pelo OpenCV em caminhos com acentos no Windows —
sem modificar o código do Filipe.

## Nota de uso responsável

Conforme a proposta técnica do projeto, o uso de `ddddocr` e do processamento de
imagem depende de **autorização institucional** e não deve servir para burlar
mecanismos de segurança ou barreiras de acesso. O portal do TRT18 aplica limite
de consultas; respeite-o (ver README principal).
