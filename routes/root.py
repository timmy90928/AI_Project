from . import *
from platform import system,node
root_bp = Blueprint('root', __name__)

@root_bp.route('/test', methods=['GET'])
def test():
    return render_template('index.html'), 200

@root_bp.route('/', methods=['GET'])
def index():
    return redirect('/help')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'restaurant.ico')

@root_bp.route('/server', methods=['GET'])
def server():
    # http://localhost:121/server?key=0fcbfd1b57e2b846caadbb6f0a4b82b08e43f68ab3c890c1b26a8dd91891a7ee
    key = request.args.get('key', None)
    if key != app.secret_key: abort(401, response='金鑰錯誤')
    data = [
        ['伺服器名稱', node()],
        ['伺服器系統', system()], 
        ['伺服器版本', app.config['VERSION']],
        ['伺服器啟動時間', app.config['SERVER_RUN_TIME']],
        ['目前連線數',len(clients)],
        ['目前連線IP', str('、'.join(clients))],
    ]
    return render_template('common/list.html', title='伺服器資訊',heads=['Key','Value'],datas=data), 200

@root_bp.route('/show/<table_name>', methods=['GET'])
def show(table_name):
    return redirect(f'/db/show/{table_name}')
@root_bp.route('/cause/<int:status_code>', methods=['GET'])
def cause(status_code:int):
    abort(status_code, response='此為測試用')

@root_bp.route('/test', methods=['GET','POST','PUT','DELETE'])
def request_test():
    ap = api_page(200, '測試用API')
    ap.json['headers'] = request.headers.to_wsgi_list()
    if ap.method == 'GET':
        ap.datas = request.args
    else:
        ap.datas = request.get_json()
    return ap.createResponse()

@root_bp.route('/test/<path:path>', methods=['GET'])
def path_test(path):
    ap = api_page(200, '測試路徑用的API')
    from os.path import isfile, isdir, split, abspath
    from os import listdir, stat
    if isfile(path):
        dirname, filename = split(abspath(path))
        ap.datas = {
            'path': abspath(path),
            'dirname': dirname,
            'filename': filename,
            'size': stat(path).st_size,
            'mode': stat(path).st_mode,
            'mtime': stat(path).st_mtime,
            'ctime': stat(path).st_ctime,
            'atime': stat(path).st_atime,
            'uid': stat(path).st_uid,
            'gid': stat(path).st_gid,
            'inode': stat(path).st_ino,
            'dev': stat(path).st_dev,
            'nlink': stat(path).st_nlink,
        }
    elif isdir(path):
        _path = abspath(path)
        dirname, filename = [], []
        for _ in listdir(_path):
            if isfile(join(_path,_)):
                filename.append(_)
            else:
                dirname.append(_)

        ap.datas = {
            'path': _path,
            'dirname': dirname,
            'filename': filename
        }
    else:
        abort(404, response='資料夾或檔案不存在')

    
    return ap.createResponse()