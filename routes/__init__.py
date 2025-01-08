from flask import Flask, Blueprint, render_template, request, url_for,redirect,make_response,session,abort,send_from_directory
from os import getenv
from utils.utils import json, now_time, timestamp

from time import time
from utils.api_page import *
from os.path import join
from os import getcwd
from utils.web import set_file_handler, logging

### Main App ###
APPNAME = 'AI Project'
app = Flask(APPNAME)

### Logger ###
LOG = set_file_handler(app)

### Configurations ###
app.secret_key = getenv('APP_SECRET_KEY')
app.config['TITLE'] = APPNAME
app.config['DESCRIPTION'] = '餐廳資料蒐集系統'
app.config['SERVER_RUN_TIME'] = now_time()
app.config['VERSION'] = '1.0.0-beta.1'  # __version__ = ".".join(("0", "6", "3"))
app.config['AUTHOR'] = 'Wei-Wen Wu'
app.config['AUTHOR_EMAIL'] = 'timmy90928@gmail.com'
app.config['GITHUB_URL'] = ''
app.config['COPYRIGHT'] = '(c) 2024 Wei-Wen Wu'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 # Set the maximum upload file size to 1024MB (1GB).
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{join(getcwd(), 'aiproject.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from utils.db import Sqlite, createDB
_db = createDB('aiproject.db', app)
db:Sqlite = Sqlite(join(getcwd(), 'aiproject.db'))
errormsg = None
clients = {}

### Request decorator ###
@app.context_processor
def inject_global_vars():
    """Injects global variables to all templates."""

    return {
        'site_header_title': 'AI Project',
    }

@app.before_request
def track_connection() -> None:
    """Tracks all the current clients (by IP) and stores them in the set clients."""
    ip = request.remote_addr
    clients[ip] = time()

@app.after_request
def log_status_code(response:Response):
    global errormsg
    ip = request.remote_addr
    page = request.path
    method = request.method
    status_code = response.status_code

    if status_code != 304: LOG.debug(f'{status_code} >>> {method:^5} >>> {ip:^12} >>> {page}')
    if errormsg: 
        LOG.debug(f'{errormsg}')
        errormsg = None
    return response

@app.teardown_request
def remove_client(exc=None):
    """Removes the client from the set clients when the request is finished."""
    for ip, timestamp in list(clients.items()):
        if time() - timestamp > 300:  # 5 minutes
            del clients[ip]

@app.route('/log')
def show_log():
    return send_from_directory('.', 'log.log', as_attachment=False)

@app.route('/create_db')
def index():
    _db.create_all()
    return str(_db.metadata.tables)
### Blueprint ###
from .root import root_bp
from .api import api_bp
from .help import help_bp
from .apidb import apidb_bp

ALL_BP = [root_bp, api_bp, help_bp, apidb_bp]


from werkzeug.exceptions import HTTPException
@app.errorhandler(HTTPException)
def baseerrorhandler(e:HTTPException):
    global errormsg
    # 記錄日誌
    errormsg = f'{e.response} >>> {e.description if e.description else e.name}'
    # abort(status_code, response=f"{status_code}")
    ap = api_page(e.code, e.response)
    ap.json["status"] = e.name
    ap.json["error_message"] = e.description if e.description else e.name
    ap.json["headers"] = e.get_headers()
    ap.json["args"] = e.args
    # LOG.debug(f'{e.code} >>> {method:^5} >>> {ip:^12} >>> {page}')
    return ap.createResponse()


from enum import IntEnum 
class roles(IntEnum):
    developer = 0
    admin = 1
    user = 2
    viewer = 3
    error = 9

""""
https://dowyuu.github.io/program/2020/05/27/Input-Datalist/
"""

"""
before_first_request: 執行初始化任務，僅在第一次請求之前執行一次。
before_request: 在每個請求之前執行，適合做身份驗證、日誌記錄等工作。
after_request: 在每個請求之後執行，適合修改回應（例如新增回應頭）。
teardown_request: 在請求結束後執行，用於清理資源（如資料庫連線）。
teardown_appcontext: 在應用程式上下文結束時執行，用於清理應用程式層級的資源。
errorhandler: 用於捕獲並處理特定 HTTP 錯誤。
url_value_preprocessor: 在 URL 參數處理之前執行，適合預處理參數。 endpoint, values
url_defaults: 在產生 URL 時填入預設參數。 endpoint, values
"""