import requests
import json
from urllib.parse import quote

text = 'GB 50176-2016'
keyword = quote(text, 'utf-8')
url = 'http://s.jianbiaoku.com/sou/?module=criterion&keyword=' + keyword
print(url)
headers = {
	"Accept": "application/json",
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
	"Cookie": "zz_client_token=ec4bd6a3ed554a95a3cc9e5287e4b67e"
}

req = requests.get(url=url, headers=headers)

print(req.text)