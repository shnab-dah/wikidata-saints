import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from tqdm.auto import tqdm
import pandas as pd
from artwork import Artwork
from saint import Saint
import community as community_louvain
from pyvis.network import Network


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
        for saint in tqdm(saints.values()):
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
                                saint.connections.append(((saints[str(artwork.depictions[x])], saints[str(artwork.depictions[y])]), artwork))
                        y += 1
                        if y == len(artwork.depictions):
                            x += 1
                            y = x + 1
        return saints

    def plot_histo(self):
        f = plt.figure()
        dates = self.odf['dates.value'].tolist()
        years = []
        for year in dates:
            year = year.split('-')
            years.append(int(year[0]))
        years.sort()
        # bins by Fred-Diacconis rule
        try:
            q25, q75 = np.percentile(years, [25, 75])
            bin_width = 2 * (q25 - q75) * len(years) ** (-1 / 3)
            bins = round((years[0] - years[len(years) - 1]) / bin_width)
        except:
            bins = 10
        if bins < 10:
            bins = 10
        plt.hist(years, density=False, bins=bins, figure=f)
        return f

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
        for node in G.nodes: label[node] = node.name
        nx.relabel_nodes(G, label, copy=False)
        node_freq = {}
        node_degree = dict(G.degree)
        nx.set_node_attributes(G, node_degree, 'size')
        G2 = Network(width='1500px', height='1000px', bgcolor='#222222', font_color='white', select_menu=True)
        G2.from_nx(G)
        G2.force_atlas_2based()
        G2.show_buttons(filter_='physics')
        return G2


if __name__ == "__main__":
    x = Corpus()
    x.show_network()