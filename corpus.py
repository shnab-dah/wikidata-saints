import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from SPARQLWrapper import SPARQLWrapper, JSON
from pyvis.network import Network
from artwork import Artwork
from saint import Saint
import community as community_louvain
import plotly.express as px
import time
from wikidata.client import Client
import multiprocessing
import functionality as func


class Corpus:
    def __init__(self, localdata=False):
        # init dicts to acces saints and artworks
        self.saintnames = {}
        self.QIDsaints = {}
        self.QIDartworks = {}

        # TODO: query saints rather than load
        # load saints
        self.sdf = pd.read_json('./data/saints.json')

        # dictionary QID: Name
        for QID in self.sdf.index.values.tolist():
            self.saintnames[QID] = self.sdf['name.value'].loc[QID]

        # query wikidata for objects
        if not localdata:
            self.odf = self.query()
            querytime = time.time()
            time_struct = time.localtime(querytime)
            self.querytime = time.strftime("%d-%m-%Y %H:%M:%S")
        else:
            self.odf = pd.read_json('./data/objects.json')
            self.querytime = 'Local data'

        # create artwork objects than saint objects
        self.artworks = self.init_artworks()
        self.saints = self.init_saints()

        # create QID - object/saint dictionaries
        for artwork in self.artworks.values():
            self.QIDartworks[artwork.QID] = artwork
        for saint in self.saints.values():
            self.QIDsaints[saint.QID] = saint

        # create networks
        self.network_snapshots = self.network_progression()
        self.network = self.main_network()

        self.typechart = self.type_frequency()

    def query(self):
        # endpoint wikidata
        endpoint_url = "https://query.wikidata.org/sparql"
        # query text
        query = """SELECT DISTINCT ?object 
        (group_concat(DISTINCT ?type;separator=";") as ?types)
        (group_concat(DISTINCT ?depicted;separator=";") as ?depictions) 
        (group_concat(DISTINCT ?d;separator=";") as ?dates)
        (group_concat(DISTINCT ?creator;separator="") as ?creators)
        (group_concat(DISTINCT ?image; separator=";") as ?images)
        (group_concat(DISTINCT ?collection; separator=";") as ?collections)
        (group_concat(DISTINCT ?material; separator=";") as ?materials)
        (group_concat(DISTINCT ?genre; separator=";") as ?genres)
        (group_concat(DISTINCT ?creation; separator=";") as ?creationlocations)
        where{
          ?object wdt:P180 ?depicted.
          ?depicted wdt:P411 ?state.
          ?object wdt:P31 ?type
          optional{?object wdt:P571 ?d.}
          optional{?object wdt:P170 ?creator.}
          optional{?object wdt:P18 ?image.}
          optional{?object wdt:P195 ?collection.}
          optional{?object wdt:P186 ?material.}
          optional{?object wdt:P136 ?genre.}
          optional{?object wdt:P1071 ?creation.}
        }
        group by ?object ?types ?depictions ?dates ?creators ?images ?colelctions ?materials ?genres ?creationlocations"""

        # set user agent
        user_agent = "SaintAnalyzer/0.0"

        # set sparql settings
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        # query wikidata
        results = sparql.query().convert()
        # convert to json pd
        data = pd.json_normalize(results['results']['bindings'])
        # extract QID from url
        new = data['object.value'].str.split("/", n=-1, expand=True)
        data["QID"] = new[4]
        # set DF columns
        cols = ['QID', 'object.value', 'types.value', 'depictions.value', 'dates.value', 'creators.value',
                'images.value', 'materials.value', 'genres.value', 'creationlocations.value', 'collections.value']
        data = data[cols]
        # set DF index = QID
        data.set_index('QID', inplace=True, drop=True)
        data.to_json('./data/objects.json')
        return data

    def init_artworks(self):
        # extract every column in objects DF and returns a dictionary {wikidata-link: artwork object}
        artworks = {}
        for uid in self.odf.index.values.tolist():
            artworks[uid] = Artwork(self.odf.loc[uid])
        return artworks

    def init_saints(self):
        saints = {}
        # make saint objects and append artworks to them
        for artwork in self.artworks.values():
            for depiction in artwork.depictions:
                if depiction not in saints:
                    saints[depiction] = Saint(artwork, depiction)
                else:
                    saints[depiction].artworks.append(artwork)
        # adds connections in artworks to saint objects ((depicted1, depicted2), artwork)
        for saint in saints.values():
            # update some vars
            saint.frequency = len(saint.artworks)
            saint.name = self.saintnames[saint.QID]
            saint.artworks = sorted(saint.artworks, key=func.get_date)
            saint.gender = self.sdf['gender.value'].loc[saint.QID]
            if saint.gender != 'male' and saint.gender != 'female':
                saint.gender = "undefined"

            orders = self.sdf['religiousOrders.value'].loc[saint.QID]
            orders = orders.split(';')
            for order in orders:
                if order != '':
                    saint.orders.append(order)
                else:
                    saint.orders.append('None')

            groups = self.sdf['religiousGroup.value'].loc[saint.QID]
            groups = groups.split(';')
            for group in groups:
                if group != '':
                    saint.groups.append(group)
                else:
                    saint.groups.append('None')

            for artwork in saint.artworks:
                if len(artwork.depictions) > 1:
                    x, y = 0, 0
                    while x < len(artwork.depictions) - 1:
                        if artwork.depictions[x] != artwork.depictions[y]:
                            saint.connections.append(
                                ((saints[str(artwork.depictions[x])], saints[str(artwork.depictions[y])]), artwork))
                        y += 1
                        if y == len(artwork.depictions):
                            x += 1
                            y = x + 1

            # clean (a, b) (b, a) differences:
            connections = []
            for connection in saint.connections:
                artwork = connection[1]
                connection = connection[0]
                inverse = (connection[1], connection[0])
                if inverse in connections:
                    connections.append((inverse, artwork))
                else:
                    connections.append((connection, artwork))
        return saints

    def plot_histo(self):
        years = [artwork.date for artwork in self.artworks.values() if artwork.dated]
        years.sort()
        df = pd.DataFrame(years, columns=['year'])
        fig = px.histogram(df, x="year")
        fig.update_layout(xaxis_title=None)
        fig.update_layout(yaxis_title=None)
        return fig

    def main_network(self):
        # init variables
        connections = []
        G = nx.Graph()

        # extract network depictions and link depicted together
        for artwork in self.artworks.values():
            if len(artwork.depictions) > 1:
                x, y = 0, 0
                while x < len(artwork.depictions) - 1:
                    connection = (self.saints[artwork.depictions[x]], self.saints[artwork.depictions[y]])
                    # (a, b) and (b, a) should be considered the same edge
                    inverse = connection[1], connection[0]
                    if artwork.depictions[x] != artwork.depictions[y]:
                        if inverse != connections:
                            connections.append(connection)
                        else:
                            connections.append(inverse)
                    y += 1
                    if y == len(artwork.depictions):
                        x += 1
                        y = x + 1

        edge_weight = {}
        # freq dict for connections
        for connection in connections:
            if connection in edge_weight:
                edge_weight[connection] += 1
            else:
                edge_weight[connection] = 1
        # make connections into edges
        for edge in edge_weight:
            G.add_edge(edge[0], edge[1], weight=edge_weight[edge])

        communities = community_louvain.best_partition(G)
        nx.set_node_attributes(G, communities, 'group')

        label = {}
        for node in G.nodes:
            orders = ''.join(node.orders)
            G.nodes[node]['order'] = node.orders
            G.nodes[node]['gender'] = node.gender
            label[node] = node.name
        nx.relabel_nodes(G, label, copy=False)
        node_degree = dict(G.degree)
        nx.set_node_attributes(G, node_degree, 'size')
        return G

    def network_progression(self, interval_size=100):
        pd.options.plotting.backend = 'plotly'

        # get list of years
        years = [artwork.date for artwork in self.artworks.values() if artwork.dated]
        # calculate the range of the years
        year_range = max(years) - min(years)
        # create a list split at interval size
        self.yearranges = [(min(years) + i * interval_size, min(years) + (i + 1) * interval_size - 1) for i in
                           range(int(year_range / interval_size) + 1)]
        graphs = []

        for start, end in self.yearranges:
            G = nx.Graph()
            connections = []
            for artwork in self.artworks.values():
                if artwork.dated:
                    depictions = []
                    if start < artwork.date < end:
                        for depiction in artwork.depictions:
                            depictions.append(depiction)
                        if len(depictions) > 1:
                            x, y = 0, 0
                            while x < len(depictions) - 1:
                                if depictions[x] != depictions[y]:
                                    connections.append((self.saints[depictions[x]], self.saints[depictions[y]]))
                                y += 1
                                if y == len(depictions):
                                    x += 1
                                    y = x + 1
            edge_weight = {}
            # freq dict for connections
            for connection in connections:
                inverse = (connection[1], connections[0])
                if connection in edge_weight:
                    edge_weight[connection] += 1
                elif inverse in edge_weight:
                    edge_weight[inverse] += 1
                else:
                    edge_weight[connection] = 1

            # make connections into edges
            for edge in edge_weight:
                G.add_edge(edge[0], edge[1], weight=edge_weight[edge])
            # communities = community_louvain.best_partition(G)
            # nx.set_node_attributes(G, communities, 'group')
            label = {}
            for node in G.nodes:
                label[node] = node.name
                G.nodes[node]['order'] = node.orders[0]
                G.nodes[node]['gender'] = node.gender
            nx.relabel_nodes(G, label, copy=False)
            node_degree = dict(G.degree)
            nx.set_node_attributes(G, node_degree, 'size')

            graphs.append({
                'nx': G,
                'start': start,
                'end': end,
            })
        return graphs

    def centrality_evolution(self, saint):
        degree_cent, closeness_cent, betwenness_cent, years = [], [], [], []
        s = saint.name

        for graph in self.network_snapshots:
            G = graph['nx']

            if s in G.nodes:
                degree = nx.degree_centrality(G)
                closeness = nx.closeness_centrality(G)
                betwenneess = nx.betweenness_centrality(G)

                degree_cent.append(degree[s])
                closeness_cent.append(closeness[s])
                betwenness_cent.append(betwenneess[s])
                years.append(graph['end'])

        df = pd.DataFrame(dict(x=years, y=degree_cent))
        degree_cent = func.set_axes(px.line(df, x="x", y="y", title=f"Degree centrality over time of {s}"))

        df = pd.DataFrame(dict(x=years, y=closeness_cent))
        closeness_cent = func.set_axes(px.line(df, x="x", y="y", title=f"Closeness centrality over time of {s}"))

        df = pd.DataFrame(dict(x=years, y=betwenness_cent))
        betweenness_cent = func.set_axes(px.line(df, x="x", y="y", title=f"Betweenness centrality over time of {s}"))

        dic = {
            'degree': degree_cent,
            'closeness': closeness_cent,
            'betweenness': betweenness_cent
        }

        return dic

    def type_frequency(self):
        artwork_types = [artwork.types for artwork in self.artworks.values()]
        freq = {}
        for obj in artwork_types:
            for typ in obj:
                typ = func.filter_QID(typ)
                if typ in freq:
                    freq[typ] += 1
                else:
                    freq[typ] = 1
        uniques = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        uniques = uniques[0:10]
        qids = [qid[0] for qid in uniques]

        with multiprocessing.Pool(processes=5) as pool:
            returns = pool.map(self.query_label, qids)

        dictionary = {}
        for d in returns:
            dictionary.update(d)
        freq_dict = {}
        for tup in uniques:
            freq_dict[dictionary[tup[0]]] = tup[1]

        # sort the dictionary by count values
        sorted_dict = {k: v for k, v in sorted(freq_dict.items(), key=lambda item: item[1], reverse=True)}

        # create pandas dataframe from dictionary
        df = pd.DataFrame({'Type': list(sorted_dict.keys()), 'Count': list(sorted_dict.values())})

        # create bar chart
        return func.set_axes(px.bar(df, x='Type', y='Count', title='Type frequency in corpus'))

    def query_label(self, qid):
        dict = {}
        client = Client()
        entity = client.get(qid)
        label = entity.label
        dict[qid] = str(label)
        return dict

    # TODO: fix color edges & edge-weigth
    def gender_network(self, save=True):
        G = self.network
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
                net.add_edge(edge[0], edge[1], color='gray', weight=edge[2]['weight'])

        net2.from_nx(net)
        net = net2
        net.force_atlas_2based()
        if save:
            net.save_graph(f'./static/temp/corpus-gender-network.html')
        else:
            return net
#TODO: fix color edges & edge-weigth
    def order_network(self, arg='Franciscans', save=True):
        G = self.network
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
            net.save_graph(f'./static/temp/corpus-{arg}-network.html')
        else:
            return net

    def order_stats(self):
        saints = [s for s in self.saints.values()]
        order_freq = {}

        for s in saints:
            orders = s.orders
            for order in orders:
                if order in order_freq:
                    order_freq[order] += 1
                else:
                    order_freq[order] = 1
        return order_freq

if __name__ == "__main__":
    corp = Corpus(localdata=True)
    corp.order_network(save=False).show('franciscans.html', notebook=False)
    corp.gender_network(save=False).show('corpus-gender.html', notebook=False)