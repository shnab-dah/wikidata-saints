import queries as quer
import saint_query as squer
from corpus import *
from saint import *
from artwork import *
import numpy as np
import pandas as pd
def update_data():
    quer.get_objects().to_json('./data/2d_objects.json')
    squer.get_saints().to_json('./data/saints.json')


if __name__ == "__main__":
    update_data()
