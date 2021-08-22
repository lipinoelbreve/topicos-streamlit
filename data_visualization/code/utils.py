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
    
    return author, illness, links, main

@st.cache(allow_output_mutation=True)
def build_graph(main, year_range, grupos, paises, author, giant, reduce):
    np.random.seed(42)
    
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

    Giant = max(nx.connected_components(g), key=len)
    Giant = g.subgraph(Giant)
    g_plot = g
    
    if giant:
        g_plot = Giant

    grado = g.degree()
    grado = pd.DataFrame(grado, columns=['Nodo','Grado'])
    grado.loc[grado.Nodo.isin(set(author.Institucion)), 'Tipo'] = 'Institucion'
    grado.loc[pd.isna(grado.Tipo), 'Tipo'] = 'Enfermedad'
    num_nodos = grado.groupby('Tipo')['Nodo'].count()
    num_ejes = grado.groupby('Tipo')['Grado'].sum()[0]

    grado_gigante = Giant.degree()
    grado_gigante = pd.DataFrame(grado_gigante, columns=['Nodo','Grado'])
    grado_gigante.loc[grado_gigante.Nodo.isin(set(author.Institucion)), 'Tipo'] = 'Institucion'
    grado_gigante.loc[pd.isna(grado_gigante.Tipo), 'Tipo'] = 'Enfermedad'
    num_nodos_gigante = grado_gigante.groupby('Tipo')['Nodo'].count()
    num_ejes_gigante = grado_gigante.groupby('Tipo')['Grado'].sum()[0]

    if reduce:
        k = int(0.1 * g_plot.number_of_nodes())
        sampled_nodes = np.random.choice(g_plot.nodes, k)
        g_plot = g_plot.subgraph(sampled_nodes)

    radio = nx.radius(Giant)
    diametro = nx.diameter(Giant)

    top_enfermedades_grado = grado[grado.Tipo == 'Enfermedad'].sort_values('Grado', ascending=False).head(3).reset_index(drop=True)
    top_instituciones_grado = grado[grado.Tipo == 'Institucion'].sort_values('Grado', ascending=False).head(3).reset_index(drop=True)

    betweenness = nx.betweenness_centrality(Giant)
    betweenness = pd.DataFrame(betweenness.items(), columns=['Nodo','Betweenness'])
    betweenness.sort_values('Betweenness', ascending=False)

    grado_gigante = grado_gigante.merge(betweenness, on='Nodo')

    top_enfermedades_btwns = grado_gigante[grado_gigante.Tipo == 'Enfermedad'].sort_values('Betweenness', ascending=False).head(1).reset_index(drop=True)
    top_instituciones_btwns = grado_gigante[grado_gigante.Tipo == 'Institucion'].sort_values('Betweenness', ascending=False).head(1).reset_index(drop=True)

    pd.DataFrame()

    return {'g_plot': g_plot,
     'radio': radio,
     'diametro': diametro,
     'top_enfermedades_grado': top_enfermedades_grado,
     'top_instituciones_grado': top_instituciones_grado,
     'top_enfermedades_btwns': top_enfermedades_btwns,
     'top_instituciones_btwns': top_instituciones_btwns,
     'nodos_ejes': pd.DataFrame(
         {'Número de Tópicos':[num_nodos['Enfermedad'], num_nodos_gigante['Enfermedad']],
          'Número de Instituciones':[num_nodos['Institucion'], num_nodos_gigante['Institucion']],
          'Número de Ejes':[num_ejes, num_ejes_gigante]},
                  index=['Red Completa','Componente Gigante'])
    }
    
def show_graph(file_name, barnes, g_plot, radio, diametro, top_enfermedades_grado, top_instituciones_grado, top_enfermedades_btwns,
                top_instituciones_btwns, nodos_ejes):
    
    nt = Network('600px', '100%', notebook=True, bgcolor="#777271", font_color='#ffffff')
    nt.from_nx(g_plot)
    
    if barnes:
        nt.barnes_hut()
    nt.show(file_name)

    HtmlFile = open(file_name, 'r', encoding='utf-8')
    source_code = HtmlFile.read() 

    st.title('Visualización de la Red')
    components.html(source_code, height = 600, width=700)

    st.title('Métricas Principales')

    st.subheader('Medidas de la componente gigante:')
    st.write('Radio:', radio)
    st.write('Diámetro:', diametro)
    st.write('Tópico de mayor Betweenness:', top_enfermedades_btwns.Nodo.values[0])
    st.write('Institución de mayor Betweenness:', top_instituciones_btwns.Nodo.values[0])

    col1, col2 = st.columns(2)

    col1.header("Tópicos más investigados:")
    col1.dataframe(top_enfermedades_grado[['Nodo','Grado']].assign(hack='').set_index('hack'))
    col2.header('Instituciones más activas:')
    col2.dataframe(top_instituciones_grado[['Nodo','Grado']].assign(hack='').set_index('hack'))

    
    #st.subheader('Tópicos más investigados:')
    #st.dataframe(top_enfermedades_grado[['Nodo','Grado']].assign(hack='').set_index('hack'))
    #st.subheader('Instituciones más activas:')
    #st.dataframe(top_instituciones_grado[['Nodo','Grado']].assign(hack='').set_index('hack'))

    st.subheader('Componente Gigante Vs. Red Entera')
    st.dataframe(nodos_ejes)