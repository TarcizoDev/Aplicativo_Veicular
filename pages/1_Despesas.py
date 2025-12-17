import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown(
    """
    <style>
    /* ================================
       AJUSTES GERAIS DA PÁGINA
       ================================ */

    /* padding geral da área principal */
    .block-container {
        padding-top: 1.9rem !important;
        padding-bottom: 0.1rem !important;
    }

    /* cada "bloco" vertical padrão do Streamlit (linha) */
    div[data-testid="stVerticalBlock"] {
        gap: 0.15rem !important;  /* espaço entre os elementos empilhados */
        margin-bottom: 0.1rem !important;
    }

    /* containers internos dos elementos (markdown, métricas, etc) */
    .element-container {
        margin-bottom: 0.1rem !important;
        padding-bottom: 0.0rem !important;
    }

    /* markdown (títulos e textos) */
    div[data-testid="stMarkdownContainer"] p {
        margin-block-start: 0.15rem !important;
        margin-block-end: 0.15rem !important;
    }

    h1, h2, h3, h4 {
        margin-top: 0.15rem !important;
        margin-bottom: 0.15rem !important;
    }

    /* reduz espaço entre colunas */
    .stColumn {
        padding-right: 0.15rem !important;
        padding-left: 0.15rem !important;
    }

    /* ================================
       AJUSTES PARA CARDS (st.metric)
       ================================ */

    div[data-testid="stMetric"] {
        padding: 0.0rem 0.05rem !important;   /* margens internas */
        margin: 0.05rem 0 !important;         /* espaço entre cards */
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

    /* fundo e cor base da sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f1117 !important; 
        color: #e5e7eb !important;
    }

    /* labels dos inputs (Ano, Meses, etc.) */
    section[data-testid="stSidebar"] label {
        color: #e5e7eb !important;
        font-weight: 600 !important;
    }

    /* itens do menu lateral (botões das páginas) */
    section[data-testid="stSidebar"] button {
        color: #f3f4f6 !important;
        background-color: transparent !important;
    }

    /* texto genérico na sidebar (spans, links, parágrafos) */
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] p {
        color: #f1f5f9 !important;
    }

    /* componentes de select/multiselect na sidebar */
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stMultiSelect {
        color: #ffffff !important;
    }

    /* texto interno das opções do dropdown */
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #000000 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


st.title("💸 Despesas – Custos do Veículo")

if "df_despesas" not in st.session_state:
    st.error("Nenhum arquivo foi carregado ainda. Volte para a página **Home** e faça o upload do BD.csv.")
    st.stop()

df_despesas = st.session_state["df_despesas"].copy()

# Garante que a coluna de data esteja em datetime
if "data" in df_despesas.columns:
    df_despesas["data"] = pd.to_datetime(df_despesas["data"], errors="coerce")
else:
    st.error("Coluna 'data' não encontrada no dataframe de despesas.")
    st.stop()

# ============================
# FILTROS GLOBAIS (ANO / MÊS) - SIDEBAR
# ============================
with st.sidebar:
    st.markdown("### Filtros de período")

    serie_data = df_despesas["data"]
    anos_disponiveis = sorted(serie_data.dropna().dt.year.unique().tolist())

    if anos_disponiveis:
        opcoes_ano = ["Todos"] + [str(a) for a in anos_disponiveis]
        ano_sel = st.selectbox("Ano", opcoes_ano, key="filtro_ano_despesas")

        meses_nomes = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
            5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
        }

        meses_disponiveis = sorted(serie_data.dropna().dt.month.unique().tolist())
        meses_labels = [f"{meses_nomes[m]} ({m})" for m in meses_disponiveis]
        map_label_to_month = dict(zip(meses_labels, meses_disponiveis))

        meses_sel_labels = st.multiselect(
            "Meses",
            meses_labels,
            default=meses_labels,
            key="filtro_meses_despesas",
        )
        meses_sel = [map_label_to_month[l] for l in meses_sel_labels]

        mask = serie_data.notna()
        if ano_sel != "Todos":
            mask &= serie_data.dt.year == int(ano_sel)
        if meses_sel:
            mask &= serie_data.dt.month.isin(meses_sel)

        df_periodo = df_despesas.loc[mask].copy()
    else:
        df_periodo = df_despesas.copy()

#st.subheader("Tabela de Despesas Teste")  # como você pediu, títulos e filtros ficam

# ============================
# FILTROS ESPECÍFICOS (TIPO / LOCAL)
# ============================
col1, col2 = st.columns(2)

with col1:
    tipos = ["(Todos)"] + sorted(df_periodo["tipo_despesa"].dropna().unique().tolist())
    tipo_sel = st.selectbox("Tipo de despesa", tipos)

with col2:
    locais = ["(Todos)"] + sorted(df_periodo["local"].dropna().unique().tolist())
    local_sel = st.selectbox("Local", locais)

df_filtrado = df_periodo.copy()

if tipo_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["tipo_despesa"] == tipo_sel]

if local_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["local"] == local_sel]

st.markdown("---")

# ============================
# RESUMO + DOWNLOAD LADO A LADO
# ============================
st.subheader("Resumo de Custos")

col_resumo, col_download = st.columns(2)

with col_resumo:
    total = df_filtrado["custo"].sum()
    st.metric(
        "Custo total filtrado (R$)",
        f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    )

with col_download:
    csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar despesas filtradas (CSV)",
        data=csv,
        file_name="despesas_filtradas.csv",
        mime="text/csv",
    )

# ============================
# GRÁFICOS INTERATIVOS (PLOTLY)
# ============================
st.markdown("---")
st.subheader("Visão gráfica dos gastos")

if df_filtrado.empty:
    st.info("Nenhum dado disponível para o período/filtros selecionados.")
else:
    # garante que a coluna data está ok
    df_filtrado["data"] = pd.to_datetime(df_filtrado["data"], errors="coerce")

    # seletor de nível de tempo para o gráfico de totais
    opcao_tempo = st.radio(
        "Nível de tempo para o total de gastos",
        ["Ano", "Mês"],
        horizontal=True,
        key="nivel_tempo_despesas",
    )

    # ============================
    # PREPARA DATAFRAME POR ANO / MÊS (TOTAL, NÃO CUMULATIVO)
    # ============================
    df_tempo = df_filtrado.dropna(subset=["data"]).copy()

    if opcao_tempo == "Ano":
        df_tempo["periodo"] = df_tempo["data"].dt.year.astype(str)
        titulo_acum = "Total de gastos por ano"
    else:
        # ano-mês (YYYY-MM) pra manter ordem
        df_tempo["periodo"] = df_tempo["data"].dt.to_period("M").astype(str)
        titulo_acum = "Total de gastos por mês"

    df_tempo = (
        df_tempo.groupby("periodo", as_index=False)["custo"]
        .sum()
        .sort_values("periodo")
    )

    # ============================
    # LAYOUT: 3 GRÁFICOS LADO A LADO
    # ============================
    col_g1, col_g2, col_g3 = st.columns(3)

    # --- Gráfico 1: total por tipo de despesa ---
    with col_g1:
        gastos_por_tipo = (
            df_filtrado.groupby("tipo_despesa", dropna=False)["custo"]
            .sum()
            .reset_index()
        )
        gastos_por_tipo["tipo_despesa"] = gastos_por_tipo["tipo_despesa"].fillna("Não informado")
        gastos_por_tipo = gastos_por_tipo.sort_values("custo", ascending=True)

        fig_tipo = px.bar(
            gastos_por_tipo,
            x="custo",
            y="tipo_despesa",
            orientation="h",
            labels={"custo": "Custo total (R$)", "tipo_despesa": "Tipo de despesa"},
            title="Gasto por tipo de despesa",
        )

        # rótulos de dados
        fig_tipo.update_traces(
            text=gastos_por_tipo["custo"].round(2),
            texttemplate="R$ %{text:,.2f}",
            textposition="outside",
            cliponaxis=False,
        )

        # Ajustar espaçamento dos rotulos de dados
        fig_tipo.update_layout(
            yaxis=dict(categoryorder="total ascending", automargin=True),
            xaxis=dict(automargin=True),
            margin=dict(l=10, r=60, t=40, b=10),  # aumenta 'r' se ainda cortar
            )

        fig_tipo.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_tipo, use_container_width=True)

    # --- Gráfico 2: total por local ---
    with col_g2:
        gastos_por_local = (
            df_filtrado.groupby("local", dropna=False)["custo"]
            .sum()
            .reset_index()
        )
        gastos_por_local["local"] = gastos_por_local["local"].fillna("Não informado")
        gastos_por_local = gastos_por_local.sort_values("custo", ascending=True)

        fig_local = px.bar(
            gastos_por_local,
            x="custo",
            y="local",
            orientation="h",
            labels={"custo": "Custo total (R$)", "local": "Local"},
            title="Gasto por local",
        )

        # rótulos de dados
        fig_local.update_traces(
            text=gastos_por_local["custo"].round(2),
            texttemplate="R$ %{text:,.2f}",
            textposition="outside",
            cliponaxis=False,
        )

        # Ajustar espaçamento dos rotulos de dados
        fig_local.update_layout(
            yaxis=dict(categoryorder="total ascending", automargin=True),
            xaxis=dict(automargin=True),
            margin=dict(l=10, r=60, t=40, b=10),  # aumenta 'r' se ainda cortar
            )

        fig_local.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_local, use_container_width=True)

    # --- Gráfico 3: total por período (Ano / Mês) ---
    with col_g3:
        if not df_tempo.empty:
            fig_tempo = px.bar(
                df_tempo,
                x="periodo",
                y="custo",
                labels={"periodo": "Período", "custo": "Custo total (R$)"},
                title=titulo_acum,
            )

            # rótulos de dados
            fig_tempo.update_traces(
                text=df_tempo["custo"].round(2),
                texttemplate="R$ %{text:,.2f}",
                textposition="outside",
                cliponaxis=False,
            )

            # ✅ FORÇA EXIBIR TODOS OS RÓTULOS NO EIXO X (principalmente no modo "Mês")
            if opcao_tempo == "Mês":
                periodos = df_tempo["periodo"].tolist()
                fig_tempo.update_xaxes(
                    type="category",
                    tickmode="array",
                    tickvals=periodos,
                    ticktext=periodos,
                    tickangle=-45,
                )
                # um pouco mais de margem embaixo p/ não cortar label inclinado
                fig_tempo.update_layout(margin=dict(b=80))
            else:
                fig_tempo.update_xaxes(type="category")

            st.plotly_chart(fig_tempo, use_container_width=True)
        else:
            st.info("Sem dados suficientes para o gráfico de totais por período.")

# ============================
# TABELA DE DESPESAS (AGORA LÁ EMBAIXO)
# ============================

def format_currency_br(x):
    if pd.isna(x):
        return ""
    return "R$ " + (
        f"{float(x):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

def format_number_br(x, decimals=0):
    if pd.isna(x):
        return ""
    return (
        f"{float(x):,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

# ============================
# TABELA DE DESPESAS (DETALHADA)
# ============================
st.markdown("---")
st.subheader("Tabela de Despesas (detalhada)")

df_tabela = df_filtrado.copy()

# --- Formatação de datas ---
if "data_hora" in df_tabela.columns:
    df_tabela["data_hora"] = pd.to_datetime(df_tabela["data_hora"], errors="coerce") \
        .dt.strftime("%d-%m-%Y %H:%M")

if "data" in df_tabela.columns:
    df_tabela["data"] = pd.to_datetime(df_tabela["data"], errors="coerce") \
        .dt.strftime("%d-%m-%Y")

# --- Cópia para exibição formatada ---
df_formatado = df_tabela.copy()

# Máscara de moeda
if "custo" in df_formatado.columns:
    df_formatado["custo"] = pd.to_numeric(df_formatado["custo"], errors="coerce") \
        .apply(format_currency_br)

# Máscaras numéricas (ajusta conforme suas colunas)
if "odometro" in df_formatado.columns:
    df_formatado["odometro"] = pd.to_numeric(df_formatado["odometro"], errors="coerce") \
        .apply(lambda v: format_number_br(v, 0))

# se tiver outras colunas numéricas que queira formatar:
# for col in ["coluna1", "coluna2"]:
#     if col in df_formatado.columns:
#         df_formatado[col] = pd.to_numeric(df_formatado[col], errors="coerce") \
#             .apply(lambda v: format_number_br(v, 2))

# --- Exibir tabela (sem índice, header fixo com scroll) ---
st.dataframe(
    df_formatado,
    use_container_width=True,
    hide_index=True,
    height=450,   # dá scroll e mantém o cabeçalho fixo
)

# --- Botão para exportar a tabela já formatada ---
csv_formatado = df_formatado.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "Baixar tabela formatada (CSV)",
    data=csv_formatado,
    file_name="despesas_formatadas.csv",
    mime="text/csv",
)