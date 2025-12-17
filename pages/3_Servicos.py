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



st.title("🛠️ Serviços – Manutenções e Cuidados")

if "df_servicos" not in st.session_state:
    st.error("Nenhum arquivo foi carregado ainda. Volte para a página **Home** e faça o upload do BD.csv.")
    st.stop()

df_servicos = st.session_state["df_servicos"].copy()

# garante colunas de data
if "data" in df_servicos.columns:
    df_servicos["data"] = pd.to_datetime(df_servicos["data"], errors="coerce")
else:
    st.error("Coluna 'data' não encontrada no dataframe de serviços.")
    st.stop()

if "data_hora" in df_servicos.columns:
    df_servicos["data_hora"] = pd.to_datetime(df_servicos["data_hora"], errors="coerce")

# ============================
# FILTROS GLOBAIS (ANO / MÊS) - SIDEBAR
# ============================
with st.sidebar:
    st.markdown("### Filtros de período")

    serie_data = df_servicos["data"]
    anos_disponiveis = sorted(serie_data.dropna().dt.year.unique().tolist())

    if anos_disponiveis:
        opcoes_ano = ["Todos"] + [str(a) for a in anos_disponiveis]
        ano_sel = st.selectbox("Ano", opcoes_ano, key="filtro_ano_servicos")

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
            key="filtro_meses_servicos",
        )
        meses_sel = [map_label_to_month[l] for l in meses_sel_labels]

        mask = serie_data.notna()
        if ano_sel != "Todos":
            mask &= serie_data.dt.year == int(ano_sel)
        if meses_sel:
            mask &= serie_data.dt.month.isin(meses_sel)

        df_periodo = df_servicos.loc[mask].copy()
    else:
        df_periodo = df_servicos.copy()

# ============================
# FILTROS ESPECÍFICOS (TIPO / LOCAL)
# ============================
st.subheader("Filtros de Serviços")

col1, col2 = st.columns(2)

with col1:
    tipos = ["(Todos)"] + sorted(df_periodo["tipo_servico"].dropna().unique().tolist())
    tipo_sel = st.selectbox("Tipo de serviço", tipos)

with col2:
    locais = ["(Todos)"] + sorted(df_periodo["local_servico"].dropna().unique().tolist())
    local_sel = st.selectbox("Local do serviço", locais)

df_filtrado = df_periodo.copy()

if tipo_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["tipo_servico"] == tipo_sel]

if local_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["local_servico"] == local_sel]

st.markdown("---")

# ============================
# FUNÇÕES DE FORMATAÇÃO
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

def format_number_br(x, decimals=1):
    if pd.isna(x):
        return ""
    return (
        f"{float(x):,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

# ============================
# MÉTRICA TOTAL GASTO
# ============================
st.subheader("Resumo dos Serviços")

if df_filtrado.empty:
    st.info("Nenhum dado disponível para o período/filtros selecionados.")
else:
    total_gasto = pd.to_numeric(df_filtrado["custo"], errors="coerce").sum()

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.metric("Total gasto em serviços (R$)", format_currency_br(total_gasto))

    with col_m2:
        # opcional: quantidade de serviços executados
        st.metric("Quantidade de serviços", int(len(df_filtrado)))

# ============================
# GRÁFICOS POR TIPO E LOCAL
# ============================
st.markdown("---")
st.subheader("Distribuição de gastos por serviço")

if not df_filtrado.empty:
    col_g1, col_g2 = st.columns(2)

    # --- Gráfico: total por tipo de serviço ---
    with col_g1:
        gastos_por_tipo = (
            df_filtrado.groupby("tipo_servico", dropna=False)["custo"]
            .sum()
            .reset_index()
        )
        gastos_por_tipo["tipo_servico"] = gastos_por_tipo["tipo_servico"].fillna("Não informado")
        gastos_por_tipo = gastos_por_tipo.sort_values("custo", ascending=False)

        fig_tipo = px.bar(
            gastos_por_tipo,
            x="tipo_servico",
            y="custo",
            labels={"tipo_servico": "Tipo de serviço", "custo": "Custo total (R$)"},
            title="Gasto por tipo de serviço",
        )
        fig_tipo.update_traces(
            text=gastos_por_tipo["custo"].round(2),
            texttemplate="R$ %{text:,.2f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig_tipo.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig_tipo, use_container_width=True)

    # --- Gráfico: total por local de serviço ---
    with col_g2:
        gastos_por_local = (
            df_filtrado.groupby("local_servico", dropna=False)["custo"]
            .sum()
            .reset_index()
        )
        gastos_por_local["local_servico"] = gastos_por_local["local_servico"].fillna("Não informado")
        gastos_por_local = gastos_por_local.sort_values("custo", ascending=False)

        fig_local = px.bar(
            gastos_por_local,
            x="local_servico",
            y="custo",
            labels={"local_servico": "Local do serviço", "custo": "Custo total (R$)"},
            title="Gasto por local de serviço",
        )
        fig_local.update_traces(
            text=gastos_por_local["custo"].round(2),
            texttemplate="R$ %{text:,.2f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig_local.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig_local, use_container_width=True)
else:
    st.info("Sem dados para gráficos de distribuição.")

# ============================
# GRÁFICO DE TOTAIS POR ANO / MÊS
# ============================
st.markdown("---")
st.subheader("Totais de serviços por período")

if not df_filtrado.empty:
    df_temp = df_filtrado.copy()
    df_temp["data"] = pd.to_datetime(df_temp["data"], errors="coerce")
    df_temp = df_temp.dropna(subset=["data"])

    opcao_tempo_serv = st.radio(
        "Nível de tempo",
        ["Ano", "Mês"],
        horizontal=True,
        key="nivel_tempo_servicos",
    )

    if opcao_tempo_serv == "Ano":
        df_temp["periodo"] = df_temp["data"].dt.year.astype(str)
        titulo_tempo = "Total gasto com serviços por ano"
    else:
        df_temp["periodo"] = df_temp["data"].dt.to_period("M").astype(str)
        titulo_tempo = "Total gasto com serviços por mês"

    df_tempo = (
        df_temp.groupby("periodo", as_index=False)["custo"]
        .sum()
        .sort_values("periodo")
    )

    if df_tempo.empty:
        st.info("Sem dados para o gráfico de totais por período.")
    else:
        fig_totais = px.bar(
            df_tempo,
            x="periodo",
            y="custo",
            labels={"periodo": "Período", "custo": "Custo total (R$)"},
            title=titulo_tempo,
        )
        fig_totais.update_traces(
            text=df_tempo["custo"].round(2),
            texttemplate="R$ %{text:,.2f}",
            textposition="outside",
            cliponaxis=False,
        )

        # ✅ FORÇA EXIBIR TODOS OS RÓTULOS NO EIXO X (principalmente no modo "Mês")
        if opcao_tempo_serv == "Mês":
            periodos = df_tempo["periodo"].tolist()
            fig_totais.update_xaxes(
                type="category",
                tickmode="array",
                tickvals=periodos,
                ticktext=periodos,
                tickangle=-45,
            )
            # um pouco mais de margem embaixo p/ não cortar label inclinado
            fig_totais.update_layout(margin=dict(b=80))
        else:
            fig_totais.update_xaxes(type="category")

        st.plotly_chart(fig_totais, use_container_width=True)
else:
    st.info("Sem dados para o gráfico de totais por período.")

# ============================
# TABELA DE SERVIÇOS (DETALHADA)
# ============================
st.markdown("---")
st.subheader("Tabela de Serviços (detalhada)")

if df_filtrado.empty:
    st.info("Sem dados para exibir na tabela.")
else:
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

    # Máscaras numéricas (odômetro, se existir)
    if "odometro" in df_formatado.columns:
        df_formatado["odometro"] = pd.to_numeric(df_formatado["odometro"], errors="coerce") \
            .apply(lambda v: format_number_br(v, 0))

    # Exibir tabela com cabeçalho fixo, sem índice
    st.dataframe(
        df_formatado,
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    # Botão para exportar tabela formatada
    csv_formatado = df_formatado.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar tabela de serviços formatada (CSV)",
        data=csv_formatado,
        file_name="servicos_formatados.csv",
        mime="text/csv",
    )