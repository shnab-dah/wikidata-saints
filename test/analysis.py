import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def uniques(y):
    z = []
    for x in y:
        if x not in z:
            z.append(x)
    return z


def only_saint_depictions(df):
    df['depictions.value'] = df['depictions.value'].str.split(';')
    df = df.explode('depictions.value')
    data = df[df['depictions.value'].isin(saintuids)]
    return data


def plot_hiso(years):
    years.sort()
    # bins by Fred-Diacconis rule
    try:
        q25, q75 = np.percentile(years, [25, 75])
        bin_width = 2 * (q25 - q75) * len(years) ** (-1 / 3)
        bins = round((years[0] - years[len(years) - 1]) / bin_width)
    except:
        bins = 10
    if bins < 10:
        bins = 1
    plt.hist(years, density=False, bins=bins)
    plt.show()


# load datasets
sdf = pd.read_json('../data/saints.json')
saintuids = sdf['saintUID.value'].tolist()
odf = pd.read_json('../data/2d_objects.json')

# only depictions of saints
sodf = only_saint_depictions(odf)

# filter odf to only show objs with saints
objs = uniques(sodf.index.values.tolist())

#reset odf and only show uniques
odf = pd.read_json('../data/2d_objects.json')
odf = odf.loc[objs]

years = []

for dat in odf['dates.value'].tolist():
    dat = dat.split('-')
    years.append(dat[0])
plot_hiso(years)
