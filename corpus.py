import networkx as nx
import pandas as pd
from pandas.plotting._matplotlib import plot

from artwork import Artwork
from saint import Saint
import community as community_louvain
import plotly.express as px

class Corpus:
    def __init__(self):
        self.artworks = {}
        # set-up saints
        self.sdf = pd.read_json('./data/saints.json')
        self.saintuids = self.sdf['saintUID.value'].tolist()

        # dictionary QID: Name
        self.saintnames = {}
        for QID in self.sdf.index.values.tolist():
            self.saintnames[QID] = self.sdf['name.value'].loc[QID]

        # load 2d-object df
        self.odf = pd.read_json('./data/2d_objects.json')

        # deal w/ double depiction entries
        self.odf['depictions.value'] = self.odf['depictions.value'].str.split(';')
        df = self.odf.explode('depictions.value')

        # filter odf to only show objs with saints
        self.odf = df[df['depictions.value'].isin(self.saintuids)]
        objs = []
        for x in self.odf.index.values.tolist():
            if x not in objs:
                objs.append(x)

        # reset odf and only show uniques
        self.odf = pd.read_json('./data/2d_objects.json')
        self.odf = self.odf.loc[objs]
        self.artworks = self.init_artworks()
        self.saints = self.init_saints()
        self.QIDsaints = {}
        self.QIDartworks= {}
        for a in self.artworks.values():
            self.QIDartworks[a.QID] = a
        for s in self.saints.values():
            self.QIDsaints[s.QID] = s

    def init_artworks(self):
        artworks = {}
        for uid in self.odf.index.values.tolist():
            artworks[uid] = Artwork(self.odf.loc[uid])
        return artworks

    def init_saints(self):
        saints = {}
        # make saint objects and append artworks to them
        for artwork in self.artworks.values():
            for depiction in artwork.depictions:
                if depiction in self.saintuids:
                    if depiction not in saints:
                        saints[depiction] = Saint(artwork, depiction)
                    else:
                        saints[depiction].artworks.append(artwork)
        # adds connections in artworks to saint objects ((depicted1, depicted2), artwork)
        for saint in saints.values():
            # update some vars
            saint.frequency = len(saint.artworks)
            saint.name = self.saintnames[saint.QID]
            saint.gender = self.sdf['gender.value'].loc[saint.QID]
            if saint.gender != 'male' and saint.gender != 'female':
                saint.gender = "undefined"
            for artwork in saint.artworks:
                if len(artwork.depictions) > 1:
                    x, y = 0, 0
                    while x < len(artwork.depictions) - 1:
                        if artwork.depictions[x] != artwork.depictions[y]:
                            if artwork.depictions[x] in self.saintuids and artwork.depictions[y] in self.saintuids:
                                saint.connections.append(
                                    ((saints[str(artwork.depictions[x])], saints[str(artwork.depictions[y])]), artwork))
                        y += 1
                        if y == len(artwork.depictions):
                            x += 1
                            y = x + 1
        return saints

    def plot_histo(self):
        dates = self.odf['dates.value'].tolist()
        years = []
        for year in dates:
            year = year.split('-')
            years.append(int(year[0]))
        years.sort()
        df = pd.DataFrame(years, columns=['year'])
        fig = px.histogram(df, x="year")
        fig.update_layout(xaxis_title=None)
        fig.update_layout(yaxis_title=None)
        return fig

    def show_network(self):
        connections = []
        for artwork in self.artworks.values():
            depictions = []
            for depiction in artwork.depictions:
                if depiction in self.saintuids:
                    depictions.append(depiction)
            if len(depictions) > 1:
                x, y = 0, 0
                while x < len(depictions) - 1:
                    if depictions[x] != depictions[y]:
                        connections.append(((self.saints[depictions[x]], self.saints[depictions[y]]), artwork))
                    y += 1
                    if y == len(depictions):
                        x += 1
                        y = x + 1
        G = nx.Graph()
        edge_weight = {}
        # freq dict for connections
        for connection in connections:
            if connection[0] in edge_weight:
                edge_weight[connection[0]] += 1
            else:
                edge_weight[connection[0]] = 1
        # make connections into edges
        for edge in edge_weight:
            G.add_edge(edge[0], edge[1], weight=edge_weight[edge])
        communities = community_louvain.best_partition(G)
        nx.set_node_attributes(G, communities, 'group')
        label = {}
        for node in G.nodes:
            label[node] = node.name
        nx.relabel_nodes(G, label, copy=False)
        node_degree = dict(G.degree)
        nx.set_node_attributes(G, node_degree, 'size')
        return G


if __name__ == "__main__":
    corp = Corpus()
    G = corp.show_network()
    pd.options.plotting.backend = 'plotly'
    #degree centrality
    degree_dict = nx.degree_centrality(G)
    degree_df = pd.DataFrame.from_dict(degree_dict, orient='index', columns=['centrality'])
    #closeness centrality
    closeness_dict = nx.closeness_centrality(G)
    closeness_df = pd.DataFrame.from_dict(closeness_dict, orient='index', columns=['centrality'])
    #betweenness centrality
    betweenness_dict = nx.betweenness_centrality(G)
    betweenness_df = pd.DataFrame.from_dict(betweenness_dict, orient='index', columns=['centrality'])

    fig1 = degree_df.sort_values('centrality', ascending=False)[0:9].plot.bar(title='Degree centrality')
    fig2 = closeness_df.sort_values('centrality', ascending=False)[0:9].plot.bar(title='Closeness centrality')
    fig3 = betweenness_df.sort_values('centrality', ascending=False)[0:9].plot.bar(title='Betweenness centrality')

    fig1.show()
    fig2.show()
    fig3.show()
