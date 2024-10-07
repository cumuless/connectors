import os
import requests
from server.logger import get_logger
import json
import http.client

logger = get_logger()

ZILLIZ_API_URL = os.getenv('ZILLIZ_API_URL')
ZILLIZ_API_KEY = os.getenv('ZILLIZ_API_KEY')
url_parts = ZILLIZ_API_URL.split('/')
host = url_parts[2]

print(ZILLIZ_API_URL)
headers = {
    "Authorization": f"Bearer {ZILLIZ_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def store_embedding(docId, embedding, content, lastUpdated, access, title, webviewUrl, mime_type):
    """
    Stores the embedding for the given docId in the vector database.
    """
    delete_all_entried_with_docId(docId)

    # Determine contentType based on mime_type
    contentType = 0
    if mime_type == 'application/vnd.google-apps.document':
        contentType = 1
    elif mime_type == 'application/vnd.google-apps.spreadsheet':
        contentType = 2
    elif mime_type == 'application/vnd.google-apps.presentation':
        contentType = 3


    # Create connection
    conn = http.client.HTTPSConnection(host)

    # Prepare payload
    payload = json.dumps({
        "collectionName": "MainCollection",
        "data": [{
            "docId": docId,
            "embedding": embedding,
            "title": title,
            "content": content,
            "lastUpdated": lastUpdated,
            # "access": access,
            "url": webviewUrl,
            "sourceType": 1,
            "contentType": contentType
        }]
    })

    # Make the request
    conn.request("POST", "/v2/vectordb/entities/insert", payload, headers)

    # Get the response
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    data = json.loads(data)

    # Close connection
    conn.close()

    # Handle the response
    if data['code'] != 0:
        logger.error(f'Failed to store embedding: {data}')
    else:
        logger.info(f'Stored in VectorDB')
    return

def check_if_updated(docId, lastUpdated):
    """
    Checks if the document with the given docId has been updated.
    If updated, drops all documents with the same docId and returns True.
    Otherwise, returns False.
    """
    
    conn = http.client.HTTPSConnection(host)
    payload = f"{{\"collectionName\":\"MainCollection\",\"filter\":\"docId == '{docId}'\"}}"
    conn.request("POST", "/v2/vectordb/entities/query", payload, headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")
    data = json.loads(data)

    if len(data['data']) == 0:
        return True
    
    try:
        if data['data'][0]['lastUpdated'] != lastUpdated:
            delete_all_entried_with_docId(data['data'][0]['docId'])
            logger.info(f"Document {data['data'][0]['url']} was updated")
            return True
    except:
        logger.info("Error when checking if doc has been updated")
    
    return False
    

def delete_all_entried_with_docId(docId):
    conn = http.client.HTTPSConnection(host)

    payload = f"{{\"collectionName\":\"MainCollection\",\"filter\":\"docId == '{docId}'\"}}"

    conn.request("POST", "/v2/vectordb/entities/delete", payload, headers)

    res = conn.getresponse()
    data = res.read()
    
    return