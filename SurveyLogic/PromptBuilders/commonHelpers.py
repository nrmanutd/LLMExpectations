def showInflation(inflation: float)->str:
    if inflation is None:
        return 'нет данных'

    return f'{inflation*100: .1f}'
