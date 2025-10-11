import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Controle de Gastos", layout="centered", initial_sidebar_state="collapsed")

# Arquivo CSV para armazenar os dados
ARQUIVO = "gastos.csv"

# Categorias padronizadas
CATEGORIAS = ["Comida", "Remédios", "Diversão", "Outros"]

# Carregar dados
def carregar_dados():
    try:
        df = pd.read_csv(ARQUIVO)
        # Tenta converter a coluna "Data" para datetime, aceitando formatos mistos
        df["Data"] = pd.to_datetime(df["Data"], format="mixed", dayfirst=True, errors="coerce")
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Data", "Valor", "Categoria", "Descrição", "Responsável"])

# Salvar dados
def salvar_dados(df):
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
    df.to_csv(ARQUIVO, index=False)

# Interface principal
def main():
    st.set_page_config(page_title="Controle de Gastos", layout="centered")
    st.title("💸 Controle Diário de Gastos")

    aba = st.sidebar.radio("Menu", ["Incluir Gasto", "Consultar", "Alterar/Excluir"])

    df = carregar_dados()

    if aba == "Incluir Gasto":
        st.subheader("Novo Gasto")

        data = st.date_input("Data", value=datetime.today(), format="DD/MM/YYYY")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        categoria = st.selectbox("Categoria", CATEGORIAS)
        descricao = st.text_input("Descrição")
        responsavel = st.text_input("Responsável")

        if st.button("Salvar"):
            novo = pd.DataFrame([[data, valor, categoria, descricao, responsavel]],
                                columns=df.columns)
            df = pd.concat([df, novo], ignore_index=True)
            salvar_dados(df)
            st.success("✅ Gasto registrado com sucesso!")

    elif aba == "Consultar":
        st.subheader("Consulta de Gastos")

        filtro_categoria = st.multiselect("Filtrar por categoria", CATEGORIAS)
        filtro_responsavel = st.text_input("Filtrar por responsável")
        filtro_data = st.date_input("Filtrar por período", [])

        consulta = df.copy()

        if filtro_categoria:
            consulta = consulta[consulta["Categoria"].isin(filtro_categoria)]
        if filtro_responsavel:
            consulta = consulta[consulta["Responsável"].str.contains(filtro_responsavel, case=False)]
        if isinstance(filtro_data, list) and len(filtro_data) == 2:
            consulta = consulta[(consulta["Data"] >= filtro_data[0]) & (consulta["Data"] <= filtro_data[1])]

        st.dataframe(consulta)

        st.subheader("Resumo por Categoria")
        st.dataframe(consulta.groupby("Categoria")["Valor"].sum().reset_index())

        st.subheader("Resumo por Responsável")
        st.dataframe(consulta.groupby("Responsável")["Valor"].sum().reset_index())

        if not consulta.empty:
            st.subheader("📤 Exportar dados")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                consulta.to_excel(writer, index=False, sheet_name="Gastos")
            st.download_button(
                label="📥 Baixar como Excel",
                data=buffer.getvalue(),
                file_name="gastos_exportados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.subheader("📊 Gráfico por Categoria")
        grafico_categoria = consulta.groupby("Categoria")["Valor"].sum()
        st.bar_chart(grafico_categoria)

        st.subheader("📊 Gráfico por Responsável")
        grafico_responsavel = consulta.groupby("Responsável")["Valor"].sum()
        st.bar_chart(grafico_responsavel)

        st.subheader("📊 Gráfico por Data")
        grafico_data = consulta.groupby("Data")["Valor"].sum().sort_index()
        st.line_chart(grafico_data)

    elif aba == "Alterar/Excluir":
        st.subheader("Alterar ou Excluir Gastos")

        if df.empty:
            st.info("Nenhum gasto registrado ainda.")
        else:
            idx = st.selectbox("Selecione o índice do gasto", df.index)
            gasto = df.loc[idx]

            st.write("Gasto selecionado:")
            st.write(gasto)

            if st.button("Excluir"):
                df = df.drop(idx)
                salvar_dados(df)
                st.success("🗑️ Gasto excluído com sucesso!")

            st.write("Alterar dados:")
            nova_data = st.date_input("Data", value=gasto["Data"], format="DD/MM/YYYY")
            novo_valor = st.number_input("Valor", value=float(gasto["Valor"]), step=0.01)
            nova_categoria = st.selectbox("Categoria", CATEGORIAS, index=CATEGORIAS.index(gasto["Categoria"]))
            nova_descricao = st.text_input("Descrição", value=gasto["Descrição"])
            novo_responsavel = st.text_input("Responsável", value=gasto["Responsável"])

            if st.button("Salvar Alterações"):
                df.loc[idx] = [nova_data, novo_valor, nova_categoria, nova_descricao, novo_responsavel]
                salvar_dados(df)
                st.success("✏️ Gasto alterado com sucesso!")

if __name__ == "__main__":
    main()