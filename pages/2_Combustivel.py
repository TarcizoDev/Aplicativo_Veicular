import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================
# ESTILO GLOBAL (mesmo padrão)
# ============================
st.markdown(
    """
    <style>
    .block-container { padding-top: 2.5rem !important; padding-bottom: 1.1rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0.15rem !important; margin-bottom: 0.1rem !important; }
    .element-container { margin-bottom: 0.1rem !important; padding-bottom: 0.5rem !important; }
    div[data-testid="stMarkdownContainer"] p { margin-block-start: 0.15rem !important; margin-block-end: 0.15rem !important; }
    h1, h2, h3, h4 { margin-top: 0.15rem !important; margin-bottom: 0.15rem !important; }
    .stColumn { padding-right: 0.15rem !important; padding-left: 0.15rem !important; }

    div[data-testid="stMetric"] { padding: 0.0rem 0.05rem !important; margin: 0.05rem 0 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.72rem !important; margin-bottom: -0.10rem !important; }
    div[data-testid="stMetricValue"] { font-size: 0.88rem !important; font-weight: 600 !important; margin-top: -0.15rem !important; margin-bottom: -0.05rem !important; }
    div[data-testid="stMetricDelta"] { font-size: 0.70rem !important; margin-top: -0.15rem !important; }

    section[data-testid="stSidebar"] { background-color: #c3d0dd !important; color: #1e293b !important; }
    section[data-testid="stSidebar"] label { color: #1e293b !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] button { color: #334155 !important; background-color: transparent !important; }
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] p { color: #475569 !important; }
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stMultiSelect { color: #020617 !important; }
    section[data-testid="stSidebar"] div[data-baseweb="select"] * { color: #020617 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⛽ Combustível – Consumo e Abastecimentos")

if "df_combustivel" not in st.session_state:
    st.error("Nenhum arquivo foi carregado ainda. Volte para a página **Home** e faça o upload do BD.csv.")
    st.stop()

df_combustivel = st.session_state["df_combustivel"].copy()

# Datas
if "data" not in df_combustivel.columns:
    st.error("Coluna 'data' não encontrada no dataframe de combustível.")
    st.stop()

df_combustivel["data"] = pd.to_datetime(df_combustivel["data"], errors="coerce")
if "data_hora" in df_combustivel.columns:
    df_combustivel["data_hora"] = pd.to_datetime(df_combustivel["data_hora"], errors="coerce")

# Colunas novas
cols_necessarias = ["distancia_calculada", "media_calculada_preenchida", "media_acumulada"]
faltando = [c for c in cols_necessarias if c not in df_combustivel.columns]
if faltando:
    st.error(
        "As colunas necessárias não foram encontradas no dataframe de combustível. "
        f"Faltando: {', '.join(faltando)}. "
        "Volte na **Home** e garanta que o ETL foi atualizado e o arquivo reprocessado."
    )
    st.stop()

# Numéricos garantidos
for c in ["custo", "volume_abastecido", "custo_por_litro", "media_calculada_preenchida", "distancia_calculada", "media_acumulada"]:
    if c in df_combustivel.columns:
        df_combustivel[c] = pd.to_numeric(df_combustivel[c], errors="coerce")

st.markdown("---")

# ============================
# FILTROS GLOBAIS (ANO / MÊS) - SIDEBAR
# ============================
with st.sidebar:
    st.markdown("### Filtros de período")

    serie_data = df_combustivel["data"]
    anos_disponiveis = sorted(serie_data.dropna().dt.year.unique().tolist())

    if anos_disponiveis:
        opcoes_ano = ["Todos"] + [str(a) for a in anos_disponiveis]
        ano_sel = st.selectbox("Ano", opcoes_ano, key="filtro_ano_combustivel")

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
            key="filtro_meses_combustivel",
        )
        meses_sel = [map_label_to_month[l] for l in meses_sel_labels]

        mask = serie_data.notna()
        if ano_sel != "Todos":
            mask &= serie_data.dt.year == int(ano_sel)
        if meses_sel:
            mask &= serie_data.dt.month.isin(meses_sel)

        df_periodo = df_combustivel.loc[mask].copy()
    else:
        df_periodo = df_combustivel.copy()

# ============================
# FILTROS ESPECÍFICOS (COMBUSTÍVEL / POSTO / MOTIVO)
# ============================
st.subheader("Filtros de Abastecimentos")

col1, col2, col3 = st.columns(3)

with col1:
    combustiveis = ["(Todos)"] + sorted(df_periodo["combustivel"].dropna().unique().tolist())
    combustivel_sel = st.selectbox("Tipo de combustível", combustiveis)

with col2:
    postos = ["(Todos)"] + sorted(df_periodo["posto"].dropna().unique().tolist())
    posto_sel = st.selectbox("Posto", postos)

with col3:
    motivos = ["(Todos)"] + sorted(df_periodo["motivo"].dropna().unique().tolist())
    motivo_sel = st.selectbox("Motivo", motivos)

df_filtrado = df_periodo.copy()
if combustivel_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["combustivel"] == combustivel_sel]
if posto_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["posto"] == posto_sel]
if motivo_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["motivo"] == motivo_sel]

st.markdown("---")

# ============================
# FUNÇÕES DE FORMATAÇÃO
# ============================
def format_currency_br(x):
    if pd.isna(x):
        return ""
    return "R$ " + (f"{float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

def format_number_br(x, decimals=1):
    if pd.isna(x):
        return ""
    return (f"{float(x):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", "."))

# ============================
# MÉTRICAS RESUMO
# ============================
st.subheader("Resumo dos Abastecimentos")

if df_filtrado.empty:
    st.info("Nenhum dado disponível para o período/filtros selecionados.")
else:
    total_gasto = pd.to_numeric(df_filtrado["custo"], errors="coerce").sum()
    total_volume = pd.to_numeric(df_filtrado["volume_abastecido"], errors="coerce").sum()

    medias_validas = pd.to_numeric(df_filtrado["media_calculada_preenchida"], errors="coerce").dropna()
    medias_validas = medias_validas[medias_validas > 0]
    menor_media = medias_validas.min() if not medias_validas.empty else 0
    maior_media = medias_validas.max() if not medias_validas.empty else 0

    # ✅ média total do veículo = última média acumulada válida (mais recente)
    eixo_data = "data_hora" if "data_hora" in df_filtrado.columns else "data"
    df_ord_media_total = df_filtrado.dropna(subset=[eixo_data]).sort_values(eixo_data)
    media_total = (
        pd.to_numeric(df_ord_media_total["media_acumulada"], errors="coerce")
        .dropna()
        .iloc[-1]
        if not df_ord_media_total.empty and df_ord_media_total["media_acumulada"].notna().any()
        else np.nan
    )

    qtd_abastecimentos = len(df_filtrado)

    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    with col_m1:
        st.metric("Total gasto (R$)", format_currency_br(total_gasto))
    with col_m2:
        st.metric("Volume abastecido (L)", format_number_br(total_volume, 1))
    with col_m3:
        st.metric("Menor média (Km/L)", format_number_br(menor_media, 2))
    with col_m4:
        st.metric("Maior média (Km/L)", format_number_br(maior_media, 2))
    with col_m5:
        st.metric("Média total (Km/L)", format_number_br(media_total, 2) if media_total == media_total else "")
    with col_m6:
        st.metric("Qtd. abastecimentos", int(qtd_abastecimentos))

# ============================
# GRÁFICOS DE PIZZA (TIPO / MOTIVO)
# ============================
st.markdown("---")
st.subheader("Distribuição dos Abastecimentos")

if not df_filtrado.empty:
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        df_tipo = (
            df_filtrado.groupby("combustivel", dropna=False)["volume_abastecido"]
            .sum()
            .reset_index()
        )
        df_tipo["combustivel"] = df_tipo["combustivel"].fillna("Não informado")

        fig_pizza_tipo = px.pie(
            df_tipo,
            names="combustivel",
            values="volume_abastecido",
            title="Volume abastecido por tipo de combustível",
            hole=0.4,
        )
        fig_pizza_tipo.update_traces(textposition="inside", texttemplate="%{label}<br>%{percent:.1%}")
        st.plotly_chart(fig_pizza_tipo, use_container_width=False)

    with col_p2:
        df_motivo = (
            df_filtrado.groupby("motivo", dropna=False)["volume_abastecido"]
            .sum()
            .reset_index()
        )
        df_motivo["motivo"] = df_motivo["motivo"].fillna("Não informado")

        fig_pizza_motivo = px.pie(
            df_motivo,
            names="motivo",
            values="volume_abastecido",
            title="Volume abastecido por motivo",
            hole=0.4,
        )
        fig_pizza_motivo.update_traces(textposition="inside", texttemplate="%{label}<br>%{percent:.1%}")
        st.plotly_chart(fig_pizza_motivo, use_container_width=False)
else:
    st.info("Sem dados para gráficos de distribuição.")

# ============================
# GRÁFICOS POR PERÍODO (Ano / Mês)
# ============================
st.markdown("---")
st.subheader("Totais e indicadores por período")

def construir_media_acumulada_continua(df_base: pd.DataFrame, nivel: str):
    """
    Regras:
    1) eixo X categórico contínuo (preenche meses/anos sem dados repetindo o valor anterior)
    2) valor do período = media_acumulada do registro mais novo daquele período
    3) retorna dataframe: periodo, periodo_ord, media_acumulada_periodo
    """
    dfb = df_base.copy()
    dfb = dfb.dropna(subset=["data"])
    eixo_data = "data_hora" if "data_hora" in dfb.columns else "data"
    dfb = dfb.sort_values(eixo_data)

    if nivel == "Ano":
        dfb["periodo_ord"] = dfb["data"].dt.to_period("Y").dt.to_timestamp()
        dfb["periodo"] = dfb["data"].dt.year.astype(str)
        freq = "YS"
    else:
        dfb["periodo_ord"] = dfb["data"].dt.to_period("M").dt.to_timestamp()
        dfb["periodo"] = dfb["data"].dt.to_period("M").astype(str)
        freq = "MS"

    ult = (
        dfb.groupby("periodo", as_index=False)
        .apply(lambda g: g.sort_values(eixo_data).tail(1))
        .reset_index(drop=True)
        .loc[:, ["periodo", "periodo_ord", "media_acumulada"]]
        .rename(columns={"media_acumulada": "media_acumulada_periodo"})
        .sort_values("periodo_ord")
    )

    if ult.empty:
        return ult

    inicio = ult["periodo_ord"].min()
    fim = ult["periodo_ord"].max()
    idx = pd.date_range(inicio, fim, freq=freq)

    full = pd.DataFrame({"periodo_ord": idx})
    if nivel == "Ano":
        full["periodo"] = full["periodo_ord"].dt.year.astype(str)
    else:
        full["periodo"] = full["periodo_ord"].dt.to_period("M").astype(str)

    full = full.merge(ult, on=["periodo", "periodo_ord"], how="left")
    full["media_acumulada_periodo"] = full["media_acumulada_periodo"].ffill()

    return full


def adicionar_rotulos_linha(fig: go.Figure, x_vals, y_vals, fmt="{:.2f}"):
    """
    Adiciona rótulos de dados em uma série de linha (Scatter) usando mode 'lines+markers+text'.
    """
    texts = []
    for v in y_vals:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            texts.append("")
        else:
            texts.append(fmt.format(float(v)).replace(".", ","))
    fig.update_traces(
        mode="lines+markers+text",
        text=texts,
        textposition="top center",
        textfont=dict(size=10),
        selector=dict(type="scatter"),
    )
    return fig


if not df_filtrado.empty:
    df_temp = df_filtrado.copy()
    df_temp["data"] = pd.to_datetime(df_temp["data"], errors="coerce")
    df_temp = df_temp.dropna(subset=["data"])

    opcao_tempo_comb = st.radio(
        "Nível de tempo",
        ["Ano", "Mês"],
        horizontal=True,
        key="nivel_tempo_combustivel",
    )

    titulo_x = "Ano" if opcao_tempo_comb == "Ano" else "Mês"

    # agregação para custo/volume/média janela
    if opcao_tempo_comb == "Ano":
        df_temp["periodo"] = df_temp["data"].dt.year.astype(str)
        df_temp["periodo_ord"] = pd.to_datetime(df_temp["periodo"] + "-01-01", errors="coerce")
    else:
        df_temp["periodo"] = df_temp["data"].dt.to_period("M").astype(str)
        df_temp["periodo_ord"] = pd.to_datetime(df_temp["periodo"] + "-01", errors="coerce")

    agg = (
        df_temp.groupby("periodo", as_index=False)
        .agg(
            periodo_ord=("periodo_ord", "min"),
            custo=("custo", "sum"),
            volume_abastecido=("volume_abastecido", "sum"),
            media_media=("media_calculada_preenchida", "mean"),
        )
        .sort_values("periodo_ord")
    )

    if agg.empty:
        st.info("Sem dados para os gráficos por período.")
    else:
        periodos = agg["periodo"].tolist()

        fig_gasto = px.bar(
            agg,
            x="periodo",
            y="custo",
            labels={"periodo": titulo_x, "custo": "Custo total (R$)"},
            title=f"Total gasto por {titulo_x.lower()}",
            category_orders={"periodo": periodos},
        )
        fig_gasto.update_traces(
            text=agg["custo"].round(2),
            texttemplate="R$ %{text:,.2f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig_gasto.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=periodos,
            tickmode="array",
            tickvals=periodos,
            ticktext=periodos,
            tickangle=-45,
        )
        fig_gasto.update_layout(margin=dict(b=80))
        st.plotly_chart(fig_gasto, use_container_width=True)

        col_g3, col_g4 = st.columns(2)

        with col_g3:
            fig_litros = px.bar(
                agg,
                x="periodo",
                y="volume_abastecido",
                labels={"periodo": titulo_x, "volume_abastecido": "Volume (L)"},
                title=f"Volume abastecido por {titulo_x.lower()}",
                category_orders={"periodo": periodos},
            )
            fig_litros.update_traces(
                text=agg["volume_abastecido"].round(1),
                texttemplate="%{text:,.1f} L",
                textposition="outside",
                cliponaxis=False,
            )
            fig_litros.update_xaxes(
                type="category",
                categoryorder="array",
                categoryarray=periodos,
                tickmode="array",
                tickvals=periodos,
                ticktext=periodos,
                tickangle=-45,
            )
            fig_litros.update_layout(margin=dict(b=80))
            st.plotly_chart(fig_litros, use_container_width=True)

        with col_g4:
            fig_media_periodo = px.line(
                agg,
                x="periodo",
                y="media_media",
                markers=True,
                labels={"periodo": titulo_x, "media_media": "Média (km/L)"},
                title=f"Média de consumo (média das janelas) por {titulo_x.lower()}",
                category_orders={"periodo": periodos},
            )
            fig_media_periodo.update_xaxes(
                type="category",
                categoryorder="array",
                categoryarray=periodos,
                tickmode="array",
                tickvals=periodos,
                ticktext=periodos,
                tickangle=-45,
            )
            fig_media_periodo.update_layout(margin=dict(b=80))
            y_max = float(pd.to_numeric(agg["media_media"], errors="coerce").max() or 0)
            fig_media_periodo.update_yaxes(range=[0, y_max * 1.1 if y_max > 0 else 1])

            # ✅ rótulos de dados na linha
            fig_media_periodo = adicionar_rotulos_linha(fig_media_periodo, agg["periodo"], agg["media_media"], fmt="{:.2f}")

            st.plotly_chart(fig_media_periodo, use_container_width=True)

        st.markdown("#### Volume abastecido por período (empilhado por combustível)")

        df_stack = (
            df_temp.groupby(["periodo", "combustivel"], dropna=False)["volume_abastecido"]
            .sum()
            .reset_index()
        )
        df_stack["combustivel"] = df_stack["combustivel"].fillna("Não informado")

        fig_stack = px.bar(
            df_stack,
            x="periodo",
            y="volume_abastecido",
            color="combustivel",
            barmode="stack",
            category_orders={"periodo": periodos},
            labels={"periodo": titulo_x, "volume_abastecido": "Volume (L)", "combustivel": "Combustível"},
            title=f"Volume abastecido por {titulo_x.lower()} (empilhado)",
        )
        fig_stack.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=periodos,
            tickmode="array",
            tickvals=periodos,
            ticktext=periodos,
            tickangle=-45,
        )
        fig_stack.update_layout(margin=dict(b=80))
        st.plotly_chart(fig_stack, use_container_width=True)

        st.markdown("#### Preço do combustível (média, mínimo e máximo)")

        preco = (
            df_temp.groupby("periodo", as_index=False)
            .agg(
                periodo_ord=("periodo_ord", "min"),
                preco_medio=("custo_por_litro", "mean"),
                preco_min=("custo_por_litro", "min"),
                preco_max=("custo_por_litro", "max"),
            )
            .sort_values("periodo_ord")
        )

        fig_preco = go.Figure()
        fig_preco.add_trace(go.Scatter(x=preco["periodo"], y=preco["preco_medio"], mode="lines+markers", name="Preço médio"))
        fig_preco.add_trace(go.Scatter(x=preco["periodo"], y=preco["preco_min"], mode="lines+markers", name="Preço mínimo"))
        fig_preco.add_trace(go.Scatter(x=preco["periodo"], y=preco["preco_max"], mode="lines+markers", name="Preço máximo"))

        fig_preco.update_layout(
            title=f"Preço por {titulo_x.lower()} (R$/L)",
            xaxis_title=titulo_x,
            yaxis_title="R$/L",
            margin=dict(b=80),
        )
        fig_preco.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=periodos,
            tickmode="array",
            tickvals=periodos,
            ticktext=periodos,
            tickangle=-45,
        )
        st.plotly_chart(fig_preco, use_container_width=True)

        # =========================================================
        # NOVO GRÁFICO: MÉDIA ACUMULADA POR PERÍODO (CONTÍNUO)
        # =========================================================
        st.markdown("#### Média de consumo acumulada por período (usando último registro do período)")

        serie_acum = construir_media_acumulada_continua(df_temp, opcao_tempo_comb)

        if serie_acum.empty or serie_acum["media_acumulada_periodo"].dropna().empty:
            st.info("Sem dados suficientes para plotar a média acumulada por período.")
        else:
            periodos_acum = serie_acum["periodo"].tolist()

            fig_media_acum = px.line(
                serie_acum,
                x="periodo",
                y="media_acumulada_periodo",
                markers=True,
                labels={"periodo": titulo_x, "media_acumulada_periodo": "Média acumulada (km/L)"},
                title=f"Média acumulada por {titulo_x.lower()} (contínuo)",
                category_orders={"periodo": periodos_acum},
            )
            fig_media_acum.update_xaxes(
                type="category",
                categoryorder="array",
                categoryarray=periodos_acum,
                tickmode="array",
                tickvals=periodos_acum,
                ticktext=periodos_acum,
                tickangle=-45,
            )
            fig_media_acum.update_layout(margin=dict(b=80))

            y_max = float(pd.to_numeric(serie_acum["media_acumulada_periodo"], errors="coerce").max() or 0)
            fig_media_acum.update_yaxes(range=[0, y_max * 1.1 if y_max > 0 else 1])

            # ✅ rótulos de dados na linha
            fig_media_acum = adicionar_rotulos_linha(fig_media_acum, serie_acum["periodo"], serie_acum["media_acumulada_periodo"], fmt="{:.2f}")

            st.plotly_chart(fig_media_acum, use_container_width=True)

else:
    st.info("Sem dados para gráficos por período.")

# ============================
# RESUMO DOS ABASTECIMENTOS - TABELA
# ============================
st.markdown("---")
st.subheader("Resumo dos Abastecimentos (mensal)")

def criar_resumo_abastecimentos(df):
    df2 = df.copy()
    df2["data"] = pd.to_datetime(df2["data"], errors="coerce")
    df2 = df2.dropna(subset=["data"])

    df2["mes_ano"] = df2["data"].dt.strftime("%b/%y")
    df2["ordem_data"] = df2["data"].dt.to_period("M").dt.to_timestamp()

    resumo = (
        df2.groupby(["mes_ano", "ordem_data"])
        .agg(
            {
                "custo": "sum",
                "volume_abastecido": "sum",
                "custo_por_litro": ["mean", "min", "max"],
                "media_calculada_preenchida": ["mean", "min", "max"],
                "data": "count",
                "distancia_calculada": "sum",
            }
        )
        .reset_index()
    )

    resumo.columns = [
        "Mês Ano",
        "Data Ordenada",
        "Custo",
        "Volume abastecido",
        "Custo Médio",
        "Custo Minimo",
        "Custo Máximo",
        "Média Consumo (calc)",
        "Mínimo da média (calc)",
        "Máx da média (calc)",
        "Contagem",
        "Distância (calc)",
    ]

    resumo = resumo.sort_values("Data Ordenada").drop(columns=["Data Ordenada"])
    return resumo

if not df_filtrado.empty:
    resumo_num = criar_resumo_abastecimentos(df_filtrado)

    resumo_fmt = resumo_num.copy()
    resumo_fmt["Custo"] = resumo_fmt["Custo"].apply(format_currency_br)
    resumo_fmt["Volume abastecido"] = resumo_fmt["Volume abastecido"].apply(
        lambda v: format_number_br(v, 1) + " L" if v == v else ""
    )

    for c in ["Custo Médio", "Custo Minimo", "Custo Máximo"]:
        resumo_fmt[c] = resumo_fmt[c].apply(lambda v: format_currency_br(v) if v == v else "")

    for c in ["Média Consumo (calc)", "Mínimo da média (calc)", "Máx da média (calc)"]:
        resumo_fmt[c] = resumo_fmt[c].apply(lambda v: format_number_br(v, 3) + " Km/L" if v == v else "")

    resumo_fmt["Contagem"] = resumo_fmt["Contagem"].apply(lambda v: str(int(v)) if v == v else "")

    resumo_fmt["Distância (calc)"] = resumo_fmt["Distância (calc)"].apply(
        lambda v: format_number_br(v, 1) + " km" if v == v else ""
    )

    acumulado = {
        "Mês Ano": "Acumulado",
        "Custo": format_currency_br(resumo_num["Custo"].sum()),
        "Volume abastecido": format_number_br(resumo_num["Volume abastecido"].sum(), 1) + " L",
        "Custo Médio": format_currency_br(resumo_num["Custo Médio"].mean()),
        "Custo Minimo": format_currency_br(resumo_num["Custo Minimo"].min()),
        "Custo Máximo": format_currency_br(resumo_num["Custo Máximo"].max()),
        "Média Consumo (calc)": format_number_br(resumo_num["Média Consumo (calc)"].mean(), 3) + " Km/L",
        "Mínimo da média (calc)": format_number_br(resumo_num["Mínimo da média (calc)"].min(), 3) + " Km/L",
        "Máx da média (calc)": format_number_br(resumo_num["Máx da média (calc)"].max(), 3) + " Km/L",
        "Contagem": str(int(resumo_num["Contagem"].sum())),
        "Distância (calc)": format_number_br(resumo_num["Distância (calc)"].sum(), 1) + " km",
    }

    resumo_fmt.loc[len(resumo_fmt)] = acumulado

    st.dataframe(
        resumo_fmt,
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    csv_resumo = resumo_fmt.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar resumo formatado (CSV)",
        data=csv_resumo,
        file_name="resumo_abastecimentos_formatado.csv",
        mime="text/csv",
    )
else:
    st.info("Sem dados para montar o resumo de abastecimentos.")