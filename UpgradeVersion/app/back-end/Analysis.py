# pip install flask streamlit pandas plotly openpyxl psutil matplotlib
# streamlit run Analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
#Define basePath
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@st.cache_data(hash_funcs={"_thread.RLock": lambda _: None})
def read_file(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        return pd.DataFrame()  #Return an empty DataFrame if file doesn't exist
#Modify to read Excel from 'files' folder with a fixed name
file_path = os.path.join(base_path, 'files', 'file.xlsx')
df = read_file(file_path)

if df.empty:
    st.warning('Nenhum arquivo encontrado para análise. Por favor, importe uma planilha.')
else:
    #Rename coluns t/be + intuitivs
    df.rename(columns={
        'Custo Gás': 'Total Gasto',
        'Litros': 'Total Litros',
        'Dif Km': 'Total Km',
        'Dif Hr': 'Total Hr',
        'Km/Lt': 'Media Km/Lt',
        'Hr/Lt': 'Media Hr/Lt'
    }, inplace=True)

    #Functn p/ calc análise mensal
    def monthly_analysis(df, month, year):
        df['Data'] = pd.to_datetime(df['Data'])
        df_filtered = df[(df['Data'].dt.month == month) & (df['Data'].dt.year == year)]
        
        if df_filtered.empty:
            st.warning('Nenhum dado encontrado para o mês e ano especificados.')
            return pd.DataFrame()  #Return an empty DataFrame if no data is found

        df_grouped = df_filtered.groupby(['Veículo/Equip.', 'Base', 'Tipo', 'Modelo', 'PLACA/']).agg({
            'Total Gasto': 'sum',
            'Total Litros': 'sum',
            'Total Km': 'sum',
            'Total Hr': 'sum',
            'Media Km/Lt': 'mean',
            'Media Hr/Lt': 'mean',
            'KmAtual': 'max',
            'Horas': 'max'
        }).reset_index()

        return df_grouped

    #Entrad d'user p/mês e ano
    st.sidebar.header('Selecione o mês e o ano')
    month = st.sidebar.selectbox('Mês', range(1, 13))
    year = st.sidebar.selectbox('Ano', range(2000, 2100))

    #Filtrs adicionais
    st.sidebar.header('Filtros adicionais')
    veiculo_placa = st.sidebar.text_input('Veículo ou Placa', '')
    base_options = df['Base'].unique().tolist()
    base = st.sidebar.multiselect('Base', base_options)
    tipo = st.sidebar.text_input('Tipo', '')

    df_monthly = monthly_analysis(df, month, year)

    if not df_monthly.empty:
        #Apply filtrs added
        if veiculo_placa:
            df_monthly = df_monthly[df_monthly['Veículo/Equip.'].str.contains(veiculo_placa, case=False, na=False) | df_monthly['PLACA/'].str.contains(veiculo_placa, case=False, na=False)]
        if base:
            df_monthly = df_monthly[df_monthly['Base'].isin(base)]
        if tipo:
            df_monthly = df_monthly[df_monthly['Tipo'].str.contains(tipo, case=False, na=False)]

        st.title(f'Análise Mensal dos Caminhões Betoneira - {month}/{year}')
        st.write("Tabela de Dados Filtrados:")
        st.write(df_monthly)
        
        fig = px.histogram(df_monthly, x='Veículo/Equip.', y='Total Km', color='Veículo/Equip.', hover_data=['KmAtual', 'Horas'])
        fig.update_layout(
            title="Distância Percorrida por Veículo",
            xaxis_title="Veículo/Equipamento",
            yaxis_title="Total Km"
        )
        st.plotly_chart(fig)
        #Export Dados t/Excel
        if st.button('Exportar Dados Mensais para Excel'):
            with pd.ExcelWriter(os.path.join(base_path, 'files', 'dados_mensais.xlsx'), engine='openpyxl') as writer:
                df_monthly.to_excel(writer, index=False, sheet_name='Dados Mensais')
            st.write('Dados exportados para Excel com sucesso!')
            with open(os.path.join(base_path, 'files', 'dados_mensais.xlsx'), 'rb') as f:
                st.download_button('Baixar Dados Mensais', f, file_name='dados_mensais.xlsx')

    #Functn t/remov arqvs
    if st.button('Limpar'):
        dir_path = os.path.join(base_path, 'files')
        for f in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, f))
        st.write('Arquivos limpos com sucesso!')