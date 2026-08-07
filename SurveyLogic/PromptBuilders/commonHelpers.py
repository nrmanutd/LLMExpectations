import re
from datetime import datetime, date
from pathlib import Path

months = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }

months_ru = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    0: 'Декабрь'
}

def getDirection(inflation: float):
    if inflation > 0.0:
        return "подорожал"

    if inflation < 0.0:
        return "подешевел"

    return "цена не изменилась"

def getDescriptionMonth(d: date, inflation: float, month: int):
    if inflation is None:
        return ''

    description = getDeltaDescription(d, month)
    direction = getDirection(inflation)
    if abs(inflation) < 0.00001:
        return f"за {description} не изменилась"

    clearInflation = (inflation + 1)**(month/12) - 1
    return f'за {description} {direction} на {showInflation(abs(clearInflation))}% (прошлые {month} месяцев)'

def getDescriptionWeeks(inflation: float, weeks: int):
    if inflation is None:
        return ''

    direction = getDirection(inflation)
    if abs(inflation) < 0.00001:
        return f"за последние {weeks} недель не изменилась"

    clearInflation = (inflation + 1) ** (weeks*7 / 365) - 1
    return f'{direction} на {showInflation(abs(clearInflation))}% за последние {weeks} недель'



def getTop5(map, goods: dict[str, float]):
    rosstatGoods = dict[str, float]()

    for k, v in goods.items():
        if k not in map:
            continue

        g = map[k]
        if g == ('нет соответствующей категории'):
            continue

        if g in rosstatGoods:
            rosstatGoods[g] += v
        else:
            rosstatGoods[g] = v

    top_5 = sorted(rosstatGoods.items(), key=lambda x: x[1], reverse=True)[:min(5, len(rosstatGoods))]
    return [item[0] for item in top_5]

def parseRosstateMonth(value: str, year: int) -> date:
    # Извлекаем день и месяц
    parts = value.replace('на ', '').strip().split()
    day = int(parts[0])
    month_name = parts[1].lower()
    month = months[month_name]

    return datetime(year, month, day).date()

def showInflation(inflation: float)->str:
    if inflation is None:
        return 'нет данных'

    return f'{inflation*100: .1f}'

def getDeltaDescription(d: date, offsetMonth: int):
    finishMonth = (d.month + 12 - 1) % 12
    if offsetMonth == 1:
        return months_ru[finishMonth]

    startMonth = (d.month + 12 - offsetMonth) % 12

    return f'{months_ru[startMonth]} - {months_ru[finishMonth]}'

def getUsdRubDirection(rate):
    if rate == None:
        return None

    if rate > 0:
        return 'обесценился'

    if rate < 0:
        return 'укрепился'

    return 'стабилен'

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
