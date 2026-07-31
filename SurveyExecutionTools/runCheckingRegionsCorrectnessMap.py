import re
from pathlib import Path

from pyreadstat import pyreadstat
from tqdm import tqdm

inflationRegionsPath = 'inflation_regions.txt'

regions = set()
with open(inflationRegionsPath, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for l in lines:
        regions.add(l.strip())

mapPath = Path(f'rlmsToInflationRegionsMapping.txt')

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

pathToIndivisuals = '../data/RLMS waves/r33i_os_84.dta'

df, meta = pyreadstat.read_dta(
    pathToIndivisuals,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)

print(rlmsMap)
allRlmsLocations = set()

for row_number, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df))):
    id = 'ccid_i'
    regionId = 'psu'
    if regionId in row.index:
        region = rlmsMap[str(int(row[regionId]))]
        allRlmsLocations.add(region)
        print(f'{row[id]}: {row[regionId]}, {region}, {map[region]}')

delta = allRlmsLocations - rlmsRegionsSet

print(f'Delta: {len(delta)}')

print(map)
print(regions)