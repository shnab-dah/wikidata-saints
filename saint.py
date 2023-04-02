import networkx as nx
import pandas as pd
import community as community_louvain
import plotly.express as px


class Saint:
    def __init__(self, artwork, name):
        self.url = name
        # isolate qid from url
        name = name.split('/')
        self.QID = name[4]
        # set name in Corpus class when building saints
        self.name = ''
        self.artworks = [artwork]
        self.connections = []
        self.frequency = 0
        self.gender = ''

    def plot_histogram(self):
        dates = [artwork.date for artwork in self.artworks]
        dates.sort()
        df = pd.DataFrame(dates, columns=['year'])
        fig = px.histogram(df, x='year', marginal='rug')
        fig.update_layout(xaxis_title=None)
        fig.update_layout(yaxis_title=None)
        return fig

    def build_network(self):
        G = nx.Graph()
        edge_weight = {}
        # freq dict for connections
        for connection in self.connections:
            if connection[0] in edge_weight:
                edge_weight[connection[0]] += 1
            else:
                edge_weight[connection[0]] = 1
        # make connections into edges
        for edge in edge_weight:
            G.add_edge(edge[0], edge[1], weight=edge_weight[edge])
        label = {}
        for node in G.nodes:
            label[node] = node.name
        nx.relabel_nodes(G, label, copy=False)
        node_degree = dict(G.degree)

        nx.set_node_attributes(G, node_degree, 'size')
        communities = community_louvain.best_partition(G)
        nx.set_node_attributes(G, communities, 'group')
        return G
