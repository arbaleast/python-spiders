import requests
import json
 
name = '办公建筑分类.jpg'
url = "https://api.github.com/repos/arbaleast/Image-Host/contents/code/" + name
token = "token " + "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"

headers = {
    "Authorization": token,
    "Accept": "application/vnd.github.v3+json"
}

get = requests.get(url=url, headers=headers, verify=False)
get_data = json.loads(get.text)
print(get_data['name'])