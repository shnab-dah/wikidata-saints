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
        fig = func.set_axes(px.histogram(df, x='year', marginal='rug', title='Depictions over time'))

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
            G.nodes[node]['order'] = node.orders
            G.nodes[node]['gender'] = node.gender
            G.nodes[node]['obj'] = node
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
                clustering, density, modularity = nx.average_clustering(G), nx.density(G), \
                    community_louvain.modularity(communities, G)
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

    def gender_network(self, save=True):
        G = self.build_network()
        net = nx.Graph()
        net2 = Network(width='100%', height='750', bgcolor='#222222', font_color='white')

        for node_id, node_attrs in G.nodes(data=True):
            gender = node_attrs['gender']
            size = node_attrs['size']
            # set color of node based on gender attribute
            if gender == 'male':
                color = 'blue'
            elif gender == 'female':
                color = 'red'
            else:
                color = 'gray'

            net.add_node(node_id, label=node_id, color=color, size=size)

        # add edges to the Pyvis network object
        for edge in G.edges(data=True):
            # color edge red if both are member of order
            if  G.nodes[edge[0]]['obj'].gender == G.nodes[edge[1]]['obj'].gender:
                if G.nodes[edge[0]]['obj'].gender == 'male':
                    net.add_edge(edge[0], edge[1], color='blue', weight=edge[2]['weight'])
                elif G.nodes[edge[0]]['obj'].gender == 'female':
                    net.add_edge(edge[0], edge[1], color='red', weight=edge[2]['weight'])
                else:
                    net.add_edge(edge[0], edge[1], color='gray', weight=edge[2]['weight'])
            else:
                net.add_edge(edge[0], edge[1], color='green', weight=edge[2]['weight'])
        net2.from_nx(net)
        net = net2
        net.force_atlas_2based()
        if save:
            net.save_graph(f'./static/temp/{self.QID}-gendernetwork.html')
        else:
            return net

    def order_network(self, arg='', save=True):
        G = self.build_network()
        net = nx.Graph()
        net2 = Network(width='100%', height='750', bgcolor='#222222', font_color='white')

        for node_id, node_attrs in G.nodes(data=True):
            order = node_attrs['order']
            size = node_attrs['size']
            # set color of node based on gender attribute
            if arg in order:
                color = 'red'
            else:
                color = 'gray'

            net.add_node(node_id, label=node_id, color=color, size=size)

        # add edges to the Pyvis network object
        for edge in G.edges(data=True):
            # color edge red if both are member of order
            if arg not in G.nodes[edge[0]]['obj'].orders or arg not in G.nodes[edge[1]]['obj'].orders:
                net.add_edge(edge[0], edge[1], color='gray', weight=edge[2]['weight'])
            else:
                net.add_edge(edge[0], edge[1], color='red', weight=edge[2]['weight'])

        net2.from_nx(net)
        net = net2
        net.force_atlas_2based()

        if save:
            net.save_graph(f'./static/temp/{self.QID}-{arg}-network.html')
        else:
            return net
