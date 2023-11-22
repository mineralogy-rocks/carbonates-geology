# -*- coding: UTF-8 -*-
import pandas as pd


archean = pd.read_csv('data/output/data/mineral_locality_archean.csv', sep=',', encoding='utf-8')
proterozoic = pd.read_csv('data/output/data/mineral_locality_proterozoic.csv', sep=',', encoding='utf-8')
phanerozoic = pd.read_csv('data/output/data/mineral_locality_phanerozoic.csv', sep=',', encoding='utf-8')

periods = (
    ('Archean', archean),
    ('Proterozoic', proterozoic),
    ('Phanerozoic', phanerozoic)
)

stats_per_period = pd.DataFrame()
for name, period in periods:
    _ = period.drop_duplicates(subset=['mineral'], keep='first')
    _stats = _.groupby('rarity_group').size().reset_index(name='counts')
    _stats['period'] = name
    stats_per_period = stats_per_period.append(_stats)

stats_per_period.to_csv('data/output/data/rarity_stats_per_period.csv', sep=',', encoding='utf-8')

_ = archean.loc[archean['rarity_group'] == 'Generally Rare']
_ = phanerozoic.loc[phanerozoic['rarity_group'] == 'Endemic']
_ = proterozoic.loc[proterozoic['rarity_group'] == 'Endemic']

