import pandas as pd
import pyreadstat
from tqdm import tqdm

from RLMSLogic.extractionHelpers import value_to_label, norm

pathToIndivisuals = '..\\data\\RLMS waves\\r18i_os_82.sav'
pathToHH = '..\\data\\RLMS waves\\r18h_os_71.sav'

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

for __, irow in df.iterrows():

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