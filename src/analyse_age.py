# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np


med = pd.read_csv('data/input/MED_export.csv', sep='\t', index_col='mindat_id')
mineral = pd.read_csv('data/input/tbl_mineral.csv', sep='\t', index_col='mineral_id')
locality_age = pd.read_csv('data/input/tbl_locality_age_cache.csv', error_bad_lines=False, encoding='unicode_escape',
                           sep='\t', index_col='mineral_id')

med = med[med.bottom_level == 1]
med['mineral'] = med['MED_minerals_all'].str.split(',')
med = med.explode('mineral')

mineral_locality = locality_age.merge(mineral, how='left', left_index=True, right_index=True)
mineral_age = med.merge(mineral_locality, how='left', left_index=True, right_index=True)

abellaite = mineral_age.loc[mineral_age.mineral_name == 'Abellaite']
