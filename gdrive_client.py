from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime

class GDriveClient:
    def __init__(self, service_account_json_key_path):
        self.service_account_json_key_path = service_account_json_key_path
        self.scope = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file(
                              filename=self.service_account_json_key_path, 
                              scopes=self.scope)
        self.service = build('drive', 'v3', credentials=credentials)

    # for a folder, get item list
    def execute_list_query(self, query, fields=""):
        all_files = []
        page_token = None
        while True:
            response = self.service.files().list(q=query, fields=fields, pageToken=page_token, orderBy='name').execute()
            files = response.get('files', [])
            all_files.extend(files)
            page_token = response.get('nextPageToken')
            print ("page_token: ", page_token, "response.keys:", response.get('nextPageToken', 'not exist !'))
            print("all_files.length: ", len(all_files))
            if not page_token:
                break
        return {"files": all_files}
    
    # for a file, get more detail
    def execute_get_query(self, file_id, fields=None):
        return self.service.files().get(fileId=file_id, fields=fields).execute()