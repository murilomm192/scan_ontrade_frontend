import base64
import datetime
from dataclasses import asdict, dataclass
from typing import Optional
import pandas as pd
import streamlit as st

from database import open_database

USER = st.secrets['USER']
PASSWORD = st.secrets['PASSWORD']

if 'erro' not in st.session_state:
    st.session_state['erro'] = False

@dataclass
class Report():
    operação: str
    pdv: int
    mes_relatorio: datetime.datetime
    nome_crm: str
    relatorio_format: str
    relatorio: bytes
    fachada: Optional[bytes] = None
    cardapio: Optional[bytes] = None
    data_coleta: datetime.datetime = datetime.datetime.today()
    status: str = 'novo'

st.set_page_config(
    page_title="Ontrade", page_icon="🍺", layout='wide', initial_sidebar_state='collapsed'
)

reduce_header_height_style = """
    <style>
        div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: black;'>Raio X do Ontrade\n</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: black;'>Coleta de Informações\n</h1>", unsafe_allow_html=True)

bases = open_database(USER, PASSWORD)

operações = pd.read_csv('op.csv', delimiter=';', encoding='latin-1')

@st.cache_data
def make_dropdown_options(df):
    return {com: list(operações[operações['comercial'] == com]['operacao'].unique()) for com in list(operações['comercial'].unique())}


st.write('preencha as informações do PDV:')
st.selectbox('Comercial', list(operações['comercial'].unique()), key='comercial')
st.selectbox('Operação', list(make_dropdown_options(operações).get(st.session_state['comercial'])), key='operação')
st.number_input('Código PDV', 1, 99999, step=1, format='%d', key='pdv')
st.date_input('Mês do relatório', datetime.datetime.today(), key='data_relatorio')
st.text_input('Nome do Sistema de Vendas do PDV', '', key='nome_sistema')
st.file_uploader('Importar o Arquivo:', type=['pdf','csv','xlsx'], help='Tamanho máximo dos aqruivos: 16Mb', key='relatorio')
st.checkbox('Tem Cardápio?', key='tem_cardapio')
if st.session_state['tem_cardapio']:
    st.camera_input('Salve a foto do cardápio, se houver.', key='cardapio')
else:
    st.session_state['cardapio'] = None
st.checkbox('Tem Fachada?', key='tem_fachada')
if st.session_state['tem_fachada']:
    st.camera_input('Salve a foto da fachada, se possível.', key='fachada')
else:
    st.session_state['fachada'] = None
    
def save_report():
    session = st.session_state
    try:
        relatorio = Report(
            session['operação'],
            session['pdv'],
            datetime.datetime.combine(session['data_relatorio'], datetime.datetime.min.time()),
            session['nome_sistema'].lower().strip(),
            session['relatorio'].name.split('.')[1],
            base64.b64encode(session['relatorio'].getvalue()),
            base64.b64encode(session['fachada'].getvalue()) if session['fachada'] else None,
            base64.b64encode(session['cardapio'].getvalue()) if session['cardapio'] else None,
        )
        bases.insert_one(asdict(relatorio))
        st.session_state['erro'] = False
    except AttributeError:
        st.session_state['erro'] = True
    
button = st.button('Salvar', on_click=save_report, key='save')

if st.session_state['save']:
    if st.session_state['erro']:
        st.error('Não é possível salvar sem o relatório!')
    else:
        st.success('Relatório Salvo! recarregue a página se quiser salvar outro relatório.')


