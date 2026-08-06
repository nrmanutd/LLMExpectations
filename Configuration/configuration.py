from pathlib import Path

path = 'Configuration'

bothub_key = Path(f'{path}/bothub_key.txt').read_text(encoding="utf-8")
bothubUrl = 'https://openai.bothub.chat/v1'

mlcluster_key = Path(f'{path}/mlcluster_key.txt').read_text(encoding="utf-8")
mlclusterUrl = 'https://litellm.mlcluster.ru'

rlmsToInflationRegionsPath = Path(f'data/rlmsToInflationRegionsMapping.txt')
rlmsToInflationProductsPath = Path(f'data/rlmsToInflationProductsMapping.txt')
rlmsToAverageSalaryRegionsPath = Path(f'data/rlmsToAverageSalaryRegionsMapping.txt')

mrotStatisticsPath = Path(f'data/MROT_history.xlsx')
averageBuyingsDataPath = Path(f'data/Average Buyings Regions 1980_2026.xlsx')
#inflationDataPath = Path(f'data/Inflation weekly by regions 2015 - 2026.xlsx')
inflationDataPath = Path(f'data/Monthly Inflation for goods and services in regions_2015_2026_v1.xlsx')

inflation20092014DataPath = Path(f'data/Monthly Inflation for goods and services in regions_2009_2014_v0.xlsx')
inflation20152020DataPath = Path(f'data/Monthly Inflation for goods and services in regions_2015_2020_v0.xlsx')
inflation20212026DataPath = Path(f'data/Monthly Inflation for goods and services in regions_2021_2026_v0.xlsx')

years20092014 = set(range(2009, 2015))
years20152020 = set(range(2015, 2021))
years20212026 = set(range(2021, 2027))

regularGoods = Path(f'data/rlms_regular_goods_map.txt')
durableGoods = Path(f'data/rlms_durable_goods_map.txt')
services = Path(f'data/rlms_services_map.txt')

weeklyRegularGoods = Path(f'data/rlmsWeeklyRegularGoods.txt')
weeklyDurableGoods = Path(f'data/rlmsWeeklyDurableGoods.txt')
weeklyServices = Path(f'data/rlmsWeeklyServices.txt')

inflationSurveysDates = Path(f'data/ExpectedInflationSurveysDates.xlsx')
weeklyInflationDataPath = Path(f'data/Nedel_ipc.xlsx')