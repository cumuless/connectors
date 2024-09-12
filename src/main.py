import asyncio
import os
from drive_handler import get_and_process_files_content
from embedder import embed_text_chunks, embed_text
from vector_db import store_embedding
from logger import setup_logging, get_logger

def load_env():
    from dotenv import load_dotenv
    load_dotenv()

async def process_file_content(content, semaphore, docId, lastUpdated, access, title, webviewUrl, mime_type):
    async with semaphore:
        chunks = embed_text_chunks(content)
        embeddings = await asyncio.gather(*[embed_text(chunk) for chunk in chunks])
        await asyncio.gather(
            *[store_embedding(docId, embedding, chunk, lastUpdated, access, title, webviewUrl, mime_type)
              for chunk, embedding in zip(chunks, embeddings)]
        )

async def main():
    setup_logging()  # Initialize logging
    logger = get_logger()
    logger.info("Starting Connectors")

    semaphore = asyncio.Semaphore(30)  # Limit to 10 concurrent tasks

    async def process_and_store_content(content, docId, lastUpdated, access, title, webviewUrl, mime_type):
        await process_file_content(content, semaphore, docId, lastUpdated, access, title, webviewUrl, mime_type)

    # Step 1: Get and process content from Google Drive
    await get_and_process_files_content(process_and_store_content)

    logger.info("Finished processing all files")

if __name__ == "__main__":
    load_env()
    asyncio.run(main())
