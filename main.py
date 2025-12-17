import streamlit as st
import os
import csv
from io import StringIO
from datetime import datetime
import numpy as np
import pandas as pd

st.markdown(
    """
    <style>
    /* ================================
       AJUSTES GERAIS DA PÁGINA
       ================================ */

<<<<<<< HEAD
    /* padding geral da área principal */
=======
>>>>>>> 7c9d753 ("Ajustes")
    .block-container {
        padding-top: 1.9rem !important;
        padding-bottom: 0.1rem !important;
    }

<<<<<<< HEAD
    /* cada "bloco" vertical padrão do Streamlit (linha) */
    div[data-testid="stVerticalBlock"] {
        gap: 0.15rem !important;  /* espaço entre os elementos empilhados */
        margin-bottom: 0.1rem !important;
    }

    /* containers internos dos elementos (markdown, métricas, etc) */
=======
    div[data-testid="stVerticalBlock"] {
        gap: 0.15rem !important;
        margin-bottom: 0.1rem !important;
    }

>>>>>>> 7c9d753 ("Ajustes")
    .element-container {
        margin-bottom: 0.1rem !important;
        padding-bottom: 0.0rem !important;
    }

<<<<<<< HEAD
    /* markdown (títulos e textos) */
=======
>>>>>>> 7c9d753 ("Ajustes")
    div[data-testid="stMarkdownContainer"] p {
        margin-block-start: 0.15rem !important;
        margin-block-end: 0.15rem !important;
    }

    h1, h2, h3, h4 {
        margin-top: 0.15rem !important;
        margin-bottom: 0.15rem !important;
    }

<<<<<<< HEAD
    /* reduz espaço entre colunas */
=======
>>>>>>> 7c9d753 ("Ajustes")
    .stColumn {
        padding-right: 0.15rem !important;
        padding-left: 0.15rem !important;
    }

    /* ================================
       AJUSTES PARA CARDS (st.metric)
       ================================ */

    div[data-testid="stMetric"] {
<<<<<<< HEAD
        padding: 0.0rem 0.05rem !important;   /* margens internas */
        margin: 0.05rem 0 !important;         /* espaço entre cards */
=======
        padding: 0.0rem 0.05rem !important;
        margin: 0.05rem 0 !important;
>>>>>>> 7c9d753 ("Ajustes")
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        margin-bottom: -0.10rem !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        margin-top: -0.15rem !important;
        margin-bottom: -0.05rem !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 0.70rem !important;
        margin-top: -0.15rem !important;
    }

    /* ================================
       ESTILO DO MENU LATERAL (SIDEBAR)
       ================================ */

<<<<<<< HEAD
    /* fundo e cor base da sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f1117 !important; 
        color: #e5e7eb !important;
    }

    /* labels dos inputs (Ano, Meses, etc.) */
=======
    section[data-testid="stSidebar"] {
        background-color: #0f1117 !important;
        color: #e5e7eb !important;
    }

>>>>>>> 7c9d753 ("Ajustes")
    section[data-testid="stSidebar"] label {
        color: #e5e7eb !important;
        font-weight: 600 !important;
    }

<<<<<<< HEAD
    /* itens do menu lateral (botões das páginas) */
=======
>>>>>>> 7c9d753 ("Ajustes")
    section[data-testid="stSidebar"] button {
        color: #f3f4f6 !important;
        background-color: transparent !important;
    }

<<<<<<< HEAD
    /* texto genérico na sidebar (spans, links, parágrafos) */
=======
>>>>>>> 7c9d753 ("Ajustes")
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] p {
        color: #f1f5f9 !important;
    }

<<<<<<< HEAD
    /* componentes de select/multiselect na sidebar */
=======
>>>>>>> 7c9d753 ("Ajustes")
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stMultiSelect {
        color: #ffffff !important;
    }

<<<<<<< HEAD
    /* texto interno das opções do dropdown */
=======
>>>>>>> 7c9d753 ("Ajustes")
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #000000 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

<<<<<<< HEAD

=======
>>>>>>> 7c9d753 ("Ajustes")
# ============================
# FUNÇÕES AUXILIARES (ETL)
# ============================

<<<<<<< HEAD
def carregar_secoes_csv(conteudo_bytes):
    """
    Lê um CSV em texto com seções iniciadas por '##NomeSecao'
    e devolve um dicionário {nome_secao: [linhas_csv]}
    """
=======
def carregar_secoes_csv(conteudo_bytes: bytes) -> dict:
>>>>>>> 7c9d753 ("Ajustes")
    texto = conteudo_bytes.decode("utf-8-sig")
    linhas = texto.splitlines()

    secoes = {}
    secao_atual = None
    buffer = []

    for linha in linhas:
        linha = linha.strip()
        if linha.startswith("##"):
<<<<<<< HEAD
            # Fecha seção anterior
=======
>>>>>>> 7c9d753 ("Ajustes")
            if secao_atual and buffer:
                secoes[secao_atual] = buffer
                buffer = []
            secao_atual = linha.strip("#")
        elif linha:
            buffer.append(linha)

    if secao_atual and buffer:
        secoes[secao_atual] = buffer

    return secoes


<<<<<<< HEAD
def criar_dataframe(dados):
    """
    Recebe uma lista de linhas (strings) e converte em DataFrame.
    Supõe primeira linha como header.
    """
=======
def criar_dataframe(dados: list[str]) -> pd.DataFrame:
>>>>>>> 7c9d753 ("Ajustes")
    if not dados:
        return pd.DataFrame()

    leitor = csv.reader(StringIO("\n".join(dados)))
    linhas = list(leitor)
    if len(linhas) < 2:
        return pd.DataFrame(columns=linhas[0]) if linhas else pd.DataFrame()
<<<<<<< HEAD
    return pd.DataFrame(linhas[1:], columns=linhas[0])


def tratar_decimal(df, col):
    return pd.to_numeric(df[col].astype(str).str.replace(",", ".", regex=False), errors="coerce")


def tratar_data_hora(df, col_data):
=======

    return pd.DataFrame(linhas[1:], columns=linhas[0])


def tratar_decimal(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(
        df[col].astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )


def tratar_data_hora(df: pd.DataFrame, col_data: str) -> pd.DataFrame:
>>>>>>> 7c9d753 ("Ajustes")
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df["data"] = df[col_data].dt.date
    df["hora"] = df[col_data].dt.time
    return df


<<<<<<< HEAD
def processar_arquivo(conteudo_bytes):
    """
    Executa TODO o ETL original usando o conteúdo do arquivo carregado.
    Retorna os 4 dataframes: combustivel, despesas, servicos, rotas
    """
=======
def processar_arquivo(conteudo_bytes: bytes):
>>>>>>> 7c9d753 ("Ajustes")
    secoes = carregar_secoes_csv(conteudo_bytes)

    df_combustivel = criar_dataframe(secoes.get("Refuelling", []))
    df_despesas = criar_dataframe(secoes.get("Expense", []))
    df_servicos = criar_dataframe(secoes.get("Service", []))
    df_rotas = criar_dataframe(secoes.get("Route", []))

    # ============================
    # TRATAMENTO - DESPESAS
    # ============================
    if not df_despesas.empty:
        df_despesas["Odômetro (km)"] = tratar_decimal(df_despesas, "Odômetro (km)")
        df_despesas["Valor total"] = tratar_decimal(df_despesas, "Valor total")
        df_despesas["Local da despesa"] = df_despesas["Local da despesa"].str.split(" / ").str[0]

        df_despesas = tratar_data_hora(df_despesas, "Data")

        df_despesas.rename(
            columns={
                "Odômetro (km)": "odometro",
                "Data": "data_hora",
                "Valor total": "custo",
                "Tipo de despesa": "tipo_despesa",
                "Local da despesa": "local",
                "Motorista": "motorista",
                "Forma de pagamento": "forma_pagamento",
                "Observação": "observacoes",
            },
            inplace=True,
        )

        df_despesas = df_despesas.astype(
            {
                "odometro": float,
                "custo": float,
                "tipo_despesa": str,
                "local": str,
                "motorista": str,
                "forma_pagamento": str,
                "observacoes": str,
            }
        )

    # ============================
    # TRATAMENTO - TRAJETOS (ROTAS)
    # ============================
    if not df_rotas.empty:
        df_rotas["Odômetro inicial"] = tratar_decimal(df_rotas, "Odômetro inicial")
        df_rotas["Odômetro final"] = tratar_decimal(df_rotas, "Odômetro final")
        df_rotas["Odômetro (km)"] = tratar_decimal(df_rotas, "Odômetro (km)")

        df_rotas["origem_tipo"] = df_rotas["Origem"].astype(str).str[-1]
        df_rotas["Origem"] = df_rotas["Origem"].str.split(" / ").str[0]
        df_rotas["destino_tipo"] = df_rotas["Destino"].astype(str).str[-1]
        df_rotas["Destino"] = df_rotas["Destino"].str.split(" / ").str[0]

        df_rotas["tipo_rota"] = df_rotas.apply(
            lambda row: "Urbano"
            if row["Origem"] == row["Destino"]
            else ("Urbano" if row["origem_tipo"] == "U" and row["destino_tipo"] == "U" else "Rodoviario"),
            axis=1,
        )

        df_rotas.rename(
            columns={
                "Data inicial": "data_inicio",
                "Data final": "data_fim",
                "Odômetro inicial": "odometro_inicial",
                "Odômetro final": "odometro_final",
                "Odômetro (km)": "odometro",
                "Valor km": "custo_km",
                "Total": "custo",
                "Origem": "origem",
                "Destino": "destino",
                "Motivo": "motivo",
                "Motorista": "motorista",
                "Observação": "observacoes",
            },
            inplace=True,
        )

        df_rotas["data_inicio"] = pd.to_datetime(df_rotas["data_inicio"], errors="coerce")
        df_rotas["data_fim"] = pd.to_datetime(df_rotas["data_fim"], errors="coerce")
        df_rotas["tipo_rota"] = df_rotas["tipo_rota"].astype("category")

    # ============================
    # TRATAMENTO - COMBUSTÍVEL
    # ============================
    if not df_combustivel.empty:
        df_combustivel.columns = [f"{col}_{i}" for i, col in enumerate(df_combustivel.columns)]
        df_combustivel.drop(df_combustivel.columns[7:17], axis=1, inplace=True)

        df_combustivel.rename(
            columns={
                "Odômetro (km)_0": "odometro",
                "Data_1": "data_hora",
                "Combustível_2": "combustivel",
                "Preço / L_3": "custo_por_litro",
                "Valor total_4": "custo",
                "Volume_5": "volume_abastecido",
                "Completou o tanque_6": "tanque_completo",
                "Média_17": "media",
                "Distância_18": "distancia_percorrida",
                "Posto de combustível_19": "posto",
                "Motorista_20": "motorista",
                "Motivo_21": "motivo",
                "Forma de pagamento_22": "forma_pagamento",
                "Observação_23": "observacoes",
            },
            inplace=True,
        )

<<<<<<< HEAD
        df_combustivel["odometro"] = tratar_decimal(df_combustivel, "odometro")
        df_combustivel["custo_por_litro"] = tratar_decimal(df_combustivel, "custo_por_litro")
        df_combustivel["custo"] = tratar_decimal(df_combustivel, "custo")
        df_combustivel["volume_abastecido"] = tratar_decimal(df_combustivel, "volume_abastecido")
        df_combustivel["distancia_percorrida"] = tratar_decimal(df_combustivel, "distancia_percorrida")

        df_combustivel["media"] = pd.to_numeric(
            df_combustivel["media"]
            .astype(str)
            .str.replace(r"[^\d,.]", "", regex=True)
            .str.replace(",", "."),
            errors="coerce",
        )

        df_combustivel = tratar_data_hora(df_combustivel, "data_hora")
=======
        for c in ["odometro", "custo_por_litro", "custo", "volume_abastecido", "distancia_percorrida"]:
            if c in df_combustivel.columns:
                df_combustivel[c] = tratar_decimal(df_combustivel, c)

        if "media" in df_combustivel.columns:
            df_combustivel["media"] = pd.to_numeric(
                df_combustivel["media"]
                .astype(str)
                .str.replace(r"[^\d,.]", "", regex=True)
                .str.replace(",", ".", regex=False),
                errors="coerce",
            )

        if "data_hora" in df_combustivel.columns:
            df_combustivel = tratar_data_hora(df_combustivel, "data_hora")

        # =========================================
        # DISTÂNCIA CALCULADA ENTRE ABASTECIMENTOS
        # =========================================
        df_combustivel = df_combustivel.sort_values(
            by=["data_hora", "odometro"],
            ascending=[True, True],
            na_position="last",
        ).reset_index(drop=True)

        df_combustivel["odometro_proximo"] = df_combustivel["odometro"].shift(-1)
        df_combustivel["distancia_calculada"] = df_combustivel["odometro_proximo"] - df_combustivel["odometro"]
        df_combustivel.loc[df_combustivel["distancia_calculada"] < 0, "distancia_calculada"] = np.nan
        df_combustivel.drop(columns=["odometro_proximo"], inplace=True)

        # =========================================================
        # MÉDIA CALCULADA (km/L) - litros na linha atual, km nas anteriores
        # =========================================================
        df_combustivel = df_combustivel.sort_values(
            by=["data_hora"],
            ascending=True,
            na_position="last",
        ).reset_index(drop=True)

        flag_sim = (
            df_combustivel["tanque_completo"]
            .astype(str).str.strip().str.lower()
            .eq("sim")
        )

        segmento = flag_sim.cumsum()

        km_por_segmento = df_combustivel.groupby(segmento)["distancia_calculada"].sum(min_count=1)

        litros_nao_por_segmento = (
            df_combustivel.loc[~flag_sim]
            .groupby(segmento)["volume_abastecido"]
            .sum(min_count=1)
        )

        idx_sim = df_combustivel.index[flag_sim]
        seg_atual = segmento.loc[idx_sim]
        seg_base = seg_atual - 1

        km_base = km_por_segmento.reindex(seg_base).to_numpy()

        litros_base_nao = (
            litros_nao_por_segmento.reindex(seg_base)
            .fillna(0)
            .to_numpy()
        )

        litros_atual = df_combustivel.loc[idx_sim, "volume_abastecido"].to_numpy()
        litros_total = litros_base_nao + litros_atual

        media = km_base / litros_total

        df_combustivel["media_calculada"] = np.nan
        df_combustivel.loc[idx_sim, "media_calculada"] = media

        df_combustivel.loc[
            df_combustivel["media_calculada"].replace([np.inf, -np.inf], np.nan).isna(),
            "media_calculada"
        ] = np.nan
        df_combustivel.loc[df_combustivel["media_calculada"] < 0, "media_calculada"] = np.nan
        df_combustivel.loc[idx_sim[litros_total <= 0], "media_calculada"] = np.nan

        df_combustivel["media_calculada_preenchida"] = df_combustivel["media_calculada"].bfill()

        # =========================================================
        # MÉDIA ACUMULADA (km/L)
        # - Não calcula na 1ª linha
        # - Começa na 2ª (linha 1) acumulando volume e distância desde a linha 0
        # - Para (não exibe) a partir do "Não" mais recente (inclusive)
        # =========================================================
        vol = pd.to_numeric(df_combustivel["volume_abastecido"], errors="coerce")
        dist = pd.to_numeric(df_combustivel["distancia_calculada"], errors="coerce")

        vol_cum = vol.cumsum()
        dist_cum = dist.cumsum()

        df_combustivel["volume_abastecido_acumulado"] = np.nan
        df_combustivel["distancia_calculada_acumulada"] = np.nan
        df_combustivel["media_acumulada"] = np.nan

        if len(df_combustivel) >= 2:
            df_combustivel.loc[1:, "volume_abastecido_acumulado"] = vol_cum.iloc[1:].to_numpy()
            df_combustivel.loc[1:, "distancia_calculada_acumulada"] = dist_cum.iloc[1:].to_numpy()

            denom = df_combustivel.loc[1:, "volume_abastecido_acumulado"].replace({0: np.nan})
            df_combustivel.loc[1:, "media_acumulada"] = (
                df_combustivel.loc[1:, "distancia_calculada_acumulada"] / denom
            )

        flag_nao = (
            df_combustivel["tanque_completo"]
            .astype(str).str.strip().str.lower()
            .isin(["não", "nao"])
        )

        if flag_nao.any():
            stop_idx = flag_nao[flag_nao].index.max()  # "Não" mais recente
            df_combustivel.loc[
                stop_idx:,
                ["volume_abastecido_acumulado", "distancia_calculada_acumulada", "media_acumulada"]
            ] = np.nan
>>>>>>> 7c9d753 ("Ajustes")

    # ============================
    # TRATAMENTO - SERVIÇOS
    # ============================
    if not df_servicos.empty:
        df_servicos.rename(
            columns={
                "Odômetro (km)": "odometro",
                "Data": "data_hora",
                "Valor total": "custo",
                "Tipo de serviço": "tipo_servico",
                "Local do serviço": "local_servico",
                "Motorista": "motorista",
                "Forma de pagamento": "forma_pagamento",
                "Observação_23": "observacoes",
            },
            inplace=True,
        )

        df_servicos["odometro"] = tratar_decimal(df_servicos, "odometro")
        df_servicos["custo"] = tratar_decimal(df_servicos, "custo")
        df_servicos["local_servico"] = df_servicos["local_servico"].str.split(" / ").str[0]
        df_servicos = tratar_data_hora(df_servicos, "data_hora")

    return df_combustivel, df_despesas, df_servicos, df_rotas


# ============================
# APP STREAMLIT - HOME
# ============================

st.set_page_config(page_title="🏁 Controle Veicular", layout="wide")

st.title("🏁 Controle Veicular")
st.markdown(
    """
Carregue o arquivo **BD.csv** e navegue pelas telas:
<<<<<<< HEAD

=======
>>>>>>> 7c9d753 ("Ajustes")
"""
)

uploaded_file = st.file_uploader("Carregue o arquivo BD.csv", type=["csv"], key="upload_bd")

if uploaded_file is not None:
<<<<<<< HEAD
    # Lê conteúdo do arquivo
    conteudo = uploaded_file.getvalue()
    file_hash = hash(conteudo)

    # Só reprocesa se for um arquivo diferente
    if "file_hash" not in st.session_state or st.session_state["file_hash"] != file_hash:
        with st.spinner("Processando arquivo..."):
            (
                df_combustivel,
                df_despesas,
                df_servicos,
                df_rotas,
            ) = processar_arquivo(conteudo)
=======
    conteudo = uploaded_file.getvalue()
    file_hash = hash(conteudo)

    if "file_hash" not in st.session_state or st.session_state["file_hash"] != file_hash:
        with st.spinner("Processando arquivo..."):
            (df_combustivel, df_despesas, df_servicos, df_rotas) = processar_arquivo(conteudo)
>>>>>>> 7c9d753 ("Ajustes")

        st.session_state["file_hash"] = file_hash
        st.session_state["df_combustivel"] = df_combustivel
        st.session_state["df_despesas"] = df_despesas
        st.session_state["df_servicos"] = df_servicos
        st.session_state["df_rotas"] = df_rotas

        st.success("Arquivo processado com sucesso! Você já pode navegar pelas outras páginas.")
    else:
        st.info("Este arquivo já foi processado. Os dados em memória continuam os mesmos.")

<<<<<<< HEAD
# Mostra um resumo rápido se já tiver dados em memória
=======
>>>>>>> 7c9d753 ("Ajustes")
if "df_combustivel" in st.session_state:
    st.subheader("Resumo dos dados carregados")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Registros de Combustível", len(st.session_state["df_combustivel"]))
    with col2:
        st.metric("Registros de Despesas", len(st.session_state["df_despesas"]))
    with col3:
        st.metric("Registros de Serviços", len(st.session_state["df_servicos"]))
    with col4:
        st.metric("Registros de Trajetos", len(st.session_state["df_rotas"]))
else:
<<<<<<< HEAD
    st.warning("Nenhum arquivo processado ainda. Faça o upload do **BD.csv** acima.")
=======
    st.warning("Nenhum arquivo processado ainda. Faça o upload do **BD.csv** acima.")
>>>>>>> 7c9d753 ("Ajustes")
