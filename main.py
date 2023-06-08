import libtorrent as lt

import time

import sys

import os

from google.oauth2 import service_account

from googleapiclient.discovery import build

from googleapiclient.errors import HttpError

from googleapiclient.http import MediaFileUpload

# Download files using magnet URLs

def download_files(magnet_urls, save_path):

    ses = lt.session()

    handles = []

    for magnet_url in magnet_urls:

        info = lt.parse_magnet_uri(magnet_url)

        params = {

            'save_path': save_path,

            'storage_mode': lt.storage_mode_t.storage_mode_sparse

        }

        handle = lt.add_magnet_uri(ses, magnet_url, params)

        handles.append(handle)

    print("Downloading files...")

    while any(handle.status().state != lt.torrent_status.seeding for handle in handles):

        time.sleep(1)

    print("Download complete.")

    return [handle.torrent_file().name() for handle in handles]

def create_folder(service, folder_name, parent_id=None):

    file_metadata = {

        'name': folder_name,

        'mimeType': 'application/vnd.google-apps.folder'

    }

    if parent_id:

        file_metadata['parents'] = [parent_id]

    folder = service.files().create(body=file_metadata, fields='id').execute()

    return folder['id']

def upload_file_to_drive(service, file_path, folder_id):

    file_metadata = {

        'name': os.path.basename(file_path),

        'parents': [folder_id]

    }

    media = MediaFileUpload(file_path, resumable=True)

    try:

        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        print(f'File ID: "{file.get("id")}".')

    except HttpError as error:

        print(f'An error occurred: {error}')

        file = None

# Upload files to Google Drive

def upload_files(file_paths, folder_id):

    # Set up Google Drive API client

    SCOPES = ['https://www.googleapis.com/auth/drive']

    SERVICE_ACCOUNT_FILE = 'serviceaccount.json'

    credentials = service_account.Credentials.from_service_account_file(

        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials, static_discovery=False)

    # Upload files

    for file_path in file_paths:

        if os.path.isdir(file_path):

            new_folder_id = create_folder(service, os.path.basename(file_path), folder_id)

            for root, _, files in os.walk(file_path):

                for file in files:

                    file_full_path = os.path.join(root, file)

                    upload_file_to_drive(service, file_full_path, new_folder_id)

        else:

            upload_file_to_drive(service, file_path, folder_id)

if __name__ == '__main__':

    magnet_urls = [

        'magnet:?xt=urn:btih:C315422FBF93E29A3171A3BBB381D012D531C414&dn=Cruel.Summer.S02E01.WEB.x264-PHOENiX&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.birkenwald.de%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fopentor.org%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.dler.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fuploads.gamecoast.net%3A6969%2Fannounce&tr=https%3A%2F%2Ftracker.foreverpirates.co%3A443%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fcoppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.zer0day.to%3A1337%2Fannounce'

    ]

    save_path = 'downloads'

    folder_id = '1MZcJ92O2rlVSMEQHtw5_QRThq3Y7LZCT'

    downloaded_files = download_files(magnet_urls, save_path)

    file_paths = [os.path.join(save_path, file) for file in downloaded_files]

    upload_files(file_paths, folder_id)

