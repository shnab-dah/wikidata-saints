import multiprocessing
from wikidata.client import Client

def get_labels(qids):
    with multiprocessing.Pool(processes=5) as pool:
        returns = pool.map(labels, qids)
    return returns

def labels(qid):
        dict = {}
        client = Client()
        entity = client.get(qid)
        label = entity.label
        dict[qid] = str(label)
        return dict

if __name__ == '__main__':
    pass