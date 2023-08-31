import re
import sys
import gdrive_db
import dotenv

db_name = dotenv.get_key(".env", "DB_NANE")
db_table_name = dotenv.get_key(".env", "DB_TABLE_NAME")
db = gdrive_db.GDriveDatabase(db_name, db_table_name)

def get_hash_by_file_id_with_orm(_id):
    result = db.get_hash_by_file_id(_id)
    if result == None:
        print("[Info] Unknown id: ", _id)
    return result

markdown_filename = "markdown_name.md"
if len(sys.argv) == 2:
    markdown_filename = sys.argv[1]
else:
    print("[Info] Use default filename.")
    # print("Usage: python script.py <markdown_file>")
    # sys.exit(1)

with open(markdown_filename, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'https://drive\.google\.com/uc\?id=([^")\s]+)'
matches = re.findall(pattern, content)

for match in matches:
    hash_id = get_hash_by_file_id_with_orm(match)
    new_link = f'http://localhost:3636/v0/i/gdrive/{hash_id}'
    content = content.replace(f'https://drive.google.com/uc?id={match}', new_link)

with open(markdown_filename, 'w', encoding='utf-8') as f:
    f.write(content)
