import pandas as pd                                 # Lib para manipução e tratamento de dados, tabelas e dataframes
import streamlit as st                              # Lib para construção de deashboards interativos
import requests                                     # Lib para requisições de APIs
import plotly.express as px                         # Lib de alto nivel para formatação rápida de gráficos
import plotly.graph_objects as go                   # Lib de baixo nível para alteração de plotagem do plotly
import locale                                       # Lib para setar o padrão de separação decimal BR
import time                                         # Módulo para pequenas manipulações de tempo interativo
import io                                           # Lib nativa para input / output binário
import xlsxwriter                                   # Lib para engine de arquivos excel



# Configurações de exibição para o usuário
st.set_page_config(page_title = 'DASHBOARD SPAECE', initial_sidebar_state = 'collapsed', layout = 'wide',
                   menu_items={'About': 'Desenvolvido por José Alves Ferreira Neto - https://www.linkedin.com/in/jos%C3%A9-alves-ferreira-neto-1bbbb8192/ | jose.alvesfn@gmail.com',
                               'Report a bug': 'https://www.linkedin.com/in/jos%C3%A9-alves-ferreira-neto-1bbbb8192/',
                               'Get help': 'https://www.seduc.ce.gov.br/'})


# Imagem principal do projeto
# image = 'spaece.jpg'
# st.image(image, use_column_width=False)

#Imagem lateral (sidebar)
image = "spaece_tp2.png"
st.sidebar.image(image)

## ------------------------ FUNCOES ------------------------ ##

# Definindo para configuração regional de separador decimal, moeda, horas, etc
#locale.setlocale(locale.LC_ALL, 'pt_BR.UTF8')
#locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Funcoes que formatam números, tanto para para utilização nas métricas

# Formatando e mantendo 2 casas decimais
# def formata_numero(valor, prefixo = ''):
#     for unidade in ['', 'mil', 'milhões']:
#         if valor < 1000:
#             return f'{prefixo} {valor:.2f} {unidade}'
#         valor = valor / 1000

# Formatando com "."
# def formata_numero(valor, prefixo=''):
#     for unidade in ['', 'mil', 'milhões']:
#         if valor < 1000:
#             if valor.is_integer():  # Verifica se o valor é um número inteiro
#                 return f'{prefixo} {int(valor):,d} {unidade}'
#             else:
#                 return f'{prefixo} {valor:,.2f} {unidade}'
#         valor = valor / 1000


# Formatando com "," (Padrão nacional)
# def formata_numero(valor, prefixo=''):
#     for unidade in ['', 'mil', 'milhões']:
#         if valor < 1000:
#             if valor.is_integer():
#                 return f'{prefixo} {locale.format("%.0f", valor, grouping=True)} {unidade}'
#             elif 100 <= valor < 1000:
#                 return f'{prefixo} {locale.format("%.1f", valor, grouping=True)} {unidade}'
#             else:
#                 return f'{prefixo} {locale.format("%.2f", valor, grouping=True)} {unidade}'
#         valor = valor / 1000

def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil', 'milhões']:
        if valor < 1000:
            valor_str = f'{valor:.2f}'  # Converte o valor para string com 2 casas decimais
            valor_str = valor_str.replace('.', '|').replace(',', '.').replace('|', ',')  # Substitui os separadores
            if valor.is_integer():
                return f'{prefixo} {valor_str.replace(",00", "")} {unidade}'  # Remove o ",00" quando for um número inteiro
            return f'{prefixo} {valor_str} {unidade}'
        valor = valor / 1000


## Funcao para valores dos rótulos dos gráficos
def formata_numero_v2(valor, prefixo=''):
    valor_formatado = f'{prefixo} {valor:.2f}'
    return valor_formatado

## Função para formatar a taxa de participação
def formata_taxa(valor):
    return f'{valor:.1f}'.replace('.', ',')

## Função para formatar a proficiência da métrica
def formata_proficiencia(valor):
    return f'{valor:.1f}'.replace('.', ',')

# Mensagem para o usuário (interajir com o side bar)
st.markdown('<span style="color: blue; font-weight: bold"> :arrow_upper_left: Interaja para mais opções.</span>', unsafe_allow_html=True)

# Definindo o título para o dashboard
st.title('Plataforma de visualização de dados do SPAECE :chart_with_upwards_trend:')
#st.markdown('<span style="color: green;"><b>2º Ano Ensino Fundamental - SPAECE ALFA - Dashboard: Estado do Ceará</b></span>', unsafe_allow_html=True)

# Funcao para capitalizar nomes completos (aqui usar nos numicípios)
def capitalizar_nome(nome_completo):
    # Palavras que não serão capitalizadas
    palavras_nao_capitalizadas = ['da', 'de', 'do', 'das', 'dos', 'e']

    # Divide o nome completo em palavras
    palavras = nome_completo.lower().split()

    # Capitaliza todas as palavras que não estão na lista de palavras não capitalizadas
    nome_capitalizado = ' '.join([palavra.capitalize() if palavra not in palavras_nao_capitalizadas else palavra for palavra in palavras])

    return nome_capitalizado

# Funcoes para dowload de arquivos
## Dowmload de .csv
@st.cache_data # Decorator necessário para evitar a geração contínua de muitos arquivos iguais
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

## Dowmload de .xlsx
@st.cache_data # Decorator necessário para evitar a geração contínua de muitos arquivos iguais
def converte_xlsx(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter', datetime_format='yyyy-mm-dd', date_format='yyyy-mm-dd') as writer:  # Para valores de datas constantes no df
        df.to_excel(writer, index=False)   # Chamada da funcao do pandas to_excel
        workbook = writer.book  # workbook é uma variável que representa o objeto do livro do Excel (Workbook) associado ao ExcelWriter (objeto writer).         
        worksheet = writer.sheets['Sheet1'] # worksheet é uma variável que representa uma planilha específica dentro do livro do Excel. 
        header_format = workbook.add_format({'border': False}) # header_format é uma variável que representa um objeto de formatação (Format) no workbook
        for col_num, value in enumerate(df.columns.values): # Usando workbook.add_format(), criamos um novo objeto de formatação e o associamos ao workbook (livro do Excel)
            worksheet.write(0, col_num, value, header_format)
    output.seek(0) # mover o cursor de leitura/escrita para a posição 0 (início) no fluxo de bytes.
    return output.getvalue()

## Mensagem de sucesso
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(3)  
    sucesso.empty()


# ------------------------ SOLICITACOES / FILTRAGENS ------------------------ ##

# Carregar o arquivo para MUN em CSV do GitHub
url_mun = 'https://raw.githubusercontent.com/jose-alves-fn/jose-alves-fn-tabelas_spaece_memoria_2008_2022/main/memoria_mun_todas_etapas_v2.csv'
dados_mun = pd.read_csv(url_mun)

## Titulo do sidebar
st.sidebar.title('Filtros')

## Filtragem de redes
dados_mun['Rede'] = dados_mun['Rede'].str.capitalize()
redes = ['Municipal', 'Estadual']
rede = st.sidebar.selectbox('Rede', redes)

# ## Filtragem da etapa
# etapas = dados_mun['Etapa'].unique()
# etapa = st.sidebar.selectbox('Etapa', etapas)

## Filtragem de município
dados_mun['Município'] = dados_mun['Município'].apply(capitalizar_nome)  # Aplicando a função capitalizar_nome()
municipios = dados_mun['Município'].unique()
municipio = st.sidebar.selectbox('Município', municipios)

# Filtragem de componente
componentes = ['Língua Portuguesa', 'Matemática']
componente = st.sidebar.selectbox('Componente', componentes)

# Filtragem das edições
st.sidebar.markdown('<span style="font-size: 13.7px;">Desmarque para escolher uma ou mais opções</span>', unsafe_allow_html=True)
todos_as_edicoes = st.sidebar.checkbox('Todas as edições', value = True)
if todos_as_edicoes: 
    edicao = dados_mun['Edição'].unique()
else:
    edicao = st.sidebar.multiselect('Edição', dados_mun['Edição'].unique())
# # Filtragem dos padroes de desempenho
# todos_os_padroes = st.sidebar.checkbox('Todos os padrões de desempenho', value = True)
# if todos_os_padroes:
#     padroes = dados_mun['Indicação do Padrão de Desempenho'].unique()
# else:
#     padroes = st.sidebar.multiselect('Indicação do Padrão de Desempenho', dados_mun['Indicação do Padrão de Desempenho'].unique())

## Filtragem da proficiencia media
todas_as_proficiencias = st.sidebar.checkbox('Todas as proficiências médias', value = True)
if todas_as_proficiencias: # Aqui por hora definimos o default acima como True, ou seja, não ocorrerá filtragem
    proficiencia = (0, 500)
else:
    proficiencia = st.sidebar.slider('Selecione um intervalo', 0, 500, value = (0,500)) # Três parâmetros, sendo 1. Label, 2. Min, 3. Max

# Filtrar os dados com base na seleção dos filtros acima
dados_filtrados = dados_mun[
                        (dados_mun['Rede'] == rede) &
                        #(dados_mun['Etapa'] == etapa) &
                        (dados_mun['Município'] == municipio) &
                        (dados_mun['Componente'] == componente) &
                        (dados_mun['Edição'].isin(edicao)) &
                        #(dados_mun['Indicação do Padrão de Desempenho'].isin(padroes)) &
                        (dados_mun['Proficiência Média'].between(proficiencia[0], proficiencia[1]))
]

## ------------------------ TABELAS ------------------------ ##

## ------------------------ 2º ANO ------------------------- ##


dados_mun_2_ano = dados_filtrados[['Etapa', 'Componente', 'Rede', 'Código da CREDE', 'CREDE', 'Município', 
                                'Edição', 'Proficiência Média', 'Desvio Padrão', 'Indicação do Padrão de Desempenho',
                                '% Não Alfabetizado', '% Alfabetização Incompleta',
                                '% Intermediário (2º Ano)', '% Suficiente', '% Desejável',
                                'Nº de Alunos Previstos', 'Nº de Alunos Avaliados', 'Participação (%)']]

### Filtro de etapa para a tabela
dados_mun_2_ano = dados_mun_2_ano[dados_mun_2_ano['Etapa'] == '2º Ano do Ensino Fundamental'] 

### Renomeando o padrão Intermediário (por default na base vem diferente)
dados_mun_2_ano = dados_mun_2_ano.rename(columns={'% Intermediário (2º Ano)': '% Intermediário'})

### Criando tabelas para a proficiencia por edicao
proficiencia_edicao_2_mun = dados_mun_2_ano.groupby('Edição')['Proficiência Média'].mean().reset_index()
proficiencia_edicao_2_mun['Proficiência Média'] = proficiencia_edicao_2_mun['Proficiência Média'].round(1)

### Criando tabela para a distribuição por padrão de desempenho
dados_barras_empilhadas_2_mun = dados_mun_2_ano[['Edição', '% Não Alfabetizado', '% Alfabetização Incompleta', '% Intermediário', '% Suficiente', '% Desejável']]

### Criando tabela para participação por edição 
dados_linhas_participação_2_mun = dados_mun_2_ano[['Edição', 'Participação (%)']]


## ------------------------ 5º ANO ------------------------- ##

dados_mun_5_ano = dados_filtrados[['Etapa', 'Componente', 'Rede', 'Código da CREDE', 'CREDE', 'Município', 
                                'Edição', 'Proficiência Média', 'Desvio Padrão', 'Indicação do Padrão de Desempenho',
                                '% Muito Crítico', '% Crítico', '% Intermediário', '% Adequado',
                                'Nº de Alunos Previstos', 'Nº de Alunos Avaliados', 'Participação (%)']]

### Filtro de etapa para a tabela
dados_mun_5_ano = dados_mun_5_ano[dados_mun_5_ano['Etapa'] == '5º Ano do Ensino Fundamental']    

### Criando tabelas para a proficiencia por edicao
proficiencia_edicao_5_mun = dados_mun_5_ano.groupby('Edição')['Proficiência Média'].mean().reset_index()
proficiencia_edicao_5_mun['Proficiência Média'] = proficiencia_edicao_5_mun['Proficiência Média'].round(1)

### Criando tabela para a distribuição por padrão de desempenho
dados_barras_empilhadas_5_mun = dados_mun_5_ano[['Edição', '% Muito Crítico', '% Crítico', '% Intermediário', '% Adequado',]]

### Criando tabela para participação por edição 
dados_linhas_participação_5_mun = dados_mun_5_ano[['Edição', 'Participação (%)']]


## ------------------------ 9º ANO ------------------------- ##

dados_mun_9_ano = dados_filtrados[['Etapa', 'Componente', 'Rede', 'Código da CREDE', 'CREDE', 'Município', 
                                'Edição', 'Proficiência Média', 'Desvio Padrão', 'Indicação do Padrão de Desempenho',
                                '% Muito Crítico', '% Crítico', '% Intermediário', '% Adequado',
                                'Nº de Alunos Previstos', 'Nº de Alunos Avaliados', 'Participação (%)']]

dados_mun_9_ano = dados_mun_9_ano[dados_mun_9_ano['Etapa'] == '9º Ano do Ensino Fundamental']    

### Criando tabelas para a proficiencia por edicao
proficiencia_edicao_9_mun = dados_mun_9_ano.groupby('Edição')['Proficiência Média'].mean().reset_index()
proficiencia_edicao_9_mun['Proficiência Média'] = proficiencia_edicao_9_mun['Proficiência Média'].round(1)

### Criando tabela para a distribuição por padrão de desempenho
dados_barras_empilhadas_9_mun = dados_mun_9_ano[['Edição', '% Muito Crítico', '% Crítico', '% Intermediário', '% Adequado',]]

### Criando tabela para participação por edição 
dados_linhas_participação_9_mun = dados_mun_9_ano[['Edição', 'Participação (%)']]


## ------------------------ 3ª SERIE ------------------------- ##

dados_mun_3_ano = dados_filtrados[['Etapa', 'Componente', 'Rede', 'Código da CREDE', 'CREDE', 'Município', 
                                'Edição', 'Proficiência Média', 'Desvio Padrão', 'Indicação do Padrão de Desempenho',
                                '% Muito Crítico', '% Crítico', '% Intermediário', '% Adequado',
                                'Nº de Alunos Previstos', 'Nº de Alunos Avaliados', 'Participação (%)']]

dados_mun_3_ano = dados_mun_3_ano[dados_mun_3_ano['Etapa'] == '3ª Série do Ensino Médio']    

### Criando tabelas para a proficiencia por edicao
proficiencia_edicao_3_mun = dados_mun_3_ano.groupby('Edição')['Proficiência Média'].mean().reset_index()
proficiencia_edicao_3_mun['Proficiência Média'] = proficiencia_edicao_3_mun['Proficiência Média'].round(1)

### Criando tabela para a distribuição por padrão de desempenho
dados_barras_empilhadas_3_mun = dados_mun_3_ano[['Edição', '% Muito Crítico', '% Crítico', '% Intermediário', '% Adequado',]]

### Criando tabela para participação por edição 
dados_linhas_participação_3_mun = dados_mun_3_ano[['Edição', 'Participação (%)']]

## ------------------------ GRÁFICOS ------------------------ ##

## ------------------------ 2º ANO ------------------------- ##

# Criação das figuras vazias para os gráficos
fig_proficiencia_edicao_2_mun = go.Figure()
fig_participacao_edicao_2_mun = go.Figure()
fig_proficiencia_edicao_2_mun_bar = go.Figure()
fig_barras_empilhadas_2_mun = go.Figure()

if componente == 'Matemática':
    pass
else:

    ### Gráfico de LINHAS para proficiência média longitudinal

    # Formatando manualmente os valores do eixo y (atenção o locale-br não funciona em todos as aplicações)
    # proficiencia_edicao_2_mun['Proficiência Média Formatada'] = proficiencia_edicao_2_mun['Proficiência Média'].apply(lambda x: locale.format('%.1f', x))
    proficiencia_edicao_2_mun['Proficiência Média Formatada'] = proficiencia_edicao_2_mun['Proficiência Média'].apply(lambda x: f'{x:.1f}'.replace('.', ','))

    fig_proficiencia_edicao_2_mun = px.line(proficiencia_edicao_2_mun,
                                x = 'Edição',
                                y = 'Proficiência Média',
                                markers=True,
                                range_y = (75, 270),
                                text='Proficiência Média Formatada',
                                #color = 'Edição',
                                #line_dash = 'Edição',
                                title = f'PROFICIÊNCIA MÉDIA - 2º ANO - {(componente).upper()} - {(municipio).upper()}'
                                )

    #fig_proficiencia_edicao_2_mun.update_layout(yaxis_title = 'Proficiência Média')
    fig_proficiencia_edicao_2_mun.update_layout(xaxis=dict(type='category', categoryorder='category ascending'))  # Definir o tipo de eixo como categoria
    #proficiencia_edicao_2_mun.update_xaxes(showgrid=False, showline=True, linecolor='lightgray')
    #proficiencia_edicao_2_mun.update_yaxes(showgrid=True, showline=True, linecolor='lightgray')
    fig_proficiencia_edicao_2_mun.update_traces(textposition='bottom center', line=dict(color='#548235'))  # Ajustar a posição dos rótulos de dados


### Gráfico de LINHAS para participação

    # Formatando manualmente os valores do eixo y
    dados_linhas_participação_2_mun['Participação Formatada'] = dados_linhas_participação_2_mun['Participação (%)'].apply(lambda x: f'{x:.1f}'.replace('.', ','))

    fig_participacao_edicao_2_mun = px.line(dados_linhas_participação_2_mun,
                                x = 'Edição',
                                y = 'Participação (%)',
                                markers=True,
                                range_y = (30, 135),
                                text='Participação Formatada',
                                #color = 'Edição',
                                #line_dash = 'Edição',
                                title = f'PARTICIPAÇÃO - 2º ANO - {(municipio).upper()}'
                                )

    fig_participacao_edicao_2_mun.update_layout(xaxis=dict(type='category', categoryorder='category ascending'))  # Definir o tipo de eixo como categoria
    # Usar o parametro do xaxis title = 0.25 ou mais para ajustar o titulo
    # fig_participacao_edicao_2_mun.update_xaxes(showgrid=False, showline=True, linecolor='lightgray')
    # fig_participacao_edicao_2_mun.update_yaxes(showgrid=True, showline=True, linecolor='lightgray')
    fig_participacao_edicao_2_mun.update_traces(textposition='bottom center', line=dict(color='#548235'))  # Ajustar a posição dos rótulos de dados

### Gráfico de BARRAS para padrões de desempenho longitudinal

    # Definir os intervalos de cores e as respectivas cores
    intervalos_2_ano = [0, 75, 100, 125, 150, 500]
    cores = ['#FF0000', '#FFC000', '#FFFF00', '#C6E0B4', '#548235']

    # Adicionar uma coluna "Intervalo" ao DataFrame com base nos intervalos
    proficiencia_edicao_2_mun['Intervalo'] = pd.cut(proficiencia_edicao_2_mun['Proficiência Média'], bins=intervalos_2_ano, labels=False)

    padrao_map = {
        0: 'Não alfabetizado',
        1: 'Alfabetização incompleta',
        2: 'Intermediário',
        3: 'Suficiente',
        4: 'Desejável'
    }

    # Formatando manualmente os valores do eixo y
    #proficiencia_edicao_2_ce['Proficiência Média Formatada'] = proficiencia_edicao_2_ce['Proficiência Média'].apply(lambda x: locale.format('%.1f', x))
    proficiencia_edicao_2_mun['Proficiência Média Formatada'] = proficiencia_edicao_2_mun['Proficiência Média'].apply(lambda x: f'{x:.1f}'.replace('.', ','))


    fig_proficiencia_edicao_2_mun_bar = go.Figure()

    for i, intervalo in enumerate(intervalos_2_ano[:-1]):
        data = proficiencia_edicao_2_mun[proficiencia_edicao_2_mun['Intervalo'] == i]
        fig_proficiencia_edicao_2_mun_bar.add_trace(go.Bar(
            x=data['Edição'],
            y=data['Proficiência Média'],
            marker=dict(color=cores[i]),
            name=padrao_map[i],
            text=data['Proficiência Média Formatada'],
            textposition='outside'
        ))

    fig_proficiencia_edicao_2_mun_bar.update_layout(
        xaxis=dict(type='category', categoryorder='category ascending'),
        yaxis=dict(range=[50, 270]),
        title=f'PADRÃO DE DESEMPENHO - 2º ANO - {(municipio.upper())}'
    )

    # fig_proficiencia_edicao_2_ce_bar.update_traces(marker=dict(line=dict(color='rgb(8,8,8)',width=1.5)))
    # fig_proficiencia_edicao_2_ce_bar.show()

### Gráfico de BARRAS EMPILHADAS para padrões de desempenho percentual

    # Alterando as edições localmente para que o eixo y compreenda
    mapeamento_edicoes = {
        '2019': '(2019)',
        '2018': '(2018)',
        '2017': '(2017)',
        '2016': '(2016)',
        '2015': '(2015)',
        '2014': '(2014)',
        '2013': '(2013)',
        '2012': '(2012)',
        '2011': '(2011)',
        '2010': '(2010)',
        '2009': '(2009)',
        '2008': '(2008)',
        '2007': '(2007)'
    }

    dados_barras_empilhadas_2_mun['Edição'] = dados_barras_empilhadas_2_mun['Edição'].replace(mapeamento_edicoes)

    # Criando um dict para passar as cores para os padrões
    intervalos_2_ano = ['% Não Alfabetizado', '% Alfabetização Incompleta', '% Intermediário', '% Suficiente', '% Desejável']
    cores = ['#FF0000', '#FFC000', '#FFFF00', '#C6E0B4', '#548235']
    mapeamento_cores = dict(zip(intervalos_2_ano, cores))

    # Criação da figura
    fig_barras_empilhadas_2_mun = go.Figure()

    # Usando um loop for para iterar e gerar cada barra
    for intervalo in intervalos_2_ano:
            fig_barras_empilhadas_2_mun.add_trace(go.Bar(
            y=dados_barras_empilhadas_2_mun['Edição'],
            x=dados_barras_empilhadas_2_mun[intervalo],
            name=intervalo,
            orientation='h',
            text = dados_barras_empilhadas_2_mun[intervalo].apply(lambda x: f'{x:.1f}'.replace('.', ',')),  # Formatação BR
            textposition='inside',
            width=0.7,
            marker=dict(color=mapeamento_cores[intervalo])
        ))

    # Agrupando as barras via layout, barmode = 'stack' (barra empilhada)
    fig_barras_empilhadas_2_mun.update_layout(
        barmode='stack',
        title=f'DISTRIBUIÇÃO POR PADRÃO DE DESEMPENHO - 2º ANO - {(municipio).upper()}',
        xaxis_title='Percentual',
        yaxis_title='Edição',
        showlegend=True,
        xaxis=dict(range=[0, 100],  showticklabels = False),
        height=675,
        bargap=0.1 # ajuste de espaçamento das barras 
        #margin=dict(l=300)  # Ajuste a margem esquerda conforme necessário
    )
    #fig_barras_empilhadas_2_ce.update_layout(width=1400)









## ------------------------ VISUALIZAÇÕES NO STREAMLIT ------------------------ ##

aba1, aba2, aba3, aba4 = st.tabs(['2º Ano do Ensino Fundamental', '5º Ano do Ensino Fundamental', '9º Ano do Ensino Fundamental', '3ª Série do Ensino Médio'])


# with aba1: # >>>>> 2º Ano do Ensino Fundamental
#     coluna1, coluna2 = st.columns(2)
#     with coluna1:
    
#         if componente != 'Matemática': # Condicional para exibir somente Língua Portuguesa
#             st.metric('População prevista', formata_numero(dados_mun_2_ano['Nº de Alunos Previstos'].sum()), help='População prevista somada de acordo coms os filtros selecionados')
#             st.metric('População avaliada', formata_numero(dados_mun_2_ano['Nº de Alunos Avaliados'].sum()), help='População avaliada somada de acordo coms os filtros selecionados')

#         if componente != 'Matemática':  # Exibir o gráfico de participação apenas se não for Matemática
#             st.plotly_chart(fig_participacao_edicao_2_mun, use_container_width=True) # GRAFICO LINHAS PARTICIPACAO LONGITUDINAL
        
#         else:
#             st.error(':no_entry_sign: Dados não encontrados. A série histórica do SPAECE não conta com Matemática no 2º Ano.')
            

with aba1: # >>>>> 2º Ano do Ensino Fundamental
    coluna1, coluna2 = st.columns(2)
    if dados_mun_2_ano['Proficiência Média'].empty:
            st.error(f'Dados não encontrados para o município de {municipio}. Verifique as opções nos filtros.', icon="🚨")
    else:
        with coluna1:
                st.metric('População prevista', formata_numero(dados_mun_2_ano['Nº de Alunos Previstos'].sum()), help='População prevista somada de acordo coms os filtros selecionados')
                st.metric('População avaliada', formata_numero(dados_mun_2_ano['Nº de Alunos Avaliados'].sum()), help='População avaliada somada de acordo coms os filtros selecionados')
                st.plotly_chart(fig_participacao_edicao_2_mun, use_container_width=True) # GRAFICO LINHAS PARTICIPACAO LONGITUDINAL

        with coluna2:
            if componente != 'Matemática':  # Condicional para exibir somente Língua Portuguesa
                num_alunos_previstos = dados_mun_2_ano['Nº de Alunos Previstos'].sum()
                num_alunos_avaliados = dados_mun_2_ano['Nº de Alunos Avaliados'].sum()
                if num_alunos_previstos > 0:
                    taxa_participacao_2_mun = (num_alunos_avaliados / num_alunos_previstos) * 100
                else:
                    taxa_participacao_2_mun = 0
                st.metric('Taxa de participação', f'{formata_taxa(taxa_participacao_2_mun)}%', help='Taxa de participação calculada de acordo com os filtros selecionados')
                st.metric('Proficiência Média', f'{formata_proficiencia(dados_mun_2_ano["Proficiência Média"].mean())}', help='Proficiência Média de acordo com os filtros selecionados')    
                st.plotly_chart(fig_proficiencia_edicao_2_mun, use_container_width=True) # GRAFICO LINHAS PROFICIENCIA LOGITUDINAL
        st.plotly_chart(fig_proficiencia_edicao_2_mun_bar, use_container_width=True) # GRAFICO BARRAS PADRAO DE DESEMPENHO
        st.plotly_chart(fig_barras_empilhadas_2_mun, use_container_width=True) # GRAFICO BARRAS EMPILHADAS DISTRIBUICAO DOS PADROES DE DESEMPENHO




    ## ------------------------ VISUALIZAÇÃO DA TABELA ------------------------ ##


    
    # Adicionando a tabela para visualização e download
    

    # Acionando os filtros (inside the expander)
        

    # Inserindo um texto sobre as colunas e linhas exibidas
    st.dataframe(dados_mun_2_ano, hide_index = True)
    st.markdown(f'A tabela possui :blue[{dados_mun_2_ano.shape[0]}] linhas e :blue[{dados_mun_2_ano.shape[1]}] colunas.')

    ## ------------------------ DOWNLOAD DAS TABELAS ------------------------ ##


    


with aba2: # >>>>> 5º Ano do Ensino Fundamental
    
    ## ------------------------ VISUALIZAÇÃO DA TABELA ------------------------ ##

    

    # Acionando os filtros (inside the expander)
        

    # Inserindo um texto sobre as colunas e linhas exibidas
    st.dataframe(dados_mun_5_ano, hide_index = True)
    st.markdown(f'A tabela possui :blue[{dados_mun_5_ano.shape[0]}] linhas e :blue[{dados_mun_5_ano.shape[1]}] colunas.')

    
    ## ------------------------ DOWNLOAD DAS TABELAS ------------------------ ##
    
    
with aba3: # >>>>> 9º Ano do Ensino Fundamental
    
            
    ## ------------------------ VISUALIZAÇÃO DA TABELA ------------------------ ##


    # Adicionando a tabela para visualização e download

    
    # Acionando os filtros (inside the expander)


    # Inserindo um texto sobre as colunas e linhas exibidas
    st.dataframe(dados_mun_9_ano, hide_index = True)
    st.markdown(f'A tabela possui :blue[{dados_mun_9_ano.shape[0]}] linhas e :blue[{dados_mun_9_ano.shape[1]}] colunas.')


    ## ------------------------ DOWNLOAD DAS TABELAS ------------------------ ##
    



with aba4: # >>>>> 3ª Série do Ensino Médio

    
    ## ------------------------ VISUALIZAÇÃO DA TABELA ------------------------ ##

    

    # Adicionando a tabela para visualização e download
        

    # Acionando os filtros (inside the expander)
            

    # Inserindo um texto sobre as colunas e linhas exibidas
    st.dataframe(dados_mun_3_ano, hide_index = True)
    st.markdown(f'A tabela possui :blue[{dados_mun_3_ano.shape[0]}] linhas e :blue[{dados_mun_3_ano.shape[1]}] colunas.')

    ## ------------------------ DOWNLOAD DAS TABELAS ------------------------ ##
    


## ------------------------ CRÉDITOS ------------------------ ##

st.markdown('*Os dados desta plataforma são fornecidos pelo Centro de Políticas Públicas e Avaliação da Educação da Universidade Federal de Juiz de Fora (CAEd/UFJF).*')
st.markdown("""
    **Desenvolvido por José Alves Ferreira Neto**  
    - LinkedIn: [José Alves Ferreira Neto](https://www.linkedin.com/in/jos%C3%A9-alves-ferreira-neto-1bbbb8192/)  
    - E-mail: jose.alvesfn@gmail.com
""")



