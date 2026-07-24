import re
import shutil
from pathlib import Path

from RLMSLogic.SimpleRLMSProfileConverter import SimpleRLMSProfileConverter
from RLMSLogic.RLMSProfileExtractor import RLMSProfileExtractor

targetDirectory = 'data\\Target profiles'
dtaSources = Path('data\\RLMS waves')
files = list(dtaSources.rglob("*.dta"))
adultAge = 18

start_wave = 33
end_wave = 20          # например, до 20-й волны
start_year = 2024

wavesToYearMap = {wave: start_year - (start_wave - wave) for wave in range(start_wave, end_wave - 1, -1)}
converter = SimpleRLMSProfileConverter()
extractor = RLMSProfileExtractor(converter)

for f in files:
    match = re.search(r'r(\d+)i', f.name)
    waveNumber = int(match.group(1))

    print(f'Parsing file: {f} for wave #{waveNumber}')

    waveYear = wavesToYearMap[waveNumber]
    waveDirectory = dtaSources / f'{waveYear}'
    waveDirectory.mkdir(parents=True, exist_ok=True)

    targetProfileDirectory = Path(targetDirectory) / f'{waveYear}'
    targetProfileDirectory.mkdir(parents=True, exist_ok=True)

    extractor.extractAndSaveRLMSProfiles(f, waveDirectory)
    extractor.generateAndSaveProfilesFromRLMS(waveDirectory, targetProfileDirectory, 100, adultAge)

    archive_base = dtaSources / f'{waveYear}'
    archive_path = shutil.make_archive(str(archive_base), 'zip', str(waveDirectory))
    shutil.rmtree(waveDirectory)

#dta_file = 'data\\r33iall_84_DTA\\r33iall_84.dta'
#dta_file = 'data\\r33i_os_84_DTA\\r33i_os_84.dta'
#out_folder = 'data\\rlms2024_os_profiles'
#profiles_out_folder = 'data\\target_rlms2024_os_based_profiles'