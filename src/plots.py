# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from src import choices as choices


archean = pd.read_csv('data/output/data/mineral_locality_archean.csv', sep=',', encoding='utf-8')
proterozoic = pd.read_csv('data/output/data/mineral_locality_proterozoic.csv', sep=',', encoding='utf-8')
phanerozoic = pd.read_csv('data/output/data/mineral_locality_phanerozoic.csv', sep=',', encoding='utf-8')

periods = (
    ('Archean', archean),
    ('Proterozoic', proterozoic),
    ('Phanerozoic', phanerozoic)
)

# single bar chart per period: counts of top-10 carbonates
for name, period in periods:
    _counts = period[period.mineral.isin(choices.TOP_10_CARBONATES)].sort_values(by='mineral')
    sns.set_theme(style="ticks")
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    sns.despine(fig)
    g = sns.histplot(
        _counts,
        x="max_age",
        hue="mineral",
        palette="Paired",
        edgecolor=".3",
        ax=ax,
        linewidth=.5,
        binwidth=30,
        multiple="stack",
    )
    plt.xlabel('Age (Ma)')
    plt.ylabel('Mineral counts')
    plt.legend(handles=g.legend_.legendHandles, labels=choices.TOP_10_CARBONATES, fontsize='small', fancybox=False, framealpha=0.2)
    plt.tight_layout()
    ax.invert_xaxis()
    ax.set_title(f"Counts of top-10 carbonates in {name}", fontsize='small')
    plt.savefig(f"data/output/plots/{name.lower()}_counts.jpeg", dpi=300, format='jpeg')
    plt.close()


# single bar chart per period: proportions of top-10 carbonates from all carbonates within specific age
_period = archean.groupby(['max_age', 'mineral']).size().reset_index(name='counts')
_period['proportion'] = _period.groupby('max_age')['counts'].apply(lambda x: x / float(x.sum())) * 100
_colors = sns.color_palette("Paired")

sns.set_theme(style="ticks")
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
sns.despine(fig)

sns.barplot(
    data=_period[_period.mineral.isin(choices.TOP_10_CARBONATES)].sort_values(by='mineral'),
    x="max_age",
    y="proportion",
    palette=_colors,
    hue="mineral",
    edgecolor=".3",
    ax=ax,
    dodge=True,
)
# g.set(xticks=np.arange(2500, 4600, 500))
plt.xlabel('Age (Ma)')
plt.ylabel('% of all carbonates')
plt.tight_layout()
plt.legend(handles=g.legend_.legendHandles, labels=choices.TOP_10_CARBONATES, fontsize='small', fancybox=False, framealpha=0.2)
ax.invert_xaxis()
ax.set_title(f"Proportions of top-10 carbonates in Archean", fontsize='small')
plt.savefig(f"data/output/plots/archean_proportions.jpeg", dpi=300, format='jpeg')
plt.close()
