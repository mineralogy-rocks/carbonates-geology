# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np


def prepare_minerals(minerals):
    minerals_ = minerals.copy()
    minerals_ = minerals_.replace(0, np.nan)

    minerals_.description = minerals_.description.replace(r"", np.nan)
    minerals_.formula = minerals_.formula.replace(r"", np.nan)

    return minerals_


def parse_mindat(data):
    """ Clean and transform mindat data  """

    data.replace('\\N', np.nan, inplace=True)

    data.rename(columns={'loccount': 'locality_counts'}, inplace=True)

    data['imayear'].replace('0', np.nan, inplace=True)

    locs_md = data[['name', 'imayear', 'yeardiscovery', 'yearrruff', 'locality_counts']]
    locs_md.loc[:, 'imayear'] = pd.to_numeric(locs_md['imayear'])
    locs_md.loc[:, 'yearrruff'] = pd.to_numeric(locs_md['yearrruff'])

    locs_md.loc[:, 'locality_counts'] = pd.to_numeric(locs_md['locality_counts'])
    locs_md.loc[~locs_md['yeardiscovery'].str.match(r'[0-9]{4}', na=False), 'yeardiscovery'] = np.nan
    locs_md.loc[:, 'yeardiscovery'] = pd.to_numeric(locs_md['yeardiscovery'])

    locs_md.rename(columns={'yeardiscovery': 'discovery_year'}, inplace=True)

    locs_md.set_index('name', inplace=True)

    return locs_md


def classify_by_rarity(data):
    data['rarity_group'] = np.nan

    data.loc[(data['locality_counts'] <= 4), 'rarity_group'] = 'Rare'
    data.loc[data['locality_counts'] <= 16, 'rarity_group'] = 'Generally Rare'
    data.loc[(data['locality_counts'] == 1), 'rarity_group'] = 'Endemic'

    data.loc[(data['locality_counts'] > 4) & (data['locality_counts'] <= 70), 'rarity_group'] = 'Transitional'

    data.loc[(data['locality_counts'] > 70), 'rarity_group'] = 'Ubiquitous'

    return data