import networkx as nx
from networkx.algorithms import bipartite
from pyvis.network import Network
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

@st.cache
def get_data():
    #author = pd.read_csv('../dummy_data/tabla_1.csv')
    #illness = pd.read_csv('../dummy_data/tabla_2.csv')
    #links = pd.read_csv('../dummy_data/tabla_3.csv')
    author = pd.read_csv('../../data-collection/autores.csv')
    illness = pd.read_csv('../../data-collection/enfermedades.csv')
    links = pd.read_csv('../../data-collection/investigaciones.csv')
    
    main = links.merge(illness, on='Enfermedad').merge(author, on='Institucion')
    #main.drop(['id_x','id_y'], axis=1, inplace=True)

    return author, illness, links, main

def build_graph(file_name, main, year_range, grupos, paises, author, giant, reduce, barnes):
    main = main[
        (main.Year.between(year_range[0], year_range[1])) &
        (main['Grupo'].isin(grupos)) &
        (main.Pais.isin(paises))
        ].reset_index(drop=True)
    
    g = nx.Graph()

    afiliaciones_paises = dict(zip(main.Institucion, main.Pais))
    for affiliation in set(main.Institucion):
        g.add_node(affiliation, bipartite=0, color='#162347', title=afiliaciones_paises[affiliation])
    enfermedades = dict(zip(main.Enfermedad, main['Grupo']))
    for enfermedad in enfermedades:
        g.add_node(enfermedad, bipartite=1, group=enfermedades[enfermedad], title=enfermedades[enfermedad])

    for idx, row in main.iterrows():
        g.add_edge(row.Enfermedad, row.Institucion, year=row.Year)

    if giant:
        Giant = max(nx.connected_components(g), key=len)
        g = g.subgraph(Giant)
    
    grado = g.degree()
    grado = pd.DataFrame(grado, columns=['Nodo','Grado'])
    grado.loc[grado.Nodo.isin(set(author.Institucion)), 'Tipo'] = 'Institucion'
    grado.loc[pd.isna(grado.Tipo), 'Tipo'] = 'Enfermedad'
    num_nodos = grado.groupby('Tipo')['Nodo'].count()
    num_ejes = grado.groupby('Tipo')['Grado'].sum()[0]

    g_plot = g
    if reduce:
        k = int(0.1 * g.number_of_nodes())
        sampled_nodes = np.random.choice(g.nodes, k)
        g_plot = g.subgraph(sampled_nodes)

    nt = Network('600px', '100%', notebook=True, bgcolor="#777271", font_color='#ffffff')
    nt.from_nx(g_plot)
    
    if barnes:
        nt.barnes_hut()
    nt.show(file_name)

    HtmlFile = open(file_name, 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 600, width=700)

    if giant:
        radio = nx.radius(g)
        diametro = nx.diameter(g)

        st.subheader('Medidas de la componente gigante:')
        st.write('Radio:', radio)
        st.write('Diámetro:', diametro)

    
    top_enfermedades = grado[grado.Tipo == 'Enfermedad'].sort_values('Grado', ascending=False).head(3).reset_index(drop=True)
    top_instituciones = grado[grado.Tipo == 'Institucion'].sort_values('Grado', ascending=False).head(3).reset_index(drop=True)

    st.subheader('Tópicos más investigados:')
    st.dataframe(top_enfermedades[['Nodo','Grado']].assign(hack='').set_index('hack'))
    st.subheader('Instituciones más activas:')
    st.dataframe(top_instituciones[['Nodo','Grado']].assign(hack='').set_index('hack'))

    st.write('Cantidad de Tópicos:', num_nodos['Enfermedad'])
    st.write('Cantidad de Instituciones:', num_nodos['Institucion'])
    st.write('Número de ejes:', num_ejes)

    betweenness = nx.betweenness_centrality(g)
    betweenness = pd.DataFrame(betweenness.items(), columns=['Nodo','Betweenness'])
    betweenness.sort_values('Betweenness', ascending=False)

    grado = grado.merge(betweenness, on='Nodo')

    top_enfermedades = grado[grado.Tipo == 'Enfermedad'].sort_values('Betweenness', ascending=False).head(1).reset_index(drop=True)
    top_instituciones = grado[grado.Tipo == 'Institucion'].sort_values('Betweenness', ascending=False).head(1).reset_index(drop=True)

    st.write('Tópico de mayor Betweenness:', top_enfermedades.Nodo.values[0])
    st.write('Institución de mayor Betweenness:', top_instituciones.Nodo.values[0])