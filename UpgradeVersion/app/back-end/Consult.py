# pip install flask streamlit pandas plotly openpyxl psutil
# streamlit run Consult.py
import streamlit as st
import pandas as pd
import os
import calendar
from io import BytesIO
#Define basePath
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@st.cache_data(hash_funcs={"_thread.RLock": lambda _: None})
def read_file(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        return pd.DataFrame()  #Return an empty DataFrame if file doesn't exist

#Modify to read Excel from 'files' folder with fixed names
file_path_main = os.path.join(base_path, 'files', 'file.xlsx')
file_path_fuel = os.path.join(base_path, 'files', 'valor_combustivel.xlsx')

df_main = read_file(file_path_main)
df_fuel = read_file(file_path_fuel)

if df_main.empty or df_fuel.empty:
    st.warning('Nenhum arquivo encontrado para análise. Por favor, importe as planilhas necessárias.')
else:
    #Rename columns t/be + intuitvs
    df_main.rename(columns={
        'Custo Gás': 'Total Gasto',
        'Litros': 'Total Litros',
        'Dif Km': 'Total Km',
        'Dif Hr': 'Total Hr',
        'Km/Lt': 'Media Km/Lt',
        'Hr/Lt': 'Media Hr/Lt'
    }, inplace=True)

    #Functn t/calc DailyCost ofGás perBase
    def daily_fuel_cost_by_base(df_main, df_fuel, month, year):
        df_main['Data'] = pd.to_datetime(df_main['Data'])
        df_fuel['Data'] = pd.to_datetime(df_fuel['Data'])
        df_filtered = df_main[(df_main['Data'].dt.month == month) & (df_main['Data'].dt.year == year)].copy()
        if df_filtered.empty:
            st.warning('Nenhum dado encontrado para o mês e ano especificados.')
            return pd.DataFrame()  #Return an empty DataFrame if no data is found

        df_filtered['Dia'] = df_filtered['Data'].dt.day
        #Create DataFrame w/all t-Month's Days & Realiz t-junção
        num_days = calendar.monthrange(year, month)[1]
        all_days = pd.DataFrame({'Dia': range(1, num_days + 1)})
        df_filtered = pd.merge(all_days, df_filtered, on='Dia', how='left')

        #Obte value unitário d-combustv t/each day based onT-date + próx
        df_fuel_sorted = df_fuel.sort_values(by='Data')
        df_filtered['Valor Unit'] = df_filtered['Data'].apply(
            lambda x: df_fuel_sorted[df_fuel_sorted['Data'] <= x]['Valor Unit'].iloc[-1] 
                      if not df_fuel_sorted[df_fuel_sorted['Data'] <= x].empty else 0
        )
        #Calc cost total d combustível
        df_filtered['Custo'] = df_filtered['Total Litros'] * df_filtered['Valor Unit']
        df_pivot = df_filtered.pivot_table(index='Base', columns='Dia', values=['Total Litros', 'Custo', 'Valor Unit'], aggfunc='sum', fill_value=0)
        df_pivot.columns = [f'{col[0]} {col[1]}' for col in df_pivot.columns]
        #Add colun Total
        df_pivot['Total Litros'] = df_pivot[[col for col in df_pivot.columns if 'Total Litros' in col]].sum(axis=1)
        df_pivot['Total Custo'] = df_pivot[[col for col in df_pivot.columns if 'Custo' in col]].sum(axis=1)
        return df_pivot
    #Entrad d user t/ month e year
    st.sidebar.header('Selecione o mês e o ano')
    month = st.sidebar.selectbox('Mês', range(1, 13))
    year = st.sidebar.selectbox('Ano', range(2000, 2100))
    if st.sidebar.button('Custo Base'):
        df_daily_cost = daily_fuel_cost_by_base(df_main, df_fuel, month, year)
        if not df_daily_cost.empty:
            st.title(f'Custo Diário de Combustível por Base - {month}/{year}')
            st.write("Tabela de Custo Diário de Combustível:")
            st.write(df_daily_cost)
            #Export Data t/Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_daily_cost.to_excel(writer, index=True, sheet_name='Custo Diário')
            buffer.seek(0)

            st.download_button(
                label='Baixar Dados de Custo Diário',
                data=buffer,
                file_name='custo_diario.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    #Functn t/remov arqvs
    if st.button('Limpar'):
        dir_path = os.path.join(base_path, 'files')
        for f in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, f))
        st.write('Arquivos limpos com sucesso!')