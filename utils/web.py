from flask import jsonify, request, Request, abort
from requests import get as _requests_get, post as _requests_post
from datetime import datetime, timedelta
from socket import socket, AF_INET, SOCK_DGRAM
from typing import  Literal, Optional, Union, TypeAlias
import logging
from colorlog import ColoredFormatter

def requests_get(url, params=None, _abort:list=None, **requests_config) -> dict:
    """
    _abort: If _abort[0] is not _abort[1], then abort(_abort[2], description=result[_abort[3]])
    >>> requests_get('url', params={'key': 'value'}, _abort=['status', 'OK', '500', 'error_message'])
    """
    response = _requests_get(url, params, **requests_config)
    response.raise_for_status()
    result:dict = response.json()
    if _abort and result[_abort[0]] != _abort[1]:
        abort(_abort[2], description=result[_abort[3]])
    return result

def requests_post(url, data=None, json=None, **requests_config) -> dict:
    response = _requests_post(url,data=data, json=json, **requests_config)
    response.raise_for_status()
    return response.json()
    
def return_page(success:str, message:str, state:int):
    return jsonify({"success": success, "message": message}), state

def get_local_ip():
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google Public DNS
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

def get_external_ip():
    try:
        # Use `ipify` to get external IP addresses
        response = requests_get('https://api.ipify.org?format=json')
        return response['ip']
    except Exception as e:
        return str(e)
    
def check_file(request:Request):
    if 'file' not in request.files:
        raise AssertionError('No file part')
    file = request.files['file']
    if file.filename == '':
        raise AssertionError('No selected file')
    return file

from flask import Flask
def set_file_handler(app:Flask, filename="log"):
    app.logger.setLevel(logging.DEBUG)
    app.logger.handlers[0].setLevel(logging.WARNING)

    forfat_file = logging.Formatter(fmt='%(asctime)s >>> %(message)s',datefmt='%Y-%m-%d  %H:%M:%S') # (in %(filename)s:%(lineno)d)'

    file_handler = logging.FileHandler(filename=f"{filename}.log", mode='a', encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt=forfat_file)  # Add Formatting.

    app.logger.addHandler(file_handler)

    return app.logger