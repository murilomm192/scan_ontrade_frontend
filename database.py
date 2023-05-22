import base64

import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def convert_to_binary(caminho):
    with open(caminho, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
        return encoded_string
    
def decode_from_b64(base64_string, file_name):
    with open(file_name, 'wb') as f:
        f.write(base64.b64decode(base64_string))

USER = st.secrets['USER']
PASSWORD = st.secrets['PASSWORD']

@st.cache_resource
def open_database(usuario, senha):
    con_string = f'mongodb+srv://{usuario}:{senha}@ontrade.q28jzum.mongodb.net'
    client = MongoClient(con_string, server_api=ServerApi('1'))
    db = client.scan
    bases = db.bases
    return bases

if __name__ == '__main__':
    bases = open_database(USER, PASSWORD)
    filter = bases.find({'relatorio_format':'xlsx'})
    
    for x in filter:
        try:
            decode_from_b64(x.get('relatorio'), f"{x.get('operação')}_{x.get('nome_crm')}.{x.get('relatorio_format')}")
        except:
            pass
    

