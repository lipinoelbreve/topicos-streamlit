import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import os
import utils


author, illness, links, main = utils.get_data()

st.title("Medical Resarch Network")
st.sidebar.header("Parámetros para visualizar")
st.sidebar.subheader("Parámetros generales")

first_year, last_year = int(main.Year.min()), int(main.Year.max())

with st.form(key = 'Form'):
    with st.sidebar:
        year_range = st.sidebar.slider(
            'Años a mostrar',
            first_year, last_year, (last_year-1, last_year))

        with st.expander('Elegir enfermedades'):
            enfermedades = list(set(main['Grupo']))
            grupos = st.multiselect(
                'Grupo',
            enfermedades,
            enfermedades[:2]
            )

        with st.expander('Elegir países'):
            paises = set(main.Pais)
            paises = st.multiselect(
                'Países',
                paises,
                paises
            )

        giant = st.checkbox('Mostrar Componente Gigante')
        reduce = st.checkbox('Visualizar Grafo Reducido')
        barnes = st.checkbox('Barnes Hut')

        submitted = st.form_submit_button(label = 'Submit')

if submitted:
    file_name = 'nx.html'
    utils.build_graph(file_name, main, year_range, grupos, paises, author, giant, reduce, barnes)