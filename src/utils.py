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

    ## Don't have any clue why mindat keeps `0` in imayear column and mixes dtypes in others (?!)

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


def split_by_rarity_groups(data):
    r = data.loc[(data['locality_counts'] <= 4)]
    re_rr_tr = data.loc[data['locality_counts'] <= 16]
    re_true = data.loc[
        ~((data['discovery_year'] > 2000) & (data['locality_counts'] == 1)) & (data['locality_counts'] == 1)]
    re = data.loc[(data['locality_counts'] == 1)]
    rr = data.loc[(data['locality_counts'] <= 4) & (data['locality_counts'] >= 2)]

    t = data.loc[(data['locality_counts'] > 4) & (data['locality_counts'] <= 70)]
    tr = data.loc[(data['locality_counts'] > 4) & (data['locality_counts'] <= 16)]
    tu = data.loc[(data['locality_counts'] > 16) & (data['locality_counts'] <= 70)]

    u = data.loc[(data['locality_counts'] > 70)]
    tu_u = data.loc[(data['locality_counts'] > 16)]

    r.set_index('mineral_name', inplace=True)
    re.set_index('mineral_name', inplace=True)
    rr.set_index('mineral_name', inplace=True)
    re_rr_tr.set_index('mineral_name', inplace=True)
    re_true.set_index('mineral_name', inplace=True)
    t.set_index('mineral_name', inplace=True)
    tr.set_index('mineral_name', inplace=True)
    tu.set_index('mineral_name', inplace=True)
    u.set_index('mineral_name', inplace=True)
    tu_u.set_index('mineral_name', inplace=True)

    r.sort_index(inplace=True)
    re.sort_index(inplace=True)
    rr.sort_index(inplace=True)
    re_rr_tr.sort_index(inplace=True)
    re_true.sort_index(inplace=True)
    t.sort_index(inplace=True)
    tr.sort_index(inplace=True)
    tu.sort_index(inplace=True)
    u.sort_index(inplace=True)
    tu_u.sort_index(inplace=True)

    return r, re_rr_tr, re_true, re, rr, t, tr, tu, u, tu_u


def classify_by_rarity(data):
    data['rarity_group'] = np.nan

    data.loc[(data['locality_counts'] <= 4), 'rarity_group'] = 'Rare'
    data.loc[data['locality_counts'] <= 16, 'rarity_group'] = 'Generally Rare'
    data.loc[(data['locality_counts'] == 1), 'rarity_group'] = 'Endemic'

    data.loc[(data['locality_counts'] > 4) & (data['locality_counts'] <= 70), 'rarity_group'] = 'Transitional'

    data.loc[(data['locality_counts'] > 70), 'rarity_group'] = 'Ubiquitous'

    return data