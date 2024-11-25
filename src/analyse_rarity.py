# -*- coding: UTF-8 -*-
import pandas as pd

from src.choices import AGE_THRESHOLD, PERIODS
from src.utils import get_outliers


archean = pd.read_csv('data/output/data/mineral_locality_archean.csv', sep=',', encoding='utf-8')
proterozoic = pd.read_csv('data/output/data/mineral_locality_proterozoic.csv', sep=',', encoding='utf-8')
phanerozoic = pd.read_csv('data/output/data/mineral_locality_phanerozoic.csv', sep=',', encoding='utf-8')

data = pd.concat([archean, proterozoic, phanerozoic])
data = get_outliers(data, 'max_age', threshold=AGE_THRESHOLD)
data = data.loc[~data['is_outlier']]

stats_per_period = pd.DataFrame()
for name, min, max in PERIODS:
    _ = data.loc[(data['max_age'] <= min) & (data['max_age'] >= max)]
    _ = _.drop_duplicates(subset=['mineral'], keep='first')
    _stats = _.groupby('rarity_group').size().reset_index(name='counts')
    _stats['period'] = name
    stats_per_period = stats_per_period.append(_stats)

stats_per_period.to_csv('data/output/data/rarity_stats_per_period.csv', sep=',', encoding='utf-8', index=False)

_ = archean.loc[archean['rarity_group'] == 'Generally Rare']
_ = phanerozoic.loc[phanerozoic['rarity_group'] == 'Endemic']
_ = proterozoic.loc[proterozoic['rarity_group'] == 'Endemic']


# Get data for timeline, sum window by 30Ma
timeline = pd.concat([archean, proterozoic, phanerozoic])
timeline = timeline.groupby(['max_age']).size().reset_index(name='counts')
timeline['max_age'] = timeline['max_age'].apply(lambda x: int(x/30)*30)
timeline = timeline.groupby(['max_age']).sum().reset_index()
timeline.to_csv('data/output/data/timeline.csv', sep=',', encoding='utf-8')