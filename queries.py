import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON


def update_data():
    get_objects().to_json('./data/2d_objects.json')
    get_saints().to_json('./data/saints.json')


def obj_date_creators():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT DISTINCT ?object (group_concat(DISTINCT ?date; separator=";") as ?dates) (group_concat(DISTINCT ?creator; separator=";") as ?creators)
WHERE
{
  ?object wdt:P571 ?date.
  FILTER (   YEAR(?date) > 500 && YEAR(?date) < 1800  ).
  optional{?object wdt:P170 ?creator.}
  ?object wdt:P31/wdt:P279* wd:Q110304307.
}
GROUP BY ?object ?dates ?creators"""
    user_agent = "SaintAnalyzer/0.0"

    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])
    new = data['object.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID', 'object.value', 'dates.value', 'creators.value']
    data = data[cols]
    data.set_index('QID', inplace=True, drop=True)
    return data


def obj_depictions():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT DISTINCT ?object (group_concat(DISTINCT ?depicts; separator=";") as ?depictions)
    WHERE
    {
      ?object wdt:P571 ?date.
      FILTER (   YEAR(?date) > 500 && YEAR(?date) < 1800  ).
      ?object wdt:P180 ?depicts.
      ?object wdt:P31/wdt:P279* wd:Q110304307.
    }
    GROUP BY ?object ?depictions"""
    user_agent = "SaintAnalyzer/0.0"

    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])
    new = data['object.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID', 'depictions.value']
    data = data[cols]
    data.set_index('QID', inplace=True, drop=True)
    return data


def obj_images():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT DISTINCT ?object (group_concat(DISTINCT ?image; separator=";") as ?images)
WHERE
{
  ?object wdt:P571 ?date.
  FILTER (   YEAR(?date) > 500 && YEAR(?date) < 1800  ).
  ?object wdt:P18 ?image.
  ?object wdt:P31/wdt:P279* wd:Q110304307.
}
GROUP BY ?object ?images"""
    user_agent = "SaintAnalyzer/0.0"

    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])
    new = data['object.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID', 'images.value']
    data = data[cols]
    data.set_index('QID', inplace=True, drop=True)
    return data


def obj_collection():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT DISTINCT ?object (group_concat(DISTINCT ?x; separator=";") as ?collection)
WHERE
{
  ?object wdt:P571 ?date.
  FILTER (   YEAR(?date) > 500 && YEAR(?date) < 1800  ).
  ?object wdt:P195 ?x.
  ?object wdt:P31/wdt:P279* wd:Q110304307.
}
GROUP BY ?object ?collection"""
    user_agent = "SaintAnalyzer/0.0"

    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])
    new = data['object.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID', 'collection.value']
    data = data[cols]
    data.set_index('QID', inplace=True, drop=True)
    return data


def obj_materials():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT DISTINCT ?object (group_concat(DISTINCT ?x; separator=";") as ?materials)
WHERE
{
  ?object wdt:P571 ?date.
  FILTER (   YEAR(?date) > 500 && YEAR(?date) < 1800  ).
  ?object wdt:P186 ?x.
  ?object wdt:P31/wdt:P279* wd:Q110304307.
}
GROUP BY ?object ?materials"""
    user_agent = "SaintAnalyzer/0.0"

    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])
    new = data['object.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID', 'materials.value']
    data = data[cols]
    data.set_index('QID', inplace=True, drop=True)
    return data


def obj_type():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT DISTINCT ?object (group_concat(DISTINCT ?x; separator=";") as ?types)
WHERE
{
  ?object wdt:P571 ?date.
  FILTER (   YEAR(?date) > 500 && YEAR(?date) < 1800  ).
  ?object wdt:P31/wdt:P279* wd:Q110304307.
  ?object wdt:P31 ?x.
}
GROUP BY ?object ?types"""
    user_agent = "SaintAnalyzer/0.0"

    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])
    new = data['object.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID', 'types.value']
    data = data[cols]
    data.set_index('QID', inplace=True, drop=True)
    return data


def obj_genre():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT DISTINCT ?object (group_concat(DISTINCT ?x; separator=";") as ?genres)
WHERE
{
  ?object wdt:P571 ?date.
  FILTER (   YEAR(?date) > 500 && YEAR(?date) < 1800  ).
  ?object wdt:P31/wdt:P279* wd:Q110304307.
  ?object wdt:P136 ?x.
}
GROUP BY ?object ?genres"""
    user_agent = "SaintAnalyzer/0.0"

    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])
    new = data['object.value'].str.split("/", n=-1, expand=True)
    data["QID"] = new[4]
    cols = ['QID', 'genres.value']
    data = data[cols]
    data.set_index('QID', inplace=True, drop=True)
    return data


def obj_creation():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """SELECT DISTINCT ?object (group_concat(DISTINCT ?x; separator=";") as ?creationPlace)
WHERE
{
  ?object wdt:P571 ?date.
  FILTER (   YEAR(?date) > 500 && YEAR(?date) < 1800  ).
  ?object wdt:P1071 ?x.
  ?object wdt:P31/wdt:P279* wd:Q110304307.
}
GROUP BY ?object ?creationPlace"""
    user_agent = "SaintAnalyzer/0.0"

    # set sparql settings
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query wikidata
    results = sparql.query().convert()
    # convert to json pd
    data = pd.json_normalize(results['results']['bindings'])
    new = data['object.value'].str.split("/", n=-1, expand=True)
    cols = ['QID', 'creationPlace.value']
    data["QID"] = new[4]
    data = data[cols]
    data.set_index('QID', inplace=True, drop=True)
    return data


def get_objects():
    dfs = [obj_date_creators(), obj_depictions(), obj_images(), obj_collection(), obj_genre(), obj_materials(),
           obj_type(), obj_creation()]
    data = pd.concat(dfs, axis=1)
    return data


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
GROUP BY ?saintUID ?name ?cannonizationState ?religiousGroup ?religiousOrders ?countryCitizen ?gender ?birthDate ?deathDate ?birthPlace ?deathPlace"""

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
    query = """SELECT  ?saintUID (group_concat(DISTINCT ?bd;separator=";") as ?birthDate)
    (group_concat(DISTINCT ?religious_order;separator=";") as ?deathDate)
    (group_concat(DISTINCT ?religious_order;separator=";") as ?birthPlace)
    (group_concat(DISTINCT ?religious_order;separator=";") as ?deathPlace)
              WHERE{
  ?saintUID  wdt:P411 ?sanctity.
  OPTIONAL {?saintUID wdt:P21 ?gen}
  OPTIONAL{?saintUID wdt:P27 ?count}
  OPTIONAL {?saintUID wdt:P569 ?bd}
  OPTIONAL {?saintUID wdt:P570 ?dd}
  OPTIONAL {?saintUID wdt:P140 ?rel}
  OPTIONAL {?saintUID wdt:P611 ?order}
  OPTIONAL {?saintUID wdt:P19 ?bp}
  OPTIONAL {?saintUID wdt:P20 ?dp}
  SERVICE wikibase:label{
    bd:serviceParam wikibase:language "en".
    ?saintUID rdfs:label ?name.
    ?sanctity rdfs:label ?cannonization_state.
    ?gen rdfs:label ?gender.
    ?count rdfs:label ?country.
    ?rel rdfs:label ?religious_group.
    ?order rdfs:label ?religious_order.
  }
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
