import pandas as pd
import pyreadstat
from tqdm import tqdm

from RLMSLogic.extractionHelpers import value_to_label, norm

pathToIndivisuals = '..\\data\\RLMS waves\\r24i_os_82.sav'
pathToHH = '..\\data\\RLMS waves\\r24h_os_82.sav'

df, meta = pyreadstat.read_sav(
    pathToIndivisuals,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)

dfhh, metahh = pyreadstat.read_sav(
    pathToHH,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)

with open('column_names_individuals_sav24.txt', 'w', encoding='utf-8') as f:
    for col in df.columns:
        f.write(col + '\n')

with open('column_names_households_sav24.txt', 'w', encoding='utf-8') as f:
    for col in dfhh.columns:
        f.write(col + '\n')

with open('questions_households_sav24.txt', 'w', encoding='utf-8') as f:
    row = dfhh.iloc[0]
    for var, raw in row.items():
        question = meta.column_names_to_labels.get(var, var)
        f.write(f'Code = {var}, Question = {question}' + '\n')

a = dfhh.columns
for x in range(1, 58):
    s0 = f'ne1_{x}a'
    s1 = f'ne1_{x}c'

    print(f'{s1}: {dfhh[s0][0]} - {dfhh[s1][0]}' )

    #print(metahh.variable_value_labels[s])
    #print(metahh.column_names_to_labels[s])
    #print(meta.value_labels[s])

for __, irow in df.iterrows():
    continue
    id = irow['nid_h']

    matched = False
    for _, hhrow in dfhh.iterrows():
        hhId = hhrow['nid_h']
        if id == hhId:
            print(f'Id = {id} matched, member id = {irow['nid_i']}, unique member = {irow['idind']}')
            print(f'Individual: {irow['region']}, {irow['psu']}, {irow['site']}, family # {irow['nh3']}, individual # {irow['nh4']}')
            print(f'Household: answering {hhrow['na8']}, {hhrow['region'], hhrow['psu'], hhrow['site']}, членов семьи {hhrow['n_nfm']}, family # {hhrow['na3']}')

            members = hhrow['n_nfm']
            print(f'1 member: {hhrow['nidind1']}')
            if members >= 2:
                print(f'2 member: {hhrow['nidind2']}')
            if members >= 3:
                print(f'3 member: {hhrow['nidind3']}')
            if members >= 4:
                print(f'4 member: {hhrow['nidind4']}')

            matched = True

    print(f'Matched hh and ind: {matched}')