import pandas as pd
import numpy as np
from functools import reduce
import os
import re
import unicodedata

# ============================================================
# CONFIGURAÇÕES DO SIMULADOR
# ============================================================

# Meta oficial do CNJ
META_ALVO = 100.0

# Ano utilizado nas simulações
ANO_SIMULACAO = 2026

# Casos novos nunca poderão ser alterados pelo usuário
CASOS_NOVOS_FIXOS = True


# Último mês com dados observados
DATA_CORTE_REAL = pd.Timestamp("2026-02-01")

DATA_FINAL_SIMULACAO = pd.Timestamp("2027-02-01")


# ============================================================
# VARIÁVEIS DO SIMULADOR
# ============================================================

# Variáveis existentes na base
VARIAVEIS = [
    "novos",
    "julgados",
    "dessobrestados",
    "suspensos"
]

# Variáveis que o usuário poderá alterar
VARIAVEIS_EDITAVEIS = [
    "julgados",
    "dessobrestados",
    "suspensos"
]

# ============================================================
# ARQUIVOS
# ============================================================

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

ARQ_NOVOS = os.path.join(PASTA_SCRIPT, "casos_novos.xlsx")
ARQ_BAIXADOS = None
ARQ_JULGADOS = os.path.join(PASTA_SCRIPT, "julgados.xlsx")
ARQ_DESSOBRESTADOS = os.path.join(PASTA_SCRIPT, "dessobrestados.xlsx")
ARQ_SUSPENSOS = os.path.join(PASTA_SCRIPT, "suspensos.xlsx")

# Evita que o Matplotlib tente gravar o cache fora da pasta do projeto.
os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(PASTA_SCRIPT, ".matplotlib")
)



# ============================================================
# 1B. LEITURA "INTELIGENTE" DE ARQUIVO  >>> NOVO
# Dois dos arquivos (.xlsx) foram salvos com o conteúdo de CSV
# colado numa única coluna. Esta função detecta isso e conserta
# automaticamente. Continua funcionando normalmente para .csv
# e para .xlsx "normais" (como os de dessobrestados/suspensos).
# ============================================================

def ler_arquivo(caminho):
    ext = os.path.splitext(caminho)[1].lower()

    if ext == ".csv":
        return pd.read_csv(caminho)

    df = pd.read_excel(caminho)

    # Caso "quebrado": uma única coluna cujo cabeçalho contém vírgulas
    # (indica que o CSV inteiro foi colado dentro de uma coluna).
    if df.shape[1] == 1 and "," in str(df.columns[0]):
        colunas = str(df.columns[0]).split(",")
        linhas = df.iloc[:, 0].astype(str).str.split(",", expand=True)
        linhas.columns = colunas
        for c in linhas.columns:
            if c not in ("data_oficial", "data_referencia"):
                linhas[c] = pd.to_numeric(linhas[c], errors="coerce")
        return linhas

    return df


# ============================================================
# 2. CONVERSÃO DE DATAS
# Aceita formatos:
# 01M2020, 02M2020...
# JAN2020, FEB2020...
# 2020-01-01
# ============================================================

def converter_data(data):
    # >>> NOVO: se já vier como Timestamp real, só normaliza pro dia 1
    if isinstance(data, pd.Timestamp):
        return pd.Timestamp(data.year, data.month, 1)

    data = str(data).strip().upper()

    # >>> NOVO: datas reais que viraram texto, ex: '2020-01-01 00:00:00'
    if "-" in data:
        ts = pd.Timestamp(data)
        return pd.Timestamp(ts.year, ts.month, 1)

    meses_ingles = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
        "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
        "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
    }

    # Formato 01M2020
    if "M" in data and data[:2].isdigit():
        mes = int(data.split("M")[0])
        ano = int(data.split("M")[1])
        return pd.Timestamp(ano, mes, 1)

    # Formato JAN2020
    mes_txt = data[:3]
    ano = int(data[3:])
    mes = meses_ingles[mes_txt]

    return pd.Timestamp(ano, mes, 1)


# ============================================================
# 3. CARREGAR NOVOS E BAIXADOS
# Essas bases têm:
# valor real + FORECAST
# ============================================================

def carregar_base_forecast(caminho, variavel, col_data="data_oficial", col_valor=None):
    if caminho is None:
        return None

    df = ler_arquivo(caminho)

    if col_valor is None:
        col_valor = variavel

    df["data"] = df[col_data].apply(converter_data)

    df[f"{variavel}_real"] = df[col_valor]
    df[f"{variavel}_forecast"] = df["FORECAST"] if "FORECAST" in df.columns else np.nan

    # Usa o valor real quando existe.
    # Quando o real está vazio, usa a previsão.
    df[variavel] = df[f"{variavel}_real"].combine_first(df[f"{variavel}_forecast"])

    df[f"{variavel}_tipo"] = np.where(
        df[f"{variavel}_real"].notna(),
        "real",
        "previsao_sas"
    )

    colunas = [
        "data",
        variavel,
        f"{variavel}_real",
        f"{variavel}_forecast",
        f"{variavel}_tipo",
        "STD",
        "L95",
        "U95",
        "RESIDUAL"
    ]

    colunas = [c for c in colunas if c in df.columns]

    return df[colunas]


# ============================================================
# 4. CARREGAR JULGADOS
# A base de julgados veio só com data_oficial e julgados.
# Ela já tem real + previsão na mesma coluna.
# ============================================================

def carregar_julgados(caminho, corte_real=DATA_CORTE_REAL):
    df = ler_arquivo(caminho)

    df["data"] = df["data_oficial"].apply(converter_data)

    

    df["julgados_real"] = np.where(
        df["data"] <= corte_real,
        df["julgados"],
        np.nan
    )

    df["julgados_forecast"] = np.where(
        df["data"] > corte_real,
        df["julgados"],
        np.nan
    )

    df["julgados_tipo"] = np.where(
        df["data"] <= corte_real,
        "real",
        "previsao_sas"
    )

    return df[
        [
            "data",
            "julgados",
            "julgados_real",
            "julgados_forecast",
            "julgados_tipo"
        ]
    ]


# ============================================================
# 5. CARREGAR AS CINCO BASES
# >>> AJUSTADO: dessobrestados/suspensos usam col_data e
# col_valor diferentes; baixados fica None (arquivo ausente).
# ============================================================

novos = carregar_base_forecast(ARQ_NOVOS, "novos", col_data="data_oficial")
baixados = carregar_base_forecast(ARQ_BAIXADOS, "baixados") if ARQ_BAIXADOS else None
julgados = carregar_julgados(ARQ_JULGADOS)
dessobrestados = carregar_base_forecast(
    ARQ_DESSOBRESTADOS, "dessobrestados",
    col_data="data_referencia", col_valor="qtd_eventos_dessobrestamento"
)
suspensos = carregar_base_forecast(
    ARQ_SUSPENSOS, "suspensos",
    col_data="data_referencia", col_valor="suspensos"
)


# ============================================================
# 6. CONSOLIDAR EM UMA BASE SÓ
# ============================================================

def consolidar_bases(*bases):

    bases_validas = [b for b in bases if b is not None]

    base = reduce(
        lambda esquerda, direita:
            pd.merge(
                esquerda,
                direita,
                on="data",
                how="outer"
            ),
        bases_validas
    )

    base = (
        base
        .sort_values("data")
        .reset_index(drop=True)
    )

    # Garante existência da coluna baixados
    if "baixados" not in base.columns:
        base["baixados"] = np.nan

    # apenas o período da simulação
    base = base[
        base["data"] <= pd.Timestamp("2027-02-01")
    ].copy()

    # Variáveis que podem ser nulas
    for coluna in ["dessobrestados","suspensos","novos","julgados"]:

        if coluna not in base.columns:
            raise ValueError(f"A coluna '{coluna}' não foi encontrada.")

        if base[coluna].isna().any():
            raise ValueError(f"A coluna '{coluna}' possui valores nulos.")
        

    base["ano"] = base["data"].dt.year
    base["mes"] = base["data"].dt.month

    return base


base = consolidar_bases(
    novos,
    baixados,
    julgados,
    dessobrestados,
    suspensos
)


# ============================================================
# 7. CONFERÊNCIA
# ============================================================

def conferir_base(base):

    print("="*60)
    print("BASE CONSOLIDADA")
    print("="*60)

    print(base.head())

    print("\nÚltimos registros")
    print(base.tail())

    print("\nPeríodo")

    print(base["data"].min())
    print(base["data"].max())

    print("\nQuantidade de registros")

    print(len(base))

    print("Data inicial:", base["data"].min())
    print("Data final:", base["data"].max())

    print("\nValores ausentes:")
    print(base[["novos", "baixados", "julgados","dessobrestados","suspensos"]].isna().sum())

conferir_base(base)




# ============================================================
# 7. VALIDAÇÃO
# ============================================================
def validar_base(base):

    obrigatorias = [
        "novos",
        "julgados",
        "dessobrestados",
        "suspensos"
    ]

    for coluna in obrigatorias:

        if base[coluna].isna().any():

            raise ValueError(
                f"A coluna '{coluna}' possui valores ausentes."
            )

# ============================================================
# 8. FÓRMULA DA META 1 (OFICIAL CNJ)
# ============================================================

def calcular_meta1(novos, julgados, dessobrestados, suspensos, piso_denominador=None):
    """
    Fórmula OFICIAL da Meta 1 — CNJ (extraída do código R oficial).
    Meta 1 = julgados / (novos + dessobrestados - suspensos) * 100

    Parâmetros:
    - novos (cnm1): casos novos do mês
    - julgados (julgadom1): casos julgados do mês
    - baixados: casos baixados do mês (não usado na fórmula, mantido por completude)
    - dessobrestados (desm1): processos dessobrestados do mês
    - suspensos (susm1): processos suspensos do mês

    Retorna NaN quando:
    - denominador (novos + dessobrestados - suspensos) == 0 ou nulo
    - julgados é nulo
    """
    denominador = novos + dessobrestados - suspensos
    if denominador is None or pd.isna(denominador) or denominador == 0:
        return np.nan

    if piso_denominador is None:
        piso_denominador = max(novos + dessobrestados, 1)

    denominador = max(denominador, piso_denominador)
    
    if julgados is None or pd.isna(julgados):
        return np.nan
    return (julgados / denominador) * 100


#  # ============================================================
# CÁLCULO DOS ACUMULADOS ANUAIS
# ============================================================

def calcular_acumulados(df):
    """
    Calcula os acumulados anuais necessários para as Metas 1 e 2.

    O acumulado é reiniciado automaticamente no início de cada ano.

    Para a Meta 2, "distribuídos" utiliza a série de casos novos,
    conforme orientação recebida para este teste.
    """

    resultado = df.copy()

    resultado = (
        resultado
        .sort_values("data")
        .reset_index(drop=True)
    )

    resultado["ano"] = resultado["data"].dt.year

    # Casos novos acumulados
    resultado["novos_acum"] = (
        resultado
        .groupby("ano")["novos"]
        .cumsum()
    )

    # Meta 2: distribuídos = casos novos.
    resultado["distribuidos"] = resultado["novos"]
    resultado["distribuidos_acum"] = resultado["novos_acum"]

    # Julgados acumulados
    resultado["julgados_acum"] = (
        resultado
        .groupby("ano")["julgados"]
        .cumsum()
    )

    # Dessobrestados acumulados
    resultado["dessobrestados_acum"] = (
        resultado
        .groupby("ano")["dessobrestados"]
        .cumsum()
    )

    # Suspensos acumulados
    resultado["suspensos_acum"] = (
        resultado
        .groupby("ano")["suspensos"]
        .cumsum()
    )

    return resultado

# ============================================================
# CÁLCULO DA META 1 ACUMULADA
# ============================================================

def calcular_meta_acumulada(df):
    """
    Calcula as Metas 1 e 2 mês a mês.

    Meta 1 usa os acumulados anuais já existentes no código recebido.

    Meta 2 usa:
    - julgados acumulados no ano;
    - distribuídos acumulados no ano (casos novos);
    - suspensos do mês corrente, tratados como estoque, e não como
      fluxo a ser somado novamente a cada mês.
    """

    resultado = calcular_acumulados(df)

    resultado["meta1"] = resultado.apply(
        lambda linha: calcular_meta1(
            julgados=linha["julgados_acum"],
            novos=linha["novos_acum"],
            dessobrestados=linha["dessobrestados_acum"],
            suspensos=linha["suspensos_acum"]
        ),
        axis=1
    )

    resultado["meta1"] = resultado["meta1"].round(2)

    resultado["meta2_denominador"] = (
        resultado["distribuidos_acum"] - resultado["suspensos"]
    )

    resultado["meta2"] = resultado.apply(
        lambda linha: formula_meta2_ano(
            julgm2a=linha["julgados_acum"],
            dism2a=linha["distribuidos_acum"],
            susm2a=linha["suspensos"]
        ),
        axis=1
    ).round(2)

    resultado["meta2_acima_95"] = resultado["meta2"].ge(95).fillna(False)
    resultado["meta2_status"] = np.select(
        [
            resultado["meta2"].isna(),
            resultado["meta2"] >= META_ALVO,
            resultado["meta2"] >= 95
        ],
        [
            "não calculável (denominador <= 0)",
            "cumprida (>= 100%)",
            "acima de 95%, abaixo de 100%"
        ],
        default="abaixo de 95%"
    )

    return resultado


# ------------------------------------------------------------
# META 2 — Fórmula do ano corrente
# ------------------------------------------------------------

def formula_meta2_ano(julgm2a: float, dism2a: float, susm2a: float) -> float:
    """
    Meta 2 (ano corrente), conforme fórmula já documentada no
    código recebido:

        Meta 2 = julgm2a / (dism2a - susm2a) * (1000 / 9.4)

    Neste teste, dism2a corresponde aos casos novos acumulados.

    A condição ``denominador <= 0`` é necessária porque, nos
    primeiros meses, o estoque de suspensos pode superar os casos
    novos acumulados. Nessa situação não existe percentual válido;
    retornar um número negativo esconderia a inconsistência.
    """
    denominador = dism2a - susm2a

    if (
        denominador is None
        or pd.isna(denominador)
        or denominador <= 0
    ):
        return np.nan

    if julgm2a is None or pd.isna(julgm2a):
        return np.nan

    return (julgm2a / denominador) * (1000 / 9.4)

# A fórmula da Meta 2 para processos antigos continua fora do cálculo.
# As bases recebidas não separam julgados, distribuídos, suspensos e
# dessobrestados pertencentes especificamente à coorte de processos
# antigos; usar os totais gerais nessa fórmula produziria um indicador
# sem correspondência metodológica.


# ============================================================
# SIMULAÇÃO
# ============================================================

def simular_cenario(df, alteracoes):
    """
    Aplica alterações em um ou mais meses e devolve uma nova base.

    As alterações são incrementais.

    Exemplo:

    {
        "2026-10": {"julgados":100},
        "2026-11": {"suspensos":-20}
    }
    """

    simulado = df.copy()

    for periodo, variaveis in alteracoes.items():

        data = pd.Timestamp(periodo + "-01")

        mascara = simulado["data"] == data

        if not mascara.any():
            continue

        for variavel, incremento in variaveis.items():

            # Casos novos nunca podem ser alterados
            if CASOS_NOVOS_FIXOS and variavel == "novos":
                continue

            if variavel not in VARIAVEIS_EDITAVEIS:
                continue

            simulado.loc[mascara, variavel] += incremento

            # Evita valores negativos
            simulado.loc[
                mascara,
                variavel
            ] = simulado.loc[
                mascara,
                variavel
            ].clip(lower=0)

    return calcular_meta_acumulada(simulado)


# ============================================================
# EXEMPLO DE TESTE DA SIMULAÇÃO
# ============================================================

'''
cenario = {
    "2026-10": {
        "julgados": 100
    }
}

resultado = simular_cenario(base, cenario)

print("\n===== TESTE DA SIMULAÇÃO =====")

print(
    resultado.loc[
        resultado["data"] == pd.Timestamp("2026-10-01"),
        [
            "data",
            "julgados",
            "julgados_acum",
            "meta1"
        ]
    ]
)
'''

# ============================================================
# CRIAR CENÁRIO
# ============================================================

def criar_cenario(nome, alteracoes):
    """
    Cria um cenário de simulação.

    Exemplo
    -------
    criar_cenario(
        "Força-tarefa Outubro",
        {
            "2026-10": {
                "julgados": 200
            }
        }
    )
    """

    return {
        "nome": nome,
        "alteracoes": alteracoes
    }


# ============================================================
# EXECUTAR CENÁRIOS
# ============================================================

def executar_cenarios(base, cenarios):
    """
    Executa todos os cenários e devolve um dicionário contendo:

    - Resultado completo
    - Metas 1 e 2 finais
    - Alterações realizadas
    """

    resultados = {}

    for cenario in cenarios:

        nome = cenario["nome"]
        alteracoes = cenario["alteracoes"]

        resultado = simular_cenario(
            base,
            alteracoes
        )

        # Metas do último mês disponível no ano da simulação.
        ultima_linha_ano = resultado.loc[
            resultado["ano"] == ANO_SIMULACAO
        ].iloc[-1]

        meta1_final = ultima_linha_ano["meta1"]
        meta2_final = ultima_linha_ano["meta2"]

        resultados[nome] = {

            "resultado": resultado,

            # Mantido para compatibilidade com as funções antigas.
            "meta_final": meta1_final,

            "meta1_final": meta1_final,

            "meta2_final": meta2_final,

            "meta2_status": ultima_linha_ano["meta2_status"],

            "alteracoes": alteracoes

        }

    return resultados

# ============================================================
# COMPARAR CENÁRIOS
# ============================================================

def comparar_cenarios(resultados):
    """
    Gera uma tabela comparando Meta 1 e Meta 2 em todos os cenários.
    """

    comparacao = []

    if "Base" not in resultados:
        raise ValueError(
            "comparar_cenarios() espera um cenário chamado 'Base' "
            "dentro de `resultados` (use criar_cenario('Base', {}) "
            "e inclua-o na lista passada para executar_cenarios())."
        )

    meta1_base = resultados["Base"]["meta1_final"]
    meta2_base = resultados["Base"]["meta2_final"]

    for nome, dados in resultados.items():

        meta1 = dados["meta1_final"]
        meta2 = dados["meta2_final"]

        diferenca_meta2 = (
            np.nan
            if pd.isna(meta2) or pd.isna(meta2_base)
            else round(meta2 - meta2_base, 2)
        )

        comparacao.append({

            "Cenário": nome,

            "Meta 1 Final (%)": round(meta1, 2),

            "Dif. Meta 1 para Base (p.p.)": round(
                meta1 - meta1_base, 2
            ),

            "Meta 2 Final (%)": (
                np.nan if pd.isna(meta2) else round(meta2, 2)
            ),

            "Dif. Meta 2 para Base (p.p.)": diferenca_meta2,

            "Meta 2 > 95%": bool(not pd.isna(meta2) and meta2 > 95),

            "Status Meta 2": dados["meta2_status"],

            # Colunas antigas mantidas para os gráficos da Meta 1.
            "Meta Final (%)": round(meta1, 2),

            "Diferença para Base (p.p.)": round(
                meta1 - meta1_base, 2
            )

        })

    comparacao = pd.DataFrame(comparacao)

    comparacao = comparacao.sort_values(
        by="Meta 2 Final (%)",
        ascending=False
    ).reset_index(drop=True)

    return comparacao

''''# ============================================================
# TESTE com comparação para montar um gráfico de linhas
# ============================================================

if __name__ == "__main__":

    cenario_base = criar_cenario(
        "Base",
        {}
    )

    cenario_a = criar_cenario(
        "Força-tarefa Outubro",
        {
            "2026-10": {
                "julgados": 100,
                "dessobrestados": 20,
                "suspensos": -15
    }
}
    )

    cenario_b = criar_cenario(
        "Outubro + Novembro",
        {
            "2026-10": {
                "julgados": 100
            },
            "2026-11": {
                "julgados": 150
            }
        }
    )

    cenarios = [
        cenario_base,
        cenario_a,
        cenario_b
    ]

    resultados = executar_cenarios(
        base,
        cenarios
    )

    comparacao = comparar_cenarios(
        resultados
    )

    print("\n===== COMPARAÇÃO DE CENÁRIOS =====")

    print(comparacao)
    '''


# ============================================================
# RESUMO DO CENÁRIO
# ============================================================

def gerar_resumo_cenario(base_original, resultado_simulado):
    """
    Gera um resumo comparando a situação atual com a simulada.

    Retorna um dicionário com os principais indicadores

    IMPORTANTE: `base_original` precisa já ter passado por
    `calcular_meta_acumulada()` (ou seja, ter "meta1" e "meta2").
    A variável global `base` NÃO tem essa coluna sozinha — use
    `calcular_meta_acumulada(base)` antes de chamar esta função.
    """

    if not {"meta1", "meta2"}.issubset(base_original.columns):
        raise ValueError(
            "gerar_resumo_cenario() recebeu uma base sem as metas "
            "calculadas. Calcule as metas da base original antes, com:\n"
            "    base_calculada = calcular_meta_acumulada(base)\n"
            "    resumo = gerar_resumo_cenario(base_calculada, resultado)"
        )


    # Meta final da base original
    meta_atual = (
        base_original.loc[
            base_original["ano"] == ANO_SIMULACAO,
            "meta1"
        ]
        .iloc[-1]
    )

    # Meta final após a simulação
    meta_simulada = (
        resultado_simulado.loc[
            resultado_simulado["ano"] == ANO_SIMULACAO,
            "meta1"
        ]
        .iloc[-1]
    )

    # Ganho obtido
    ganho = meta_simulada - meta_atual

    meta2_atual = (
        base_original.loc[
            base_original["ano"] == ANO_SIMULACAO,
            "meta2"
        ]
        .iloc[-1]
    )

    meta2_simulada = (
        resultado_simulado.loc[
            resultado_simulado["ano"] == ANO_SIMULACAO,
            "meta2"
        ]
        .iloc[-1]
    )

    ganho_meta2 = meta2_simulada - meta2_atual

    # Quantidade adicionada em cada variável
    julgados_extra = (
        resultado_simulado["julgados"] -
        base_original["julgados"]
    ).sum()

    dessobrestados_extra = (
        resultado_simulado["dessobrestados"] -
        base_original["dessobrestados"]
    ).sum()

    suspensos_extra = (
        resultado_simulado["suspensos"] -
        base_original["suspensos"]
    ).sum()

    return {

        "meta_atual": round(meta_atual, 2),

        "meta_simulada": round(meta_simulada, 2),

        "ganho_percentual": round(ganho, 2),

        "meta2_atual": round(meta2_atual, 2),

        "meta2_simulada": round(meta2_simulada, 2),

        "ganho_meta2_pontos_percentuais": round(ganho_meta2, 2),

        "julgados_adicionados": int(julgados_extra),

        "dessobrestados_adicionados": int(dessobrestados_extra),

        "suspensos_alterados": int(suspensos_extra)

    }

'''TESTE
resultado = simular_cenario(
    base,
    {
        "2026-10": {
            "julgados": 100
        }
    }
)

resumo = gerar_resumo_cenario(
    base,
    resultado
)

print(resumo)
'''

# ============================================================
# 10. BUSCA AUTOMÁTICA DO MENOR AJUSTE NECESSÁRIO
# ============================================================
# Objetivo: em vez do usuário testar cenários manualmente
# (tentativa e erro), encontrar automaticamente o menor
# incremento (em módulo) em uma variável editável que seja
# suficiente para que a Meta 1 acumulada do fim do ano atinja
# um percentual-alvo (por padrão, META_ALVO = 100%).
#
# A fórmula da Meta 1 é monotônica em cada variável:
#   - julgados       ↑  =>  meta1 ↑
#   - suspensos      ↑  =>  meta1 ↑   (reduz o denominador)
#   - dessobrestados ↑  =>  meta1 ↓   (aumenta o denominador)
#
# ============================================================
 
def _meta_final_com_incremento(base, variavel, mes, incremento, ano=ANO_SIMULACAO):
    """
    Aplica um incremento hipotético a `variavel` no mês `mes` e
    devolve a Meta 1 acumulada no último mês do ano `ano`.
    """
    resultado = simular_cenario(
        base,
        {mes: {variavel: incremento}}
    )
    return resultado.loc[
        resultado["ano"] == ano,
        "meta1"
    ].iloc[-1]
 
 
def encontrar_ajuste_minimo(
    base,
    variavel,
    mes,
    meta_alvo=META_ALVO,
    ano=ANO_SIMULACAO,
    passo_inicial=50,
    max_expansoes=40,
    tolerancia=0.5,
    max_iteracoes=60
):
    """
    Encontra automaticamente o menor incremento (em módulo) em
    `variavel`, aplicado no mês `mes`, necessário para que a
    Meta 1 acumulada de `ano` atinja `meta_alvo`.
 
    
    Retorna
    -------
    dict com:
        - variavel, mes, meta_alvo
        - meta_atual: meta de fim de ano sem nenhum ajuste
        - incremento_necessario: menor incremento (inteiro,
          arredondado "para cima" no sentido que garante a meta)
          que atinge a meta_alvo
        - meta_resultante: meta de fim de ano após aplicar o
          incremento encontrado
        - mensagem: explicação em texto
    """
 
    if variavel not in VARIAVEIS_EDITAVEIS:
        raise ValueError(
            f"A variável '{variavel}' não pode ser ajustada pelo "
            f"usuário. Use uma destas: {VARIAVEIS_EDITAVEIS}"
        )
 
    meta_atual = _meta_final_com_incremento(base, variavel, mes, 0, ano)
 
    # Já está na meta (ou acima): não precisa de nenhum ajuste.
    if meta_atual >= meta_alvo:
        return {
            "variavel": variavel,
            "mes": mes,
            "meta_alvo": meta_alvo,
            "meta_atual": round(meta_atual, 2),
            "incremento_necessario": 0,
            "meta_resultante": round(meta_atual, 2),
            "mensagem": (
                f"A meta de {meta_alvo}% já está atingida "
                f"({round(meta_atual, 2)}%). Nenhum ajuste é necessário."
            )
        }
 
    # 1) Descobre em que direção a variável precisa se mover para
    #    aumentar a meta (normalmente positiva para julgados e
    #    suspensos

    meta_teste = _meta_final_com_incremento(
        base, variavel, mes, passo_inicial, ano
    )
    direcao = 1 if meta_teste > meta_atual else -1
 
    # 2) Expande o intervalo de busca até "passar" da meta.
    lo, hi = 0.0, float(passo_inicial)
    for _ in range(max_expansoes):
        meta_hi = _meta_final_com_incremento(
            base, variavel, mes, direcao * hi, ano
        )
        if meta_hi >= meta_alvo:
            break
        hi *= 2
    else:
        raise RuntimeError(
            "Não foi possível encontrar um incremento suficiente "
            "dentro do limite de busca. Verifique se a meta é "
            "atingível ajustando apenas essa variável nesse mês."
        )
 
    # 3) Busca binária (bisseção) no intervalo [lo, hi].
    for _ in range(max_iteracoes):
        meio = (lo + hi) / 2
        meta_meio = _meta_final_com_incremento(
            base, variavel, mes, direcao * meio, ano
        )
        if meta_meio >= meta_alvo:
            hi = meio
        else:
            lo = meio
        if hi - lo < tolerancia:
            break
 
    # 4) Arredonda "para cima" no sentido do ajuste, garantindo
    #    que a meta realmente seja atingida (não apenas aproximada).
    incremento_bruto = direcao * hi
    incremento_necessario = (
        int(np.ceil(incremento_bruto)) if direcao == 1
        else int(np.floor(incremento_bruto))
    )
 
    meta_resultante = _meta_final_com_incremento(
        base, variavel, mes, incremento_necessario, ano
    )
 
    # Garantia extra: se o arredondamento deixou por 0.01 abaixo
    # da meta, incrementa mais uma unidade na direção certa.
    while meta_resultante < meta_alvo:
        incremento_necessario += direcao
        meta_resultante = _meta_final_com_incremento(
            base, variavel, mes, incremento_necessario, ano
        )
 
    return {
        "variavel": variavel,
        "mes": mes,
        "meta_alvo": meta_alvo,
        "meta_atual": round(meta_atual, 2),
        "incremento_necessario": incremento_necessario,
        "meta_resultante": round(meta_resultante, 2),
        "mensagem": (
            f"Para atingir {meta_alvo}% em {ano}, é necessário "
            f"alterar '{variavel}' em {incremento_necessario:+d} "
            f"a partir de {mes}. Meta resultante: "
            f"{round(meta_resultante, 2)}%."
        )
    }
 
 
def quantos_julgamentos_para_meta(base, mes, meta_alvo=META_ALVO, ano=ANO_SIMULACAO):
    """
    Atalho para a pergunta mais comum: "quantos julgamentos
    adicionais são necessários para bater a meta em `mes`?"
    """
    return encontrar_ajuste_minimo(
        base, "julgados", mes, meta_alvo=meta_alvo, ano=ano
    )
 
 
'''
EXEMPLO DE USO
--------------
 
resultado = quantos_julgamentos_para_meta(base, "2026-10")
print(resultado["mensagem"])
# -> "Para atingir 100.0% em 2026, é necessário alterar
#     'julgados' em +XXXX a partir de 2026-10. Meta
#     resultante: 100.0%."
 
# Ou, de forma genérica, para qualquer variável editável:
resultado = encontrar_ajuste_minimo(base, "suspensos", "2026-10", meta_alvo=100)
print(resultado)
'''

# ============================================================
# 11. GRÁFICOS
# ============================================================
 
import matplotlib.pyplot as plt
 
def plotar_series_consolidadas(base, data_corte=DATA_CORTE_REAL):
    """
    Gráfico das séries mensais consolidadas: novos, julgados,
    baixados (se existir), dessobrestados e suspensos.
    """
 
    plt.figure(figsize=(14, 7))
 
    plt.plot(base["data"], base["novos"], label="Casos novos", linewidth=2)
    plt.plot(base["data"], base["julgados"], label="Casos julgados", linewidth=2)
 
    # "baixados" pode não existir na prática (ARQ_BAIXADOS = None);
    # só desenha se houver algum valor real.
    if "baixados" in base.columns and base["baixados"].notna().any():
        plt.plot(base["data"], base["baixados"], label="Casos baixados", linewidth=2)
 
    plt.plot(base["data"], base["dessobrestados"], label="Dessobrestados", linestyle="--")
    plt.plot(base["data"], base["suspensos"], label="Suspensos", linestyle="--")
 
    plt.axvline(data_corte, color="gray", linestyle=":", label="Início das previsões")
 
    plt.title("Séries mensais consolidadas: novos, julgados, baixados, dessobrestados e suspensos")
    plt.xlabel("Data")
    plt.ylabel("Quantidade")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
 
 
def construir_tabela_meta1_por_cenario(resultados):
    """
    A partir do dicionário devolvido por `executar_cenarios()`,
    monta uma tabela larga com uma coluna "meta1_<nome_do_cenário>"
    por cenário, alinhada por data. É essa tabela (e não a de
    `comparar_cenarios()`) que serve de entrada para o gráfico
    mensal comparativo.
    """
 
    tabelas = []
 
    for nome, dados in resultados.items():
        tabela = (
            dados["resultado"][["data", "meta1"]]
            .rename(columns={"meta1": f"meta1_{nome}"})
        )
        tabelas.append(tabela)
 
    tabela_final = reduce(
        lambda esquerda, direita: pd.merge(esquerda, direita, on="data", how="outer"),
        tabelas
    )
 
    return tabela_final.sort_values("data").reset_index(drop=True)
 
 
def plotar_meta1_por_cenario(resultados, ano=ANO_SIMULACAO, meta_alvo=META_ALVO):
    """
    Gráfico comparando a Meta 1 mensal entre cenários.
 
    Parâmetros
    ----------
    resultados : dict
        Saída de `executar_cenarios()`.
    ano : int ou None
        Se informado, restringe o gráfico a esse ano (recomendado,
        já que a meta é acumulada e reinicia todo ano). Use None
        para ver todo o histórico.
    meta_alvo : float
        Desenha uma linha horizontal de referência com a meta.
    """
 
    tabela = construir_tabela_meta1_por_cenario(resultados)
 
    if ano is not None:
        tabela = tabela[tabela["data"].dt.year == ano]
 
    plt.figure(figsize=(14, 7))
 
    for col in tabela.columns:
        if col.startswith("meta1_"):
            nome_cenario = col.replace("meta1_", "")
            plt.plot(
                tabela["data"], tabela[col],
                label=nome_cenario, marker="o", markersize=3
            )
 
    plt.axhline(
        meta_alvo, color="red", linestyle="--", linewidth=1,
        label=f"Meta ({meta_alvo}%)"
    )
 
    plt.title("Meta 1 mensal por cenário")
    plt.xlabel("Mês")
    plt.ylabel("Meta 1 (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
 
 
def plotar_comparacao_cenarios(comparacao, meta_alvo=META_ALVO):
    """
    Gráfico de barras com a Meta 1 final de cada cenário — o
    complemento "visão geral" do `plotar_meta1_por_cenario`
    (que mostra a trajetória mensal). Usa direto a tabela que
    `comparar_cenarios()` já devolve.
 
    Barras acima da meta ficam verdes, abaixo ficam vermelhas,
    e cada barra é rotulada com o valor e a diferença em pontos
    percentuais em relação ao cenário "Base".
    """
 
    dados = comparacao.sort_values("Meta Final (%)").reset_index(drop=True)
 
    cores = [
        "#2ca02c" if valor >= meta_alvo else "#d62728"
        for valor in dados["Meta Final (%)"]
    ]
 
    plt.figure(figsize=(10, 6))
 
    barras = plt.barh(dados["Cenário"], dados["Meta Final (%)"], color=cores)
 
    plt.axvline(
        meta_alvo, color="black", linestyle="--", linewidth=1,
        label=f"Meta ({meta_alvo}%)"
    )
 
    # Rótulo em cada barra: valor final + diferença para o Base
    for barra, valor, diferenca in zip(
        barras, dados["Meta Final (%)"], dados["Diferença para Base (p.p.)"]
    ):
        rotulo = f"{valor:.2f}%"
        if diferenca != 0:
            rotulo += f" ({diferenca:+.2f} p.p.)"
        plt.text(
            barra.get_width() + 0.5,
            barra.get_y() + barra.get_height() / 2,
            rotulo,
            va="center", fontsize=9
        )
 
    plt.title("Meta 1 final por cenário")
    plt.xlabel("Meta 1 (%)")
    plt.legend()
    plt.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.show()
 
 
'''
EXEMPLO DE USO
--------------
 
plotar_series_consolidadas(base)
 
cenarios = [
    criar_cenario("Base", {}),
    criar_cenario("Força-tarefa Outubro", {
        "2026-10": {"julgados": 100, "dessobrestados": 20, "suspensos": -15}
    }),
]
 
resultados = executar_cenarios(base, cenarios)
 
# Trajetória mensal, cenário a cenário
plotar_meta1_por_cenario(resultados, ano=2026)
 
# Comparação "foto final" entre os cenários
comparacao = comparar_cenarios(resultados)
plotar_comparacao_cenarios(comparacao)
'''

# ============================================================
# 12. EXPORTAR RESULTADOS
# ============================================================
 
def _slugify(texto):
    """Transforma o nome de um cenário em algo seguro para nome de arquivo."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    texto = re.sub(r"[\s-]+", "_", texto)
    return texto or "cenario"
 
 
def exportar_resultados(base, resultados=None, pasta="."):
    """
    Exporta os resultados das Metas 1 e 2 em CSV.
 
    Sempre exporta:
    - base_consolidada_metas.csv: a base bruta consolidada
      (novos, julgados, baixados, dessobrestados, suspensos).
    - resultado_metas_mensal.csv: a mesma base com os acumulados
      e as Metas 1 e 2 calculadas mês a mês (cenário Base).
 
    Se `resultados` for passado (a saída de `executar_cenarios()`),
    também exporta:
    - resultado_metas_<cenário>.csv para cada cenário simulado.
    - comparacao_cenarios.csv com o resumo final (via
      `comparar_cenarios`), pronto pra abrir no Excel.
 
    Parâmetros
    ----------
    base : DataFrame
        Base consolidada (a variável global `base`).
    resultados : dict ou None
        Saída de `executar_cenarios()`. Se None, exporta só a
        base e o resultado mensal do cenário real.
    pasta : str
        Diretório onde os arquivos serão salvos (criado se não
        existir). Padrão: diretório atual.
 
    Retorna
    -------
    list[str] com os caminhos de todos os arquivos gerados.
    """
 
    os.makedirs(pasta, exist_ok=True)
 
    arquivos_gerados = []
 
    # Base bruta
    caminho_base = os.path.join(pasta, "base_consolidada_metas.csv")
    base.to_csv(caminho_base, index=False, encoding="utf-8-sig")
    arquivos_gerados.append(caminho_base)
 
    # Resultado mensal do cenário real (equivalente ao "resultado_base")
    resultado_base = calcular_meta_acumulada(base)
    caminho_resultado_base = os.path.join(pasta, "resultado_metas_mensal.csv")
    resultado_base.to_csv(caminho_resultado_base, index=False, encoding="utf-8-sig")
    arquivos_gerados.append(caminho_resultado_base)
 
    # Cenários simulados (opcional)
    if resultados is not None:
 
        for nome, dados in resultados.items():
            nome_arquivo = f"resultado_metas_{_slugify(nome)}.csv"
            caminho = os.path.join(pasta, nome_arquivo)
            dados["resultado"].to_csv(caminho, index=False, encoding="utf-8-sig")
            arquivos_gerados.append(caminho)
 
        comparacao = comparar_cenarios(resultados)
        caminho_comparacao = os.path.join(pasta, "comparacao_cenarios.csv")
        comparacao.to_csv(caminho_comparacao, index=False, encoding="utf-8-sig")
        arquivos_gerados.append(caminho_comparacao)
 
    return arquivos_gerados
 
 
'''
EXEMPLO DE USO
--------------
 
# Só a base e o resultado mensal do cenário real:
exportar_resultados(base)
 
# Com todos os cenários simulados e a comparação final:
cenarios = [
    criar_cenario("Base", {}),
    criar_cenario("Força-tarefa Outubro", {
        "2026-10": {"julgados": 100, "dessobrestados": 20, "suspensos": -15}
    }),
]
resultados = executar_cenarios(base, cenarios)
 
arquivos = exportar_resultados(base, resultados=resultados, pasta="saida")
print(arquivos)
'''

if __name__ == "__main__":
    cenarios = [
        criar_cenario("Base", {}),
        criar_cenario(
            "Aumento de 1.000 julgados em Out",
            {"2026-10": {"julgados": 1000}}
        ),
        criar_cenario(
            "Redução de 1.000 julgados em Out",
            {"2026-10": {"julgados": -1000}}
        ),
        criar_cenario(
            "Aumento de 2.000 suspensos em Dez",
            {"2026-12": {"suspensos": 2000}}
        ),
        criar_cenario(
            "Redução de 2.000 suspensos em Dez",
            {"2026-12": {"suspensos": -2000}}
        ),
    ]

    resultados = executar_cenarios(base, cenarios)
    comparacao = comparar_cenarios(resultados)

    colunas_comparacao = [
        "Cenário",
        "Meta 1 Final (%)",
        "Meta 2 Final (%)",
        "Dif. Meta 2 para Base (p.p.)",
        "Meta 2 > 95%",
        "Status Meta 2"
    ]

    print("\n===== COMPARAÇÃO DE CENÁRIOS — METAS 1 E 2 =====")
    print(comparacao[colunas_comparacao].to_string(index=False))

    resultado_base = resultados["Base"]["resultado"]
    meta2_mensal_2026 = resultado_base.loc[
        resultado_base["ano"] == ANO_SIMULACAO,
        [
            "data",
            "distribuidos_acum",
            "julgados_acum",
            "suspensos",
            "meta2_denominador",
            "meta2",
            "meta2_status"
        ]
    ]

    print("\n===== META 2 MÊS A MÊS — CENÁRIO BASE =====")
    print(meta2_mensal_2026.to_string(index=False))

    meta2_base = resultados["Base"]["meta2_final"]
    if not pd.isna(meta2_base) and meta2_base > 95:
        print(
            "\nALERTA DE DADOS: a Meta 2 do cenário Base ficou acima "
            f"de 95% ({meta2_base:.2f}%). O cálculo está respondendo "
            "corretamente às alterações dos cenários, mas a base de "
            "julgados contém o total geral, não necessariamente apenas "
            "os processos pertencentes ao recorte da Meta 2. Substitua "
            "julgados.xlsx quando a base específica estiver disponível."
        )

    pasta_saida = os.path.join(PASTA_SCRIPT, "saida_meta2")
    arquivos = exportar_resultados(
        base,
        resultados=resultados,
        pasta=pasta_saida
    )

    resumo_txt = os.path.join(pasta_saida, "resumo_teste_meta2.txt")
    with open(resumo_txt, "w", encoding="utf-8") as arquivo:
        arquivo.write("COMPARAÇÃO DE CENÁRIOS — METAS 1 E 2\n\n")
        arquivo.write(comparacao[colunas_comparacao].to_string(index=False))
        arquivo.write("\n\nMETA 2 MÊS A MÊS — CENÁRIO BASE\n\n")
        arquivo.write(meta2_mensal_2026.to_string(index=False))
        arquivo.write(
            "\n\nObservação: distribuídos = casos novos acumulados; "
            "suspensos = estoque do mês corrente. Quando o denominador "
            "é menor ou igual a zero, a Meta 2 é marcada como não "
            "calculável.\n"
        )

    print("\nArquivos exportados:")
    for caminho in arquivos + [resumo_txt]:
        print(" -", caminho)

''''''
'''''plotar_comparacao_cenarios(comparacao)   # gráfico de barras
plotar_meta1_por_cenario(resultados, ano=2026)  # trajetória mensal

base_calculada = calcular_meta_acumulada(base)

dezembro_2026 = base_calculada[
    (base_calculada["ano"] == 2026)
].tail(3)  # últimos 3 meses do ano, pra ver a tendência

print(dezembro_2026[[
    "data", "novos_acum", "julgados_acum",
    "dessobrestados_acum", "suspensos_acum", "meta1"
]])

print(
    base[["data", "novos", "julgados", "dessobrestados", "suspensos"]].tail(12)
)'''

'''
resultado = quantos_julgamentos_para_meta(base, "2026-10")
print(resultado["mensagem"])'''

'''resultado = calcular_meta_acumulada(base)

print(resultado.loc[
    resultado["ano"] == 2026,
    [
        "novos_acum",
        "julgados_acum",
        "dessobrestados_acum",
        "suspensos_acum",
        "meta1"
    ]
].tail(1))'''
