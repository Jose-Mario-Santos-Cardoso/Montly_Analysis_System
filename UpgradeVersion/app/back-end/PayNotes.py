import pandas as pd
import streamlit as st
import os

# Definir caminho base
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@st.cache_data(hash_funcs={"_thread.RLock": lambda _: None})
def read_file(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        return pd.DataFrame()  # Retorna um DataFrame vazio se o arquivo não existir

# Carregar as planilhas importadas
compras_todas_path = os.path.join(base_path, 'files', 'compras_todas.xlsx')
compras_pendentes_path = os.path.join(base_path, 'files', 'compras_pendentes.xlsx')

df_compras_todas = read_file(compras_todas_path)
df_compras_pendentes = read_file(compras_pendentes_path)

if df_compras_todas.empty or df_compras_pendentes.empty:
    st.warning('Nenhuma das planilhas de compras foi encontrada. Por favor, importe as planilhas.')
else:
    # Excluir colunas desnecessárias
    colunas_excluir = ['Status', 'Dt.Venc.Prazo']
    df_compras_todas = df_compras_todas.drop(columns=colunas_excluir, errors='ignore')
    df_compras_pendentes = df_compras_pendentes.drop(columns=colunas_excluir, errors='ignore')

    # Criar coluna "Ref" para verificar duplicidade usando merge
    df_compras_pendentes = df_compras_pendentes.merge(
        df_compras_todas[['Chave Dfe']],
        on='Chave Dfe',
        how='left',
        indicator='Ref'
    )
    df_compras_pendentes['Ref'] = df_compras_pendentes['Ref'].apply(lambda x: 'N/D/A' if x == 'left_only' else 'Duplicado')

    # Filtrar registros que ainda não foram inseridos
    df_compras_novas = df_compras_pendentes[df_compras_pendentes['Ref'] == 'N/D/A'].copy()

    # Adicionar novas colunas e preencher com valores padrão
    df_compras_novas.loc[:, 'Produto'] = ''
    df_compras_novas.loc[:, 'Forma Pagamento'] = ''
    df_compras_novas.loc[:, 'Autorizado por:'] = ''
    df_compras_novas.loc[:, 'NF'] = ''
    df_compras_novas.loc[:, 'Comentário'] = ''

    # Dicionário de palavras-chave e classificações para Produto
    classificacoes_produto = {
        '##': ['C******', 'A****', 'E***', 'P*#', 'C#'],
        'P# G#': ['P#', 'P*', 'P#', 'C#', 'P# */*'],
        'C# B**': ['F*', 'I#'],
        'M* F*': ['F#', 'P# A#', 'V#', 'M#', 'F#', 'M#', 'E# H#', 'A# P#'],
        'A*#': ['P* Q*', 'M#'],
        'P# L# C#': ['S* D#'],
        'P# T#': ['P# * D#'],
        'D*': ['P*', 'P*', 'B*'],
        'L# * C#': ['L#'],
        'M# R# P#': ['P# C# * S#'],
        'M# C#': ['T* M*'],
        'B#': ['D# X#'],
        'R#': ['R#*'],
        'M# P#': ['W*'],
        'M# U#': ['U*-B*'],
        'B#': ['B#'],
        'A* U* I*': ['L#'],
        'A###': ['G##'],
        'A##': ['#']
    }

    # Função para classificar produtos
    def classificar_produto(nome):
        for categoria, palavras in classificacoes_produto.items():
            if any(palavra in nome for palavra in palavras):
                return categoria
        return ''

    # Aplicar a classificação dos produtos
    df_compras_novas.loc[:, 'Produto'] = df_compras_novas['Nome'].apply(classificar_produto)

    # Regras para preencher a coluna "Forma Pagamento"
    def definir_forma_pagamento(produto):
        if produto == '**':
            return 'F#'
        elif produto == 'P# G#':
            return 'T#'
        return ''

    # Aplicar a definição de forma de pagamento
    df_compras_novas.loc[:, 'Forma Pagamento'] = df_compras_novas['Produto'].apply(definir_forma_pagamento)

    # Regras para preencher a coluna "Autorizado por:"
    def definir_autorizado_por(linha):
        nome, produto, forma_pagamento = linha['Nome'], linha['Produto'], linha['Forma Pagamento']
        if forma_pagamento in ['F#', 'T#']:
            return ''
        elif 'CIA #' in nome or 'EM##' in nome:
            return ''
        elif produto in ['', '', '', '', '']:
            return ''
        elif produto in ['', '', '', '', '']:
            return ''
        return ''

    # Aplicar a definição de autorizado por
    df_compras_novas.loc[:, 'Autorizado por:'] = df_compras_novas.apply(definir_autorizado_por, axis=1)

    # Regras para preencher a coluna "Status"
    def definir_status(produto):
        if produto == '':
            return ''
        elif produto == '':
            return ''
        return ''

    # Aplicar a definição de status
    df_compras_novas.loc[:, 'Status'] = df_compras_novas['Produto'].apply(definir_status)

    # Reorganizar a ordem das colunas
    colunas_ordem = ['Filial', 'Num. Dfe XML', 'Chave Dfe', 'CNPJ', 'Nome', 'Valor DFe XML', 
                     'Dt.Emissão', 'Produto', 'Forma Pagamento', 'Autorizado por:', 
                     'NF', 'Status', 'Comentário']
    df_compras_novas = df_compras_novas.reindex(columns=colunas_ordem)

    # Exibir os registros de compras pendentes prontos para serem registrados
    st.write("Registros de Compras (Pendentes) Prontos para Registro:")
    st.write(df_compras_novas)

    # Exportar o resultado filtrado para um arquivo Excel
    output_path = os.path.join(base_path, 'files', 'relatorio_compras_pendentes.xlsx')
    df_compras_novas.to_excel(output_path, index=False)
    st.success(f'Relatório gerado: {output_path}')
    st.download_button(label='Baixar Relatório', data=open(output_path, 'rb').read(), file_name='relatorio_compras_pendentes.xlsx')
