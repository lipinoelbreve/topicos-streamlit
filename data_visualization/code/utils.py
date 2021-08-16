import networkx as nx
from networkx.algorithms import bipartite
from pyvis.network import Network
import pandas as pd
import streamlit as st

@st.cache
def get_data():
    author = pd.read_csv('../dummy_data/tabla_1.csv')
    illness = pd.read_csv('../dummy_data/tabla_2.csv')
    links = pd.read_csv('../dummy_data/tabla_3.csv')
    
    main = links.merge(illness, left_on='id_enfermedad', right_on='id').merge(author, left_on='id_autor', right_on='id')
    main.drop(['id_x','id_y'], axis=1, inplace=True)

    return main

def build_graph(file_name, main, year_range, grupos, paises):
    main = main[
        (main.year.between(year_range[0], year_range[1])) &
        (main['Grupo de Enfermedad'].isin(grupos)) &
        (main.Pais.isin(paises))
        ].reset_index(drop=True)
    
    g = nx.Graph()

    for affiliation in set(main.Afiliacion):
        g.add_node(affiliation, bipartite=0, color='#162347')
    enfermedades = dict(zip(main.Enfermedad, main['Grupo de Enfermedad']))
    for enfermedad in enfermedades:
        g.add_node(enfermedad, bipartite=1, group=enfermedades[enfermedad])

    for idx, row in main.iterrows():
        g.add_edge(row.Enfermedad, row.Afiliacion, year=row.year)

    nt = Network('600px', '100%', notebook=True)
    nt.from_nx(g)
    #nt.barnes_hut()
    nt.show(file_name)