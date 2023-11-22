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

_counts = phanerozoic[phanerozoic.mineral.isin(choices.TOP_10_CARBONATES)].sort_values(by='mineral')
_counts = _counts.groupby(['mineral', 'max_age']).size().reset_index(name='counts').sort_values(by='max_age')
_counts.to_csv('data/output/data/top-10-carbonates-phanerozoic.csv', sep=',', encoding='utf-8', index=False)

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
        hue_order=choices.TOP_10_CARBONATES,
    )
    plt.xlabel('Age (Ma)')
    plt.ylabel('Mineral counts')
    plt.legend(handles=g.legend_.legendHandles, labels=choices.TOP_10_CARBONATES, fontsize='small', fancybox=False, framealpha=0.2)
    plt.tight_layout()
    ax.invert_xaxis()
    ax.set_title(f"Counts of top-10 carbonates in {name}", fontsize='small')
    plt.savefig(f"data/output/plots/{name.lower()}_counts.jpeg", dpi=300, format='jpeg')
    plt.close()


# Kernel Density Plot of top-10 carbonates for all periods
_all = pd.concat([archean, proterozoic, phanerozoic])
_colors = sns.color_palette("Paired")
sns.set_theme(style="ticks")
fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
sns.despine(fig)
sns.kdeplot(
    data=_all[_all.mineral.isin(choices.TOP_10_CARBONATES)].sort_values(by='mineral'),
    x="max_age",
    palette=_colors,
    hue="mineral",
    ax=ax,
    cut=0,
    linewidth=0.4,
    multiple="stack",
)
plt.xlabel('Age (Ma)')
plt.ylabel('Density')
plt.tight_layout()
plt.legend(
    handles=g.legend_.legendHandles,
    labels=choices.TOP_10_CARBONATES,
    fontsize='small',
    fancybox=False,
    framealpha=0.2,
    loc='upper left',
)
ax.invert_xaxis()
ax.set_title(f"Kernel Density Estimates of top-10 carbonates", fontsize='small')
plt.savefig(f"data/output/plots/top-10_density.jpeg", dpi=300, format='jpeg')
plt.close()


# Regression plots showing the Proportion of every top-10 mineral from all carbonates
_all = pd.concat([archean, proterozoic, phanerozoic])
_all = _all.groupby(['max_age', 'mineral']).size().reset_index(name='counts').sort_values(by='mineral')
_all['proportion'] = _all.groupby('max_age')['counts'].apply(lambda x: x / float(x.sum())) * 100
_all = _all[_all.mineral.isin(choices.TOP_10_CARBONATES)].sort_values(by='mineral')
_colors = sns.color_palette("Paired")

sns.set_theme(style="ticks")
fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
sns.despine(fig)
g = sns.lmplot(
        data=_all,
        x="max_age",
        y="proportion",
        col="mineral",
        hue="mineral",
        palette=_colors,
        col_wrap=3,
        height=2,
        lowess=True,
        aspect=1.5,
        legend=False,
        scatter=False,
    )

for mineral, ax in g.axes_dict.items():
    _data = _all[_all.mineral == mineral]
    ax.text(.1, .85, mineral, transform=ax.transAxes, fontweight="normal", fontsize='medium')
    sns.scatterplot(
        data=_data,
        x="max_age",
        y="proportion",
        color='grey',
        edgecolor='grey',
        alpha=0.3,
        ax=ax,
        legend=False,
        size=4,
    )
    ax.invert_xaxis()

g.set_titles("")
g.set_axis_labels("Age (Ma)", "Proportion (%)")
g.tight_layout()
ax.invert_xaxis()
plt.savefig(f"data/output/plots/top-10_proportions.jpeg", dpi=300, format='jpeg')
plt.close()


# Single bar chart with 3 bars showing proportion of top-10 carbonates for each period
archean['period'] = 'Archean'
proterozoic['period'] = 'Proterozoic'
phanerozoic['period'] = 'Phanerozoic'
_all = pd.concat([archean, proterozoic, phanerozoic])
_all = _all[_all.mineral.isin(choices.TOP_10_CARBONATES)].sort_values(by='mineral')
_all = _all.groupby(['period', 'mineral']).size().reset_index(name='counts').sort_values(by='mineral')
_all['proportion'] = _all.groupby('period')['counts'].apply(lambda x: x / float(x.sum())) * 100

_colors = sns.color_palette("Paired")
sns.set_theme(style="ticks")
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
sns.despine(fig)
g = sns.barplot(
    data=_all,
    x="period",
    y="proportion",
    hue="mineral",
    palette=_colors,
    edgecolor=".3",
    ax=ax,
    linewidth=.5,
    hue_order=choices.TOP_10_CARBONATES,
    order=['Archean', 'Proterozoic', 'Phanerozoic'],
)
plt.xlabel('')
plt.ylabel('Percentage (%)')
# plt.legend(handles=g.legend_.legendHandles, labels=choices.TOP_10_CARBONATES, fontsize='small', fancybox=False, framealpha=0.2, loc='upper left')
plt.tight_layout()
ax.set_title(f"Average percentage of top-10 carbonates per period", fontsize='small')
plt.savefig(f"data/output/plots/top-10-proportions-per-period.jpeg", dpi=300, format='jpeg')