import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import os
import utils


main = utils.get_data()

st.title("Medical Resarch Network 🦠 👨‍⚕️ 😷 💉")

st.markdown('Aplicación cuyo fin es mostrar las interacciones entre instituciones investigadoras y tópicos médicos estudiados por la comunidad científica, en el contexto de la materia Tópicos Avanzados hecha por los alumnos Nicolás Lupi, Victoria Matta y Ezequiel Raigorodsky. Los datos son sacados de [PubMed](https://pubmed.ncbi.nlm.nih.gov/), de donde se obtienen artículos que representan interacciones entre autores y tópicos.')
st.sidebar.header("Parámetros de la Red")
st.sidebar.subheader('')
first_year, last_year = int(main.year.min()), int(main.year.max())

with st.form(key = 'Form'):
    with st.sidebar:
        year_range = st.sidebar.slider(
            'Años a mostrar',
            first_year, last_year, (last_year-1, last_year))

        with st.expander('Elegir enfermedades'):
            enfermedades = ['Todos'] + list(set(main['grupo']))
            grupos = st.multiselect(
                'grupo',
            enfermedades,
            enfermedades[1:3]
            )

            if 'Todos' in grupos:
                grupos = enfermedades

        with st.expander('Elegir países'):
            paises = set(main.pais)
            paises_aux = []
            for pais in ['United Kingdom','United States','Argentina','China','India']:
                if pais in paises:
                    paises_aux.append(pais)
            
            if len(paises_aux) == 0:
                paises_aux = np.random.choice(list(paises))
            paises_seleccionados = st.multiselect(
                'Países',
                ['Todos'] + list(paises),
                paises_aux
            )

            if 'Todos' in paises_seleccionados:
                paises_seleccionados = paises


        giant = st.checkbox('Mostrar Componente Gigante')
        reduce = st.checkbox('Visualizar Red Reducida')
        barnes = st.checkbox('Barnes Hut (visualización rápida)')
        #btwns = st.checkbox('Calcular Betweenness (bajo su propio riesgo)')

        submitted = st.form_submit_button(label = 'Submit')

if submitted:
    file_name = 'nx.html'
    params_dict = utils.build_graph(main, year_range, grupos, paises_seleccionados, giant, reduce)
    
    utils.show_graph(file_name, barnes, **params_dict)