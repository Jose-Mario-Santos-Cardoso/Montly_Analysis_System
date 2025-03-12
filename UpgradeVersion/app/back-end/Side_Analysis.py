# pip install flask streamlit pandas plotly openpyxl psutil
# streamlit run Side_Analysis.py
import streamlit as st
import pandas as pd
import os
import calendar
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
    #Rename coluns p/be + intuitvs
    df.rename(columns={
        'Custo Gás': 'Total Gasto',
        'Litros': 'Total Litros',
        'Dif Km': 'Total Km',
        'Dif Hr': 'Total Hr',
        'Km/Lt': 'Media Km/Lt',
        'Hr/Lt': 'Media Hr/Lt'
    }, inplace=True)
    #Funç p/calc consum daily-lts/base
    def daily_consumption_by_base(df, month, year):
        df['Data'] = pd.to_datetime(df['Data'])
        df_filtered = df[(df['Data'].dt.month == month) & (df['Data'].dt.year == year)].copy()
        if df_filtered.empty:
            st.warning('Nenhum dado encontrado para o mês e ano especificados.')
            return pd.DataFrame()  #Return an empty DataFrame if no data is found
        df_filtered['Dia'] = df_filtered['Data'].dt.day
        #Creat DataFrame c/all day d mês&realiz junção
        num_days = calendar.monthrange(year, month)[1]
        all_days = pd.DataFrame({'Dia': range(1, num_days + 1)})
        df_filtered = pd.merge(all_days, df_filtered, on='Dia', how='left')
        df_pivot = df_filtered.pivot_table(index='Base', columns='Dia', values='Total Litros', aggfunc='sum', fill_value=0)
        df_pivot.columns = [f'{col}°' if col == 1 else f'Dia {col}' for col in df_pivot.columns]
        #Add colun Total
        df_pivot['Total'] = df_pivot.sum(axis=1)
        return df_pivot
    #Entrad user p/mês e ano
    st.sidebar.header('Selecione o mês e o ano')
    month = st.sidebar.selectbox('Mês', range(1, 13))
    year = st.sidebar.selectbox('Ano', range(2000, 2100))
    #Filtrs added
    st.sidebar.header('Filtros adicionais')
    base_options = df['Base'].unique().tolist()
    base = st.sidebar.multiselect('Base', base_options)
    df_daily = daily_consumption_by_base(df, month, year)
    if not df_daily.empty:
        #Apply filtrsAdicionais
        if base:
            df_daily = df_daily[df_daily.index.isin(base)]
        st.title(f'Consumo Diário de Litros por Base - {month}/{year}')
        st.write("Tabela de Consumo Diário de Litros:")
        st.write(df_daily)
        #Export Data p/Excel
        if st.button('Exportar Dados Diários para Excel'):
            with pd.ExcelWriter(os.path.join(base_path, 'files', 'consumo_diario.xlsx'), engine='openpyxl') as writer:
                df_daily.to_excel(writer, index=True, sheet_name='Consumo Diário')
            st.write('Dados exportados para Excel com sucesso!')
            with open(os.path.join(base_path, 'files', 'consumo_diario.xlsx'), 'rb') as f:
                st.download_button('Baixar Dados Diários', f, file_name='consumo_diario.xlsx')
    #Functn p/remov arqvs
    if st.button('Limpar'):
        dir_path = os.path.join(base_path, 'files')
        for f in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, f))
        st.write('Arquivos limpos com sucesso!')