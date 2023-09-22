import multiprocessing
import community
import community as community_louvain
import networkx as nx
import pandas as pd
from flask import Flask, render_template
from plotly.offline import plot
from pyvis.network import Network
import functionality as func
from corpus import Corpus
import os


corp = Corpus(localdata=False)
pd.options.plotting.backend = 'plotly'
app = Flask('Saint analysis')


def clean_temp():
    for filename in os.listdir('./static/temp'):
        file_path = os.path.join('./static/temp', filename)
        os.remove(file_path)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/corpus')
def corpus():
    G = corp.network
    corp.centrality_over_frequency()
    # network data
    clustering = nx.average_clustering(G)
    density = nx.density(G)
    partition = community.best_partition(G)
    modularity = community.modularity(partition, G)
    plot(corp.type_frequency(), filename=f'./static/temp/corpus-typefreq.html', auto_open=False)
    plot(corp.plot_histo(), filename=f'./static/temp/corpus-histo.html', auto_open=False)
    # degree centrality
    degree_dict = nx.degree_centrality(G)
    degree_df = pd.DataFrame.from_dict(degree_dict, orient='index', columns=['centrality'])
    # closeness centrality
    closeness_dict = nx.closeness_centrality(G)
    closeness_df = pd.DataFrame.from_dict(closeness_dict, orient='index', columns=['centrality'])
    # betweenness centrality
    betweenness_dict = nx.betweenness_centrality(G)
    betweenness_df = pd.DataFrame.from_dict(betweenness_dict, orient='index', columns=['centrality'])
    fig1 = degree_df.sort_values('centrality', ascending=False)[0:9].plot.bar(title='Degree centrality')
    fig2 = closeness_df.sort_values('centrality', ascending=False)[0:9].plot.bar(title='Closeness centrality')
    fig3 = betweenness_df.sort_values('centrality', ascending=False)[0:9].plot.bar(title='Betweenness centrality')
    fig1, fig2, fig3 = func.set_axes(fig1), func.set_axes(fig2), func.set_axes(fig3)
    plot(fig1, filename=f'./static/temp/corpus-degcent.html', auto_open=False)
    plot(fig2, filename=f'./static/temp/corpus-clocent.html', auto_open=False)
    plot(fig3, filename=f'./static/temp/corpus-betwcent.html', auto_open=False)

    return render_template('corpus.html', num_artworks=len(corp.artworks), num_saints=len(corp.saints),
                           date=corp.querytime, clustering=clustering, density=density, modularity=modularity)


@app.route('/corpus/network')
def corp_network():
    G = corp.network
    G2 = Network(width='1450', height='800px', bgcolor='#222222', font_color='white', filter_menu=False)
    # fix saint object error TODO: figure out cause
    for node in G.nodes:
        G.nodes[node]['obj'] = None
    G2.from_nx(G)
    G2.force_atlas_2based()
    G2.save_graph('./static/temp/corpus-network.html')
    return render_template('network.html')


@app.route('/saint')
def saint_index():
    saints = []
    for saint in corp.saints.values():
        saints.append((saint.QID, saint.name, saint.frequency))
    saints.sort(key=lambda a: a[2], reverse=True)
    return render_template('saint_index.html', saints=saints)


@app.route('/saint/<s>')
def saint_page(s):
    qid = s
    s = corp.QIDsaints[s]
    objs = [x for x in s.artworks]
    artworks = []
    G = s.build_network()
    # network data
    try:
        clustering = nx.average_clustering(G)
        density = nx.density(G)
        partition = community_louvain.best_partition(G)
        modularity = community_louvain.modularity(partition, G)
    except:
        clustering, density, partition, modularity = 0, 0, 0, 0

    # fix saint object error TODO: figure out cause
    for node in G.nodes:
        G.nodes[node]['obj'] = None
    # plot network
    G2 = Network(width='100%', height='750', bgcolor='#222222', font_color='white')
    G2.from_nx(G)
    G2.force_atlas_2based()
    G2.save_graph(f'./static/temp/{qid}-network.html')
    plot(s.plot_histogram(), filename=f'./static/temp/{qid}-histo.html', auto_open=False)

    # degree centrality
    degree_dict = nx.degree_centrality(G)
    degree_df = pd.DataFrame.from_dict(degree_dict, orient='index', columns=['centrality'])
    # closeness centrality
    closeness_dict = nx.closeness_centrality(G)
    closeness_df = pd.DataFrame.from_dict(closeness_dict, orient='index', columns=['centrality'])
    # betweenness centrality
    betweenness_dict = nx.betweenness_centrality(G)
    betweenness_df = pd.DataFrame.from_dict(betweenness_dict, orient='index', columns=['centrality'])

    # create figures
    fig1 = degree_df.sort_values('centrality', ascending=False)[1:10].plot.bar(title='Degree centrality')
    fig2 = closeness_df.sort_values('centrality', ascending=False)[1:10].plot.bar(title='Closeness centrality')
    fig3 = betweenness_df.sort_values('centrality', ascending=False)[1:10].plot.bar(title='Betweenness centrality')
    fig1, fig2, fig3 = func.set_axes(fig1), func.set_axes(fig2), func.set_axes(fig3)

    # plot figures
    plot(fig1, filename=f'./static/temp/{qid}-degcent.html', auto_open=False)
    plot(fig2, filename=f'./static/temp/{qid}-clocent.html', auto_open=False)
    plot(fig3, filename=f'./static/temp/{qid}-betwcent.html', auto_open=False)

    for artwork in objs:
        artworks.append((artwork.QID, artwork.objectvalue, artwork.date, artwork.types))

    # plot centrality progression
    centrality_pogression = corp.centrality_evolution(s)
    plot(centrality_pogression['degree'], filename=f'./static/temp/{qid}-evolution-degree.html', auto_open=False)
    plot(centrality_pogression['closeness'], filename=f'./static/temp/{qid}-evolution-closeness.html', auto_open=False)
    plot(centrality_pogression['betweenness'], filename=f'./static/temp/{qid}-evolution-betweenness.html', auto_open=False)

    return render_template('saint.html', name=s.name, url=s.url, objs=artworks, qid=qid, clustering=clustering,
                           density=density, modularity=modularity)


@app.route('/saint/<s>/network_progression')
def network_progression(s):
    qid = s
    s = corp.QIDsaints[s]
    ranges = s.network_progression()
    for range in ranges:
        range['G'].save_graph(f'./static/temp/{qid}-{range["start"]}-{range["end"]}-network.html')
        plot(range['degree'], filename=f'./static/temp/{qid}-{range["start"]}-{range["end"]}-degree.html', auto_open=False)
        plot(range['closeness'], filename=f'./static/temp/{qid}-{range["start"]}-{range["end"]}-closeness.html',
             auto_open=False)
        plot(range['betweenness'], filename=f'./static/temp/{qid}-{range["start"]}-{range["end"]}-betweenness.html',
             auto_open=False)
    return render_template('network_progression.html', ranges=ranges, name=s.name, qid=qid)

@app.route('/saint/<s>/network_comparison')
def saint_network_compare(s):
    qid = s
    s = corp.QIDsaints[s]
    G = s.build_network()
    community_network = Network(width='100%', height='750', bgcolor='#222222', font_color='white')
    for node in G.nodes:
        G.nodes[node]['obj'] = None
    community_network.from_nx(G)
    community_network.force_atlas_2based()
    community_network.save_graph(f'./static/temp/{qid}-network-com.html')
    s.gender_network()
    orders = [order for order in s.orders if order != 'None']
    for order in s.orders:
        if order != 'None':
            s.order_network(arg=order)
    return render_template('saint-network-comparison.html', orders=orders, name=s.name, qid=qid)

@app.route('/saint/<qid>/images/<int:page>')
def saint_images(qid, page):
    s = corp.QIDsaints[qid]
    items_per_page = 20
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    artworks = [artwork for artwork in s.artworks if artwork.hasimage]
    total_pages = (len(artworks)//items_per_page) + 1
    artworks = [artwork.list_info() for artwork in artworks[start_index:end_index]]
    return render_template('saint_artworks.html', page=page, name=s.name, artworks=artworks, num_pages=total_pages,
                           current_page=page, qid=qid)

@app.route("/saint/<qid>/image_dump")
def saint_images_dump(qid):
    s = corp.QIDsaints[qid]
    artworks = [artwork for artwork in s.artworks if artwork.hasimage]
    objs = []
    for artwork in artworks:
        objs.append({
            'source': artwork.objectvalue,
            'images': artwork.images
        })
    return render_template('image_dump.html', name=s.name, objs=objs)

@app.route('/artwork/<a>')
def artwork(a):
    a = corp.QIDartworks[a]
    obj = a.info()
    return render_template('artwork.html', obj=obj)


if __name__ == '__main__':
    clean_temp()
    multiprocessing.freeze_support()
    app.run(debug=False)
