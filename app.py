import streamlit as st
from st_on_hover_tabs import on_hover_tabs
import folium
from streamlit_folium import folium_static, st_folium
from streamlit_js_eval import streamlit_js_eval
from streamlit_javascript import st_javascript
import geocoder
from pyproj import Transformer
import pandas as pd
import requests
import re
from datetime import datetime
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import random
import string
import pandas as pd

st.set_page_config(page_icon=":world_map:", page_title="Mapeamento de Áreas", layout="wide")
st.markdown('<style>' + open('./css/styles.css').read() + '</style>', unsafe_allow_html=True)

def reverse_geocode_with_retry(latitude, longitude): 
    retries=3
    delay=1
    geolocator = Nominatim(user_agent="my_unique_geopy_app", timeout=10)
    for i in range(retries):
        try:
            location = geolocator.reverse((latitude, longitude))
            return location
        except GeocoderTimedOut:
            time.sleep(delay)
    return None

def gera_protocolo():
    today = datetime.now()
    year_last_two = today.strftime('%y')
    month = today.strftime('%m')
    day = today.strftime('%d')    
    
    date_code = f"{year_last_two}{month}{day}"
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
    result = date_code + random_chars
    return result

def get_screen_dimensions():
    width = streamlit_js_eval(js_expressions="window.innerWidth", key="get_width")
    height = 700
    return [width, height]

def converte_coord_unica(dms_str):
    if re.match(r"(\d+)°(\d+)'(\d+\.\d+|\d+)\"([NSEW])", dms_str):
        pattern = re.compile(r"(\d+)°(\d+)'(\d+\.\d+|\d+)\"([NSEW])")
        match = pattern.match(dms_str)
        graus, minutos, segundos, direcao = match.groups()
        decimal = float(graus) + float(minutos) / 60 + float(segundos) / 3600
        if direcao in ['S', 'W']:
            decimal = -decimal
    elif re.match(r"(\d+):(\d+):(\d+\.\d+|\d+)", dms_str):
        pattern = re.compile(r"(\d+):(\d+):(\d+\.\d+|\d+)")
        match = pattern.match(dms_str)
        graus, minutos, segundos = match.groups()
        decimal = float(graus) + float(minutos) / 60 + float(segundos) / 3600
    else:
        raise ValueError("Formato DMS inválido")
    return decimal

def trata_coordenada(lat_str, lon_str):
    lat_decimal = converte_coord_unica(lat_str)
    lon_decimal = converte_coord_unica(lon_str)
    return lat_decimal, lon_decimal

def verifica_conexao_internet():
    url = "http://www.google.com"
    timeout = 5
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

def retorna_localizacao(localizacao):
    if localizacao.ok:
        latitude = localizacao.latlng[0]
        longitude = localizacao.latlng[1]
        return latitude, longitude, "Válido"
    else:
        return 0, 0, "Inválido"

def transforma_coornenadas_UTM(lat, long):
    transformer = Transformer.from_crs("epsg:4326", "epsg:31983")
    utm_x, utm_y = transformer.transform(lat, long)
    return utm_x, utm_y

def carregar_lista_txt(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as file:
        conteudo = file.read()
    return conteudo.splitlines()

def calcular_idade(data_nascimento):
    data_atual = datetime.now().date()
    # Calcular a diferença de anos
    anos = data_atual.year - data_nascimento.year
    
    # Ajustar a idade se ainda não tiver feito aniversário no ano atual
    if (data_atual.month, data_atual.day) < (data_nascimento.month, data_nascimento.day):
        anos -= 1
    
    return anos

def formulario_acoes(probabilidade):
    if probabilidade == 'Ocorrida':
        #Ações a serem tomadas
        st.markdown("###### Ações Imediatas")
        # Ações de Prevenção Tomadas
        st.subheader('Ações de Prevenção Tomadas')
        monitoramento_area = st.checkbox('Monitoramento da área')
        obras_contencao = st.checkbox('Obras de contenção e drenagem')
        evacuacao_preventiva = st.checkbox('Evacuação preventiva')
        comunicacao_populacao = st.checkbox('Comunicação com a população')
        outras_prevencao = st.text_input('Outras Ações de Prevenção:', '')

        # Ações Durante o Evento
        st.markdown("###### Ações Durante o Evento")
        evacuacao_afetadas = st.checkbox('Evacuação das áreas afetadas')
        montagem_abrigos = st.checkbox('Montagem de abrigos temporários')
        isolamento_area = st.checkbox('Isolamento da área afetada')
        resgate_vitimas = st.checkbox('Resgate de vítimas')
        distribuicao_kits = st.checkbox('Distribuição de kits de emergência')
        comunicacao_durante = st.checkbox('Comunicação com a população')
        outras_durante = st.text_input('Outras Ações Durante o Evento:', '')

        st.markdown("###### Ações Pós-Evento")
        # Medidas de Recuperação
        st.subheader('Medidas de Recuperação')
        reparos_infraestrutura = st.checkbox('Reparos de infraestrutura')
        atendimento_medico = st.checkbox('Atendimento médico e psicológico')
        distribuicao_suprimentos = st.checkbox('Distribuição de suprimentos')
        monitoramento_continuo = st.checkbox('Monitoramento contínuo')
        outras_recuperacao = st.text_input('Outras Medidas de Recuperação:', '')

    else:
        st.markdown("###### Ações de Prevenção Tomadas")
        monitoramento_area = st.checkbox('Monitoramento da área')
        obras_contencao = st.checkbox('Obras de contenção e drenagem')
        evacuacao_preventiva = st.checkbox('Evacuação preventiva')
        comunicacao_populacao = st.checkbox('Comunicação com a população')
        outras_prevencao = st.text_input('Outras Ações de Prevenção:', '')

    st.markdown("###### Comentários Adicionais")
    comentarios = st.text_area('Comentários Adicionais:')

    # Botão para Submeter
    if st.button('Submeter'):
        st.write('Formulário submetido com sucesso!')
        # Aqui você pode adicionar código para salvar os dados, enviar um e-mail, etc.


################################################ QUESTIONARIOS ###################################################################
def deslizamento_de_terra():
    st.markdown("###### Avaliação de Risco de Deslizamento de Terra")
    
    historico = st.radio("Histórico de Deslizamentos na Área:", ("Sim", "Não"))
    declividade = st.selectbox("Declividade do Terreno:", ["Baixa (0-10%)", "Moderada (10-30%)", "Alta (30-50%)", "Muito Alta (>50%)"])
    tipo_solo = st.selectbox("Tipo de Solo:", ["Argiloso", "Arenoso", "Rochoso", "Outros"])
    vegetacao = st.selectbox("Presença de Vegetação:", ["Abundante", "Moderada", "Escassa"])
    interferencia = st.multiselect("Interferência Antrópica:", ["Construção de estradas", "Desmatamento", "Outros"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def inundacao():
    st.markdown("###### Avaliação de Risco de Inundação")
    
    historico = st.radio("Histórico de Inundações na Área:", ("Sim", "Não"))
    proximidade = st.selectbox("Proximidade de Corpos Hídricos:", ["Próximo a rios", "Próximo a lagos", "Próximo a represas"])
    terreno = st.selectbox("Características do Terreno:", ["Plano", "Levemente inclinado", "Inclinado"])
    drenagem = st.selectbox("Sistema de Drenagem:", ["Adequado", "Inadequado", "Ausente"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def enchentes():
    st.markdown("###### Avaliação de Risco de Enchentes")
    
    historico = st.radio("Histórico de Enchentes na Área:", ("Sim", "Não"))
    proximidade = st.selectbox("Proximidade de Corpos Hídricos:", ["Próximo a rios", "Próximo a lagos", "Próximo a represas"])
    terreno = st.selectbox("Características do Terreno:", ["Plano", "Levemente inclinado", "Inclinado"])
    drenagem = st.selectbox("Sistema de Drenagem:", ["Adequado", "Inadequado", "Ausente"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def erosao():
    st.markdown("###### Avaliação de Risco de Erosão")
    
    historico = st.radio("Histórico de Erosão na Área:", ("Sim", "Não"))
    tipo_erosao = st.selectbox("Tipo de Erosão:", ["Laminar", "Sulcos", "Ravinas", "Voçorocas"])
    uso_solo = st.selectbox("Uso do Solo:", ["Agricultura", "Pecuária", "Urbano", "Outros"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def desabamento_e_colapso():
    st.markdown("###### Avaliação de Risco de Desabamento e Colapso de Estruturas")
    
    historico = st.radio("Histórico de Desabamentos na Área:", ("Sim", "Não"))
    estado = st.selectbox("Estado de Conservação das Estruturas:", ["Bom", "Regular", "Ruim"])
    material = st.selectbox("Material das Estruturas:", ["Concreto", "Madeira", "Alvenaria", "Outros"])
    interferencias = st.multiselect("Interferências Antrópicas Recentes:", ["Reformas", "Construções próximas", "Outros"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def trincas_e_rachaduras():
    st.markdown("###### Avaliação de Risco de Trincas e Rachaduras")
    
    historico = st.radio("Histórico de Trincas e Rachaduras na Área:", ("Sim", "Não"))
    tipo = st.selectbox("Tipo de Trincas e Rachaduras:", ["Superficiais", "Profundas", "Estruturais"])
    estado = st.selectbox("Estado de Conservação das Estruturas:", ["Bom", "Regular", "Ruim"])
    interferencias = st.multiselect("Interferências Antrópicas Recentes:", ["Reformas", "Construções próximas", "Outros"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def afundamento_do_solo():
    st.markdown("###### Avaliação de Risco de Afundamento do Solo")
    
    historico = st.radio("Histórico de Afundamentos na Área:", ("Sim", "Não"))
    tipo_solo = st.selectbox("Tipo de Solo:", ["Argiloso", "Arenoso", "Rochoso", "Outros"])
    cavidades = st.radio("Presença de Cavidades Subterrâneas:", ("Sim", "Não"))
    interferencias = st.multiselect("Interferências Antrópicas Recentes:", ["Extração mineral", "Perfuração de poços", "Outros"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def queda_de_arvore():
    st.markdown("###### Avaliação de Risco de Queda de Árvore")
    
    historico = st.radio("Histórico de Quedas de Árvores na Área:", ("Sim", "Não"))
    especie = st.selectbox("Espécie das Árvores:", ["Nativas", "Exóticas", "Frutíferas", "Outros"])
    estado = st.selectbox("Estado de Conservação das Árvores:", ["Bom", "Regular", "Ruim"])
    doencas = st.radio("Presença de Doenças ou Pragas:", ("Sim", "Não"))
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def incendios():
    st.markdown("###### Avaliação de Risco de Incêndios")
    
    historico = st.radio("Histórico de Incêndios na Área:", ("Sim", "Não"))
    fonte_ignicao = st.selectbox("Fonte Potencial de Ignição:", ["Elétrica", "Fogos de artifício", "Queimadas", "Outros"])
    inflamaveis = st.radio("Presença de Materiais Inflamáveis:", ("Sim", "Não"))
    sistema_prevencao = st.selectbox("Sistema de Prevenção e Combate a Incêndios:", ["Adequado", "Inadequado", "Ausente"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def contaminacao_ambiental():
    st.markdown("###### Avaliação de Risco de Contaminação Ambiental")
    
    historico = st.radio("Histórico de Contaminação na Área:", ("Sim", "Não"))
    fonte_contaminacao = st.selectbox("Fonte Potencial de Contaminação:", ["Industrial", "Doméstica", "Agrícola", "Outros"])
    tipo_contaminante = st.selectbox("Tipo de Contaminante:", ["Químico", "Biológico", "Radioativo", "Outros"])
    monitoramento = st.selectbox("Sistema de Monitoramento Ambiental:", ["Adequado", "Inadequado", "Ausente"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def tempestades_vendavais():
    st.markdown("###### Avaliação de Risco de Tempestades e Vendavais")
    
    historico = st.radio("Histórico de Tempestades e Vendavais na Área:", ("Sim", "Não"))
    intensidade = st.selectbox("Intensidade das Tempestades:", ["Leves", "Moderadas", "Fortes"])
    estruturas = st.radio("Presença de Estruturas Vulneráveis:", ("Sim", "Não"))
    alerta_prevencao = st.selectbox("Sistema de Alerta e Prevenção:", ["Adequado", "Inadequado", "Ausente"])
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

def geadas():
    st.markdown("###### Avaliação de Risco de Geadas")
    
    historico = st.radio("Histórico de Geadas na Área:", ("Sim", "Não"))
    frequencia = st.selectbox("Frequência de Ocorrência:", ["Rara", "Ocasional", "Frequente"])
    impacto = st.selectbox("Impacto em Culturas Agrícolas:", ["Leve", "Moderado", "Grave"])
    protecao = st.radio("Medidas de Proteção Existentes:", ("Sim", "Não"))
    
    st.text_area("Recomendações para Redução de Riscos:")
    
    st.radio("Avaliação Final do Risco:", ["Baixo", "Moderado", "Alto"])
    
    st.text_area("Observações Adicionais:")

########################################################## PDF ########################################################
def generate_html(form_data):
    html_content = f"""
    <html>
    <head>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .container {{
        width: 100%;
        margin: 0 auto;
    }}
    .header {{
        text-align: center;
        padding: 10px;
    }}
    .content {{
        padding: 10px;
    }}
    .titulo-dp{{
        padding-top: 0.15em;
        padding-bottom: 0.15em;
    }}
    .dados-pessoais{{
        margin: 1 auto;
        padding: 0.5em 0.5em;
        border: 1.25px solid #808080;
        border-radius: 0.5em;
    }}
    .col {{
        display: inline-block;
        vertical-align: top;
    }}
    .col-dp{{
        width: 20%;
    }}
    .col-1 {{
        width: 72.5%;
    }}
    .col-2 {{
        width: 27.5%;
    }}
    .col-3 {{
        width: 67.5%;
    }}
    .col-4 {{
        width: 27.5%;
    }}
    .col-5 {{
        width: 70%;
    }}
    .col-6 {{
        width: 30%;
    }}
    .col-7 {{
        width: 23%;
    }}
    .col-8 {{
        width: 23%;
    }}
    .col-9 {{
        width: 25%;
    }}
    .col-10 {{
        width: 8%;
    }}
    .col-11 {{
        width: 17%;
    }}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h1>Cadastro de Atendimento</h1>
        </div>
        <div class="header">
            <h2>Protocolo {form_data['protocolo']}</h2>
        </div>
        <div class="content">
            <div class="dados-pessoais">
                <h3 class="titulo-dp">Dados Pessoais</h3>
                <div class="col col-dp">
                    <h4>Solicitante</h4>
                    <p>{form_data['paciente']}</p>
                </div>
                <div class="col col-dp">
                    <h4>Nome Social</h4>
                    <p>{form_data['paciente']}</p>
                </div>
                <div class="col col-dp">
                    <h4>Data de Nascimento</h4>
                    <p>{form_data['paciente']}</p>
                </div>
                <div class="col col-dp">
                    <h4>Idade</h4>
                    <p>{form_data['paciente']} Anos</p>
                </div>
            </div>

            <div>
                <h2>Solicitante</h2>
                <p>{form_data['paciente']}</p>
            </div>
            <div class="col col-5">
                <h2>Apelido</h2>
                <p>{form_data['apelido']}</p>
            </div>
            <div class="col col-6">
                <h2>Data de Nascimento</h2>
                <p>{form_data['dt_nascimento']}</p>
            </div>
            <div class="col col-7">
                <h2>Idade</h2>
                <p>{form_data['idade']}</p>
            </div>
            <div class="col col-8">
                <h2>Sexo</h2>
                <p>{form_data['genero']}</p>
            </div>
            <div class="col col-9">
                <h2>Telefone</h2>
                <p>({form_data['ddd_telefone']}) {form_data['telefone']}</p>
            </div>
            <div class="col col-11">
                <h2>Email</h2>
                <p>{form_data['email']}</p>
            </div>
            <div>
                <h2>Área da Ocorrência</h2>
                <p>Latitude: {form_data['latend']}</p>
                <p>Longitude: {form_data['longend']}</p>
                <p>Endereço: {form_data['endereco']}</p>
                <p>Nº: {form_data['numero']}</p>
                <p>Bairro: {form_data['bairro']}</p>
                <p>Cidade: {form_data['cidade']}</p>
                <p>Estado: {form_data['estado']}</p>
                <p>CEP: {form_data['cep']}</p>
            </div>
            <div>
                <h2>Identificação da Ocorrência</h2>
                <p>{form_data['nome_area']}</p>
            </div>
            <div>
                <h2>Risco</h2>
                <p>{form_data['tipo_risco']}</p>
            </div>
            <div>
                <h2>Tipo de Área</h2>
                <p>{form_data['op_area']}</p>
            </div>
            <div>
                <h2>Tipo de Propriedade</h2>
                <p>{form_data['op_tpprop']}</p>
            </div>
            <div>
                <h2>Vegetação</h2>
                <p>{form_data['op_vegetacao']}</p>
            </div>
            <div>
                <h2>Probabilidade de Ocorrência</h2>
                <p>{form_data['op_probocorre']}</p>
            </div>
            <div>
                <h2>Danos</h2>
                <p>{', '.join(form_data['op_danos'])}</p>
            </div>
            <div>
                <h2>Descrição dos Danos</h2>
                <p>{form_data['descricao']}</p>
            </div>
            <div class="col col-2">
                <h2>Protocolo</h2>
                <p>{form_data['protocolo']}</p>
            </div>
            <div class="col col-3">
                <h2>Técnico Responsável</h2>
                <p>{form_data['tec_resp']}</p>
            </div>
            <div class="col col-4">
                <h2>Data do Registro</h2>
                <p>{form_data['data_registro']}</p>
            </div>
        </div>
    </div>
    </body>
    </html>
    """
    return html_content

def download_html(html_content):
    st.download_button(
        label="Baixar HTML",
        data=html_content,
        file_name="formulario.html",
        mime="text/html"
    )

###############################################################################################################################

######################################################## CARREGAMENTOS ########################################################

lista_generos = carregar_lista_txt("other/generos_simplificados.txt")
lista_riscos = carregar_lista_txt("other/riscos.txt")

#######################################################################################################################

with st.sidebar:
    tabs = on_hover_tabs(tabName=['Início', 'Explorando a Área', 'Cadastro de Áreas', 'Cadastro de Técnicos'],
                         iconName=['home', 'travel_explore', 'crisis_alert', 'person_add'],
                         styles={'navtab': {'background-color': '#111', 'color': '#EEE', 'font-size': '18px'},
                                 'icon': {'color': 'orange', 'font-size': '18px'},
                                 'navtab_hover': {'background-color': '#333', 'color': '#FFF'}})

if tabs == 'Início':
    st.title("Início")
elif tabs == 'Explorando a Área':
    st.title("Explorando a Área")
    initial_coordinates = [-19.500, -40.8575]
    mapa = folium.Map(location=initial_coordinates, zoom_start=8)
    dimensions = get_screen_dimensions()
    folium_static(mapa, width=dimensions[0], height=dimensions[1])
elif tabs == 'Cadastro de Áreas':
    st.title("Cadastro de Áreas de Risco")
    st.write("")

    colprot1, colprot2 = st.columns([0.725, 0.275]) 
    protocolo = colprot2.text_input("Protocolo", value=gera_protocolo(), disabled=True)
    st.write("")

    dados_tec = {'Técnico':['Fernando Guirra', 'Normando Messina'], 'Mátricula':['123465','654321']}
    df_tec = pd.DataFrame(dados_tec)
    col1, cole, col2 = st.columns([0.675, 0.05, 0.275])
    tec_resp = col1.selectbox("Técnico Responsável", options=df_tec['Técnico'].tolist())
    data_registro = col2.date_input(label="Data do Registro", value=datetime.now(), format="DD/MM/YYYY", disabled=True)
    st.write("")
    if verifica_conexao_internet():
        ponto_imagem = geocoder.ip('me')
        possui_solicitante = st.toggle("Área cadastrada por solicitante?", value=True)
        if possui_solicitante:
            with st.container(border=True):
                st.markdown("##### Dados Pessoais")
                st.write("")
                c11, c12 = st.columns([0.7, 0.3])
                paciente = c11.text_input("Solicitante")
                apelido = c12.text_input("Nome Social", help="Como gosta de ser chamado")
                c21, c21vazio, c22, c22vazio, c23, c23vazio, c24, c25 = st.columns([0.23, 0.02, 0.23, 0.02, 0.25, 0.02, 0.08, 0.17])
                dt_nascimento = c21.date_input("Data de Nascimento", format="DD/MM/YYYY")
                idade = c22.number_input("Idade", disabled=True, value=calcular_idade(dt_nascimento))
                genero = c23.selectbox("Sexo", options=lista_generos)
                ddd_telefone = c24.number_input("DDD", placeholder="DDD", value=None, step=1)
                telefone = c25.number_input("Nº Telefone", max_value=999999999, value=None, placeholder="99999-9999")
                st.text_input("E - mail", value=None, placeholder='usuario@email.com')
                st.write("")
        st.write("")

        with st.container(border=True):
            st.markdown("#### Área da Ocorrência")
            col1end, col2end = st.columns([0.6, 0.4])
            col11end, col12end = col1end.columns(2)
            latend, longend, status = retorna_localizacao(ponto_imagem)
            location = reverse_geocode_with_retry(latend, longend)
            if location:
                col11end.text_input("Latitude", value=str(latend), disabled=True)
                col12end.text_input("Longitude", value=longend, disabled=True)
                col11end.text_input("Endereço", value=location.raw['address']['road'], disabled=True)
                col12end.text_input("Nº", placeholder="Nº")
                col11end.text_input("Bairro", value=location.raw['address']['suburb'], disabled=True)
                #col12end.text_input("Cidade", value=location.raw['address']['city_district'], disabled=True)
                col11end.text_input("Estado", value= location.raw['address']['state'], disabled=True)
                col12end.text_input("CEP", value=location.raw['address']['postcode'], disabled=True)
                mpend = folium.Map(location=[latend, longend], zoom_start=15)
                folium.Marker([latend, longend], tooltip='Localização do Ponto').add_to(mpend)
                with col2end:
                    st_folium(mpend, height=280)
            else:
                st.write("Não foi possível obter a localização após múltiplas tentativas.")
                cep_manual = st.text_input("CEP")

        st.write("")

        with st.container(border=True):
            st.markdown("### Dados da Área")
            c11, c11e, c12 = st.columns([0.475, 0.05, 0.475])
            nome_area = c11.text_input("Identificação da Ocorrência", placeholder="Identificação")
            tipo_risco = c12.selectbox("Risco", options=lista_riscos, placeholder="Riscos", index=None)
            op_area = c11.selectbox("Tipo de Área", options=['Rural', 'Urbana'], index=None, placeholder="Tipo da Área")
            op_tpprop = c12.selectbox("Tipo de Propriedade", options=['Privada', 'Pública'], index=None, placeholder="Tipo da Propriedade")
            op_vegetacao = c11.selectbox("Vegetação", options=['Mata', 'Pastagem', 'Cultivo agrícola', 'Conservação', 'Sem vegetação'], index=None, placeholder="Tipo da Área", help="Por uso e cobertura do solo")
            op_probocorre = c12.selectbox("Probabilidade de Ocorrência", options=['Ocorrida', 'Alta', 'Média', 'Baixa'], index=None, placeholder="Probabilidade")
            foto_input = st.file_uploader("Carregar Imagem", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
            
            st.markdown("##### Formulário de Avaliação de Riscos")

            if tipo_risco == "Deslizamento de Terra":
                deslizamento_de_terra()
            elif tipo_risco == "Inundação":
                inundacao()
            elif tipo_risco == "Enchentes":
                enchentes()
            elif tipo_risco == "Erosão":
                erosao()
            elif tipo_risco == "Desabamento e Colapso de Estruturas":
                desabamento_e_colapso()
            elif tipo_risco == "Trincas e Rachaduras":
                trincas_e_rachaduras()
            elif tipo_risco == "Afundamento do Solo":
                afundamento_do_solo()
            elif tipo_risco == "Queda de Árvore":
                queda_de_arvore()
            elif tipo_risco == "Incêndios":
                incendios()
            elif tipo_risco == "Contaminação Ambiental":
                contaminacao_ambiental()
            elif tipo_risco == "Tempestades e Vendavais":
                tempestades_vendavais()
            elif tipo_risco == "Geadas":
                geadas()
            st.write("")
            op_danos = st.multiselect("Danos", options=['Impacto Humano', 'Impacto Material', 'Impacto Ambiental', 'Impacto Econômico'])
            descricao = st.text_area("Descrição dos Danos", placeholder="Descrição")
            st.write("")
            if op_probocorre:
                formulario_acoes(op_probocorre)
        st.markdown("")
        st.markdown(" ")

        utm_x, utm_y = transforma_coornenadas_UTM(latend, longend)

        df = pd.DataFrame({
            'Imagem': [foto_input.name if hasattr(foto_input, 'name') else "N/A"],
            'Latitude': [latend],
            'Longitude': [longend],
            'X UTM': [utm_x],
            'Y UTM': [utm_y],
            'Descrição': [descricao]
        })

        st.table(df)

        cbs, ceb, cbe = st.columns([0.485, 0.03, 0.485])

        bt_salva = cbs.button("Salvar", type='secondary', use_container_width=True, help="Salvar as informações mas inserir mais de uma imagem referente ao ponto cadastrado")
        bt_envia = cbe.button("Enviar Informações", type='primary', use_container_width=True, help="Avançar para salvar informações no banco de dados")

        if bt_envia:
            form_data = {
                'protocolo': 'PROTOCOLO12345',
                'tec_resp': 'Fernando Guirra',
                'data_registro': '01/01/2024',
                'paciente': 'Solicitante Exemplo',
                'apelido': 'Exemplo',
                'dt_nascimento': '01/01/1990',
                'idade': '34',
                'genero': 'Masculino',
                'ddd_telefone': '27',
                'telefone': '999999999',
                'email': 'exemplo@email.com',
                'latend': '-20.3155',
                'longend': '-40.3128',
                'endereco': 'Rua Exemplo',
                'numero': '123',
                'bairro': 'Centro',
                'cidade': 'Vitória',
                'estado': 'ES',
                'cep': '29000-000',
                'nome_area': 'Ocorrência Exemplo',
                'tipo_risco': 'Deslizamento de Terra',
                'op_area': 'Rural',
                'op_tpprop': 'Privada',
                'op_vegetacao': 'Mata',
                'op_probocorre': 'Alta',
                'op_danos': ['Impacto Humano', 'Impacto Material'],
                'descricao': 'Descrição dos danos exemplo.'
            }

            html_content = generate_html(form_data)
            download_html(html_content)

    else:
        st.write("Sem conexão com a internet")
elif tabs == 'Cadastro de Técnicos':
    st.title("Cadastro de Técnicos")
    dados_tec = {'Técnico':['Fernando Guirra', 'Normando Messina'], 'Mátricula':['123465','654321']}
    df_tec = pd.DataFrame(dados_tec)
    st.table(df_tec)
    st.write("")

    cad_novo_tec = st.button("Cadastrar Técnico")
    if cad_novo_tec:
        ct11, ct12 = st.columns([0.75, 0.25])
        nome_tec = ct11.text_input("Nome")
        sexo_tec = ct12.selectbox("Sexo", options=['Masculino', 'Feminino', 'Prefiro não informar'], index=None)
        ct21, ct22, ct23, ct24 =  st.columns(4)
        matricula_tec = ct21.text_input('Matrícula')
        cpf_tec = ct22.number_input('CPF', step=1, placeholder='00000000000', value=None)
        dt_nascimento_tec = ct23.date_input('Data de Nascimento', format="DD/MM/YYYY")
        idade_tec = ct24.number_input('Idade', value=calcular_idade(dt_nascimento_tec), disabled=True)
        ct31, ct32, ct33, ct34 = st.columns([0.4, 0.25, 0.15, 0.2])
        email_tec = ct31.text_input("Email", value=None, placeholder='usuario@email.com')
        func_tec = ct32.text_input("Função / Cargo", value=None, placeholder='Função')
        ddd_tec = ct33.number_input("DDD", value=None, min_value=0, max_value=99, step=1, placeholder="DDD")
        telefone_tec = ct34.number_input("Telefone", value=None, placeholder="000000000", max_value=999999999)
        st.write("")
        salva_dados_tec = st.button("Salvar", type='primary', use_container_width=True)