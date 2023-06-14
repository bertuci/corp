import streamlit as st
import os
import pandas as pd
import glob
import zipfile
import numpy as np
from prophet import Prophet
import plotly.express as px

def zipar_arquivos_por_extensao(extensao, nome_zip):
    arquivos = glob.glob(f'*.{extensao}')  # Localiza os arquivos com a extensão desejada

    with zipfile.ZipFile(nome_zip, 'w') as zipf:
        for arquivo in arquivos:
            zipf.write(arquivo)  # Adiciona cada arquivo ao arquivo zip

    print(f'Arquivos zipados com sucesso em {nome_zip}!')
    return True

def deletar_arquivos_por_extensao(extensao):
    arquivos = glob.glob(f'*.{extensao}')  # Localiza os arquivos com a extensão desejada

    for arquivo in arquivos:
        os.remove(arquivo)  # Deleta cada arquivo encontrado

    print(f'Arquivos com extensão .{extensao} foram deletados!')


def section1():
    # Conteúdo da seção 1
    #deletar_temp()
    file3 = st.file_uploader("Carregar arquivo Excel", type="xlsx") 
       

    if file3 is not None:
        type_file = st.selectbox("", ["AURORA", "CONCORRENCIA", "\t"])
        conteudo= file3.read()
        nome_arquivo = file3.name
        caminho_arquivo = os.path.join(os.getcwd(), nome_arquivo)
        with open(caminho_arquivo, "wb") as f:
            f.write(conteudo)
            f.close()

        # Ler o arquivo CSV usando o Pandas
        df = pd.read_excel(nome_arquivo, sheet_name=type_file)
        
        # Exibir o DataFrame
        st.subheader("Dados do arquivo Base")
        st.write(df)

        if st.button("Gerar"): 

            full_path = nome_arquivo    
            raw = pd.read_excel(full_path, sheet_name=type_file)
            deletar_arquivos_por_extensao('xlsx')
            lista_mercados = raw.MERCADO.unique().tolist()
            lista_categorias = raw.CATEGORIA.unique().tolist()

               
            for categoria in lista_categorias:
                target_categoria = raw.loc[raw['CATEGORIA'] == categoria]
                for mercado in lista_mercados:
                    target_mercados = target_categoria.loc[target_categoria['MERCADO'] == mercado]
                    name_file = 'dados_'+categoria+'_'+mercado+'_'+type_file.lower()+'.csv'
                    name_file = name_file.replace(" ", "_")
                    target_mercados.to_csv(name_file, sep=',', index=None, header=True)              
            zipar_arquivos_por_extensao('csv', 'dados'+type_file+'.zip')
            deletar_arquivos_por_extensao('csv')
            st.success("Dados Fontes processados com sucesso!")
   
        substring2 = ".zip"
        directory  = os.getcwd()
        
        if st.button("Baixar Arquivo"):
            for file_name in os.listdir(directory):
                if substring2 in file_name:
                    file_path = os.path.join(directory, file_name)
                    if not os.path.isfile(file_path):
                        st.error("O arquivo não existe!")
                    else:
                        with open(file_path, "rb") as file:
                            file_data = file.read()
                        st.download_button(
                            label="Clique aqui para baixar o arquivo",
                            data=file.
