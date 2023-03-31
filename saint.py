import matplotlib.pyplot as plt
import networkx as nx
from corpus import *
from tqdm.auto import tqdm
from pyvis.network import Network
import community as community_louvain


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
        f = plt.figure()
        dates = [artwork.date for artwork in self.artworks]
        years = []
        for date in dates:
            date = date.split('-')
            years.append(int(date[0]))
        years.sort()
        # bins by Fred-Diacconis rule
        if len(years) > 10:
            # some entries create errors -> therefore except clause
            try:
                q25, q75 = np.percentile(years, [25, 75])
                bin_width = 2 * (q25 - q75) * len(years) ** (-1 / 3)
                bins = round((years[0] - years[len(years) - 1]) / bin_width)
            except:
                bins = 10
        else:
            bins = 10
        plt.hist(years, density=False, bins=bins, figure=f)
        f.suptitle(f'Year frequency of {self.name}')
        return f


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
        for node in G.nodes:label[node] = node.name
        nx.relabel_nodes(G, label, copy=False)
        node_freq = {}
        # for edge in G.edges:
        #    for dep in edge:
        #        if dep in node_freq:
        #            node_freq[dep] += 1
        #        else:
        #            node_freq[dep] = 1
        node_degree = dict(G.degree)
        # print(node_degree)
        nx.set_node_attributes(G, node_degree, 'size')
        communities = community_louvain.best_partition(G)
        nx.set_node_attributes(G, communities, 'group')
        G2 = Network(width='1500px', height ='1000px', bgcolor='#222222', font_color='white', select_menu=True)
        G2.from_nx(G)
        G2.force_atlas_2based()
        G2.show(f"network_of_{self.name}.html", notebook=False)

if __name__ == "__main__":
    x = Corpus()
    z = []
    for saint in x.saints.values():
        z.append(saint)
    for saint in z[:10]:
        saint.build_network()
