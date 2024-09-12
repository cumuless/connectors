import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from pprint import pprint

# Define the scope
scope = ['https://www.googleapis.com/auth/drive']

# Path to your service account key file
service_account_json_key = './key.json'

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    filename=service_account_json_key,
    scopes=scope
)

# Initialize the Drive API client
service = build('drive', 'v3', credentials=credentials)

def get_file_content(file_id, mime_type, file_name):
    """Get the text content of a file from Google Drive"""
    if mime_type == 'application/vnd.google-apps.document':
        # Export Google Docs as plain text
        request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    elif mime_type == 'application/vnd.google-apps.spreadsheet':
        # Export Google Sheets as CSV
        request = service.files().export_media(fileId=file_id, mimeType='text/csv')
    elif mime_type == 'application/vnd.google-apps.presentation':
        # Export Google Slides as plain text
        request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    else:
        # Handle other text file types, e.g., plain text or CSV
        return
    
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    fh.seek(0)
    return fh.read().decode('utf-8')

def get_all_files_content():
    """Get the text content of all files from Google Drive"""
    # Call the Drive v3 API
    print("Getting Files from Google Drive")
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
        print("Found " + str(len(items)) + " items")
        nextPageToken = additional_results.get('nextPageToken', None)
    print("Now Downloading Content")
    
    # Retrieve and print content of each file
    for item in items:
        file_id = item['id']
        file_name = item['name']
        mime_type = item['mimeType']
        try:
            content = get_file_content(file_id, mime_type, file_name)
            print(f"Content of {file_name}:\n{content}\n{'-'*40}\n")
        except HttpError as error:
            print(f"An error occurred while retrieving content from {file_name}: {error}")

# Run the function to get all files' content
print("Starting Connectors")
get_all_files_content()
