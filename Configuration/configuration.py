from pathlib import Path

path = 'Configuration'

bothub_key = Path(f'{path}/bothub_key.txt').read_text(encoding="utf-8")
mlcluster_key = Path(f'{path}/mlcluster_key.txt').read_text(encoding="utf-8")