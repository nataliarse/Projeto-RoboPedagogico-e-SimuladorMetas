# Coleta e decifracao de captcha

Projeto em Python para abrir a consulta processual, capturar a imagem do captcha,
tratar a imagem, decifrar os caracteres com OCR e preencher o campo automaticamente.

## Como Rodar

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Se nao houver Chrome ou Edge instalado nos caminhos padrao do Windows, instale os
navegadores do Playwright:

```powershell
playwright install
```

Execute o sistema usando o processo padrao configurado no codigo:

```powershell
python .\main.py
```

Ou informe um numero de processo no formato CNJ, com ou sem pontuacao:

```powershell
python .\main.py 0011000-82.1981.5.18.0051
```

## Como Funciona

O arquivo `main.py` funciona como orquestrador. Ele recebe o numero do processo e
chama o fluxo de raspagem em `raspagem_dados.py`.

O fluxo abre o navegador com Playwright, acessa a URL de consulta, captura a imagem
do captcha em base64, salva temporariamente como `img_captured.png` e envia essa
imagem para o decifrador.

A decifracao fica concentrada em `decifra_coleta.py` e no diretorio `DCF_CODE`.
O pipeline prepara a imagem antes do OCR: remove parte da pixelacao, aumenta a
legibilidade, recorta a faixa onde os caracteres aparecem e divide o captcha em
6 recortes menores, um para cada caractere esperado.

Depois disso, cada recorte e enviado separadamente para o `ddddocr`. O resultado
final e montado juntando a leitura individual de cada posicao. Ao final do uso, a
imagem temporaria `img_captured.png` e removida.

Se o captcha preenchido nao for aceito, o navegador e fechado completamente e uma
nova tentativa e feita. O limite atual e de 5 tentativas; se nenhuma funcionar, o
sistema exibe no terminal que nao foi possivel acessar.

## Bibliotecas e Decisoes Tecnicas

### Playwright

O Playwright foi usado para automatizar o navegador, abrir a pagina de consulta,
capturar a imagem do captcha e preencher o campo com o texto decifrado. Ele permite
controlar o navegador real de forma estavel e observar eventos da pagina, como
requests contendo imagens em base64.

### OpenCV e NumPy

O OpenCV, junto com NumPy, foi usado para o processamento da imagem. A decisao veio
do padrao observado no captcha: os caracteres tinham posicoes relativamente fixas,
a quantidade de caracteres era fixa e existia ruido visual que atrapalhava a leitura
direta.

Por isso, a abordagem foi separar o tratamento em etapas:

- reduzir pixelacao e ruido;
- melhorar contraste e nitidez;
- recortar a parte util da imagem;
- dividir a imagem final em 6 partes, uma para cada caractere;
- tentar extrair apenas um elemento por quadro.

Essa estrategia melhorou bastante a qualidade da leitura, porque o OCR deixou de
tentar interpretar a imagem inteira com ruido e passou a receber pequenos recortes
mais limpos e previsiveis.

### ddddocr

O `ddddocr` foi escolhido para a etapa final de OCR. Testes com OCR mais generico
tiveram resultado inferior. O Docling chegou a apresentar um resultado um pouco
melhor em alguns cenarios, mas ainda sofria com os ruidos presentes na imagem.

Com a imagem tratada e segmentada em caracteres individuais, o `ddddocr` teve o
melhor resultado para esse caso, principalmente porque cada entrada enviada para
ele ja estava mais simples e focada em apenas um caractere.

## Estrutura

```text
.
|-- main.py
|-- raspagem_dados.py
|-- decifra_coleta.py
|-- requirements.txt
|-- README.md
`-- DCF_CODE/
    |-- decifra.py
    |-- leitura_ddddocr.py
    |-- prepara_leitura.py
    |-- remove_ruido.py
    `-- segmenta_chars.py
```

### Arquivos principais

- `main.py`: ponto de entrada do sistema e orquestrador geral.
- `raspagem_dados.py`: abre o navegador, acessa a consulta, captura o captcha,
  preenche o campo e controla as tentativas.
- `decifra_coleta.py`: adapta a imagem capturada para o pipeline de OCR e remove
  a imagem temporaria depois do uso.
- `DCF_CODE/decifra.py`: coordena o pipeline interno de tratamento, segmentacao e
  OCR.
- `DCF_CODE/prepara_leitura.py`: trata a imagem, reduz ruido, melhora leitura e
  gera o recorte util.
- `DCF_CODE/segmenta_chars.py`: divide a imagem recortada em 6 caracteres.
- `DCF_CODE/remove_ruido.py`: aplica limpeza adicional nos recortes.
- `DCF_CODE/leitura_ddddocr.py`: executa a leitura OCR com `ddddocr` e normaliza o
  texto final.
