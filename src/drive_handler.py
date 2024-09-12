import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import asyncio
from logger import get_logger

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

async def get_all_files_content():
    logger.info("Getting Files from Google Drive")
    results = service.files().list(pageSize=1000, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    nextPageToken = results.get('nextPageToken', None)

    while nextPageToken:
        additional_results = service.files().list(
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=nextPageToken
        ).execute()
        items.extend(additional_results.get('files', []))
        
        logger.info(f"Found {len(items)} items")
        nextPageToken = None # additional_results.get('nextPageToken', None)

    downloaded = 0
    async def download_and_return(item):
        nonlocal downloaded
        content = await download_file(item['id'], item['mimeType'])
        
        downloaded += 1
        logger.info(f'Downloaded {downloaded} of {len(items)} files')
        return content

    download_tasks = [download_and_return(item) for item in items]
    for download_task in asyncio.as_completed(download_tasks):
        content = await download_task
        if content:
            yield content
