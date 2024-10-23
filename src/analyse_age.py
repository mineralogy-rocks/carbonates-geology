# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

from src.connectors import Connection
from src import choices as choices
from src.utils import (
    parse_mindat, classify_by_rarity, get_outliers
)
from src.plots import timeline

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
rarity_groups = rarity_groups.loc[rarity_groups.index.isin(api.carbonates_mindat.name.values)]
del localities

rarity_groups = pd.read_csv('data/output/data/rarity_groups.csv', index_col='name')


mineral_locality_tuple = mineral_locality_tuple.merge(rarity_groups[['rarity_group']], how='left', left_on='mineral',
                                                      right_index=True)

# subset rarity by carbonates only and find top 10 most common
carbonates_rarity = rarity_groups.loc[rarity_groups.index.isin(mineral_locality_tuple.mineral.values)]
carbonates_rarity.sort_values(by='locality_counts', ascending=False, inplace=True)
print(carbonates_rarity.head(10))

# find top-10 most endemic minerals discovered before 2000
_temp = rarity_groups.loc[(rarity_groups.rarity_group == 'Endemic') & (rarity_groups.discovery_year < 2000)]

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


# Load data from local pre-processed files
archean = pd.read_csv('data/output/data/mineral_locality_archean.csv', sep=',', encoding='utf-8')
proterozoic = pd.read_csv('data/output/data/mineral_locality_proterozoic.csv', sep=',', encoding='utf-8')
phanerozoic = pd.read_csv('data/output/data/mineral_locality_phanerozoic.csv', sep=',', encoding='utf-8')


# Construct single timelines with outliers
_data = get_outliers(archean, 'max_age', choices.AGE_THRESHOLD)
timeline(_data, 'max_age', '4.2', { 'binwidth': 20 })

_data = get_outliers(proterozoic, 'max_age', choices.AGE_THRESHOLD)
timeline(_data, 'max_age', '4.3', { 'binwidth': 20 })

_data = get_outliers(phanerozoic, 'max_age', choices.AGE_THRESHOLD)
timeline(_data, 'max_age', '4.4', { 'binwidth': 7 })

_full = pd.concat([archean, proterozoic, phanerozoic])
_data = get_outliers(_full, 'max_age', choices.AGE_THRESHOLD)
timeline(_data, 'max_age', '4.1', { 'binwidth': 30 })


# Archean timeline grouped by rarity
sns.set_theme(style="ticks")
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(10, 5), dpi=300)
sns.despine(fig)

for i, rarity_group in enumerate(archean.rarity_group.unique()):
    ax = axes[i]
    data_subset = archean[archean["rarity_group"] == rarity_group]
    g = sns.histplot(data_subset, x="max_age", ax=ax, color="darkslateblue", edgecolor=".3", linewidth=.2, binwidth=50)
    g.set(xticks=np.arange(2500, 4600, 500))
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    ax.invert_xaxis()
    if i == 0:
        ax.set_ylabel("Mineral count")
    else:
        ax.set_ylabel("")
    if i == 1:
        ax.set_xlabel("Age (Ma)")
    else:
        ax.set_xlabel("")
    ax.set_title(rarity_group)

plt.tight_layout()
plt.savefig("data/output/plots/timeline_archean_by_rarity.jpeg", dpi=300, format='jpeg')


# Proterozoic timeline grouped by rarity
sns.set_theme(style="ticks")
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10), dpi=300)
sns.despine(fig)

for i, rarity_group in enumerate(proterozoic.rarity_group.unique()):
    ax = axes[i // 2, i % 2]
    data_subset = proterozoic[proterozoic["rarity_group"] == rarity_group]
    g = sns.histplot(data_subset, x="max_age", ax=ax, color="darkslateblue", edgecolor=".3", linewidth=.2, binwidth=30)
    g.set(xticks=np.arange(0, 2500, 500))
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    ax.invert_xaxis()
    ax.set_xlabel("")
    if i // 2 == 1:
        ax.set_xlabel("Age (Ma)")
    if i % 2 == 0:
        ax.set_ylabel("Mineral count")
    else:
        ax.set_ylabel("")
    ax.set_title(rarity_group)

plt.tight_layout()
plt.savefig("data/output/plots/timeline_proterozoic_by_rarity.jpeg", dpi=300, format='jpeg')

# Phanerozic timeline grouped by rarity
sns.set_theme(style="ticks")
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10), dpi=300)
sns.despine(fig)

for i, rarity_group in enumerate(phanerozoic.rarity_group.unique()):
    ax = axes[i // 2, i % 2]
    data_subset = phanerozoic[phanerozoic["rarity_group"] == rarity_group]
    g = sns.histplot(data_subset, x="max_age", ax=ax, color="darkslateblue", edgecolor=".3", linewidth=.2, binwidth=10)
    g.set(xticks=np.arange(0, 538, 100))
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    ax.invert_xaxis()
    ax.set_xlabel("")
    if i // 2 == 1:
        ax.set_xlabel("Age (Ma)")
    if i % 2 == 0:
        ax.set_ylabel("Mineral count")
    else:
        ax.set_ylabel("")
    ax.set_title(rarity_group)

plt.tight_layout()
plt.savefig("data/output/plots/timeline_phanerozoic_by_rarity.jpeg", dpi=300, format='jpeg')


# timeline faceted for top 10 most common carbonates
_data = mineral_locality_tuple[mineral_locality_tuple.mineral.isin(carbonates_rarity.head(10).index.values)]
_minerals = _data["mineral"].unique()[:10]
_minerals.sort()

sns.set_theme(style="ticks")
fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(20, 10), dpi=300)
sns.despine(fig)

for i, _mineral in enumerate(_minerals):
    ax = axes[i // 5, i % 5]
    data_subset = _data[_data["mineral"] == _mineral]
    g = sns.histplot(data_subset, x="max_age", ax=ax, color="skyblue", edgecolor=".3", linewidth=.2, binwidth=30)
    g.set(xticks=np.arange(0, 4600, 1000))
    ax.invert_xaxis()
    ax.set_xlabel("")
    if i // 5 == 1:
        ax.set_xlabel("Age (Ma)")
    if i % 5 == 0:
        ax.set_ylabel("Mineral count")
    else:
        ax.set_ylabel("")
    ax.set_title(_mineral)

plt.tight_layout()
plt.savefig("data/output/plots/timeline-top-10.jpeg", dpi=300, format='jpeg')
plt.close()


rarity_groups['mineral_name'] = rarity_groups.index
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


# Join references context with minerals and prepare output for Archean outliers
references = pd.read_csv('data/input/MED-ages-reordered-20200131.csv', on_bad_lines='skip', sep='\t')
_locality_age = pd.read_csv('data/input/tbl_locality_age_cache_alt.csv', on_bad_lines='skip', encoding='unicode_escape',
                            sep='\t', index_col='mindat_id')
archean = pd.read_csv('data/output/data/mineral_locality_archean.csv', sep=',', encoding='utf-8')
_archean = get_outliers(archean, 'max_age', AGE_THRESHOLD)
_archean = _data.loc[_data['is_outlier']]
_archean = _archean.merge(_locality_age, how='inner', left_on=['locality_longname', 'mineral'],
                         right_on=['locality_longname', 'mineral_display_name'])

_archean.merge(references, how='inner', left_on='min_age_ref_id', right_on='ref_id')
_ = references.loc[references['mindat_id'] == 27328]