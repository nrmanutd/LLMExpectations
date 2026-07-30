from openai import OpenAI
from Configuration.configuration import bothub_key
import requests
import time


taskFile = 'data/my_tasks.jsonl'
client = OpenAI(
    api_key=bothub_key,
    base_url='https://bothub.chat/api/v2/openai/v1'
)

print('Openai initiated...')
file = client.files.create(
    file=open(taskFile, "rb"),
    purpose="batch"
)
print('File created...')
batchId = file.id
print(f'Batch id: {batchId}') # Сохраните этот ID для следующего шага

batch = client.batches.create(
    input_file_id=str(batchId), # ID из предыдущего шага
    endpoint="/v1/chat/completions",
    completion_window="24h"
)
print(batch)

def get_result():
    response = requests.get(
        "https://api.bothub.chat/openai/v1/files/АЙДИ_ФАЙЛА",
        headers={"Authorization": f"Bearer {bothub_key}"}
    )

    link = response.text
    print(link)
    return link

while(True):
    batch = client.batches.retrieve(batchId)
    print("Текущий статус:", batch.status)

    if batch.status == "completed":
        print("ID готового файла:", batch.output_file_id)
        link = get_result()
        print(link)

    time.sleep(60)

