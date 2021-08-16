import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import os
import utils


main = utils.get_data()

st.title("Medical Resarch Network")
st.sidebar.header("Parámetros para visualizar")
st.sidebar.subheader("Parámetros generales")

first_year, last_year = int(main.year.min()), int(main.year.max())

with st.form(key = 'Form'):
    with st.sidebar:
        year_range = st.sidebar.slider(
            'Años a mostrar',
            first_year, last_year, (last_year-1, last_year))

        enfermedades = list(set(main['Grupo de Enfermedad']))
        grupos = st.sidebar.multiselect(
            'Grupo de enfermedad',
        enfermedades,
        enfermedades[:2]
        )

        paises = set(main.Pais)
        paises = st.sidebar.multiselect(
            'Países',
            paises,
            paises
        )

        submitted = st.form_submit_button(label = 'Submit')

if submitted:
    file_name = 'nx.html'
    utils.build_graph(file_name, main, year_range, grupos, paises)
    HtmlFile = open(file_name, 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 600, width=700)