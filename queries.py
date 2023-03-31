from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd


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


if __name__ == "__main__":
    pass
