from . import *
from utils.utils import  now_time, timestamp, unquote, strip_whitespace
from utils.web import requests_get
from os import getenv

apidb_bp = Blueprint('apidb', __name__, url_prefix='/db')

@apidb_bp.route('/', methods=['GET'])
def apidb_index():
    datas = []
    for table in db.get_table():
        datas.append([f'<a href="/db/{table}">{table}</a>'])
    return render_template('common/list.html',title='資料表',datas=datas, heads=['table_name'])

@apidb_bp.route("/<table_name>", methods=['GET'])
def show_table(table_name):
    return render_template('common/list.html',title=table_name,datas=db.get_col(table_name,'*'),heads=db.get_head(table_name))

@apidb_bp.route("/api", methods=['GET'])
def show_table_api():
    ap = api_page(200, '資料庫所有的資料表')
    ap.datas = db.get_table()
    return ap.createResponse()

@apidb_bp.route("api/<table_name>", methods=['GET'])
def show_table_name_api(table_name):
    _search = {
        'gid': f"%{request.args.get('gid','')}%",
        'name': f"%{request.args.get('name','')}%",
        'rating': f"%{request.args.get('rating','')}%",
        'price_level': f"%{request.args.get('price_level','')}%",
    }
    
    ap = api_page(200, f'{table_name} 的資料')
    ap.datas = [{'head':db.get_head(table_name)}, {'data':db.get_col(table_name,'*',_search)}]
    return ap.createResponse()