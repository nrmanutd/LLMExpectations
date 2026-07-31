from pathlib import Path

path = 'Configuration'

bothub_key = Path(f'{path}/bothub_key.txt').read_text(encoding="utf-8")
mlcluster_key = Path(f'{path}/mlcluster_key.txt').read_text(encoding="utf-8")

rlmsToInflationRegionsPath = Path(f'data/rlmsToInflationRegionsMapping.txt')
rlmsToInflationProductsPath = Path(f'data/rlmsToInflationProductsMapping.txt')
rlmsToAverageSalaryRegionsPath = Path(f'data/rlmsToAverageSalaryRegionsMapping.txt')

mrotStatisticsPath = Path(f'data/MROT_history.xlsx')
averageBuyingsDataPath = Path(f'data/Average Buyings Regions 1980_2026.xlsx')
inflationDataPath = Path(f'data/Inflation weekly by regions 2015 - 2026.xlsx')