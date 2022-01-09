import os
from io import BytesIO
import requests
from PIL import Image
import uuid
import base64
import re

import json

def save_img(url, filename, dirname):										#下载链接图片，命名保存
	req = requests.get(url)

	image = Image.open(BytesIO(req.content))

	dir = './pic/' + dirname												#pic文件夹不存在，则在当前目录创建pic
	if not os.path.exists(dir):
		os.makedirs(dir)

	with open('pic/' + dirname + '/' + filename + '.jpg', 'wb') as f:			#保存文件到/pic/目录下
		f.write(req.content)

def base64_img(filename, dirname):
	with open('pic/' + dirname + '/' + filename + '.jpg', 'rb') as f:
		src = f.read()
		enc_data = base64.b64encode(src).decode()
	return enc_data

def status_img(url, headers, name):
	try:
		get = requests.get(url=url, headers=headers, verify=False)	#请求远端文件数据
		get_data = json.loads(get.text)								
		text = re.split(r'[.]',get_data['name'])					#提取远端文件名

		if get_data['name'] == name:
			return True
		else:
			return False
	except:
		return False

def upload_img(filename, dirname, src, msg):						#上传至图床，返回cdn链接
	name = filename + '.jpg'
	url = "https://api.github.com/repos/arbaleast/Image-Host/contents/code/" + dirname + '/' + name
	token = "token " + "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"

	headers = {
		"Authorization": token,
		"Accept": "application/vnd.github.v3+json"
	}
	req_body = {
		"message": msg,
		"content": src,
		"sha": ""
	}

	data = json.dumps(req_body)															#将dict类型转为json类型

	if status_img(url, headers, name):
		cdn_url = "https://cdn.jsdelivr.net/gh/arbaleast/Image-Host/code/" + dirname + '/' + name
		return cdn_url
	else:
		req = requests.put(url=url, data=data, headers=headers, verify=False)			#上传文件（路径不存在将创建）
		req.encoding = 'utf-8'
		re_data = json.loads(req.text)

		cdn_url = upload_img(filename, dirname, src, msg)
		return cdn_url

def main(url, filename, dirname, msg):
	save_img(url, filename, dirname)

	data = base64_img(filename, dirname)

	url = upload_img(filename, dirname, data, msg)
	return url

