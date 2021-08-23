import networkx as nx
from networkx.algorithms import bipartite
from pyvis.network import Network
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from tqdm import tqdm
import plotly.graph_objects as go

@st.cache
def get_data():
    #main = pd.read_csv('../../data-processing/tabla_de_to_los_links.csv')
    main = pd.read_csv('/app/topicos-streamlit/data-processing/tabla_de_to_los_links.csv')
    
    return main

@st.cache(allow_output_mutation=True)
def build_graph(main, year_range, grupos, paises, giant, reduce):
    np.random.seed(42)
    
    main = main[
        (main.year.between(year_range[0], year_range[1])) &
        (main['grupo'].isin(grupos)) &
        (main.pais.isin(paises))
        ].reset_index(drop=True)

    plot_data = pd.pivot_table(main, values='enfermedad', index='year', columns='grupo', aggfunc='count')

    g = nx.Graph()

    afiliaciones_paises = dict(zip(main.institucion, main.pais))
    for affiliation in set(main.institucion):
        g.add_node(affiliation, bipartite=0, color='#162347', title=afiliaciones_paises[affiliation])
    enfermedades = dict(zip(main.enfermedad, main['grupo']))
    for enfermedad in enfermedades:
        g.add_node(enfermedad, bipartite=1, group=enfermedades[enfermedad], title=enfermedades[enfermedad])

    for idx, row in main.iterrows():
        g.add_edge(row.enfermedad, row.institucion, year=row.year)

    Giant = max(nx.connected_components(g), key=len)
    Giant = g.subgraph(Giant)
    g_plot = g
    
    if giant:
        g_plot = Giant

    grado = g.degree()
    grado = pd.DataFrame(grado, columns=['Nodo','Grado'])
    grado.loc[grado.Nodo.isin(set(main.institucion)), 'Tipo'] = 'institucion'
    grado.loc[pd.isna(grado.Tipo), 'Tipo'] = 'enfermedad'
    num_nodos = grado.groupby('Tipo')['Nodo'].count()
    num_ejes = grado.groupby('Tipo')['Grado'].sum()[0]

    grado_gigante = Giant.degree()
    grado_gigante = pd.DataFrame(grado_gigante, columns=['Nodo','Grado'])
    grado_gigante.loc[grado_gigante.Nodo.isin(set(main.institucion)), 'Tipo'] = 'institucion'
    grado_gigante.loc[pd.isna(grado_gigante.Tipo), 'Tipo'] = 'enfermedad'
    num_nodos_gigante = grado_gigante.groupby('Tipo')['Nodo'].count()
    num_ejes_gigante = grado_gigante.groupby('Tipo')['Grado'].sum()[0]

    if reduce:
        k = int(0.1 * g_plot.number_of_nodes())
        sampled_nodes = np.random.choice(g_plot.nodes, k)
        g_plot = g_plot.subgraph(sampled_nodes)

    radio = nx.radius(Giant)
    diametro = nx.diameter(Giant)

    top_enfermedades_grado = grado[grado.Tipo == 'enfermedad'].sort_values('Grado', ascending=False).head(3).reset_index(drop=True)
    top_instituciones_grado = grado[grado.Tipo == 'institucion'].sort_values('Grado', ascending=False).head(3).reset_index(drop=True)

    # if btwns:
    #     betweenness = nx.betweenness_centrality(Giant)
    #     betweenness = pd.DataFrame(betweenness.items(), columns=['Nodo','Betweenness'])
    #     betweenness.sort_values('Betweenness', ascending=False)

    #     grado_gigante = grado_gigante.merge(betweenness, on='Nodo')

    #     top_enfermedades_btwns = grado_gigante[grado_gigante.Tipo == 'enfermedad'].sort_values('Betweenness', ascending=False).head(1).reset_index(drop=True)
    #     top_instituciones_btwns = grado_gigante[grado_gigante.Tipo == 'institucion'].sort_values('Betweenness', ascending=False).head(1).reset_index(drop=True)

    return {'g_plot': g_plot,
     'radio': radio,
     'diametro': diametro,
     'top_enfermedades_grado': top_enfermedades_grado,
     'top_instituciones_grado': top_instituciones_grado,
     #'top_enfermedades_btwns': top_enfermedades_btwns,
     #'top_instituciones_btwns': top_instituciones_btwns,
     'nodos_ejes': pd.DataFrame(
         {'Número de Tópicos':[num_nodos['enfermedad'], num_nodos_gigante['enfermedad']],
          'Número de instituciones':[num_nodos['institucion'], num_nodos_gigante['institucion']],
          'Número de Ejes':[num_ejes, num_ejes_gigante]},
                  index=['Red Completa','Componente Gigante']),
     'plot_data':plot_data
    }
    
def show_graph(file_name, barnes, grupos, paises, g_plot, radio, diametro, top_enfermedades_grado, top_instituciones_grado, nodos_ejes, plot_data):
    
    nt = Network('600px', '100%', notebook=True, bgcolor="#777271", font_color='#ffffff')
    nt.from_nx(g_plot)
    
    if barnes:
        nt.barnes_hut()
    nt.show(file_name)

    HtmlFile = open(file_name, 'r', encoding='utf-8')
    source_code = HtmlFile.read() 

    st.title('Visualización de la Red')
    st.write('Países:', ', '.join(paises))
    st.write('Enfermedades:', ', '.join(grupos))
    components.html(source_code, height = 600, width=700)

    st.title('Métricas Principales')

    st.subheader('Medidas de la componente gigante:')
    st.write('Radio:', radio)
    st.write('Diámetro:', diametro)
    #st.write('Tópico de mayor Betweenness:', top_enfermedades_btwns.Nodo.values[0])
    #st.write('institución de mayor Betweenness:', top_instituciones_btwns.Nodo.values[0])

    col1, col2 = st.columns(2)

    col1.header("Tópicos más investigados:")
    col1.dataframe(top_enfermedades_grado[['Nodo','Grado']].assign(hack='').set_index('hack'))
    col2.header('instituciones más activas:')
    col2.dataframe(top_instituciones_grado[['Nodo','Grado']].assign(hack='').set_index('hack'))

    st.subheader('Componente Gigante Vs. Red Entera')
    st.dataframe(nodos_ejes)

    fig = go.Figure()
    for col in plot_data:

        fig.add_trace(
            go.Scatter(
                x=plot_data.index,
                y=plot_data[col],
                name=col.title()
            )
        )
    fig.update_layout(
        title = 'Cantidad de Investigaciones por Año'
    )

    #st.subheader('')
    fig.update_yaxes(title_text='Cantidad')
    st.plotly_chart(fig)