import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import time


def update_data():
    get_saints().to_json('./data/saints.json')


def get_saints1():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT  ?saintUID ?name 
    (group_concat(DISTINCT ?x;separator=";") as ?gender)
    (group_concat(DISTINCT ?religious_order;separator=";") as ?religiousOrders)
(group_concat(DISTINCT ?religious_group;separator=";") as ?religiousGroup)
(group_concat(DISTINCT ?country;separator=";") as ?countryCitizen)
(group_concat(DISTINCT ?cannonization_state;separator=";") as ?cannonizationState)
              WHERE{
  ?saintUID  wdt:P411 ?sanctity.
  OPTIONAL {?saintUID wdt:P21 ?gen}
  OPTIONAL{?saintUID wdt:P27 ?count}
  OPTIONAL {?saintUID wdt:P140 ?rel}
  OPTIONAL {?saintUID wdt:P611 ?order}
  SERVICE wikibase:label{
    bd:serviceParam wikibase:language "en".
    ?saintUID rdfs:label ?name.
    ?sanctity rdfs:label ?cannonization_state.
    ?gen rdfs:label ?x.
    ?count rdfs:label ?country.
    ?rel rdfs:label ?religious_group.
    ?order rdfs:label ?religious_order.
  }
}
GROUP BY ?saintUID ?name ?cannonizationState ?religiousGroup ?religiousOrders ?countryCitizen ?gender"""

    user_agent = "SaintAnalyzer/0.0"
    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])

    # add QID
    new = data['saintUID.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID',
            'saintUID.value',
            'name.value',
            'cannonizationState.value',
            'religiousGroup.value',
            'religiousOrders.value',
            'countryCitizen.value',
            'gender.value',
            ]
    data = data[cols]
    data = data.set_index("QID", drop=True)
    return data


def get_saints2():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT  ?saintUID 
    (group_concat(DISTINCT ?bd;separator=";") as ?birthDate)
    (group_concat(DISTINCT ?dd;separator=";") as ?deathDate)
    (group_concat(DISTINCT ?dd;separator=";") as ?birthPlace)
    (group_concat(DISTINCT ?religious_order;separator=";") as ?deathPlace)
              WHERE{
  ?saintUID  wdt:P411 ?sanctity.
  OPTIONAL {?saintUID wdt:P569 ?bd}
  OPTIONAL {?saintUID wdt:P570 ?dd}
  OPTIONAL {?saintUID wdt:P19 ?bp}
  OPTIONAL {?saintUID wdt:P20 ?dp}
}
GROUP BY ?saintUID ?birthDate ?deathDate ?birthPlace ?deathPlace"""

    user_agent = "SaintAnalyzer/0.0"
    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])

    # add QID
    new = data['saintUID.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID',
            'birthDate.value',
            'deathDate.value',
            'birthPlace.value',
            'deathPlace.value'
            ]
    data = data[cols]
    data = data.set_index("QID", drop=True)
    return data


def get_saints():
    dfs = [get_saints1(), get_saints2()]
    data = pd.concat(dfs, axis=1)
    return data


if __name__ == "__main__":
    update_data()
