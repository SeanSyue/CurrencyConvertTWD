import configparser
import requests


config = configparser.ConfigParser()
config.read('config.ini')

# Location of online currency exchange table
_URL = config['TABLE']['url']

r = requests.get(_URL)
print(r.headers)
print(r.headers['Content-Disposition'])
print(type(r.headers['Content-Disposition']))
