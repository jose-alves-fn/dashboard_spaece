import pandas as pd                                 # Lib para manipução e tratamento de dados, tabelas e dataframes
import streamlit as st                              # Lib para construção de deashboards interativos
import requests                                     # Lib para requisições de APIs
import plotly.express as px                         # Lib de alto nivel para formatação rápida de gráficos
import plotly.graph_objects as go                   # Lib de baixo nível para alteração de plotagem do plotly
import locale                                       # Lib para setar o padrão de separação decimal BR
import time                                         # Módulo para pequenas manipulações de tempo interativo
import io                                           # Lib nativa para input / output binário
import xlsxwriter                                   # Lib para engine de arquivos excel



st.title('Em breve!')
# st.markdown('<span style="color: red; font-weight: bold">EM DESENVOLVIMENTO!</span>', unsafe_allow_html = True)


# Imagem de estamos trabalhando
image = 'trabalhando.png'
st.image(image, width = 200)

st.write('Gostou da imagem? Visite https://www.flaticon.com')
