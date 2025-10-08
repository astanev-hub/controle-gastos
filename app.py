import streamlit as st
import pandas as pd
import io
from datetime import datetime

ARQUIVO = "gastos.csv"

st.set_page_config(
    page_title="Controle de Gastos",
    layout="centered",
    initial_sidebar_state="collapsed"
)
st.cache_data.clear()

# Funções
def carregar_dados():
    try:
        df = pd.read_csv(ARQUIVO)
        df["Data"] = pd.to_datetime(df["Data"], format="mixed", dayfirst=True, errors="coerce")
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Data", "Valor", "Categoria", "Descrição", "Responsável"])

def salvar_dados(df):
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
    df.to_csv(ARQUIVO, index=False)

# Interface
st.title("📱 Controle de Gastos Pessoal")

aba1, aba2, aba3 = st.tabs(["💸 Registrar", "📊 Consultar", "📥 Exportar"])

with aba1:
    st.subheader("💸 Registrar novo gasto")
    with st.form("formulario_gasto"):
        data = st.date_input("Data", value=datetime.today())
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Saúde", "Lazer", "Outros"])
        descricao = st.text_input("Descrição")
        responsavel = st.text_input("Responsável")
        enviado = st.form_submit_button("💾 Salvar", use_container_width=True)

        if enviado:
            novo = pd.DataFrame([{
                "Data": data,
                "Valor": valor,
                "Categoria": categoria,
                "Descrição": descricao,
                "Responsável": responsavel
            }])
            df = carregar_dados()
            df = pd.concat([df, novo], ignore_index=True)
            salvar_dados(df)
            st.success("Gasto registrado com sucesso!")

with aba2:
    st.subheader("📊 Consultar gastos")
    df = carregar_dados()

    if df.empty:
        st.info("Nenhum gasto registrado ainda.")
    else:
        filtro_responsavel = st.selectbox("Filtrar por responsável", ["Todos"] + sorted(df["Responsável"].dropna().unique().tolist()))
        filtro_categoria = st.selectbox("Filtrar por categoria", ["Todas"] + sorted(df["Categoria"].dropna().unique().tolist()))

        consulta = df.copy()
        if filtro_responsavel != "Todos":
            consulta = consulta[consulta["Responsável"] == filtro_responsavel]
        if filtro_categoria != "Todas":
            consulta = consulta[consulta["Categoria"] == filtro_categoria]

        st.dataframe(consulta[["Data", "Valor", "Categoria"]], use_container_width=True)

        st.markdown("### 📊 Gráficos")

        if not consulta.empty:
            st.bar_chart(consulta.groupby("Categoria")["Valor"].sum(), use_container_width=True)
            st.bar_chart(consulta.groupby("Responsável")["Valor"].sum(), use_container_width=True)
            st.line_chart(consulta.groupby("Data")["Valor"].sum().sort_index(), use_container_width=True)

with aba3:
    st.subheader("📥 Exportar dados para Excel")
    df = carregar_dados()
    if df.empty:
        st.info("Nenhum dado para exportar.")
    else:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Gastos")
        st.download_button(
            label="📥 Baixar Excel",
            data=buffer.getvalue(),
            file_name="gastos_exportados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )