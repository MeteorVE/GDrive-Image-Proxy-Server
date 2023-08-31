from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime
from chacha20_encrypt import encrypt_with_chacha20

def add_folder_from_gdrive(db, gdrive_client, folder_id, path_prefix, tag=""):
    query = f"'{folder_id}' in parents"
    fields = "nextPageToken, files(name, id, parents, mimeType, size, createdTime, modifiedTime, owners)"
    results = gdrive_client.execute_list_query(query, fields)
    files = results.get('files', []) # check 'files' in keys, if not, return []. (python build-in function)
    
    key = b'abcdefgh'+ b'\x00' * (32 - len(b'abcdefgh'))
    nonce = b'00000000'

    for file in files:
        hashed_path = encrypt_with_chacha20(path_prefix + file['name'], key, nonce)
        
        created_time_str = file.get('createdTime', 'Unknown')
        created_time = datetime.strptime(created_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        db.insert_data(file['id'], hashed_path, file['name'], file['mimeType'], folder_id, path_prefix, tag, created_time)
        # print(f"file_id: {file['id']}, hashed_path: {hashed_path}, filename: {file['name']},mime_type: {file['mimeType']}, createTime: {file['createdTime']}")

def update_file_id_in_folder(db, gdrive_client, new_folder_id, path_prefix):
    query = f"'{new_folder_id}' in parents"
    fields = "files(name, id, parents, mimeType, size, createdTime, modifiedTime, owners)"
    results = gdrive_client.execute_list_query(query, fields)
    files = results.get('files', []) # check 'files' in keys, if not, return []. (python build-in function)

    key = b'abcdefgh'+ b'\x00' * (32 - len(b'abcdefgh'))
    nonce = b'00000000'

    for file in files:
        hashed_path = encrypt_with_chacha20(path_prefix + file['name'], key, nonce)
        print (f"new file_id: {file['id']}, type: {file['mimeType']}")
        db.update_data(hashed_path, {"file_id":file['id'], "record_time": "CURRENT_TIMESTAMP" })


