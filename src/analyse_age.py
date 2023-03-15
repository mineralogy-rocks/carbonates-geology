# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

from src.connectors import Connection
from src.utils import (
    parse_mindat, classify_by_rarity
)

api = Connection()
api.connect_db()
api.fetch_tables()
api.get_minerals()
api.disconnect_db()

localities = pd.read_csv('data/input/mindat_locs.csv')
localities = parse_mindat(localities)
_locality_age = pd.read_csv('data/input/tbl_locality_age_cache_alt.csv', on_bad_lines='skip', encoding='unicode_escape',
                            sep='\t', index_col='mindat_id')

_locality_age = _locality_age.loc[_locality_age.at_locality == 1]
_locality_age = _locality_age.loc[_locality_age.is_remote == 0]
mineral_locality_tuple = _locality_age.merge(api.carbonates_mindat, how='inner', left_on='mineral_display_name',
                                             right_on='name')
mineral_locality_tuple.rename(columns={'mineral_display_name': 'mineral'}, inplace=True)
mineral_locality_tuple.set_index('id', inplace=True)

rarity_groups = classify_by_rarity(localities)
del localities

mineral_locality_tuple = mineral_locality_tuple.merge(rarity_groups[['rarity_group']], how='left', left_on='mineral',
                                                      right_index=True)

# mineral/locality Archean
archean = mineral_locality_tuple[mineral_locality_tuple.max_age >= 2500]
archean = archean[['mineral', 'min_age', 'max_age', 'locality_longname', 'rarity_group']].sort_values(by=['mineral',
                                                                                                          'min_age','max_age'])
archean_report = archean.groupby('mineral').agg(min_age=pd.NamedAgg(column="min_age", aggfunc="min"),
                                                max_age=pd.NamedAgg(column="max_age", aggfunc="max"))
archean.to_csv('data/output/data/mineral_locality_archean.csv', sep=',', encoding='utf-8')
archean_report.to_csv('data/output/data/mineral_locality_archean_summary.csv', sep=',', encoding='utf-8')

# mineral/locality Proterozoic
proterozoic = mineral_locality_tuple[(mineral_locality_tuple.max_age >= 538) & (mineral_locality_tuple.max_age < 2500)]
proterozoic = proterozoic[['mineral', 'min_age', 'max_age', 'locality_longname', 'rarity_group']].sort_values(by=['mineral',
                                                                                                                  'min_age',
                                                                                                                  'max_age'])
proterozoic_report = proterozoic.groupby('mineral').agg(min_age=pd.NamedAgg(column="min_age", aggfunc="min"),
                                                        max_age=pd.NamedAgg(column="max_age", aggfunc="max"))
proterozoic.to_csv('data/output/data/mineral_locality_proterozoic.csv', sep=',', encoding='utf-8')
proterozoic_report.to_csv('data/output/data/mineral_locality_proterozoic_summary.csv', sep=',', encoding='utf-8')

# mineral/locality Phanerozoic
phanerozoic = mineral_locality_tuple[(mineral_locality_tuple.max_age >= 0) & (mineral_locality_tuple.max_age < 538)]
phanerozoic = phanerozoic[['mineral', 'min_age', 'max_age', 'locality_longname', 'rarity_group']].sort_values(by=['mineral',
                                                                                                                  'min_age',
                                                                                                                  'max_age'])
phanerozoic_report = phanerozoic.groupby('mineral').agg(min_age=pd.NamedAgg(column="min_age", aggfunc="min"),
                                                        max_age=pd.NamedAgg(column="max_age", aggfunc="max"))
phanerozoic.to_csv('data/output/data/mineral_locality_phanerozoic.csv', sep=',', encoding='utf-8')
phanerozoic_report.to_csv('data/output/data/mineral_locality_phanerozoic_summary.csv', sep=',', encoding='utf-8')


sns.set_theme(style="ticks")
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
sns.despine(fig)

g = sns.histplot(
    mineral_locality_tuple.sort_values(by='rarity_group'),
    x="max_age",
    hue='rarity_group',
    palette="rocket",
    edgecolor=".3",
    ax=ax,
    linewidth=.5,
    binwidth=30,
    multiple="stack",
)
g.legend_.set_title('Rarity Groups')
plt.xlabel('Age (Ma)')
plt.ylabel('Mineral count')

ax_ = ax.twinx()
sns.kdeplot(
    data=mineral_locality_tuple,
    x="max_age",
    palette=['darkblue',],
    ax=ax_,
    linewidth=.2,
    legend=False
)
ax.invert_xaxis()
plt.axis('off')
plt.savefig(f"data/output/plots/timeline.jpeg", dpi=300, format='jpeg')
plt.close()


rarity_stats = rarity_groups.groupby('rarity_group').agg(mineral_count=pd.NamedAgg(column="mineral_name", aggfunc="count"))
rarity_stats['percentage_from_carbonates'] = rarity_stats.mineral_count / np.sum(rarity_stats.mineral_count) * 100
rarity_stats['percentage_from_all'] = np.nan
rarity_stats.loc[rarity_stats.index == 'Endemic', 'percentage_from_all'] = \
    rarity_stats.loc[rarity_stats.index == 'Endemic', 'mineral_count'] / 1232 * 100
rarity_stats.loc[rarity_stats.index == 'Generally Rare', 'percentage_from_all'] = \
    rarity_stats.loc[rarity_stats.index == 'Generally Rare', 'mineral_count'] / 4018 * 100
rarity_stats.loc[rarity_stats.index == 'Transitional', 'percentage_from_all'] = \
    rarity_stats.loc[rarity_stats.index == 'Transitional', 'mineral_count'] / 2153 * 100
rarity_stats.loc[rarity_stats.index == 'Ubiquitous', 'percentage_from_all'] = \
    rarity_stats.loc[rarity_stats.index == 'Ubiquitous', 'mineral_count'] / 701 * 100
rarity_stats.to_csv('data/output/data/rarity_stats.csv')

stats = pd.DataFrame(mineral_age.groupby('mineral')['mineral'].count())
stats.rename(columns={'mineral': 'counts'}, inplace=True)
stats.sort_values('counts', ascending=False, inplace=True)
stats.to_csv('data/output/data/mineral_age_counts.csv')