import streamlit as st
import os
import pandas as pd
import glob
import zipfile
import numpy as np
from prophet import Prophet
import plotly.graph_objects as go
import plotly.io as pio

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
    file1 = st.file_uploader("Carregar arquivo Excel", type="xlsx") 
       

    if file1 is not None:
        type_file = st.selectbox("", ["AURORA", "CONCORRENCIA", "\t"])
        conteudo= file1.read()
        nome_arquivo = file1.name
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
                    target_mercados.to_csv(name_file, sep=',', index=None, header = True)              
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
                                    data=file_data,
                                    file_name=file_name,
                                )
                                deletar_arquivos_por_extensao('zip')
                               
    else:
        deletar_arquivos_por_extensao('xlsx')

def section2():
    # Conteúdo da seção 2
   
    # Carregar o arquivo CSV*
    
    file2 = st.file_uploader("Carregar arquivo CSV", type="csv")
    separator2 = st.selectbox("Selecione o separador", [",", ";", "\t"])
   

    if file2 is not None:

        conteudo= file2.read()
        nome_arquivo = file2.name
        caminho_arquivo = os.path.join(os.getcwd(), nome_arquivo)
        with open(caminho_arquivo, "wb") as f:
            f.write(conteudo)
            f.close()

        # Ler o arquivo CSV usando o Pandas
        df = pd.read_csv(nome_arquivo, sep=separator2)

        # Exibir o DataFrame
        st.subheader("Dados do arquivo CSV")
        st.write(df)

        if st.button("Executar Modelo"): 
            raw = df
            raw_aux = raw.copy()

            # Obs.: Como os dados estÃ£o em um perÃ­odo bimestral e o modelo Prophet espera o formato mensal, para o campo MES foi repetido o registro do respectivo bimestre, exemploo: Mes 1 e Mes 2 possuem os mesmo valores anteriormente representando pelo 1 bimestre

            raw.loc[raw['BIM'] == 1, 'MES'] = '1'
            raw.loc[raw['BIM'] == 2, 'MES'] = '3'
            raw.loc[raw['BIM'] == 3, 'MES'] = '5'
            raw.loc[raw['BIM'] == 4, 'MES'] = '7'
            raw.loc[raw['BIM'] == 5, 'MES'] = '9'
            raw.loc[raw['BIM'] == 6, 'MES'] = '11'

            raw_aux.loc[raw_aux['BIM'] == 1, 'MES'] = '2'
            raw_aux.loc[raw_aux['BIM'] == 2, 'MES'] = '4'
            raw_aux.loc[raw_aux['BIM'] == 3, 'MES'] = '6'
            raw_aux.loc[raw_aux['BIM'] == 4, 'MES'] = '8'
            raw_aux.loc[raw_aux['BIM'] == 5, 'MES'] = '10'
            raw_aux.loc[raw_aux['BIM'] == 6, 'MES'] = '12'

            series = pd.concat([raw, raw_aux])

            series['media_mensal_bim_vendas_volume'] = round(series['VENDAS VOLUME (in 000 KG)'].astype(float) / 2, 2)
            series['media_mensal_bim_vendas_valor'] = round(series['VENDAS VALOR (in 000)'].astype(float) / 2, 2)

            series['data_completa'] = series['ANO'].astype('str') + '-' + series['MES'].astype('str') + '-'+ '1'

            series['data_completa'] = pd.to_datetime( series['data_completa'] )


            # Aurora

            series_aurora = series.loc[series['MERCADO'] == 'aurora']
            series_aurora = series.replace(np.nan, 0)
            series_aurora = series_aurora.groupby( ['data_completa'] ).sum().reset_index()
            series_aurora = series_aurora.set_index('data_completa')
            dataset_aurora_valor = series_aurora[['media_mensal_bim_vendas_valor' ]]
            dataset_aurora_volume = series_aurora[['media_mensal_bim_vendas_volume' ]]
            dataset_aurora_valor = series_aurora.reset_index()
            dataset_aurora_volume = series_aurora.reset_index()

            # Target Valor
            dataset_aurora_valor = dataset_aurora_valor.rename(columns={'data_completa':'ds','media_mensal_bim_vendas_valor':'y'})

            m_aurora_valor = Prophet()
            m_aurora_valor.fit(dataset_aurora_valor)  # df is a pandas.DataFrame with 'y' and 'ds' columns
            future_aurora_valor = m_aurora_valor.make_future_dataframe(periods=365)
            m_aurora_valor.predict(future_aurora_valor)

            df_export_valor =  m_aurora_valor.predict(future_aurora_valor)
            df_export_valor = df_export_valor[['ds', 'yhat_lower','yhat_upper', 'yhat']]
            df_export_valor.to_csv('predict_valor_'+ nome_arquivo, sep=',', index=None, header=True)

            # Target Volume
            dataset_aurora_volume = dataset_aurora_volume.rename(columns={'data_completa':'ds','media_mensal_bim_vendas_volume':'y'})


            m_aurora_volume = Prophet()
            m_aurora_volume.fit(dataset_aurora_volume)  # df is a pandas.DataFrame with 'y' and 'ds' columns
            future_aurora_volume = m_aurora_volume.make_future_dataframe(periods=365)
            m_aurora_volume.predict(future_aurora_volume)


            df_export_volume =  m_aurora_volume.predict(future_aurora_volume)
            df_export_volume = df_export_volume[['ds', 'yhat_lower','yhat_upper', 'yhat']]
            df_export_volume.to_csv('predict_volume_'+ nome_arquivo, sep=',', index=None, header=True)

            st.success("Modelo treinado com sucesso!")
            
        zipar_arquivos_por_extensao('csv', 'fonte_e_predicts.zip')
        
        substring2 = "predict"
        directory  = os.getcwd()
    
       
        if st.button("Baixar Arquivo"):
                    deletar_arquivos_por_extensao('csv')
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
                                    data=file_data,
                                    file_name=file_name,
                                )
                                deletar_arquivos_por_extensao('zip')   
                                                      
                               
                                

def section3():

    # Conteúdo da seção 3
    
    #st.title("Gráfico de Linhas")

    # Carregar o arquivo CSV
    st.subheader("Carregar arquivos: Principal e Comparado (Opcional)")
    file3_1 = st.file_uploader("Carregar arquivo CSV principal", type="csv", key="file1")    
    separator3_1 = st.selectbox("Selecione o separador", [",", ";", "\t"], key="separator1")
    st.write("\n")
    file3_2 = st.file_uploader("Carregar arquivo CSV a ser comparado (opcional)", type="csv" , key="file2")
    separator3_2 = st.selectbox("Selecione o separador", [",", ";", "\t"], key="separator2")



    if file3_1 is not None:

        conteudo3_1= file3_1.read()
        nome_arquivo3_1 = file3_1.name
        caminho_arquivo3_1 = os.path.join(os.getcwd(), nome_arquivo3_1)

        with open(caminho_arquivo3_1, "wb") as f:
            f.write(conteudo3_1)
        # Ler o arquivo CSV usando o Pandas
        df3_1 = pd.read_csv(nome_arquivo3_1, sep=separator3_1)

        # Exibir o DataFrame
        st.subheader("Dados do arquivo CSV principal")
        st.write(df3_1)


        if file3_2 is not None:
            conteudo3_2= file3_2.read()
            nome_arquivo3_2 = file3_2.name
            caminho_arquivo3_2 = os.path.join(os.getcwd(), nome_arquivo3_2)

            with open(caminho_arquivo3_2, "wb") as f:
                f.write(conteudo3_2)
            # Ler o arquivo CSV usando o Pandas
            df3_2 = pd.read_csv(nome_arquivo3_2, sep=separator3_2)

            # Exibir o DataFrame
            st.subheader("Dados do arquivo CSV comparado")
            st.write(df3_2)

        # Gerar o gráfico de linhas
        
        x_column3_1 = st.selectbox("Selecione a coluna para o eixo X", df3_1.columns, key="df3_1_x")        
        days = st.text_input("Digite a quantidade de dias (útlimos) para o eixo X :", "30")        
        days = int(days)       
        y_column3_1 = st.selectbox("Selecione a coluna para o eixo Y principal", df3_1.columns, key="df3_1_y")   
        if file3_2 is not None: 
            y_column3_2 = st.selectbox("Selecione a coluna para o eixo Y comparado", df3_2.columns, key="df3_2_y")   

        st.subheader("Gráfico de Linhas")
     
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df3_1[x_column3_1].tail(days), y=df3_1[y_column3_1], mode='lines', name="Principal"))
        if file3_2 is not None:
            fig.add_trace(go.Scatter(x=df3_1[x_column3_1].tail(days), y=df3_2[y_column3_2], mode='lines', name="Comparado"))
            

        fig.update_layout(title="Evolução dos valores no tempo",
               
                xaxis_title=x_column3_1,
                yaxis_title=y_column3_1,
                width=800, height=400)       

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)



        





        deletar_arquivos_por_extensao('csv')

# Configurando as abas
tabs = {
    "Carregar e Separar": section1,
    "Carregar e Treinar": section2,
    "Carregar e Exibir": section3,

}

if __name__ == '__main__':

    # Título do aplicativo
    st.title("Aurora Predictions")

    # Criação das abas
    current_tab = st.sidebar.radio("Seções", list(tabs.keys()))

    # Executa a função correspondente à aba selecionada
    tabs[current_tab]()





        
