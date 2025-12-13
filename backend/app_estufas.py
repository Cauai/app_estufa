import streamlit as st
import pandas as pd
from datetime import date, datetime

import plotly.graph_objects as go  # para o mapa visual

st.set_page_config(page_title="App Estufas - Mapa Mock", layout="wide")

# -------------------------------------------------
# Metadados dos blocos (ajuste aqui se necessário)
# -------------------------------------------------
BLOCOS_META = {
    1: {"area_total": 1.30, "area_nave": 0.057, "n_naves": 23},
    2: {"area_total": 1.08, "area_nave": 0.057, "n_naves": 19},
    3: {"area_total": 1.08, "area_nave": 0.057, "n_naves": 19},
    4: {"area_total": 1.08, "area_nave": 0.057, "n_naves": 19},
    5: {"area_total": 1.30, "area_nave": 0.060, "n_naves": 23},
    6: {"area_total": 1.30, "area_nave": 0.060, "n_naves": 23},
    7: {"area_total": 1.30, "area_nave": 0.060, "n_naves": 23},
}

# Blocos 8 a 25 – mock 1,2 ha, 0,06 ha/nave, 20 naves
for b in range(8, 26):
    BLOCOS_META[b] = {"area_total": 1.20, "area_nave": 0.060, "n_naves": 20}

ORDEM_BLOCOS = list(range(1, 26))

# -------------------------------------------------
# Paleta de cores fixa
# -------------------------------------------------
COLOR_PALETTE = [
    ("Vermelho", "#FF4B4B", "🔴"),
    ("Verde", "#2ECC71", "🟢"),
    ("Amarelo", "#F1C40F", "🟡"),
    ("Azul", "#3498DB", "🔵"),
    ("Roxo", "#9B59B6", "🟣"),
    ("Laranja", "#E67E22", "🟠"),
    ("Preto", "#2D2D2D", "⚫"),
    ("Branco", "#FFFFFF", "⚪"),
]

# -------------------------------------------------
# Estado da aplicação
# -------------------------------------------------
if "ocupacao_naves" not in st.session_state:
    # chave: (bloco, nave) -> dict(...)
    st.session_state["ocupacao_naves"] = {}

if "df_inventario" not in st.session_state:
    st.session_state["df_inventario"] = pd.DataFrame(
        columns=[
            "Bloco",
            "Naves",
            "Ano",
            "Semana",
            "Cultura",
            "Data_Plantio",
            "Idade_sem",
            "Espac_Linha_m",
            "Espac_Planta_m",
            "Linhas_Por_Camalhao",
            "Plantas_ha_calc",
            "N_Linhas_bloco",
            "N_Naves_Selecionadas",
            "Area_nave_ha",
            "Area_total_grupo_ha",
            "Cor",
            "Observacoes",
        ]
    )

if "selecionados" not in st.session_state:
    st.session_state["selecionados"] = []  # lista de (bloco, nave)

if "cor_selecionada" not in st.session_state:
    st.session_state["cor_selecionada"] = "#FF4B4B"

if "selection_reset_token" not in st.session_state:
    # usado para "resetar" visualmente os checkboxes após aplicar
    st.session_state["selection_reset_token"] = 0

if "df_param_cultura" not in st.session_state:
    # tabela mock de parâmetros de cultura
    st.session_state["df_param_cultura"] = pd.DataFrame(
        [
            ["Tomate", 1.0, 0.35, 2, 120, "#FF4B4B"],
            ["Couve Repolho", 0.8, 0.40, 2, 90, "#2ECC71"],
            ["Alface", 0.3, 0.30, 4, 60, "#F1C40F"],
            ["Pimento", 1.0, 0.40, 2, 120, "#E67E22"],
        ],
        columns=[
            "Cultura",
            "Espac_Linha_padrao_m",
            "Espac_Planta_padrao_m",
            "Linhas_por_camalhao_padrao",
            "Ciclo_med_dias",
            "Cor_padrao",
        ],
    )

# -------------------------------------------------
# Funções auxiliares
# -------------------------------------------------
def set_selecao_nave(bloco, nave, marcado):
    """Atualiza a lista de naves selecionadas."""
    key = (bloco, nave)
    if marcado and key not in st.session_state["selecionados"]:
        st.session_state["selecionados"].append(key)
    elif not marcado and key in st.session_state["selecionados"]:
        st.session_state["selecionados"].remove(key)


def calcular_idade_semanas(data_plantio, ano, semana):
    try:
        ref = datetime.strptime(f"{ano}-W{semana}-3", "%G-W%V-%u").date()
        dias = (ref - data_plantio).days
        return max(dias // 7, 0)
    except Exception:
        return None


def calcular_plantas_ha(esp_linha, esp_planta, linhas_camalhao):
    try:
        if esp_linha <= 0 or esp_planta <= 0 or linhas_camalhao <= 0:
            return None
        return (1 / (esp_linha * esp_planta)) * linhas_camalhao
    except Exception:
        return None


def formatar_naves_lista(naves):
    """Ex.: [1,2,5,6,9] -> 'Naves 1 a 2, 5 a 6, 9'."""
    if not naves:
        return ""
    naves = sorted(set(naves))
    grupos = []
    ini = naves[0]
    prev = ini
    for n in naves[1:]:
        if n == prev + 1:
            prev = n
        else:
            grupos.append((ini, prev))
            ini = prev = n
    grupos.append((ini, prev))
    partes = [f"{a}" if a == b else f"{a} a {b}" for a, b in grupos]
    return "Nave " + ", ".join(partes) if len(partes) == 1 else "Naves " + ", ".join(partes)


# -------------------------------------------------
# Aplicar cultura às naves selecionadas
# -------------------------------------------------
def aplicar_cultura(
    ano,
    semana,
    cultura,
    cor,
    data_plantio,
    espac_linha,
    espac_planta,
    linhas_camalhao,
    n_linhas_bloco,
    obs,
):
    idade = calcular_idade_semanas(data_plantio, ano, semana)
    plantas_ha = calcular_plantas_ha(espac_linha, espac_planta, linhas_camalhao)

    # Atualiza nave a nave
    for bloco, nave in st.session_state["selecionados"]:
        st.session_state["ocupacao_naves"][(bloco, nave)] = {
            "cultura": cultura,
            "cor": cor,
            "data_plantio": data_plantio,
            "espac_linha": espac_linha,
            "espac_planta": espac_planta,
            "linhas_camalhao": linhas_camalhao,
            "n_linhas_bloco": n_linhas_bloco,
            "obs": obs,
            "idade_sem": idade,
            "plantas_ha": plantas_ha,
        }

    # Gera tabela consolidada agrupando naves consecutivas com mesmos parâmetros
    registros = []
    occ = st.session_state["ocupacao_naves"]

    for bloco in ORDEM_BLOCOS:
        dados = [(n, v) for (b, n), v in occ.items() if b == bloco]
        if not dados:
            continue

        dados.sort(key=lambda x: x[0])
        grupo = []
        cur = None

        def salvar():
            if not grupo or cur is None:
                return
            meta = BLOCOS_META[bloco]
            area_nave = meta["area_nave"]
            total = len(grupo)
            registros.append(
                {
                    "Bloco": bloco,
                    "Naves": formatar_naves_lista(grupo),
                    "Ano": ano,
                    "Semana": semana,
                    "Cultura": cur["cultura"],
                    "Data_Plantio": cur["data_plantio"],
                    "Idade_sem": cur["idade_sem"],
                    "Espac_Linha_m": cur["espac_linha"],
                    "Espac_Planta_m": cur["espac_planta"],
                    "Linhas_Por_Camalhao": cur["linhas_camalhao"],
                    "Plantas_ha_calc": cur["plantas_ha"],
                    "N_Linhas_bloco": cur["n_linhas_bloco"],
                    "N_Naves_Selecionadas": total,
                    "Area_nave_ha": area_nave,
                    "Area_total_grupo_ha": area_nave * total,
                    "Cor": cur["cor"],
                    "Observacoes": cur["obs"],
                }
            )

        for nave, info in dados:
            if cur is None:
                cur = info
                grupo = [nave]
            else:
                iguais = all(
                    [
                        cur[k] == info[k]
                        for k in [
                            "cultura",
                            "data_plantio",
                            "espac_linha",
                            "espac_planta",
                            "linhas_camalhao",
                            "n_linhas_bloco",
                            "obs",
                        ]
                    ]
                )
                if iguais:
                    grupo.append(nave)
                else:
                    salvar()
                    cur = info
                    grupo = [nave]
        salvar()

    st.session_state["df_inventario"] = pd.DataFrame(registros)

    # limpa seleção (lógica e visual)
    st.session_state["selecionados"] = []
    st.session_state["selection_reset_token"] += 1


# -------------------------------------------------
# Desenhar um bloco (checkbox + retângulo colorido)
# -------------------------------------------------
def desenhar_bloco(bloco, ano, semana):
    meta = BLOCOS_META[bloco]
    n_naves = meta["n_naves"]

    st.markdown(
        f"<b>Bloco {bloco}</b> — {meta['area_total']:.2f} ha • "
        f"{meta['area_nave']:.3f} ha/nave • {n_naves} naves",
        unsafe_allow_html=True,
    )

    cols = st.columns(n_naves)

    for idx, nave in enumerate(range(1, n_naves + 1)):
        key = (bloco, nave)
        info = st.session_state["ocupacao_naves"].get(key)
        marcado_default = key in st.session_state["selecionados"]

        with cols[idx]:
            marcado = st.checkbox(
                "",
                value=marcado_default,
                key=f"chk_{bloco}_{nave}_{st.session_state['selection_reset_token']}",
                label_visibility="hidden",
            )

            set_selecao_nave(bloco, nave, marcado)

            cor_bg = info["cor"] if info else "#3a3a3a"
            borda = "3px solid yellow" if marcado else "1px solid #555"

            st.markdown(
                f"""
                <div style="
                    height:48px;
                    background-color:{cor_bg};
                    border:{borda};
                    border-radius:4px;
                    display:flex;
                    align-items:flex-end;
                    justify-content:center;
                    color:white;
                    font-size:0.7rem;
                ">{nave}</div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
#  MAPA VISUAL (Plotly) - shapes por bloco/nave
# ============================================================

# Layout aproximado em 3 colunas (esquerda, centro, direita)
BLOCO_LAYOUT = {
    1: dict(col=0, row=0),
    2: dict(col=0, row=1),
    3: dict(col=0, row=2),
    4: dict(col=0, row=3),
    5: dict(col=0, row=4),
    6: dict(col=0, row=5),
    7: dict(col=0, row=6),
    8: dict(col=1, row=0),
    9: dict(col=1, row=1),
    10: dict(col=1, row=2),
    11: dict(col=1, row=3),
    12: dict(col=1, row=4),
    13: dict(col=1, row=5),
    14: dict(col=1, row=6),
    15: dict(col=1, row=7),
    16: dict(col=1, row=8),
    17: dict(col=1, row=9),
    18: dict(col=1, row=10),
    19: dict(col=1, row=11),
    20: dict(col=2, row=0),
    21: dict(col=2, row=1),
    22: dict(col=2, row=2),
    23: dict(col=2, row=3),
    24: dict(col=2, row=4),
    25: dict(col=2, row=5),
}

# ---------- PARÂMETROS VISUAIS DO MAPA ----------
NAVE_STEP = 3.0    # distância entre centros das naves na horizontal
ROW_SPAN  = 5.0    # distância vertical entre linhas de blocos

# TAMANHO DO RETÂNGULO EM UNIDADES DO GRÁFICO
NAVE_W = 1.6       # largura do retângulo
NAVE_H = 1.6       # altura do retângulo

NAVE_FONT = 16     # tamanho do número dentro do retângulo
TITLE_FONT = 11    # tamanho do texto "Bloco X – ..."
FIG_HEIGHT = 900   # altura total do gráfico (px)


def build_mapa_plotly(filtro_culturas=None):
    """
    Gera um mapa das estufas usando Plotly, com um retângulo por nave
    e o número centralizado dentro. Filtro opcional por cultura.
    """
    if filtro_culturas is None:
        filtro_culturas = []

    fig = go.Figure()
    annotations = []

    hover_x = []
    hover_y = []
    hover_texts = []

    # maior nº de naves entre os blocos -> para calcular espaço horizontal
    max_naves = max(meta["n_naves"] for meta in BLOCOS_META.values())
    COL_SPAN = NAVE_STEP * (max_naves + 4)

    for bloco in ORDEM_BLOCOS:
        meta = BLOCOS_META[bloco]
        n_naves = meta["n_naves"]

        layout = BLOCO_LAYOUT[bloco]
        col = layout["col"]
        row = layout["row"]

        # origem (x,y) do bloco
        base_x = col * COL_SPAN
        base_y = -row * ROW_SPAN

        # título do bloco
        annotations.append(
            dict(
                x=base_x + NAVE_STEP * (n_naves + 1) / 2,
                y=base_y + (NAVE_H / 2) + 1.4,
                text=(
                    f"Bloco {bloco} – {meta['area_total']:.2f} ha • "
                    f"{meta['area_nave']:.3f} ha/nave • {n_naves} naves"
                ),
                showarrow=False,
                font=dict(size=TITLE_FONT, color="white"),
                xanchor="center",
            )
        )

        # naves
        for idx, nave in enumerate(range(1, n_naves + 1), start=1):
            key = (bloco, nave)
            info = st.session_state["ocupacao_naves"].get(key)

            if info:
                cultura = info.get("cultura") or "Sem cultura"
                cor_base = info.get("cor") or "#FF4B4B"
                if filtro_culturas and cultura not in filtro_culturas:
                    cor = "#303030"  # outra cultura -> cinza
                else:
                    cor = cor_base
            else:
                cultura = "Sem cultura"
                cor = "#3A3A3A"

            # centro do retângulo da nave
            x_center = base_x + idx * NAVE_STEP
            y_center = base_y

            # coordenadas do retângulo
            x0 = x_center - NAVE_W / 2
            x1 = x_center + NAVE_W / 2
            y0 = y_center - NAVE_H / 2
            y1 = y_center + NAVE_H / 2

            # retângulo colorido
            fig.add_shape(
                type="rect",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                line=dict(color="#000000", width=1),
                fillcolor=cor,
            )

            # número da nave CENTRALIZADO
            annotations.append(
                dict(
                    x=x_center,
                    y=y_center,
                    text=str(nave),
                    showarrow=False,
                    font=dict(size=NAVE_FONT, color="white"),
                    xanchor="center",
                    yanchor="middle",
                )
            )

            # texto de hover
            if info and info.get("data_plantio"):
                data_plantio_txt = info["data_plantio"].strftime("%d/%m/%Y")
                idade = info.get("idade_sem")
                idade_txt = f"{idade} sem" if idade is not None else "-"
            else:
                data_plantio_txt = "-"
                idade_txt = "-"

            hover_x.append(x_center)
            hover_y.append(y_center)
            hover_texts.append(
                f"Bloco {bloco} - Nave {nave}<br>"
                f"Cultura: {cultura}<br>"
                f"Data plantio: {data_plantio_txt}<br>"
                f"Idade: {idade_txt}"
            )

    # trace invisível só para hover
    fig.add_trace(
        go.Scatter(
            x=hover_x,
            y=hover_y,
            mode="markers",
            marker=dict(size=10, opacity=0),
            hovertext=hover_texts,
            hoverinfo="text",
            showlegend=False,
        )
    )

    fig.update_layout(
        height=FIG_HEIGHT,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=annotations,
    )

    return fig


# -------------------------------------------------
# Layout principal
# -------------------------------------------------
st.title("Mapa das Estufas – Mock Otimizado (Blocos Colapsáveis)")

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    ano = st.selectbox("Ano", [2025, 2026], key="ano_select")
with col2:
    semana = st.selectbox("Semana", list(range(1, 53)), index=47, key="semana_select")
with col3:
    st.caption("Versão otimizada: expanders por bloco + mapa visual Plotly.")

st.markdown("---")

col_mapa, col_div, col_form = st.columns([2.2, 0.05, 1])

# -------------------- MAPA (expanders) ------------------------
with col_mapa:
    st.subheader("📗 Mapa de blocos (edição por nave)")

    ultimo_bloco = None
    if st.session_state["selecionados"]:
        ultimo_bloco = st.session_state["selecionados"][-1][0]

    for bloco in ORDEM_BLOCOS:
        expanded = bloco == ultimo_bloco
        with st.expander(
            f"Bloco {bloco} – {BLOCOS_META[bloco]['n_naves']} naves",
            expanded=expanded,
        ):
            desenhar_bloco(bloco, ano, semana)

# -------------------- DIVISÓRIA ------------------------
with col_div:
    st.markdown(
        "<div style='height:100%; border-left:1px solid #999;'></div>",
        unsafe_allow_html=True,
    )

# -------------------- FORMULÁRIO ------------------------
with col_form:
    st.subheader("✏️ Aplicar cultura às naves selecionadas")

    selec = st.session_state["selecionados"]
    if selec:
        st.write("Naves selecionadas:")
        blocos = {}
        for b, n in selec:
            blocos.setdefault(b, []).append(n)
        for b, ns in blocos.items():
            st.write(f"• Bloco {b}: {formatar_naves_lista(ns)}")
    else:
        st.info("Nenhuma nave selecionada.")

    cultura = st.text_input("Cultura", "Tomate", key="cultura_input")

    st.write("Cor da cultura:")
    cols_cor = st.columns(len(COLOR_PALETTE))
    for i, (nome, hexcor, emoji) in enumerate(COLOR_PALETTE):
        with cols_cor[i]:
            if st.button(emoji, key=f"corbtn_{nome}"):
                st.session_state["cor_selecionada"] = hexcor
            st.markdown(
                f"<div style='font-size:0.7rem; text-align:center;'>{nome}</div>",
                unsafe_allow_html=True,
            )

    cor_escolhida = st.color_picker(
        "Cor personalizada (pode sobrescrever a paleta)",
        st.session_state["cor_selecionada"],
    )
    st.session_state["cor_selecionada"] = cor_escolhida
    st.markdown(
        f"<div style='margin-top:4px; display:flex; align-items:center;'>"
        f"<div style='width:20px; height:20px; background-color:{cor_escolhida}; "
        f"border:1px solid #aaa; margin-right:6px;'></div>"
        f"<span style='font-size:0.85rem;'>Cor selecionada: {cor_escolhida}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("**Parâmetros de espaçamento**")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        espac_linha = st.number_input(
            "Espaçamento entre linhas (m)", min_value=0.0, value=1.0, step=0.1
        )
    with col_e2:
        espac_planta = st.number_input(
            "Espaçamento entre plantas (m)", min_value=0.0, value=0.35, step=0.05
        )

    linhas_camalhao = st.selectbox("Nº de linhas por camalhão", [1, 2, 4], index=1)
    n_linhas_bloco = st.number_input(
        "Nº total de linhas no bloco (opcional)", min_value=0, step=1
    )

    data_plantio = st.date_input("Data de plantio", value=date.today())
    obs = st.text_area("Observações (opcional)", "", height=80)

    idade_preview = calcular_idade_semanas(data_plantio, ano, semana)
    if idade_preview is not None:
        st.caption(
            f"Idade aproximada na semana {semana}/{ano}: **{idade_preview} semanas**."
        )

    plantas_ha_preview = calcular_plantas_ha(
        espac_linha, espac_planta, linhas_camalhao
    )
    if plantas_ha_preview is not None:
        st.caption(f"Plantas/ha (estimado): **{plantas_ha_preview:,.0f}**")

    if st.button("Aplicar às naves selecionadas"):
        if not st.session_state["selecionados"]:
            st.warning("Nenhuma nave selecionada.")
        else:
            aplicar_cultura(
                ano,
                semana,
                cultura,
                cor_escolhida,
                data_plantio,
                espac_linha,
                espac_planta,
                linhas_camalhao,
                int(n_linhas_bloco) if n_linhas_bloco > 0 else None,
                obs.strip() or None,
            )
            st.success("Aplicado com sucesso!")

# -------------------------------------------------
# Inventário
# -------------------------------------------------
st.markdown("---")
st.subheader("📊 Inventário consolidado")

df_inv = st.session_state["df_inventario"]
if df_inv.empty:
    st.info("Nenhum registro ainda.")
else:
    st.dataframe(df_inv, use_container_width=True)
    st.download_button(
        "⬇ Baixar inventário (CSV)",
        df_inv.to_csv(index=False).encode("utf-8"),
        file_name=f"inventario_{ano}_sem{semana}.csv",
        mime="text/csv",
    )

# -------------------------------------------------
# Parâmetros de cultura (mock)
# -------------------------------------------------
st.markdown("---")
st.subheader("📚 Parâmetros padrão por cultura (mock)")

st.dataframe(st.session_state["df_param_cultura"], use_container_width=True)

# -------------------------------------------------
# Mapa visual Plotly + filtros
# -------------------------------------------------
st.markdown("---")
st.subheader("🧭 Mapa visual das estufas (Plotly)")

# culturas presentes na ocupação para filtro
culturas_existentes = sorted(
    {
        v.get("cultura")
        for v in st.session_state["ocupacao_naves"].values()
        if v.get("cultura")
    }
)

col_f1, col_f2 = st.columns([2, 3])
with col_f1:
    filtro_culturas = st.multiselect(
        "Filtrar mapa pelas culturas (deixe vazio para mostrar todas):",
        options=culturas_existentes,
        default=culturas_existentes,
    )

# legenda simples
with col_f2:
    st.markdown("**Legenda de culturas no mapa:**")
    if culturas_existentes:
        for cult in culturas_existentes:
            # tenta pegar a primeira cor usada nessa cultura
            cor_cult = None
            for info in st.session_state["ocupacao_naves"].values():
                if info.get("cultura") == cult:
                    cor_cult = info.get("cor")
                    break
            if cor_cult is None:
                cor_cult = "#555555"
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:6px;">
                    <div style="width:18px; height:18px; background-color:{cor_cult};
                                border-radius:3px; border:1px solid #aaa;"></div>
                    <span style="font-size:0.9rem;">{cult}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("Nenhuma cultura aplicada ainda.")

fig_mapa = build_mapa_plotly(filtro_culturas=filtro_culturas)
st.plotly_chart(fig_mapa, use_container_width=True)
