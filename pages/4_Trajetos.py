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


st.title("🗺️ Trajetos – Onde o Veículo Andou")

if "df_rotas" not in st.session_state:
    st.error("Nenhum arquivo foi carregado ainda. Volte para a página **Home** e faça o upload do BD.csv.")
    st.stop()

df_rotas = st.session_state["df_rotas"].copy()

# garante colunas de data
if "data_inicio" in df_rotas.columns:
    df_rotas["data_inicio"] = pd.to_datetime(df_rotas["data_inicio"], errors="coerce")
else:
    st.error("Coluna 'data_inicio' não encontrada no dataframe de rotas.")
    st.stop()

# ============================
# FUNÇÕES DE FORMATAÇÃO
# ============================
def format_number_br(x, decimals=1):
    if pd.isna(x):
        return ""
    return (
        f"{float(x):,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

def format_currency_br(x):
    if pd.isna(x):
        return ""
    return "R$ " + (
        f"{float(x):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

# ============================
# FILTROS GLOBAIS (ANO / MÊS) - SIDEBAR
# ============================
with st.sidebar:
    st.markdown("### Filtros de período")

    serie_data = df_rotas["data_inicio"]
    anos_disponiveis = sorted(serie_data.dropna().dt.year.unique().tolist())

    if anos_disponiveis:
        opcoes_ano = ["Todos"] + [str(a) for a in anos_disponiveis]
        ano_sel = st.selectbox("Ano", opcoes_ano, key="filtro_ano_trajetos")

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
            key="filtro_meses_trajetos",
        )
        meses_sel = [map_label_to_month[l] for l in meses_sel_labels]

        mask = serie_data.notna()
        if ano_sel != "Todos":
            mask &= serie_data.dt.year == int(ano_sel)
        if meses_sel:
            mask &= serie_data.dt.month.isin(meses_sel)

        df_periodo = df_rotas.loc[mask].copy()
    else:
        df_periodo = df_rotas.copy()

# ============================
# FILTROS ESPECÍFICOS (ORIGEM / DESTINO / MOTIVO)
# ============================
st.subheader("Filtros de Trajetos")

col1, col2, col3 = st.columns(3)

with col1:
    origens = ["(Todos)"] + sorted(df_periodo["origem"].dropna().unique().tolist())
    origem_sel = st.selectbox("Origem", origens)

with col2:
    destinos = ["(Todos)"] + sorted(df_periodo["destino"].dropna().unique().tolist())
    destino_sel = st.selectbox("Destino", destinos)

with col3:
    motivos = ["(Todos)"] + sorted(df_periodo["motivo"].dropna().unique().tolist())
    motivo_sel = st.selectbox("Motivo", motivos)

df_filtrado = df_periodo.copy()

if origem_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["origem"] == origem_sel]

if destino_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["destino"] == destino_sel]

if motivo_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["motivo"] == motivo_sel]

st.markdown("---")

# ============================
# MÉTRICAS: TOTAL ODÔMETRO, DESTINO E MOTIVO MAIS USADOS
# ============================
st.subheader("Resumo dos Trajetos")

if df_filtrado.empty:
    st.info("Nenhum dado disponível para o período/filtros selecionados.")
else:
    # garante que odometro é numérico
    df_filtrado["odometro"] = pd.to_numeric(df_filtrado["odometro"], errors="coerce")

    # distância total
    total_odometro = df_filtrado["odometro"].sum()

    # destino mais usado (por km rodado)
    if df_filtrado.dropna(subset=["destino", "odometro"]).empty:
        destino_mais = "—"
    else:
        destino_agrupado = (
            df_filtrado
            .dropna(subset=["destino", "odometro"])
            .groupby("destino")["odometro"]
            .sum()
            .sort_values(ascending=False)
        )
        destino_mais = destino_agrupado.index[0]

    # motivo mais usado (por km rodado)
    if df_filtrado.dropna(subset=["motivo", "odometro"]).empty:
        motivo_mais = "—"
    else:
        motivo_agrupado = (
            df_filtrado
            .dropna(subset=["motivo", "odometro"])
            .groupby("motivo")["odometro"]
            .sum()
            .sort_values(ascending=False)
        )
        motivo_mais = motivo_agrupado.index[0]

    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.metric("Distância total percorrida (km)", format_number_br(total_odometro, 1))

    with col_m2:
        st.metric("Destino mais usado (km rodados)", destino_mais)

    with col_m3:
        st.metric("Motivo mais usado (km rodados)", motivo_mais)


# ============================
# GRÁFICOS: ODÔMETRO POR ORIGEM / DESTINO
# ============================
st.markdown("---")
st.subheader("Distância por origem e destino")

if not df_filtrado.empty:
    col_g1, col_g2 = st.columns(2)

    # --- Odômetro por origem ---
    with col_g1:
        por_origem = (
            df_filtrado.groupby("origem", dropna=False)["odometro"]
            .sum()
            .reset_index()
        )
        por_origem["origem"] = por_origem["origem"].astype("string")
        por_origem["origem"] = por_origem["origem"].fillna("Não informado")
        por_origem = por_origem.sort_values("odometro", ascending=False)

        fig_origem = px.bar(
            por_origem,
            x="origem",
            y="odometro",
            labels={"origem": "Origem", "odometro": "Distância total (km)"},
            title="Distância por origem",
        )
        fig_origem.update_traces(
            text=por_origem["odometro"].round(1),
            texttemplate="%{text:,.1f} km",
            textposition="outside",
            cliponaxis=False,
        )
        fig_origem.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig_origem, use_container_width=True)

    # --- Odômetro por destino ---
    with col_g2:
        por_destino = (
            df_filtrado.groupby("destino", dropna=False)["odometro"]
            .sum()
            .reset_index()
        )
        por_destino["destino"] = por_destino["destino"].astype("string")
        por_destino["destino"] = por_destino["destino"].fillna("Não informado")
        por_destino = por_destino.sort_values("odometro", ascending=False)

        fig_destino = px.bar(
            por_destino,
            x="destino",
            y="odometro",
            labels={"destino": "Destino", "odometro": "Distância total (km)"},
            title="Distância por destino",
        )
        fig_destino.update_traces(
            text=por_destino["odometro"].round(1),
            texttemplate="%{text:,.1f} km",
            textposition="outside",
            cliponaxis=False,
        )
        fig_destino.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig_destino, use_container_width=True)
else:
    st.info("Sem dados para gráficos por origem/destino.")

# ============================
# GRÁFICOS: ODÔMETRO POR MOTIVO / TIPO DE ROTA
# ============================
st.markdown("---")
st.subheader("Distância por motivo e tipo de rota")

if not df_filtrado.empty:
    col_g3, col_g4 = st.columns(2)

    # --- Odômetro por motivo ---
    with col_g3:
        por_motivo = (
            df_filtrado.groupby("motivo", dropna=False)["odometro"]
            .sum()
            .reset_index()
        )
        por_motivo["motivo"] = por_motivo["motivo"].astype("string")
        por_motivo["motivo"] = por_motivo["motivo"].fillna("Não informado")
        por_motivo = por_motivo.sort_values("odometro", ascending=False)

        fig_motivo = px.bar(
            por_motivo,
            x="motivo",
            y="odometro",
            labels={"motivo": "Motivo", "odometro": "Distância total (km)"},
            title="Distância por motivo",
        )
        fig_motivo.update_traces(
            text=por_motivo["odometro"].round(1),
            texttemplate="%{text:,.1f} km",
            textposition="outside",
            cliponaxis=False,
        )
        fig_motivo.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig_motivo, use_container_width=True)

    # --- Odômetro por tipo de rota (gráfico que já existia, agora turbinado) ---
    with col_g4:
        por_tipo = (
            df_filtrado.groupby("tipo_rota", dropna=False)["odometro"]
            .sum()
            .reset_index()
        )
        # garante que não seja Categorical antes de mexer
        por_tipo["tipo_rota"] = por_tipo["tipo_rota"].astype("string")
        por_tipo["tipo_rota"] = por_tipo["tipo_rota"].fillna("Não informado")
        por_tipo = por_tipo.sort_values("odometro", ascending=False)

        fig_tipo = px.bar(
            por_tipo,
            x="tipo_rota",
            y="odometro",
            labels={"tipo_rota": "Tipo de rota", "odometro": "Distância total (km)"},
            title="Distância por tipo de rota",
        )
        fig_tipo.update_traces(
            text=por_tipo["odometro"].round(1),
            texttemplate="%{text:,.1f} km",
            textposition="outside",
            cliponaxis=False,
        )
        st.plotly_chart(fig_tipo, use_container_width=True)
else:
    st.info("Sem dados para gráficos por motivo/tipo de rota.")

# ============================
# TOTAIS POR ANO / MÊS (SELETOR)
# ============================
st.markdown("---")
st.subheader("Total de distância por período")

if not df_filtrado.empty:

    df_temp = df_filtrado.copy()
    df_temp["data_inicio"] = pd.to_datetime(df_temp["data_inicio"], errors="coerce")
    df_temp = df_temp.dropna(subset=["data_inicio"])
    df_temp["odometro"] = pd.to_numeric(df_temp["odometro"], errors="coerce")

    # seletor
    opcao_periodo = st.radio(
        "Escolha o nível de tempo:",
        ["Ano", "Mês"],
        horizontal=True,
        key="selecionar_periodo_trajetos",
    )

    if opcao_periodo == "Ano":
        df_temp["periodo"] = df_temp["data_inicio"].dt.year.astype(str)
        titulo = "Total percorrido por ano"
    else:
        df_temp["periodo"] = df_temp["data_inicio"].dt.to_period("M").astype(str)
        titulo = "Total percorrido por mês"

    df_tempo = (
        df_temp.groupby("periodo", as_index=False)["odometro"]
        .sum()
        .sort_values("periodo")
    )

    if df_tempo.empty:
        st.info("Sem dados suficientes para montar o gráfico.")
    else:
        fig_tempo = px.bar(
            df_tempo,
            x="periodo",
            y="odometro",
            labels={"periodo": "Período", "odometro": "Distância total (km)"},
            title=titulo,
        )
        fig_tempo.update_traces(
            text=df_tempo["odometro"].round(1),
            texttemplate="%{text:,.1f} km",
            textposition="outside",
            cliponaxis=False,
        )
# ✅ FORÇA EXIBIR TODOS OS RÓTULOS NO EIXO X (principalmente no modo "Mês")
        if opcao_periodo == "Mês":
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
    st.info("Sem dados para totais por período.")


# ============================
# TABELA DE TRAJETOS (DETALHADA)
# ============================
st.markdown("---")
st.subheader("Tabela de Trajetos (detalhada)")

if df_filtrado.empty:
    st.info("Sem dados para exibir na tabela.")
else:
    df_tabela = df_filtrado.copy()

    # Formatação de datas (sem separar data/hora em colunas distintas)
    if "data_inicio" in df_tabela.columns:
        df_tabela["data_inicio"] = pd.to_datetime(df_tabela["data_inicio"], errors="coerce") \
            .dt.strftime("%d-%m-%Y %H:%M")

    if "data_fim" in df_tabela.columns:
        df_tabela["data_fim"] = pd.to_datetime(df_tabela["data_fim"], errors="coerce") \
            .dt.strftime("%d-%m-%Y %H:%M")

    # Formatação numérica
    for col in ["odometro", "odometro_inicial", "odometro_final"]:
        if col in df_tabela.columns:
            df_tabela[col] = pd.to_numeric(df_tabela[col], errors="coerce") \
                .apply(lambda v: format_number_br(v, 1))

    if "custo" in df_tabela.columns:
        df_tabela["custo"] = pd.to_numeric(df_tabela["custo"], errors="coerce") \
            .apply(format_currency_br)

    if "custo_km" in df_tabela.columns:
        df_tabela["custo_km"] = pd.to_numeric(df_tabela["custo_km"], errors="coerce") \
            .apply(lambda v: format_currency_br(v))

    # garante que tipo_rota está presente (já vem do ETL, só não removemos)
    # exibir tabela
    st.dataframe(
        df_tabela,
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    # botão para exportar tabela formatada
    csv_formatado = df_tabela.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar tabela de trajetos formatada (CSV)",
        data=csv_formatado,
        file_name="trajetos_formatados.csv",
        mime="text/csv",
    )