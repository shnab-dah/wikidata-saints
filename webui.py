import networkx as nx
import pandas as pd
from flask import Flask, render_template
from corpus import Corpus
from plotly.offline import plot
from pyvis.network import Network

corp = Corpus()
pd.options.plotting.backend = 'plotly'
app = Flask('Saint analysis')
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/corpus')
def corpus():
    G = corp.show_network()
    plot(corp.plot_histo(), filename=f'./static/corpus-histo.html', auto_open=False)
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
    fig1.update_layout(xaxis_title=None)
    fig1.update_layout(yaxis_title=None)
    fig2.update_layout(xaxis_title=None)
    fig2.update_layout(yaxis_title=None)
    fig3.update_layout(xaxis_title=None)
    fig3.update_layout(yaxis_title=None)
    fig1.update_layout(showlegend=False)
    fig2.update_layout(showlegend=False)
    fig3.update_layout(showlegend=False)
    plot(fig1, filename=f'./static/corpus-degcent.html', auto_open=False)
    plot(fig2, filename=f'./static/corpus-clocent.html', auto_open=False)
    plot(fig3, filename=f'./static/corpus-betwcent.html', auto_open=False)
    saints = []
    for saint in corp.saints.values():
        saints.append((saint.QID, saint.name, saint.frequency))
    return render_template('corpus.html', num_artworks=len(corp.artworks), num_saints=len(corp.saints), saints=saints)

@app.route('/corpus/network')
def corp_network():
    G = corp.show_network()
    G2 = Network(width='1450', height='800px', bgcolor='#222222', font_color='white', filter_menu=False)
    G2.from_nx(G)
    G2.force_atlas_2based()
    G2.save_graph('./static/corpus-network.html')
    return render_template('network.html')

@app.route('/saint/<s>')
def saint(s):
    qid = s
    s = corp.QIDsaints[s]
    objs = [x for x in s.artworks]
    artworks = []
    G = s.build_network()
    G2 = Network(width='100%', height='750', bgcolor='#222222', font_color='white')
    G2.from_nx(G)
    G2.force_atlas_2based()
    G2.save_graph(f'./static/{qid}-network.html')
    plot(s.plot_histogram(), filename=f'./static/{qid}-histo.html', auto_open=False)
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
    fig1.update_layout(xaxis_title=None)
    fig1.update_layout(yaxis_title=None)
    fig2.update_layout(xaxis_title=None)
    fig2.update_layout(yaxis_title=None)
    fig3.update_layout(xaxis_title=None)
    fig3.update_layout(yaxis_title=None)
    fig1.update_layout(showlegend=False)
    fig2.update_layout(showlegend=False)
    fig3.update_layout(showlegend=False)
    plot(fig1, filename=f'./static/{qid}-degcent.html', auto_open=False)
    plot(fig2, filename=f'./static/{qid}-clocent.html', auto_open=False)
    plot(fig3, filename=f'./static/{qid}-betwcent.html', auto_open=False)
    for artwork in objs:
        artworks.append((artwork.QID, artwork.objectvalue, artwork.date, artwork.types))
    return render_template('saint.html', name=s.name, url=s.url, objs=artworks, qid=qid)

@app.route('/artwork/<a>')
def artwork(a):
    a = corp.QIDartworks[a]
    name, materials, collection, creators = a.get_english()
    str_materials = ''
    if len(materials) > 1:
        for mat in materials:
            str_materials = str_materials+str(mat)+'; '
    else:
        str_materials = materials[0]
    str_collection = ''
    if len(collection) > 1:
        for col in collection:
            str_collection = str_collection+str(col)+'; '
    else:
        str_collection = collection[0]
    str_creators = ''
    if len(creators) > 1:
        for cre in creators:
            str_creators = str_creators+str(cre)+'; '
    else:
        str_creators = creators[0]
    date = str(a.date)
    return render_template('artwork.html', name=name, date=date, materials=str_materials, collection=str_collection, creators=str_creators, url=a.objectvalue, images=a.images)


if __name__ == '__main__':
    app.run(debug=True)
