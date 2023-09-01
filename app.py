from flask import Flask, Response, redirect
from webptools import dwebp
import requests
import gdrive_db
import urllib.parse
from werkzeug.routing import Map, Rule, RequestRedirect
import requests
import time
import dotenv
import sys

app = Flask(__name__)
app.config['LOG_LEVEL'] = 'DEBUG'
from logging import StreamHandler
app.logger.addHandler(StreamHandler())

# /v1/i/gdrive/webp/quality/size/id
# http://localhost:3636/v1/i/gdrive/webp/quality/size/X0YnnnJR5uFZJDeqGzBdJJrccw==
# http://localhost:3636/v0/i/gdrive/X0YnnnJR5uFZJDeqGzBdJJrccw==

db_name = dotenv.get_key(".env", "DB_NANE")
db_table_name = dotenv.get_key(".env", "DB_TABLE_NAME")

url_map = Map([
    Rule('/v0/i/gdrive/<string:webp>/<string:quality>/<string:size>/<string:_id>', endpoint='process_gdrive_url'),
    Rule('/v0/i/gdrive/<path:path>', endpoint='tester')
])

# e.g.: http://localhost:3636/v0/i/gdrive/X0YnnnJR5uFZJDeqGzBdJJrccw==
@app.route('/v0/i/gdrive/<string:_id>')
def process_gdrive_url(_id):
    _id = urllib.parse.unquote(_id)
    print(_id, flush=True)
    start_time = time.time()
    new_url = get_file_id_by_hash_with_orm(_id)
    end_time = time.time()
    loading_time = end_time - start_time
    app.logger.debug(f"[Debug] Spending loading time: {loading_time:.6f} seconds")
    print(f"[Debug] Spending loading time: {loading_time:.6f} seconds", flush=True)
    # return new_url, 203
    return redirect(new_url)

@app.route(r"/v0/i/gdrive/([^/]+)")
def gid_unmatch():
    return "gdrive test"

# e.g.: http://localhost:3636/v0/i/gdrive/webp/quality/size/X0YnnnJR5uFZJDeqGzBdJJrccw==
@app.route('/v0/i/gdrive/<string:webp>/<string:quality>/<string:size>/<string:_id>')
def v1(webp, quality, size, _id):
    # not implement
    return

# middleware
def webp_middleware(webp):
    print(f"Calling webp middleware with webp={webp}")

def quality_middleware(quality):
    print(f"Calling quality middleware with quality={quality}")

def size_middleware(size):
    print(f"Calling size middleware with size={size}")

def get_file_id_by_hash_with_orm(_id):
    db = gdrive_db.GDriveDatabase(db_name, db_table_name)
    result = db.get_file_id_by_hash(_id)
    app.logger.debug("print result:", flush=True)
    app.logger.debug(result, flush=True)
    db.close()
    return "https://drive.google.com/uc?id="+result


@app.route('/webp_image')
def get_webp_image():
    remote_url = 'https://a.com/photo.jpg'
    try:
        response = requests.get(remote_url)
        response.raise_for_status()  # 檢查狀態碼
        image_data = response.content
        webp_data = dwebp(image_data)
        return Response(webp_data, content_type='image/webp')

    except requests.exceptions.RequestException as e:
        return f"Error fetching image: {e}", 500

    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    _port = 3636
    if len(sys.argv) == 2:
        _port = sys.argv[1]
    app.run(host='0.0.0.0', port=_port)
