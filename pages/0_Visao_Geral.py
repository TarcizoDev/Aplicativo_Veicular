import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================
# ESTILO GLOBAL
# ============================
st.markdown(
    """
    <style>
    /* ================================
       AJUSTES GERAIS DA PÁGINA
       ================================ */

    /* padding geral da área principal */
    .block-container {
        padding-top: 1.9rem !important;
        padding-bottom: 1.1rem !important;
    }

    /* cada "bloco" vertical padrão do Streamlit (linha) */
    div[data-testid="stVerticalBlock"] {
        gap: 0.15rem !important;  /* espaço entre os elementos empilhados */
        margin-bottom: 0.1rem !important;
    }

    /* containers internos dos elementos (markdown, métricas, etc) */
    .element-container {
        margin-bottom: 0.1rem !important;
        padding-bottom: 0.5rem !important;
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



st.title("🏁 Visão Geral – Uso e Custos do Veículo")

# ============================
# VERIFICA DATAFRAMES CARREGADOS
# ============================
required_keys = ["df_despesas", "df_combustivel", "df_servicos", "df_rotas"]
missing = [k for k in required_keys if k not in st.session_state]

if missing:
    st.error(
        "Alguns dados ainda não foram carregados. "
        "Volte para a página **Home** e faça o upload do arquivo BD.csv."
    )
    st.stop()

df_despesas = st.session_state["df_despesas"].copy()
df_combustivel = st.session_state["df_combustivel"].copy()
df_servicos = st.session_state["df_servicos"].copy()
df_rotas = st.session_state["df_rotas"].copy()

# ============================
# FUNÇÕES DE FORMATAÇÃO
# ============================
def format_currency_br(x):
    if pd.isna(x):
        return "R$ 0,00"
    return "R$ " + (
        f"{float(x):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

def format_number_br(x, decimals=1):
    if pd.isna(x):
        return "0"
    return (
        f"{float(x):,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

# ============================
# GARANTE COLUNAS DE DATA E NÚMEROS
# ============================
# datas
if "data" in df_despesas.columns:
    df_despesas["data"] = pd.to_datetime(df_despesas["data"], errors="coerce")
if "data" in df_combustivel.columns:
    df_combustivel["data"] = pd.to_datetime(df_combustivel["data"], errors="coerce")
if "data" in df_servicos.columns:
    df_servicos["data"] = pd.to_datetime(df_servicos["data"], errors="coerce")
if "data_inicio" in df_rotas.columns:
    df_rotas["data_inicio"] = pd.to_datetime(df_rotas["data_inicio"], errors="coerce")

# numéricos
for df, col in [
    (df_despesas, "custo"),
    (df_combustivel, "custo"),
    (df_servicos, "custo"),
    (df_rotas, "custo"),
    (df_rotas, "odometro"),
    (df_rotas, "odometro_inicial"),
    (df_rotas, "odometro_final"),
]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ============================
# FILTROS GLOBAIS (ANO / MÊS) - SIDEBAR
# ============================
with st.sidebar:
    st.markdown("### Filtros de período")

    # junta todas as datas disponíveis num único vetor pra montar os filtros
    series_datas = []

    if "data" in df_despesas.columns:
        series_datas.append(df_despesas["data"])
    if "data" in df_combustivel.columns:
        series_datas.append(df_combustivel["data"])
    if "data" in df_servicos.columns:
        series_datas.append(df_servicos["data"])
    if "data_inicio" in df_rotas.columns:
        series_datas.append(df_rotas["data_inicio"])

    if series_datas:
        serie_data_global = pd.concat(series_datas).dropna()
        if not serie_data_global.empty:
            anos_disponiveis = sorted(serie_data_global.dt.year.unique().tolist())
        else:
            anos_disponiveis = []
    else:
        anos_disponiveis = []

    if anos_disponiveis:
        opcoes_ano = ["Todos"] + [str(a) for a in anos_disponiveis]
        ano_sel = st.selectbox("Ano", opcoes_ano, key="filtro_ano_geral")

        meses_nomes = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
            5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
        }

        meses_disponiveis = sorted(serie_data_global.dt.month.unique().tolist())
        meses_labels = [f"{meses_nomes[m]} ({m})" for m in meses_disponiveis]
        map_label_to_month = dict(zip(meses_labels, meses_disponiveis))

        meses_sel_labels = st.multiselect(
            "Meses",
            meses_labels,
            default=meses_labels,
            key="filtro_meses_geral",
        )
        meses_sel = [map_label_to_month[l] for l in meses_sel_labels]
    else:
        ano_sel = "Todos"
        meses_sel = []

# ============================
# APLICA FILTRO GLOBAL EM CADA DF
# ============================
def filtrar_por_periodo(df, col_data, ano_sel, meses_sel):
    if col_data not in df.columns:
        return df.copy()
    s = pd.to_datetime(df[col_data], errors="coerce")
    mask = s.notna()
    if anos_disponiveis:
        if ano_sel != "Todos":
            mask &= s.dt.year == int(ano_sel)
        if meses_sel:
            mask &= s.dt.month.isin(meses_sel)
    return df.loc[mask].copy()

df_despesas_f = filtrar_por_periodo(df_despesas, "data", ano_sel, meses_sel)
df_combustivel_f = filtrar_por_periodo(df_combustivel, "data", ano_sel, meses_sel)
df_servicos_f = filtrar_por_periodo(df_servicos, "data", ano_sel, meses_sel)
df_rotas_f = filtrar_por_periodo(df_rotas, "data_inicio", ano_sel, meses_sel)

# ============================
# BLOCO 1 – RESUMO DE CUSTOS
# ============================
st.markdown("---")
st.markdown("## 💸 - Resumo de Despesas")

# --- Totais gerais por categoria (já filtrados) ---
total_despesas = df_despesas_f["custo"].sum() if "custo" in df_despesas_f.columns else 0
total_combustivel = df_combustivel_f["custo"].sum() if "custo" in df_combustivel_f.columns else 0
total_servicos = df_servicos_f["custo"].sum() if "custo" in df_servicos_f.columns else 0

total_geral = total_despesas + total_combustivel + total_servicos

st.markdown("#### Totais por tipo de gasto")

col_t1, col_t2, col_t3, col_t4 = st.columns(4)

with col_t1:
    st.metric("Total Geral (R$)", format_currency_br(total_geral))

with col_t2:
    st.metric("Despesas (R$)", format_currency_br(total_despesas))

with col_t3:
    st.metric("Combustível (R$)", format_currency_br(total_combustivel))

with col_t4:
    st.metric("Serviços (R$)", format_currency_br(total_servicos))

# --- Custo por km rodado ---
st.markdown("#### Custo por km rodado")

total_km = df_rotas_f["odometro"].sum() if "odometro" in df_rotas_f.columns else 0

def custo_por_km(custo_total, km_total):
    if not km_total or km_total == 0:
        return 0.0
    return custo_total / km_total

custo_geral_km = custo_por_km(total_geral, total_km)
custo_desp_km = custo_por_km(total_despesas, total_km)
custo_comb_km = custo_por_km(total_combustivel, total_km)
custo_serv_km = custo_por_km(total_servicos, total_km)

col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    st.metric("Custo geral por km", f"{format_currency_br(custo_geral_km)} / km")

with col_k2:
    st.metric("Custo de despesas por km", f"{format_currency_br(custo_desp_km)} / km")

with col_k3:
    st.metric("Custo de combustível por km", f"{format_currency_br(custo_comb_km)} / km")

with col_k4:
    st.metric("Custo de serviços por km", f"{format_currency_br(custo_serv_km)} / km")

# --- Maiores categorias de gasto (por soma) ---
st.markdown("#### Maiores fontes de gastos")

# maior despesa (tipo_despesa)
if "tipo_despesa" in df_despesas_f.columns and not df_despesas_f.empty:
    grupo_desp = (
        df_despesas_f.groupby("tipo_despesa", dropna=True)["custo"]
        .sum()
        .sort_values(ascending=False)
    )
    maior_tipo_desp = grupo_desp.index[0]
    maior_valor_desp = grupo_desp.iloc[0]
else:
    maior_tipo_desp, maior_valor_desp = "—", 0

# maior serviço (tipo_servico)
if "tipo_servico" in df_servicos_f.columns and not df_servicos_f.empty:
    grupo_serv = (
        df_servicos_f.groupby("tipo_servico", dropna=True)["custo"]
        .sum()
        .sort_values(ascending=False)
    )
    maior_tipo_serv = grupo_serv.index[0]
    maior_valor_serv = grupo_serv.iloc[0]
else:
    maior_tipo_serv, maior_valor_serv = "—", 0

# tipo de combustível com maior gasto
if "combustivel" in df_combustivel_f.columns and not df_combustivel_f.empty:
    grupo_comb = (
        df_combustivel_f.groupby("combustivel", dropna=True)["custo"]
        .sum()
        .sort_values(ascending=False)
    )
    maior_tipo_comb = grupo_comb.index[0]
    maior_valor_comb = grupo_comb.iloc[0]
else:
    maior_tipo_comb, maior_valor_comb = "—", 0

col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.metric(
        "Maior despesa",
        maior_tipo_desp if maior_tipo_desp else "—",
        help="Tipo de despesa com maior gasto acumulado",
    )
    st.caption(f"Total gasto: {format_currency_br(maior_valor_desp)}")

with col_m2:
    st.metric(
        "Maior serviço",
        maior_tipo_serv if maior_tipo_serv else "—",
        help="Tipo de serviço/manutenção com maior gasto acumulado",
    )
    st.caption(f"Total gasto: {format_currency_br(maior_valor_serv)}")

with col_m3:
    st.metric(
        "Combustível mais usado",
        maior_tipo_comb if maior_tipo_comb else "—",
        help="Tipo de combustível com maior gasto acumulado",
    )
    st.caption(f"Total gasto: {format_currency_br(maior_valor_comb)}")

# --- GRÁFICOS GERAIS (Pizza + Ano/Mês) ---
st.markdown("#### Distribuição e evolução dos gastos")

col_g1, col_g2 = st.columns(2)

with col_g1:
    # gráfico de pizza por categoria (Despesas, Combustível, Serviços)
    df_cat = pd.DataFrame(
        {
            "Categoria": ["Despesas", "Combustível", "Serviços"],
            "Custo": [total_despesas, total_combustivel, total_servicos],
        }
    )
    df_cat = df_cat[df_cat["Custo"] > 0]

    if df_cat.empty:
        st.info("Sem valores para montar o gráfico de pizza de categorias.")
    else:
        fig_pizza = px.pie(
            df_cat,
            names="Categoria",
            values="Custo",
            title="Participação de cada categoria no total",
            hole=0.4,
        )
        fig_pizza.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%}<br>R$ %{value:,.2f}",
        )
        fig_pizza.update_layout(height=360)
        st.plotly_chart(fig_pizza, use_container_width=True)

with col_g2:
    # gráfico de barras por Ano/Mês (total de gastos somando todas as categorias)
    dfs_all = []

    for df_src in [df_despesas_f, df_combustivel_f, df_servicos_f]:
        if not df_src.empty and "data" in df_src.columns and "custo" in df_src.columns:
            tmp = df_src[["data", "custo"]].copy()
            dfs_all.append(tmp)

    if not dfs_all:
        st.info("Sem dados para montar o gráfico por período.")
    else:
        df_all = pd.concat(dfs_all)
        df_all["data"] = pd.to_datetime(df_all["data"], errors="coerce")
        df_all = df_all.dropna(subset=["data"])

        opcao_tempo = st.radio(
            "Nível de tempo",
            ["Ano", "Mês"],
            horizontal=True,
            key="nivel_tempo_visao_geral",
        )

        if opcao_tempo == "Ano":
            df_all["periodo"] = df_all["data"].dt.year.astype(str)
            titulo_tempo = "Total de gastos por ano"
        else:
            df_all["periodo"] = df_all["data"].dt.to_period("M").astype(str)
            titulo_tempo = "Total de gastos por mês"

        df_tempo = (
            df_all.groupby("periodo", as_index=False)["custo"]
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
            if opcao_tempo == "Mês":
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

            fig_totais.update_layout(height=360)
            st.plotly_chart(fig_totais, use_container_width=True)

# ============================
# BLOCO 2 – RESUMO DE USO (TRAJETOS)
# ============================
st.markdown("---")
st.markdown("## 🗺️ – Resumo de Uso do Veículo")

# --- Distância total, menor e maior hodômetro ---
st.markdown("#### Distância e hodômetros")

if df_rotas_f.empty:
    st.info("Nenhum trajeto registrado para o período selecionado.")
else:
    odometro_total = df_rotas_f["odometro"].sum() if "odometro" in df_rotas_f.columns else 0

    menor_hodometro = (
        df_rotas_f["odometro_inicial"].min()
        if "odometro_inicial" in df_rotas_f.columns
        else None
    )
    maior_hodometro = (
        df_rotas_f["odometro_final"].max()
        if "odometro_final" in df_rotas_f.columns
        else None
    )

    col_u1, col_u2, col_u3 = st.columns(3)

    with col_u1:
        st.metric(
            "Distância total percorrida (km)",
            format_number_br(odometro_total, 1),
        )

    with col_u2:
        st.metric(
            "Menor hodômetro registrado",
            format_number_br(menor_hodometro, 0),
        )

    with col_u3:
        st.metric(
            "Maior hodômetro registrado",
            format_number_br(maior_hodometro, 0),
        )

# --- Top 3 destinos e motivos (por km rodados) ---
st.markdown("#### Top 3 destinos e motivos")

col_top1, col_top2 = st.columns(2)

# TOP 3 DESTINOS ---------------------------------------------------------
with col_top1:
    st.markdown("**Top 3 destinos (por km rodados)**")
    if (
        "destino" in df_rotas_f.columns
        and "odometro" in df_rotas_f.columns
        and not df_rotas_f.empty
    ):
        df_tmp_dest = df_rotas_f.dropna(subset=["destino", "odometro"]).copy()
        if df_tmp_dest.empty:
            st.write("Sem dados de destino com odômetro válido para o período selecionado.")
        else:
            top_dest = (
                df_tmp_dest.groupby("destino", dropna=False)["odometro"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
                .reset_index()
            )
            top_dest["km_fmt"] = top_dest["odometro"].apply(
                lambda v: format_number_br(v, 1)
            )

            fig_top_dest = px.bar(
                top_dest,
                x="odometro",
                y="destino",
                orientation="h",
                labels={"destino": "Destino", "odometro": "Distância (km)"},
                title="Destinos com maior distância",
            )
            fig_top_dest.update_traces(
                text=top_dest["km_fmt"],
                texttemplate="%{text} km",
                textposition="outside",
                cliponaxis=False,
            )
            # 1) margem extra (principalmente à direita)
            fig_top_dest.update_layout(
                yaxis=dict(categoryorder="total ascending", automargin=True),
                xaxis=dict(automargin=True),
                margin=dict(l=10, r=60, t=40, b=10),  # aumenta 'r' se ainda cortar
            )
            # 2) dá "folga" no eixo X para caber o texto outside
            max_x = float(top_dest["odometro"].max()) if not top_dest.empty else 0.0
            fig_top_dest.update_xaxes(range=[0, max_x * 1.20])  # 20% de folga

            st.plotly_chart(fig_top_dest, use_container_width=True, key="top_destinos")
    else:
        st.write("Sem dados de destino para o período selecionado.")

# TOP 3 MOTIVOS ----------------------------------------------------------
with col_top2:
    st.markdown("**Top 3 motivos (por km rodados)**")
    if (
        "motivo" in df_rotas_f.columns
        and "odometro" in df_rotas_f.columns
        and not df_rotas_f.empty
    ):
        df_tmp_mot = df_rotas_f.dropna(subset=["motivo", "odometro"]).copy()
        if df_tmp_mot.empty:
            st.write("Sem dados de motivo com odômetro válido para o período selecionado.")
        else:
            top_mot = (
                df_tmp_mot.groupby("motivo", dropna=False)["odometro"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
                .reset_index()
            )
            top_mot["km_fmt"] = top_mot["odometro"].apply(
                lambda v: format_number_br(v, 1)
            )

            fig_top_mot = px.bar(
                top_mot,
                x="odometro",
                y="motivo",
                orientation="h",
                labels={"motivo": "Motivo", "odometro": "Distância (km)"},
                title="Motivos com maior distância",
            )
            fig_top_mot.update_traces(
                text=top_mot["km_fmt"],
                texttemplate="%{text} km",
                textposition="outside",
                cliponaxis=False,
            )
            # 1) margem extra (principalmente à direita)
            fig_top_mot.update_layout(
                yaxis=dict(categoryorder="total ascending", automargin=True),
                xaxis=dict(automargin=True),
                margin=dict(l=10, r=60, t=40, b=10),  # aumenta 'r' se ainda cortar
            )
            # 2) dá "folga" no eixo X para caber o texto outside
            max_x2 = float(top_mot["odometro"].max()) if not top_mot.empty else 0.0
            fig_top_mot.update_xaxes(range=[0, max_x2 * 1.20])  # 20% de folga

            st.plotly_chart(fig_top_mot, use_container_width=True, key="top_motivos")
    else:
        st.write("Sem dados de motivo para o período selecionado.")

# ============================
# EVOLUÇÃO DO CUSTO POR KM (ACUMULADO)
# ============================
st.markdown("---")
st.markdown("## 📈 – Evolução do Custo por Km (acumulado)")

# seletor de nível de tempo (igual padrão do app)
nivel_tempo_ckm = st.radio(
    "Nível de tempo",
    ["Ano", "Mês"],
    horizontal=True,
    key="nivel_tempo_custo_km",
)

def _agrupar_custo(df, col_data, nome_col_custo="custo"):
    """Agrupa custo por período (ano ou mês) e retorna DataFrame com colunas: periodo, custo."""
    if df.empty or col_data not in df.columns or nome_col_custo not in df.columns:
        return pd.DataFrame(columns=["periodo", "custo"])

    tmp = df[[col_data, nome_col_custo]].copy()
    tmp[col_data] = pd.to_datetime(tmp[col_data], errors="coerce")
    tmp[nome_col_custo] = pd.to_numeric(tmp[nome_col_custo], errors="coerce")
    tmp = tmp.dropna(subset=[col_data])

    if nivel_tempo_ckm == "Ano":
        tmp["periodo"] = tmp[col_data].dt.year.astype(str)
    else:
        tmp["periodo"] = tmp[col_data].dt.to_period("M").astype(str)

    out = (
        tmp.groupby("periodo", as_index=False)[nome_col_custo]
        .sum()
        .rename(columns={nome_col_custo: "custo"})
        .sort_values("periodo")
    )
    return out

def _agrupar_km(df_rotas):
    """Agrupa km (odometro) por período e retorna DataFrame com colunas: periodo, km."""
    if df_rotas.empty or "data_inicio" not in df_rotas.columns or "odometro" not in df_rotas.columns:
        return pd.DataFrame(columns=["periodo", "km"])

    tmp = df_rotas[["data_inicio", "odometro"]].copy()
    tmp["data_inicio"] = pd.to_datetime(tmp["data_inicio"], errors="coerce")
    tmp["odometro"] = pd.to_numeric(tmp["odometro"], errors="coerce")
    tmp = tmp.dropna(subset=["data_inicio"])

    if nivel_tempo_ckm == "Ano":
        tmp["periodo"] = tmp["data_inicio"].dt.year.astype(str)
    else:
        tmp["periodo"] = tmp["data_inicio"].dt.to_period("M").astype(str)

    out = (
        tmp.groupby("periodo", as_index=False)["odometro"]
        .sum()
        .rename(columns={"odometro": "km"})
        .sort_values("periodo")
    )
    return out

# 1) custos por período (não acumulado ainda)
custo_desp_p = _agrupar_custo(df_despesas_f, "data")
custo_comb_p = _agrupar_custo(df_combustivel_f, "data")
custo_serv_p = _agrupar_custo(df_servicos_f, "data")
km_p = _agrupar_km(df_rotas_f)

# 2) cria base única de períodos (união de tudo)
periodos = sorted(
    set(km_p["periodo"].tolist())
    | set(custo_desp_p["periodo"].tolist())
    | set(custo_comb_p["periodo"].tolist())
    | set(custo_serv_p["periodo"].tolist())
)

if not periodos:
    st.info("Sem dados suficientes para calcular a evolução do custo por km no período selecionado.")
else:
    base = pd.DataFrame({"periodo": periodos})

    # merge custos e km
    base = base.merge(custo_desp_p, on="periodo", how="left").rename(columns={"custo": "custo_desp"})
    base = base.merge(custo_comb_p, on="periodo", how="left").rename(columns={"custo": "custo_comb"})
    base = base.merge(custo_serv_p, on="periodo", how="left").rename(columns={"custo": "custo_serv"})
    base = base.merge(km_p, on="periodo", how="left")

    # fillna com 0 para acumular corretamente
    for c in ["custo_desp", "custo_comb", "custo_serv", "km"]:
        base[c] = pd.to_numeric(base[c], errors="coerce").fillna(0.0)

    # custo total por período
    base["custo_total"] = base["custo_desp"] + base["custo_comb"] + base["custo_serv"]

    # 3) acumulados (regra #1)
    base["custo_desp_acum"] = base["custo_desp"].cumsum()
    base["custo_comb_acum"] = base["custo_comb"].cumsum()
    base["custo_serv_acum"] = base["custo_serv"].cumsum()
    base["custo_total_acum"] = base["custo_total"].cumsum()
    base["km_acum"] = base["km"].cumsum()

    # 4) custo por km acumulado (evita divisão por zero)
    base["ckm_total"] = base.apply(lambda r: (r["custo_total_acum"] / r["km_acum"]) if r["km_acum"] > 0 else None, axis=1)
    base["ckm_desp"]  = base.apply(lambda r: (r["custo_desp_acum"]  / r["km_acum"]) if r["km_acum"] > 0 else None, axis=1)
    base["ckm_comb"]  = base.apply(lambda r: (r["custo_comb_acum"]  / r["km_acum"]) if r["km_acum"] > 0 else None, axis=1)
    base["ckm_serv"]  = base.apply(lambda r: (r["custo_serv_acum"]  / r["km_acum"]) if r["km_acum"] > 0 else None, axis=1)

    # 5) prepara formato longo para Plotly (uma linha por série)
    df_long = base.melt(
        id_vars=["periodo"],
        value_vars=["ckm_total", "ckm_desp", "ckm_serv", "ckm_comb"],
        var_name="Serie",
        value_name="Custo_por_km",
    )

    mapa_series = {
        "ckm_total": "Total (todos os custos)",
        "ckm_desp":  "Despesas",
        "ckm_serv":  "Serviços",
        "ckm_comb":  "Combustível",
    }
    df_long["Serie"] = df_long["Serie"].map(mapa_series)

    # 6) gráfico de linhas (eixo X categórico + legenda)
    titulo = "Evolução do custo acumulado por km (por ano)" if nivel_tempo_ckm == "Ano" else "Evolução do custo acumulado por km (por mês)"

    fig_ckm = px.line(
        df_long.dropna(subset=["Custo_por_km"]),
        x="periodo",
        y="Custo_por_km",
        color="Serie",
        markers=True,
        labels={"periodo": "Período", "Custo_por_km": "R$ / km"},
        title=titulo,
    )

    fig_ckm.update_xaxes(type="category", tickangle=-45 if nivel_tempo_ckm == "Mês" else 0)
    fig_ckm.update_layout(
        legend_title_text="Série",
        height=420,
        margin=dict(l=10, r=10, t=50, b=80 if nivel_tempo_ckm == "Mês" else 30),
    )

    st.plotly_chart(fig_ckm, use_container_width=True, key="evolucao_custo_por_km")

st.markdown("### 🔎 Detalhamento por categoria (acumulado)")

def grafico_categoria(base_df, titulo, col_custo_acum, col_ckm, key):
    dfp = base_df.copy().sort_values("periodo")
    x = dfp["periodo"].astype(str).tolist()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Custo acumulado (R$) - eixo esquerdo
    fig.add_trace(
        go.Scatter(
            x=x,
            y=dfp[col_custo_acum],
            mode="lines+markers",
            name="Custo acumulado (R$)",
            hovertemplate="Período: %{x}<br>Custo acumulado: R$ %{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # Km acumulado (km) - eixo esquerdo
    fig.add_trace(
        go.Scatter(
            x=x,
            y=dfp["km_acum"],
            mode="lines+markers",
            name="Km acumulado (km)",
            hovertemplate="Período: %{x}<br>Km acumulado: %{y:,.1f} km<extra></extra>",
        ),
        secondary_y=False,
    )

    # Custo por km acumulado (R$/km) - eixo direito
    fig.add_trace(
        go.Scatter(
            x=x,
            y=dfp[col_ckm],
            mode="lines+markers",
            name="Custo por km (R$/km)",
            hovertemplate="Período: %{x}<br>Custo por km: R$ %{y:,.4f} / km<extra></extra>",
        ),
        secondary_y=True,
    )

    # ✅ eixos iniciando em zero
    fig.update_yaxes(rangemode="tozero", secondary_y=False)
    fig.update_yaxes(rangemode="tozero", secondary_y=True)

    # ✅ eixo X categórico
    fig.update_xaxes(type="category", tickangle=-45 if nivel_tempo_ckm == "Mês" else 0)

    fig.update_layout(
        title=titulo,
        height=420,
        margin=dict(l=10, r=10, t=50, b=80 if nivel_tempo_ckm == "Mês" else 30),
        legend_title_text="Séries",
    )

    fig.update_yaxes(title_text="Custo (R$) / Km (km)", secondary_y=False)
    fig.update_yaxes(title_text="Custo por km (R$/km)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True, key=key)


# ✅ Um gráfico por linha (4 linhas)
grafico_categoria(
    base,
    "Total – Acumulado (Custo, Km e R$/km)",
    col_custo_acum="custo_total_acum",
    col_ckm="ckm_total",
    key="det_total",
)

grafico_categoria(
    base,
    "Despesas – Acumulado (Custo, Km e R$/km)",
    col_custo_acum="custo_desp_acum",
    col_ckm="ckm_desp",
    key="det_desp",
)

grafico_categoria(
    base,
    "Serviços – Acumulado (Custo, Km e R$/km)",
    col_custo_acum="custo_serv_acum",
    col_ckm="ckm_serv",
    key="det_serv",
)

grafico_categoria(
    base,
    "Combustível – Acumulado (Custo, Km e R$/km)",
    col_custo_acum="custo_comb_acum",
    col_ckm="ckm_comb",
    key="det_comb",
)