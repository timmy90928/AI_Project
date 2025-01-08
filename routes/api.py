
from . import *
from utils.utils import  now_time, timestamp, unquote, strip_whitespace
from utils.web import requests_get
from os import getenv
from typing import Literal
api_bp = Blueprint('api', __name__, url_prefix='/api')
api_key = getenv('GOOGLE_GEOLOCATION_API_KEY')

url_nearbysearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
url_place_detail = "https://maps.googleapis.com/maps/api/place/details/json"
url_textsearch = "https://maps.googleapis.com/maps/api/place/textsearch/json"


@api_bp.route('/', methods=['GET'])
def api_index():
    ap = api_page(200)
    ap.json['status'] = 'OK'
    return ap.createResponse()


@api_bp.route('/nearbysearch', methods=['GET'])
def nearbysearch():
    params = {
        'location': request.args.get('location','23.566429, 120.472377'), # 25.0338,121.5646
        'radius': request.args.get('location','1000'),
        'keyword': request.args.get('keyword','午餐'),
        'type': request.args.get('type','restaurant'),
        'opennow': request.args.get('opennow','false'),
        'minprice': request.args.get('minprice','0'),
        'maxprice': request.args.get('maxprice','4'),
        'rankby': request.args.get('rankby','prominence'),
        'language': request.args.get('language','zh-TW'),
        'key': request.args.get('key',api_key),
    }
    response = requests_get(url_nearbysearch, params=params)
    results = response['results']
    datas = get_restaurant_info(results)
    ap = api_page(200, f'以 ({params["location"]}) 為中心, 半徑為 {params["radius"]} 公尺, 搜尋附近的 {params["keyword"]} 餐廳')
    ap.datas = datas if not request.args.get('origin',False) else results

    return ap.createResponse()

@api_bp.route('/placeinfo', methods=['GET'])
def placeinfo():
    params = {
        'placeid': request.args.get('placeid','ChIJIeEH6U--bjQR0fRT8ItpVOk'),
        'key': api_key
    }
    if db.exist('Restaurant',['gid',params['placeid']]) and not request.args.get('online',False):
        ap = api_page(200, '該餐廳的基本資訊(來自資料庫)')
        ap.datas = convert_restaurant_db2dict(db.get_col('Restaurant','*',{'gid':params['placeid']}))
    else:
        response = requests_get(url_place_detail, params=params, _abort=['status','OK',400,'error_message'])
        results = response['result']
        datas = get_restaurant_info([results])
        ap = api_page(200, '該餐廳的基本資訊(來自GOOGLE API)')
        ap.datas = datas if not request.args.get('origin',False) else results
    return ap.createResponse()

@api_bp.route('/textsearch/<name>', methods=['GET'])
def textsearch(name):
    params = {
        'query': name,
        'key': api_key
    }
    response = requests_get(url_textsearch, params=params, _abort=['status','OK',400,'error_message'])
    results = response['results']
    datas = get_restaurant_info(results)
    ap = api_page(200, f"搜尋 {name} 的地點")
    ap.datas = datas if not request.args.get('origin',False) else results
    return ap.createResponse()

@api_bp.route('/opentime', methods=['GET'])
def opentime():
    weekday = request.args.get('weekday','%')
    hour = request.args.get('hour',None)
    minute = request.args.get('minute','00')

    time_check = f"AND '{hour}:{minute}' BETWEEN OpenTime.start AND OpenTime.end" if hour else ""

    query = f"""
    SELECT DISTINCT Restaurant.*
    FROM OpenTime
    INNER JOIN Restaurant
    ON Restaurant.id = OpenTime.rid
    WHERE OpenTime.weekday LIKE '{weekday}' {time_check}
    """
    ap = api_page(200, '指定時間中有開放的餐廳(此API僅回傳資料庫內的餐廳)')
    ap.datas = convert_restaurant_db2dict(db(query))
    return ap.createResponse()

@api_bp.route('/footfall', methods=['GET'])
def footfall():
    params = {
        'placeid': request.args.get('placeid','ChIJUVWFEyGUbjQRvMIXG_6EvsA'),
    }

@api_bp.route('/review', methods=['GET'])
def review():
    apiReview = Review(request.args.get('placeid','ChIJIeEH6U--bjQR0fRT8ItpVOk'))
    results = apiReview.result

    datas = apiReview.get_datas()
            
    ap = apiReview.create_api_page()
    ap.datas = datas if not request.args.get('origin',False) else results
    return ap.createResponse()

@api_bp.route('/placetime', methods=['GET'])
def placetime():
    params = {
        'placeid': request.args.get('placeid','ChIJUVWFEyGUbjQRvMIXG_6EvsA'),
        'key': api_key
    }
    rid = db.get_row('Restaurant',['gid',params['placeid']],"id")[0][0]
    response = requests_get(url_place_detail, params=params, _abort=['status','OK',400,'error_message'])
    weekday_texts:list[str] = response['result']['current_opening_hours']['weekday_text']
    name:str = response['result']['name']
    datas = []
    no = 0

    for n, weekday_text in enumerate(weekday_texts,1):
        
        _open = analysis_1_of_weekday_text(weekday_text, no+1)
        if not _open:
            continue
        week_text, time_list, no = _open
        datas.append({
            'week': n,
            'week_text': week_text,
            'time': time_list,
        })
    try:
        for data in datas:
            week = data['week']
            for time in data['time']:   
                db.add('OpenTime',{'rid':rid,'timeslot_id':time['no'],'weekday':week,'start':time['start'],'end':time['end']})
    except Exception as e:
        pass

    ap = api_page(200, f"[{name}] 營業時間")
    ap.datas = datas if not request.args.get('details',False) else response['result']
    return ap.createResponse() 


@errorCallback('分析時間錯誤')
def analysis_1_of_weekday_text(data:str, start_no:int = 0):
    time_list = []
    week_text, week_time = data.split(': ')
    if '–' not in week_time:
        return False
    if "," in week_time:
        week_times = week_time.split(", ")
        for n, week_time in enumerate(week_times):
            end_no = start_no + n
            start, end = convert_time(week_time.split('–'))
            time_list.append({'no': end_no, 'start': strip_whitespace(start), 'end': strip_whitespace(end)})
    else:
        end_no = start_no
        start, end = convert_time(week_time.split('–'))
        time_list.append({'no': end_no, 'start': strip_whitespace(start), 'end': strip_whitespace(end)})
    return week_text, time_list, end_no

@errorCallback('轉換時間錯誤')
def convert_time(times:list[str]):
    result = []
    for time in times:
        time = strip_whitespace(time)
        if 'AM' in time:
            time = time.replace('AM','')
            result.append(time)
        else:
            hour = int(time.split(':')[0])
            time = time.replace('PM','')
            time = time.replace(str(hour),str(hour+12))
            result.append(time)
    return result
        
def get_restaurant_info(results:list[dict]):
    datas = []
    for n, result in enumerate(results,1):
        datas.append({
            'no': n,
            'gid': result['place_id'],
            'name': unquote(result['name']),
            'longitude':"%.6f" % result['geometry']['location']['lng'],
            'latitude':"%.6f" % result['geometry']['location']['lat'],
            'rating': result.get('rating',-1),
            'price_level': result.get('price_level',-1),
        })
        add_restaurant_to_db(datas[-1])

    return datas

def convert_restaurant_db2dict(datas:list[dict]):
    new_datas = []
    for data in datas:
        new_datas.append({
            'no': data[0],
            'gid': data[1],
            'name': data[2],
            'longitude':data[3],
            'latitude':data[4],
            'rating': data[5],
            'price_level': data[6],
        })
    return new_datas

def add_restaurant_to_db(data:dict):
    try:
        del data['no']
        db.add('Restaurant',data)
    except Exception as e:
        print(e)

class ApiPlaceDetail:
    _instance = {}
    source:Literal['GOOGLE API','DataBase'] = None
    url_place_detail = "https://maps.googleapis.com/maps/api/place/details/json"

    def __init__(self, placeid:str, table:str = None) -> None:
        self._datas = []
        self.table = table if table else self.__class__.__name__
        self.params = {
            'placeid': placeid,
            'language': 'zh-TW',
            'region': 'TW',
            'key': api_key
        }

    @property
    def result(self) -> dict:
        self._datas = self._request_get() if self._datas == [] else self._datas
        return self._datas['result']
    
    @property
    def name(self) -> str:
        if db.exist("Restaurant",['gid',self.params['placeid']]):
            return db.get_col("Restaurant","name",{'gid':self.params['placeid']})[0][0]
        else:
            return self.result['name']
    
    def db_exist(self, gid_name:str = "gid") -> bool:
        return db.exist(self.table,[gid_name, self.params['placeid']])
    
    @errorCallback('新增至資料庫錯誤')
    def add2db(self, data:dict, delete:list=[]):
        data = dict(filter(lambda item: item[0]  not in delete, data.items())) # {key: value for key, value in a.items() if key != 'a'}
        db.add(self.table, data)

    def _request_get(self):
        self.source = 'GOOGLE API'
        return requests_get(url = self.url_place_detail, params=self.params, _abort=['status','OK',400,'error_message'])
    
class Review(ApiPlaceDetail):
    def __new__(cls, placeid:str):
        if cls._instance.get(placeid) is not None:
            client:cls = cls._instance.get(placeid)
            return client
        else:
            client:cls = super().__new__(cls)  
            cls._instance[placeid] = client
            return client
        
    def __init__(self, placeid:str):
        super().__init__(placeid)
        self.datas:list[dict] = []
    
    def get_datas(self):
        if self.db_exist():
            self.source = 'DataBase'
            return self.get_datas_from_db()
        else:
            return self.get_datas_from_google()
    def create_api_page(self):
        return api_page(200, f'{self.name} 的評論 (Source: {self.source})')
    
    def get_datas_from_google(self):
        self.source = 'GOOGLE API'
        reviews = self.result['reviews']
        for n, review in enumerate(reviews,1):
            self.datas.append({
                'no': n,
                'time': review['time'],
                'rating': review['rating'],
                'text': review['text'],
            })
            data = self.datas[-1].copy()
            data['gid'] = self.params['placeid']
            self.add2db(data)
        return  self.datas
    
    def get_datas_from_db(self):
        datas = []
        self.source = 'DataBase'
        for d in db.get_col('Review','*',{'gid':self.params['placeid']}):
            datas.append({
                'no': d[1],
                'time': d[2],
                'rating': d[3],
                'text': d[4],
            })
        return datas