import os
from dotenv import load_dotenv
from base64 import b64encode

load_dotenv() 
username = os.getenv('LOGIN')
password = os.getenv('PASSWORD')

proxies = {
    "http": "http://192.168.141.2:26280",
    "https": "http://192.168.141.2:26280"
    }  

def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "multipart/form-data; boundary=---------------------------8677523423436311045504554915",
        "Authorization": basic_auth(username, password),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
