import re
from pathlib import Path

from pyreadstat import pyreadstat
from tqdm import tqdm
import pandas as pd

averageBuyingsRegionsPath = 'average_buyings_regions.txt'
buynigsPath = '../data/Average Buyings Regions 1980_2026.xlsx'

df = pd.read_excel(buynigsPath, sheet_name=0, header=None, skiprows=[0, 1])
data_start_row = 0
region_col = 1

regions = set()
for row in range(data_start_row, len(df)):
    val = df.iloc[row, region_col]
    if pd.notna(val):
        region = str(val).strip()
        regions.add(region)

with open(averageBuyingsRegionsPath, 'w', encoding='utf-8') as f:
    for r in regions:
        f.write(f'{r}\n')

mapPath = Path(f'rlmsToAverageBuyingsRegionsMapping.txt')

rlmsMap = dict()
map = dict()
rlmsRegionsSet = set()

with open(mapPath, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for l in lines:
        pattern = r'(\d{1,2})\s*(.*);(.*)$'
        m = re.match(pattern, l.strip())

        number, rlms, infl = m.groups()
        rlmsRegionsSet.add(rlms)

        map[rlms] = infl
        rlmsMap[number] = rlms

for k, v in map.items():
    if v not in regions:
        print(f'Region {v} in map is absent in regions')