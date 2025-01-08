from datetime import timedelta,datetime,timedelta
from shutil import copy2, rmtree, ignore_patterns, copytree
from os import environ,mkdir
from os.path import isfile, isdir, split as path_split,join
from base64 import b64encode,b64decode
from urllib.parse import quote, unquote
from typing import Any, Union, Optional, Callable
import math
from hashlib import sha3_256
from json import load, dump
from pystray import MenuItem, Icon as _icon, Menu as StrayMenu
from PIL import Image
from threading import Thread
import webbrowser
from itsdangerous import URLSafeTimedSerializer

def hash(text:str) -> str:
    """
    Hash the text using SHA3-256.

    ## Example
    >>> hash('home')
    'a20243f409be1afca9a63f66224b3467eaa9194753561e33b4d1202294cabd21'
    """
    return sha3_256(text.encode()).hexdigest()

class json:
    """
    ### Example
    ```
    from utils.utils import json
    _json = json('static/config.json')
    print(_json('base/UPLOAD_FOLDER'))
    _json_data = _json.load()
    print(_json_data['success'])
    _json_data['success'] = False
    _json.dump(_json_data)
    ```
    """
    def __init__(self, path:str) -> None:
        self.path = path

    def __call__(self, key:str, value = None) -> Any:
        keys = key.split('/')
        if value: 
            result = self._set(keys, value)
            self.dump(result)
            return result
        else:
            return self._get(keys)

    def _set(self, keys:list, value:Any) -> dict:
        temp =  self.load().copy()
        _ = "temp"
        for k in keys:
            if k == '': continue
            _ += f"['{k}']"
        exec(f"{_} = value")
        return temp
        
    def _get(self, keys:list) -> Any:

        self.data = self.load()
        result = self.data.copy()
        for k in keys:
            if k == '': continue
            result = result[k]
        return result
    def load(self) -> dict:
        with open(self.path, 'r', encoding='utf-8') as f:
            return load(f)

    def dump(self, data:dict) -> bool:
        with open(self.path, 'w', encoding='utf-8') as f:
            dump(data, f, ensure_ascii=False, indent=4)
        return True

def msgw(title:str="Title", text:str="contant", style:int=0, time:int=0) -> int:
    """
    ctypes.windll.user32.MessageBoxTimeoutW()

    Styles
    ------
    ```
    0 : OK
    1 : OK | Cancel
    2 : Abort | Retry | Ignore
    3 : Yes | No | Cancel
    4 : Yes | No
    5 : Retry | No 
    6 : Cancel | Try Again | Continue
    ```

    Example
    -------
    >>> msg=msgw('title','contant',0,1)  # time (ms)
    """
    import ctypes
    # MessageBoxTimeoutW(父窗口句柄,消息內容,標題,按鈕,語言ID,等待時間)
    return ctypes.windll.user32.MessageBoxTimeoutW(0, text, title, style,0,time)

def now_time() -> str:
    """
    ## Example
    >>> now_time() # doctest: +SKIP
    '2022-08-31 23:59:59'
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def timestamp(year=1999, month=1, day=1, hour=0, minute=0, second=0, dday=0, dhour=0, dminute=0, dsecond=0, ts:Union[int,float] = None, string:str = None) -> float:
    """
    ## Example
    >>> timestamp(2024,10+1,dsecond=-1)
    1730390399.0
    >>> timestamp(string='2024-10-31 23:59:59')
    1730390399.0
    >>> timestamp(ts=1730390399.0)
    '2024-10-31 23:59:59'
    """
    if ts:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    elif string:
        arr_string = string.split(" ")
        if len(arr_string) == 1:
            arr = arr_string[0].split("-")
            return timestamp(year=int(arr[0]), month=int(arr[1]), day=int(arr[2]))
        else:
            arr0 = arr_string[0].split("-")
            arr1 = arr_string[1].split(":")
            return timestamp(year=int(arr0[0]), month=int(arr0[1]), day=int(arr0[2]),hour=int(arr1[0]), minute=int(arr1[1]), second=int(arr1[2]))
    else:
        dt = timedelta(days=dday, hours=dhour, minutes=dminute, seconds=dsecond)
        t = datetime.strptime(f'{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}', "%Y-%m-%d %H:%M:%S") + dt
        return t.timestamp()

    
class base64:
    """
    Base64 encoding and decoding.

    ## Example
    >>> value_str = 'abcde'
    >>> value_list = ['ac','cd']
    >>> b64_str = base64(value_str).encode()
    >>> b64_list = base64(value_list).encode()
    >>> b64_str
    'YWJjZGU%3D'
    >>> b64_list
    'YWMsY2Q%3D'
    >>> base64(b64_str).decode()
    'abcde'
    >>> base64(b64_list).decode()
    ['ac', 'cd']
    """
    # __slots__ = ("data",)

    def __init__(self, data: Union[str,list]) -> None:
        self.data = str(','.join(data))  if isinstance(data, list) else str(data)

    def encode(self) -> str:
        """Encode the stored data to a base64 string."""
        b64 = b64encode(self.data.encode()).decode("utf-8")
        return quote(b64)

    def decode(self) -> Union[str, list[str]]:
        """
        Decode the stored base64 string to the original string.

        Returns a list of strings if the original data was a list, otherwise a single string.
        """
        decoded_string = b64decode(unquote(self.data)).decode()
        return decoded_string.split(",") if "," in decoded_string else decoded_string

def convert_size(size_bytes):
    """
    >>> convert_size(1024)
    '1.0 KB'
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"  

def errorCallback(errorCallback:Optional[Callable[[str],Any]]=None, *errorCallbackArgs, **errorCallbackKwargs):
    def decorator(func:Callable):
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)   # print(func.__name__)
            except Exception as e:
                if errorCallback:
                    errorCallback(e, *errorCallbackArgs, **errorCallbackKwargs)
                else:
                    print(e)
        return wrap
    return decorator

def strip_whitespace(text: str) -> str:
    """
    Remove all whitespace characters from a given string.

    This function will replace 3 types of whitespace characters in a given string with an empty string:

    1. The normal space character (`` ` ``)
    2. The non-breaking space character (`` ``)

    >>> strip_whitespace('  hello  world  ')
    'helloworld'
    """
    
    return text.replace(' ','').replace(' ','').replace('\u202f','').replace('\u2009','')

class Token(URLSafeTimedSerializer):
    """```
    >>> tkn = Token()
    >>> token = tkn.generate({'user':'timmy'})
    >>> datas = tkn.verify(token, 1)

    ```"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None: 
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__('AIzaSyAuPZ4LWUaWTFxWGgl09CxRlze6Diq3dZE','my_custom_salt')

    def generate(self, datas):
        return self.dumps(datas)
    
    def verify(self, token, expire_seconds=None):
        return self.loads(token, max_age=expire_seconds)
    
if __name__ == '__main__':
    import doctest
    print(doctest.testmod())
    print(hash('aiproject-bearer'))