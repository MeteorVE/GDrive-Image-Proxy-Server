import sqlite3
import dotenv

db_table_name = dotenv.get_key(".env", "DB_TABLE_NAME")

class GDriveDatabase:
    def __init__(self, db_name, table_name=db_table_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.table_name = table_name
    
    def insert_data(self, file_id, hashed_path, filename, mime_type, folder_id, path="", tag="", created_time=0):
        query = f"INSERT OR IGNORE INTO {self.table_name} (file_id, hashed_path, filename, mime_type, folder_id, path, tag, created_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, (file_id, hashed_path, filename, mime_type, folder_id, path, tag, created_time))
        self.conn.commit()
    
    def update_data(self, hashed_path, update_columns):
        for key, value in update_columns.items():
            if key == "record_time" and value == "CURRENT_TIMESTAMP":
                query = f"UPDATE {self.table_name} SET {key} = CURRENT_TIMESTAMP WHERE hashed_path = ?"
                self.cursor.execute(query, (hashed_path,))
            else:
                query = f"UPDATE {self.table_name} SET {key} = ? WHERE hashed_path = ?"
                self.cursor.execute(query, (value, hashed_path))
        self.conn.commit()

    def delete_data(self, hashed_path):
        query = f"DELETE FROM {self.table_name} WHERE hashed_path=?"
        self.cursor.execute(query, (hashed_path,))
        self.conn.commit()
    
    # 要把它改成可以 fetch many
    def get_hash_by_filename(self, filename):
        query = f"SELECT hashed_path FROM {self.table_name} WHERE filename = ?"
        self.cursor.execute(query, (filename,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    
    def get_filename_by_hash(self, hashed_path):
        query = f"SELECT filename, path FROM {self.table_name} WHERE hashed_path = ?"
        self.cursor.execute(query, (hashed_path,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        
    def get_file_id_by_hash(self, hashed_path):
        query = f"SELECT file_id FROM {self.table_name} WHERE hashed_path = ?"
        self.cursor.execute(query, (hashed_path,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    
    def get_hash_by_file_id(self, file_id):
        query = f"SELECT hashed_path FROM {self.table_name} WHERE file_id = ?"
        self.cursor.execute(query, (file_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    
    def close(self):
        self.conn.close()
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gdrive_data (
                id INTEGER PRIMARY KEY,
                file_id TEXT NOT NULL,
                hashed_path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                mime_type TEXT,
                folder_id TEXT,
                path TEXT ,
                tag TEXT ,
                created_time TIMESTAMP
            )
        ''')

        # Demo how to alter
        self.cursor.execute('ALTER TABLE gdrive_data ADD COLUMN record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP')

        # add INDEX to another column
        self.cursor.execute('CREATE INDEX IF NOT EXISTS hashed_path_index ON gdrive_data(hashed_path)')
        self.conn.commit()
        return 