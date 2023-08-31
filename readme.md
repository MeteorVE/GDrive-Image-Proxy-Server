# GDrive-Image-Proxy-Server

此專案的用途是希望能將照片上傳到 Google Drive 後，我們能將其當作 imgur 來使用。

## Inspiration

一般來說，其實我們只要找到 file/image 對應的 id 即可實現功能
例如，我們對一個檔案或是一個資料夾，選擇 "分享"，得到了以下的網址

```
https://drive.google.com/file/d/1WbpzNBIGXXgezNStAS3ixXA3DWP1f1YG/view
```

其中 ``file_id`` 就是 ``1WbpzNBIGXXgezNStAS3ixXA3DWP1f1YG``。
對網址做一點手腳，可以被換成

```
https://drive.google.com/uc?id=1WbpzNBIGXXgezNStAS3ixXA3DWP1f1YG
```

即可被 markdown 或是 HTML 的 img tag 給識別成一張圖片網址。
於是我們在寫文章的時候，就可以上傳到 Google Drive，並且提取文章 ID、改成 ``uc`` 格式並放到文章中。

但這麼做有一個缺點，就是如果 Google Drive 的免費空間被限縮了，那這些圖片就得搬走、file_id 就會改變，那我們就會很難受。
又或是我今天想要搬到別的雲端 (例如 pCloud, AWS)，那我過去的文章網址就得手動重改。
所以，如果我能固定一個網址，並且後面可以自由的去 routing，那就能解決問題了。

## Solution

### Google Drive

因為 Google Drive (後面簡稱 gDrive) 有著 "得知 file_id 後即可得到圖片的 direcet link" 的特性
所以當我們 access 這樣的網址 : ``/v0/i/gdrive/{hash_id}``，
再去查找 database 對應的 gDrive file_id，就能得到 image direct link 了。

### About ``hash_id``

``hash_id`` 是由 ``path+filename`` 進行對稱式加密後得到的。
path 在我原本的預想之中，會希望是 "他在 gDrive 中的 path"，
但是以目前的 file api 很難高效的得到實際路徑，所以這邊就想像成 "local 端存放的 path"。

舉例來說，path 可以是 ``/travel/2023/03/japan/``，而 filename 可以是 ``IMAG0001.jpg``
所以兩者相加得到 ``/travel/2023/03/japan/IMAG0001.jpg``，並且可以進行雜湊。

當我們在寫文章時，可能會註記 : 這個位置想要使用 ``IMAG0001.jpg`` 這樣的資訊
想要得知對應的 hash_id 的時候，可以從 table 撈、也能手動計算雜湊；

然而，使用雜湊(hash)會有一個缺點 : 
我只能單向的計算出另一邊。

若我們使用可以根據路徑＋檔名直接定位檔案的雲端，例如 aws / 私有 cloud
使用雜湊，我們必須用雜湊定位到 db 中的 row，然後找到 path 和 filename，再返回檔案資料；
然而，使用對稱式加密的話，就能直接將 hash_id 轉回 path+filename，並且再透過 API 去 access 檔案。
path -> hash_id 的動作是加密(encrypt)，而 hash_id -> path 的動作是解密(decrypt)。

故這邊寫的 hash_id，其實是一個經過 encrypt 的亂碼，並不是真的經過一個 hash function。
順帶一提，這邊使用的是 chacha20 來進行對稱式加密，它在後續有被 Google 繼續優化並採用。

## Usage

- 首先 import 對應 lib

```python
import gdrive_db
import gdrive_client as gdrive_client_lib
import chacha20_encrypt
```

- 如果還沒有 db 或是 db 內沒有對應 table，需要先執行 ``db.create_table()``

```python
import dotenv
service_account_json_key_path = dotenv.get_key(".env", "SERVICE_ACCOUNT_JSON_KEY_PATH")
db_name = dotenv.get_key(".env", "DB_NANE")
table_name = dotenv.get_key(".env", "DB_TABLE_NAME")

gdrive_client = gdrive_client_lib.GDriveClient(service_account_json_key_path)
db = gdrive_db.GDriveDatabase(db_name, table_name)
db.create_table()   # 註: 建立的表格的名字，已經寫死了，目前尚未去更改他。
```

- 如果想要把指定的 google_folder_id 給導入 db 的 table 中，可以跑下面的程式
  - ``tag`` 是一個 optional 的參數，為了方便有更多的應用擴展，例如查詢同個主題的照片們。

```python
from update_db_operations import add_folder_from_gdrive
import dotenv
db_name = dotenv.get_key(".env", "DB_NANE")
table_name = dotenv.get_key(".env", "DB_TABLE_NAME")

folder_id = '1-9tSbXEcJZbHS_4W4Xn3uExzqV8Tn9-0'  # GDrive Folder ID
db = gdrive_db.GDriveDatabase(db_name, table_name)
add_folder_from_gdrive(db, folder_id, "travel/2023/03/", tag="tokyo")
db.close()
```

- 如果今天你移動了檔案 (將檔案們從 Google_Drive_A 移動到 Google_Drive_B )
  你想要更改那些檔案的 ``file_id`` (provided by Google) 在 db 中的紀錄
  那你可以跑以下的程式

```python
from update_db_operations import update_file_id_in_folder
import dotenv
db_name = dotenv.get_key(".env", "DB_NANE")
table_name = dotenv.get_key(".env", "DB_TABLE_NAME")

new_folder_id = "2smsM9Pve5K1hkjaoLR73foXudtsy0Shc"  # GDrive Folder ID
db = gdrive_db.GDriveDatabase(db_name, table_name)
update_file_id_in_folder(db, new_folder_id, "travel/2023/03/")
db.close()
```

- 如果你今天有一篇已經寫好的文章，已經採用 ``drive.google.com/uc?id=`` 的格式嵌入圖片了
  那你可以考慮去修改 ``replace_url_in_markdown.py``
  - 修改 ``new_link`` 的前綴網址，改成你的 service domain

```python
new_link = f'http://localhost:3636/v0/i/gdrive/{hash_id}'
```

並執行

```python
python .\replace_url_in_markdown.py test.md
```

