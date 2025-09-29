import streamlit as st
import pandas as pd
import altair as alt

# Configuração da página para um layout mais amplo
st.set_page_config(layout="wide")

def process_uploaded_file(uploaded_file):
    """
    Função para processar o arquivo CSV de estoque que foi upado.
    Esta função lê o arquivo e o transforma em um formato de dados limpo e organizado.
    """
    try:
        # Pula as primeiras 3 linhas que são cabeçalhos e lê os dados do arquivo em memória
        df = pd.read_csv(uploaded_file, skiprows=3, encoding='latin1')

        # O arquivo parece ter várias tabelas lado a lado.
        # Vamos processar a primeira seção como exemplo: "RIO BONITO BRASIL 4,5 KG"
        # Esta parte pode precisar de ajustes se a estrutura do seu arquivo mudar.
        
        df_produto = df.iloc[:, :5]
        df_produto.columns = ['ENTRADA', 'SAIDA', 'SALDO', 'DATA', 'ESTOQUE_CX_PARACATU']
        df_produto['PRODUTO'] = "RIO BONITO BRASIL 4,5 KG" # Nome do produto

        # Limpeza e formatação dos dados
        df_produto = df_produto.dropna(subset=['DATA'])
        df_produto['DATA'] = pd.to_datetime(df_produto['DATA'], errors='coerce')
        df_produto = df_produto.dropna(subset=['DATA'])

        # Converter colunas numéricas, tratando erros
        for col in ['ENTRADA', 'SAIDA', 'SALDO', 'ESTOQUE_CX_PARACATU']:
            df_produto[col] = pd.to_numeric(df_produto[col], errors='coerce')

        return df_produto.dropna() # Remove linhas com dados numéricos inválidos

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
        return None

# --- Início do Dashboard ---

st.title('📊 Dashboard Interativo de Controle de Estoque')
st.write("Faça o upload da sua planilha de estoque (.csv) para visualizar os dados.")

# --- Widget de Upload na barra lateral ---
st.sidebar.header("Carregar Planilha")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None:
    data = process_uploaded_file(uploaded_file)

    if data is not None and not data.empty:
        st.header('Visão Geral dos Dados')
        st.dataframe(data)

        st.header('Visualizações Interativas')

        # Gráfico de Entradas e Saídas ao longo do tempo
        st.subheader('Movimentação de Estoque (Entradas vs. Saídas)')
        
        chart_data = data.melt(id_vars=['DATA'], value_vars=['ENTRADA', 'SAIDA'], 
                               var_name='Tipo de Movimentação', value_name='Quantidade')

        line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('DATA:T', title='Data'),
            y=alt.Y('Quantidade:Q', title='Quantidade de Caixas'),
            color='Tipo de Movimentação:N',
            tooltip=['DATA:T', 'Quantidade:Q', 'Tipo de Movimentação:N']
        ).interactive()

        st.altair_chart(line_chart, use_container_width=True)

        # Gráfico de Saldo ao longo do tempo
        st.subheader('Evolução do Saldo em Estoque')
        
        saldo_chart = alt.Chart(data).mark_area(
            line={'color':'darkgreen'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='white', offset=0),
                       alt.GradientStop(color='darkgreen', offset=1)],
                x1=1,
                x2=1,
                y1=1,
                y2=0
            )
        ).encode(
            x=alt.X('DATA:T', title='Data'),
            y=alt.Y('SALDO:Q', title='Saldo (Caixas)'),
            tooltip=['DATA:T', 'SALDO:Q']
        ).interactive()

        st.altair_chart(saldo_chart, use_container_width=True)
else:
    st.info("Aguardando o upload de uma planilha no formato CSV na barra lateral esquerda.")