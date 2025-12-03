import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="App Estufas - Inventário", layout="wide")

st.title("📋 Inventário das Estufas – Kibala (versão de validação)")

# ---------------------------------------------------------
# Cabeçalho – seleção de semana/ano e botões
# ---------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

with col1:
    ano = st.selectbox("Ano", [2025, 2026], index=0)

with col2:
    semana = st.selectbox("Semana", list(range(1, 53)), index=47)  # 48 como default

with col3:
    st.button("Carregar PDF", disabled=True, help="(somente mock por enquanto)")

with col4:
    st.button("Salvar", disabled=True, help="Funcionalidade real virá depois (banco).")

with col5:
    st.button("Exportar PDF", disabled=True, help="Será implementado depois.")

st.markdown("---")

# ---------------------------------------------------------
# Dados MOCK – INVENTÁRIO (para teste visual)
# ---------------------------------------------------------
dados_inventario = [
    {
        "Bloco": 7,
        "Naves": "1 a 22",
        "Nº Naves": 22,
        "Área/Nave (ha)": 0.06,
        "Área Total (ha)": 1.32,
        "Cultura": "Tomate",
        "Data Plantio": date(2025, 11, 4),
        "Idade (sem)": 3,
        "Nº Linhas (bloco)": None,
    },
    {
        "Bloco": 14,
        "Naves": "1 a 10",
        "Nº Naves": 10,
        "Área/Nave (ha)": 0.06,
        "Área Total (ha)": 0.60,
        "Cultura": "Alface",
        "Data Plantio": date(2025, 10, 31),
        "Idade (sem)": 4,
        "Nº Linhas (bloco)": 2,
    },
    {
        "Bloco": 5,
        "Naves": "9 a 22",
        "Nº Naves": 14,
        "Área/Nave (ha)": 0.06,
        "Área Total (ha)": 0.84,
        "Cultura": "Alface",
        "Data Plantio": None,
        "Idade (sem)": None,
        "Nº Linhas (bloco)": None,
    },
]

df_inventario = pd.DataFrame(dados_inventario)

st.subheader("📊 Inventário semanal (mock para validação do layout)")

edited_inventario = st.data_editor(
    df_inventario,
    num_rows="dynamic",
    use_container_width=True,
    key="inventario_editor",
)

st.caption(
    "➕ Você pode clicar nas células e editar como se fosse um Excel. "
    "Nesta versão de validação nada é salvo no banco ainda."
)

st.markdown("---")

# ---------------------------------------------------------
# Dados MOCK – PARÂMETROS DAS CULTURAS
# ---------------------------------------------------------
dados_parametros = [
    {
        "Cultura": "Tomate",
        "Espac. Linhas (m)": 1.20,
        "Espac. Plantas (m)": 0.40,
        "Nº Linhas (padrão)": 4,
        "Ciclo (sem)": 14,
        "Plantas/ha (padrão)": 83332,  # só mock, depois calculamos
    },
    {
        "Cultura": "Alface",
        "Espac. Linhas (m)": 0.30,
        "Espac. Plantas (m)": 0.25,
        "Nº Linhas (padrão)": 4,
        "Ciclo (sem)": 6,
        "Plantas/ha (padrão)": 533333,
    },
    {
        "Cultura": "Feijão-Verde",
        "Espac. Linhas (m)": 0.50,
        "Espac. Plantas (m)": 0.20,
        "Nº Linhas (padrão)": 2,
        "Ciclo (sem)": 10,
        "Plantas/ha (padrão)": 200000,
    },
]

df_parametros = pd.DataFrame(dados_parametros)

st.subheader("🌱 Parâmetros das culturas (mock para validação)")

edited_parametros = st.data_editor(
    df_parametros,
    num_rows="dynamic",
    use_container_width=True,
    key="parametros_editor",
)

st.caption(
    "➕ Esta tabela representa o padrão agronômico de cada cultura "
    "(espaçamentos, linhas, ciclo e plantas/ha)."
)

st.markdown("---")

st.info(
    "Versão de validação: nada está sendo salvo no banco ainda. "
    "Se o layout fizer sentido para você e para o chefe das estufas, "
    "no próximo passo conectamos essas tabelas ao PostgreSQL."
)
