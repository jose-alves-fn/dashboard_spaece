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
                return f'{prefixo} {valor_str.replace(".00", "")} {unidade}'  # Remove o ".00" quando for um número inteiro
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

url_mun = 'https://raw.githubusercontent.com/jose-alves-fn/jose-alves-fn-tabelas_spaece_memoria_2008_2022/main/memoria_mun_todas_etapas.csv'
dados_mun = pd.read_csv(url_mun)

## Titulo do sidebar
st.sidebar.title('Filtros')

## Filtragem de redes
dados_mun['Rede'] = dados_mun['Rede'].str.capitalize()
redes = ['Estadual', 'Municipal']
rede = st.sidebar.selectbox('Rede', redes)

# ## Filtragem da etapa
# etapas = dados_ce['Etapa'].unique()
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

# Filtragem dos padroes de desempenho
todos_os_padroes = st.sidebar.checkbox('Todos os padrões de desempenho', value = True)
if todos_os_padroes:
    padroes = dados_mun['Indicação do Padrão de Desempenho'].unique()
else:
    padroes = st.sidebar.multiselect('Indicação do Padrão de Desempenho', dados_mun['Indicação do Padrão de Desempenho'].unique())

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
                          (dados_mun['Indicação do Padrão de Desempenho'].isin(padroes)) &
                          (dados_mun['Proficiência Média'].between(proficiencia[0], proficiencia[1]))
]











## ------------------------ VISUALIZAÇÕES NO STREAMLIT ------------------------ ##

aba1, aba2, aba3, aba4 = st.tabs(['2º Ano do Ensino Fundamental', '5º Ano do Ensino Fundamental', '9º Ano do Ensino Fundamental', '3ª Série do Ensino Médio'])

# with aba1: # >>>>> 2º Ano do Ensino Fundamental
    

    ## ------------------------ VISUALIZAÇÃO DA TABELA ------------------------ ##
    

    ## ------------------------ DOWNLOAD DAS TABELAS ------------------------ ##
    


# with aba2: # >>>>> 5º Ano do Ensino Fundamental
    
    ## ------------------------ VISUALIZAÇÃO DA TABELA ------------------------ ##
   

    # Adicionando a tabela para visualização e download
   
        # Acionando os filtros (inside the expander)
        

    # Inserindo um texto sobre as colunas e linhas exibidas
    
    ## ------------------------ DOWNLOAD DAS TABELAS ------------------------ ##
    
    
# with aba3: # >>>>> 9º Ano do Ensino Fundamental
    
            
    ## ------------------------ VISUALIZAÇÃO DA TABELA ------------------------ ##

  
    # Adicionando a tabela para visualização e download
    
    # Acionando os filtros (inside the expander)
   

    # Inserindo um texto sobre as colunas e linhas exibidas
    

    ## ------------------------ DOWNLOAD DAS TABELAS ------------------------ ##
    



# with aba4: # >>>>> 3ª Série do Ensino Médio
    

    ## ------------------------ VISUALIZAÇÃO DA TABELA ------------------------ ##
   
        # Adicionando a tabela para visualização e download
        

            # Acionando os filtros (inside the expander)
            

        # Inserindo um texto sobre as colunas e linhas exibidas
        

    ## ------------------------ DOWNLOAD DAS TABELAS ------------------------ ##
    


## ------------------------ CRÉDITOS ------------------------ ##

st.markdown('*Os dados desta plataforma são fornecidos pelo Centro de Políticas Públicas e Avaliação da Educação da Universidade Federal de Juiz de Fora (CAEd/UFJF).*')
st.markdown("""
    **Desenvolvido por José Alves Ferreira Neto**  
    - LinkedIn: [José Alves Ferreira Neto](https://www.linkedin.com/in/jos%C3%A9-alves-ferreira-neto-1bbbb8192/)  
    - E-mail: jose.alvesfn@gmail.com
""")







