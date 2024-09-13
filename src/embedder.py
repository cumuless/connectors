import boto3
from logger import get_logger
import json

logger = get_logger()
client = boto3.client('bedrock-runtime', region_name='us-east-1')

def embed_text_chunks(content, chunk_size=200):
    words = content.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def embed_text(chunk):
    # Assuming you have a method to get AWS Bedrock client
    input_payload = json.dumps({"inputText": chunk, "dimensions": 1024})
    try:
        response = client.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            body=input_payload,
            contentType='application/json'
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            response_body = response['body'].read().decode('utf-8')
            response_json = json.loads(response_body)
            logger.info(f'Embedded Text!')
            return response_json.get('embedding')
        else:
            logger.info(f"Failed to get embedding: {response}")
            return None
    except Exception as e:
        logger.info(f"Error embedding text: {e}")
        return None