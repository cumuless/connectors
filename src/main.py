import asyncio
import os
from drive_handler import get_all_files_content
from embedder import embed_text_chunks, embed_text
from vector_db import store_embedding
from logger import setup_logging, get_logger

def load_env():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.env'))

async def process_file_content(content, semaphore):
    async with semaphore:
        chunks = embed_text_chunks(content)
        embeddings = await asyncio.gather(*[embed_text(chunk) for chunk in chunks])
        await asyncio.gather(*[store_embedding(embedding) for embedding in embeddings])

async def main():
    setup_logging()  # Initialize logging
    logger = get_logger()
    logger.info("Starting Connectors")

    semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent tasks

    # Step 1: Get content from Google Drive
    tasks = []
    async for content in get_all_files_content():
        logger.info("Downloaded a file")
        task = asyncio.create_task(process_file_content(content, semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)
    logger.info("Finished processing all files")

if __name__ == "__main__":
    load_env()
    asyncio.run(main())
