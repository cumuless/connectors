import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import asyncio
from server.logger import get_logger
from server.vector_db import check_if_updated

logger = get_logger()

# Define the scope
scope = ['https://www.googleapis.com/auth/drive']
service_account_json_key = os.path.join(os.path.dirname(__file__), '..', 'config', 'key.json')

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    filename=service_account_json_key,
    scopes=scope
)

# Initialize the Drive API client
service = build('drive', 'v3', credentials=credentials)

async def download_file(file_id, mime_type):
    try:
        if mime_type == 'application/vnd.google-apps.document':
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            request = service.files().export_media(fileId=file_id, mimeType='text/csv')
        elif mime_type == 'application/vnd.google-apps.presentation':
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
        else:
            return None
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return fh.read().decode('utf-8')
    except HttpError as error:
        logger.error(f"An error occurred while retrieving content: {error}")
        return None

async def get_and_process_files_content(process_file_callback, max_concurrent_downloads=30):
    # logger.info("Getting Files from Google Drive")
    results = service.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, webViewLink, permissions)",
        orderBy="modifiedTime desc"
    ).execute()

    items = results.get('files', [])
    nextPageToken = results.get('nextPageToken', None)

    while nextPageToken:
        additional_results = service.files().list(
            pageSize=10,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, webViewLink, permissions)",
            orderBy="modifiedTime desc",
            pageToken=nextPageToken
        ).execute()
        items.extend(additional_results.get('files', []))
        # logger.info(f"Found {len(items)} items")

        if len(items) >= 20:
            break

        nextPageToken = additional_results.get('nextPageToken', None)

    semaphore = asyncio.Semaphore(max_concurrent_downloads)  # Limit concurrent downloads

    downloaded = 0
    skipped = 0
    total_items = len(items)
    async def download_and_process(item):
        nonlocal downloaded, skipped

        if(downloaded + skipped == total_items):
            return
        
        updated = check_if_updated(item['id'], item['modifiedTime'])
        if not updated:
            skipped += 1
            # logger.info(f"Downloaded {downloaded}, skipped {skipped} of {total_items} items")
            return
        async with semaphore:
            content = await download_file(item['id'], item['mimeType'])
            if content == None:
                skipped += 1
                # logger.info(f"Downloaded {downloaded}, skipped {skipped} of {total_items} items")
                return
            
            downloaded += 1
            # logger.info(f"Downloaded {downloaded}, skipped {skipped} of {total_items} items")
            
            access_list = []
            for user in item['permissions']:
                try:
                    access_list.append(user['emailAddress'])
                except: 
                    pass
            if content:
                process_file_callback(content, item['id'], item['modifiedTime'], access_list, item['name'], item['webViewLink'], item['mimeType'])

    download_tasks = [download_and_process(item) for item in items]
    await asyncio.gather(*download_tasks)
