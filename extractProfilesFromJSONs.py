import shutil
from pathlib import Path

from RLMSLogic.RLMSProfileExtractor import RLMSProfileExtractor
from RLMSLogic.SimpleRLMSProfileConverter import SimpleRLMSProfileConverter

targetDirectory = 'data\\Target profiles temp'
jsonSources = Path('data\\RLMS waves temp')
files = list(jsonSources.rglob("*.zip"))

converter = SimpleRLMSProfileConverter()
extractor = RLMSProfileExtractor(converter)

adultAge = 18

folder = Path(targetDirectory)
if folder.exists():
    shutil.rmtree(folder)  # удаляем папку целиком

folder.mkdir(parents=True, exist_ok=True)  # создаём заново

for f in files:
    waveYear = f.stem
    print(f'Parsing file: {f}, year = {waveYear}')

    targetProfileDirectory = Path(targetDirectory) / f'{waveYear}'
    targetProfileDirectory.mkdir(parents=True, exist_ok=True)

    extract_dir = f.with_suffix('')  # Убираем .zip, получаем имя папки

    # Распаковываем
    shutil.unpack_archive(str(f), str(extract_dir), 'zip')

    extractor.generateAndSaveProfilesFromRLMS(extract_dir, targetProfileDirectory, 100, adultAge)

    shutil.rmtree(extract_dir)
