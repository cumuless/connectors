import asyncio
import os
from drive_handler import get_and_process_files_content
from embedder import embed_text_chunks, embed_text
from vector_db import store_embedding
from logger import setup_logging, get_logger

interval = 10  # 3 minutes in seconds

setup_logging()  # Initialize logging
logger = get_logger()

def load_env():
    from dotenv import load_dotenv
    load_dotenv()

def process_file_content(content, docId, lastUpdated, access, title, webviewUrl, mime_type):
    chunks = embed_text_chunks(content)

    for chunk in chunks:
        embedding = embed_text(chunk)
        store_embedding(docId, embedding, chunk, lastUpdated, access, title, webviewUrl, mime_type)

async def main():
    # logger.info("Starting Connectors")

    # Step 1: Get and process content from Google Drive
    await get_and_process_files_content(process_file_content)

    # logger.info("Finished processing all files")

async def run_periodically(interval, coroutine):
    while True:
        await coroutine()
        await asyncio.sleep(interval)

if __name__ == "__main__":
    load_env()
    asyncio.run(run_periodically(interval, main))