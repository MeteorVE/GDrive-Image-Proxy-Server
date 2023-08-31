import gdrive_db
import gdrive_client as gdrive_client_lib
import chacha20_encrypt
import dotenv

service_account_json_key_path = dotenv.get_key(".env", "SERVICE_ACCOUNT_JSON_KEY_PATH")
db_name = dotenv.get_key(".env", "DB_NANE")
table_name = dotenv.get_key(".env", "DB_TABLE_NAME")
gdrive_client = gdrive_client_lib.GDriveClient(service_account_json_key_path)
db = gdrive_db.GDriveDatabase(db_name, table_name)
db.create_table()   # 註: 建立的表格的名字，已經寫死了，目前尚未去更改他。