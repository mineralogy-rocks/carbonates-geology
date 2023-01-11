# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

from src.connectors import Connection
from src.utils import (
    parse_mindat, split_by_rarity_groups, classify_by_rarity
)

api = Connection()
api.connect_db()
api.fetch_tables()
api.get_minerals()
api.disconnect_db()

med = pd.read_csv('data/input/MED_export.csv', sep='\t')
mineral = pd.read_csv('data/input/tbl_mineral.csv', sep='\t', index_col='mineral_id')
localities = pd.read_csv('data/input/mindat_locs.csv')
locality_age = pd.read_csv('data/input/tbl_locality_age_cache.csv', error_bad_lines=False, encoding='unicode_escape',
                           sep='\t', index_col='mindat_id')

mineral = mineral.merge(api.carbonates_mindat, how='inner', left_on='mineral_name', right_on='name')
mineral.set_index('id', inplace=True)

localities = parse_mindat(localities)

locality_age = locality_age.loc[(~locality_age.max_age.isna()) | (~locality_age.min_age.isna())]
locality_age.sort_index(inplace=True)

med = med[med.bottom_level == 1]
med['mineral'] = med['MED_minerals_all'].str.split(',')
med = med.explode('mineral')
med = med[['mindat_id', 'mineral',]]
med = med.merge(mineral, how='inner', left_on='mineral', right_on='mineral_name')
med.set_index('mindat_id', inplace=True)
med.sort_index(inplace=True)

mineral_age = med.merge(locality_age, how='inner', left_index=True, right_index=True)
mineral_age.drop_duplicates(subset=['mineral', 'max_age', 'min_age'], inplace=True)
mineral_age.sort_values('mineral', inplace=True)

localities = localities.merge(mineral, how='inner', left_index=True, right_on='mineral_name')
rarity_groups = classify_by_rarity(localities)
del localities

mineral_age = mineral_age.merge(rarity_groups, how='left', left_on='mineral_name', right_on='mineral_name')

sns.set_theme(style="ticks")
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
sns.despine(fig)

g = sns.histplot(
    mineral_age,
    x="max_age",
    hue='rarity_group',
    palette="rocket",
    edgecolor=".3",
    ax=ax,
    linewidth=.5,
)
g.legend_.set_title('Rarity Groups')
plt.xlabel('Age (Ma)')
plt.ylabel('Mineral count')

ax_ = ax.twinx()
sns.kdeplot(
    data=mineral_age,
    x="max_age",
    palette=['darkblue',],
    ax=ax_,
    linewidth=.2,
    legend=False
)
ax.invert_xaxis()
plt.axis('off')
plt.savefig(f"data/output/plots/mineral_max_age.jpeg", dpi=300, format='jpeg')
plt.close()


stats = pd.DataFrame(mineral_age.groupby('mineral')['mineral'].count())
stats.rename(columns={'mineral': 'counts'}, inplace=True)
stats.sort_values('counts', ascending=False, inplace=True)
stats.to_csv('data/output/data/mineral_age_counts.csv')