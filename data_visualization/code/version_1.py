import networkx as nx
from networkx.algorithms import bipartite
import pandas as pd
from pyvis.network import Network

author = pd.read_csv('../dummy_data/tabla_1.csv')
illness = pd.read_csv('../dummy_data/tabla_2.csv')
links = pd.read_csv('../dummy_data/tabla_3.csv')

g = nx.Graph()

for i in author["id"]:
    g.add_node(i, bipartite=0)
for j in illness["id"]:
    g.add_node(j, bipartite=1)
# g.add_nodes_from(list(author['id'].values), bipartite=0)
# g.add_nodes_from(list(illness['id'].values), bipartite=1)
g.add_edges_from(
    [(links.loc[i, "id_autor"], links.loc[i, "id_enfermedad"]) for i in range(links.shape[0])]
)

nx.draw(g, with_labels=True)
nt = Network()
nt.from_nx(g)
nt.show()
