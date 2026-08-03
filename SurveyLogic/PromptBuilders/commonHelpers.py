import re
from pathlib import Path


def showInflation(inflation: float)->str:
    if inflation is None:
        return 'нет данных'

    return f'{inflation*100: .1f}'

def loadRlmsGoodsToRosstatGoodsMap(pathes: list[Path]) -> dict[str, str]:

    result = dict[str, str]()
    pattern = r'^[^\s]+'
    for path in pathes:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                key = re.match(pattern, line).group().replace('.', '_').strip()
                value = line.split(';')[1].strip()
                result[key] = value

    return result
