import os

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

            for root, _, files in os.walk(file_path):

                for file in files:

                    file_full_path = os.path.join(root, file)

                    file_metadata = {

                        'name': os.path.basename(file_full_path),

                        'parents': [folder_id]

                    }

                    media = MediaFileUpload(file_full_path, resumable=True)

                    try:

                        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

                        print(f'File ID: "{file.get("id")}".')

                    except HttpError as error:

                        print(f'An error occurred: {error}')

                        file = None

        else:

            print(f'Skipping non-directory path: {file_path}')

