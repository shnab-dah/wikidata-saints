from wikidata.client import Client


def set_axes(fig):
    fig.update_layout(xaxis_title=None)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(showlegend=False)
    return fig


def filter_QID(string):
    string = string.split('/')
    return string[4]


def query_label(qid):
    client = Client()
    try:
        entity = client.get(qid, load=True)
        return str(entity.label)
    except:
        return 'data error'


def query_list(list):
    if list != ['']:
        return ', '.join([query_label(filter_QID(item)) for item in list if list != ['']])
    else:
        return 'No data'

def get_date(obj):
    if obj.dated:
        return obj.date
    else:
        return 2050


def colour_network(G, arg, val):
    if arg == 'gender':
        pass
    elif arg == 'order':
        pass
