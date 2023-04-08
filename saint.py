import networkx as nx
import pandas as pd
import community as community_louvain
import plotly.express as px
from pyvis.network import Network
import functionality as func

pd.options.plotting.backend = 'plotly'

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
        self.orders = []
        self.groups = []

    def plot_histogram(self):
        dates = [artwork.date for artwork in self.artworks if artwork.dated]
        dates.sort()
        df = pd.DataFrame(dates, columns=['year'])
        fig = px.histogram(df, x='year', marginal='rug', title='Depictions over time')
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

    def yearranges(self):
        years = [artwork.date for artwork in self.artworks if artwork.dated]
        years.sort()

        start = (years[0] // 100) * 100
        if years[len(years) -1 ] % 100 != 0:
            end = (years[len(years) - 1] // 100) * 100 + 100
        else:
            end = years[len(years) - 1]
        startdates = [y for y in range(start, end, 100)]
        yearrange = []
        for date in startdates:
            yearrange.append((date, date+100))
        return yearrange

    def network_progression(self):
        yearranges = self.yearranges()
        graphs = []
        for start, end in yearranges:
            G = nx.Graph()
            weighed_edges = {}
            G.add_node(self)
            for connection in self.connections:
                if connection[1].dated:
                    edge = connection[0]
                    date = connection[1].date
                    if date > start and date < end:
                        if edge in weighed_edges:
                            weighed_edges[edge] += 1
                        else:
                            weighed_edges[edge] = 1
            for edge in weighed_edges:
                G.add_edge(edge[0], edge[1], weight=weighed_edges[edge])
            label = {}
            for node in G.nodes:
                label[node] = node.name
            nx.relabel_nodes(G, label, copy=False)

            node_degree = dict(G.degree)
            nx.set_node_attributes(G, node_degree, 'size')
            communities = community_louvain.best_partition(G)
            nx.set_node_attributes(G, communities, 'group')

            try:
                clustering, density, modularity = nx.average_clustering(G), nx.density(G), community_louvain.modularity(communities, G)
            except:
                clustering, density, modularity = 0, 0, 0

            # degree centrality
            degree_dict = nx.degree_centrality(G)
            degree_df = pd.DataFrame.from_dict(degree_dict, orient='index', columns=['centrality'])
            # closeness centrality
            closeness_dict = nx.closeness_centrality(G)
            closeness_df = pd.DataFrame.from_dict(closeness_dict, orient='index', columns=['centrality'])
            # betweenness centrality
            betweenness_dict = nx.betweenness_centrality(G)
            betweenness_df = pd.DataFrame.from_dict(betweenness_dict, orient='index', columns=['centrality'])

            # make graphs
            fig1 = degree_df.sort_values('centrality', ascending=False)[1:10].plot.bar(title='Degree centrality')
            fig2 = closeness_df.sort_values('centrality', ascending=False)[1:10].plot.bar(title='Closeness centrality')
            fig3 = betweenness_df.sort_values('centrality', ascending=False)[1:10].plot.bar(
                title='Betweenness centrality')

            # clean titles
            fig1, fig2, fig3 = func.set_axes(fig1), func.set_axes(fig2), func.set_axes(fig3)

            G2 = Network(width='100%', height='750', bgcolor='#222222', font_color='white')
            G2.from_nx(G)
            G2.force_atlas_2based()
            graphs.append({
                'G': G2,
                'nx': G,
                'start': start,
                'end': end,
                'degree': fig1,
                'closeness': fig2,
                'betweenness': fig3,
                'clustering': clustering,
                'density': density,
                'modularity': modularity
            })
        return graphs