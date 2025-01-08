from . import *

help_bp = Blueprint('help', __name__, url_prefix='/help')

api_heads = ['參數', '預設值', '格式', '說明']

@help_bp.route('/', methods=['GET'])
def help_index():
    ilist = [
        ['<a href="/help/nearbysearch">nearbysearch</a>','蒐集附近的地點','Google(place/nearbysearch), 並將結果存入資料庫'],
        ['<a href="/help/placeinfo">placeinfo</a>','根據餐廳id, 回傳該餐廳的基本資訊','本地資料庫與Google(place/details), 若資料庫有資料, 則會顯示本地資料, 否則線上, 並將結果存入資料庫'],
        ['<a href="/help/textsearch">textsearch</a>','根據餐廳名稱，檢索部分名稱符合的餐廳','Google(place/textsearch)'],
        ['<a href="/help/opentime">opentime</a>','根據營業時間, 回傳有開的餐廳','本地資料庫'],
        ['<a href="/help/footfall">footfall</a>','根據餐廳Id, 提供歷史人流','爬蟲'],
        ['<a href="/help/review">review</a>','根據餐廳Id, 提供該餐廳的評論','本地資料庫與Google(place/details), 若資料庫有資料, 則會顯示本地資料, 否則線上, 並將結果存入資料庫'],
        ['-','-','-'],
        ['<a href="/db/api">/db/api</a>','資料庫所有的資料表', '本地資料庫 (<a href="/db">查看資料庫</a>)'],
        ['/db/api/$(table_name)','該資料表的所有資料', '本地資料庫 (<a href="/db">查看資料庫</a>)'],
        ['-','-','-' ],
        ['<a href="/help/placetime">placetime</a>','蒐集地點的營業時間','Google(place/details)'],
    ]
    return render_template('common/list.html', title='幫助', heads=['API', '說明', '資料提供'], datas=ilist), 200

@help_bp.route('/nearbysearch', methods=['GET'])
def help_nearbysearch():
    _data = [
        ['location', '23.566429, 120.472377', '{latitude, longitude}', '搜尋中心點'],
        ['radius', '1000', '{1 ~ 50000}', '搜尋範圍的半徑, 以meter為單位'],
        ['keyword', '午餐', '', '搜尋關鍵字，支持中文，若直接在網址需使用 urlencode()'],
        ['type', 'restaurant', '', '類型'],
        ['opennow', 'false', '{true | false}', '是否只返回當前開放的地點'],
        ['minprice', '0', '{0 ~ 4}', '最低價格級別'],
        ['maxprice', '4', '{0 ~ 4}', '最高價格級別'],
        ['rankby', 'prominence', '{prominence(知名度) | distance}', '結果排序方式'],
        ['language', 'zh-TW', '{en | zh-TW | etc.}', '語言'],
        ['origin', 'False', '{ true }', '是否返回原始資料, 若不需要請不要指定origin參數'],
    ]
    return render_template('common/list.html', title='nearbysearch', heads=api_heads, datas=_data), 200

@help_bp.route('/placeinfo', methods=['GET'])
def help_placeinfo():
    _datas = [
        ['placeid', 'ChIJIeEH6U--bjQR0fRT8ItpVOk', '', '地點的唯一識別碼(由google提供)'],
        ['origin', 'False', '{ true }', '是否返回原始資料, 若不需要請不要指定origin參數'],
        ['online', 'False', '{ true }', '是否返強迫使用線上資料, 若不需要請不要指定online參數'],
    ]
    return render_template('common/list.html', title='placeinfo', heads=api_heads, datas=_datas), 200

@help_bp.route('/textsearch', methods=['GET'])
def help_textsearch():
    _datas = [
        ['/textsearch/$(name)', '', '', '要搜尋的關鍵字'],
        ['origin', 'False', '{ true }', '是否返回原始資料, 若不需要請不要指定origin參數'],
    ]   
    return render_template('common/list.html', title='textsearch', heads=api_heads, datas=_datas), 200
@help_bp.route('/placetime', methods=['GET'])
def help_placetime():
    _datas = [
        ['placeid', 'ChIJUVWFEyGUbjQRvMIXG_6EvsA', '', '地點ID'],
    ]
    return render_template('common/list.html', title='placetime', heads=api_heads, datas=_datas), 200



@help_bp.route('/opentime', methods=['GET'])
def help_opentime():
    _datas = [
        ['weekday', '*', '{1~7}', '要查詢的星期(7為星期日)'],
        ['hour', None, '{00~23}', '要查詢的小時'],
        ['minute', '00', '{00~59}', '要查詢的分鐘'],
    ]
    return render_template('common/list.html', title='opentime', heads=api_heads, datas=_datas), 200

@help_bp.route('/footfall', methods=['GET'])
def help_footfall():
    _datas = [
        ['placeid', 'ChIJIeEH6U--bjQR0fRT8ItpVOk', '', '地點的唯一識別碼(由google提供)'],
        ['origin', 'False', '{ true }', '是否返回原始資料, 若不需要請不要指定origin參數'],
    ]
    return render_template('common/list.html', title='footfall', heads=api_heads, datas=_datas), 200

@help_bp.route('/review', methods=['GET'])
def help_review():
    _datas = [
        ['placeid', 'ChIJIeEH6U--bjQR0fRT8ItpVOk', '', '地點的唯一識別碼(由google提供)'],
        ['origin', 'False', '{ true }', '是否返回原始資料, 若不需要請不要指定origin參數'],
    ]
    return render_template('common/list.html', title='review', heads=api_heads, datas=_datas), 200