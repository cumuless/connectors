import os
import requests
from logger import get_logger

logger = get_logger()

ZILLIZ_API_URL = os.getenv('ZILLIZ_API_URL')
ZILLIZ_API_KEY = os.getenv('ZILLIZ_API_KEY')

async def store_embedding(embedding):
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': f'Bearer {ZILLIZ_API_KEY}'
    # }
    
    # response = requests.post(f"{ZILLIZ_API_URL}/vectors", headers=headers, json=embedding)
    # if response.status_code == 200:
    #     logger.info("Embedding stored successfully")
    # else:
    #     logger.error(f"Failed to store embedding: {response.text}")
    logger.info('stored something in vectordb')
    print('stored in vdb')
    # print(embedding)
