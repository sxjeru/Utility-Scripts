import requests
import re, json, time
from .log import log
from ruamel.yaml import YAML

yaml=YAML()
with open('id.yml', 'r', encoding='utf-8') as f:
    yml = yaml.load(f)

def getClassid(name):
    Classid = yml['classID']
    if name in Classid:
        return str(Classid[name])
    else:
        url = yml['mcmod-api'] + name.lower() # api非公开，请私聊重生
        try:
            res = requests.get(url)
        except requests.exceptions.RequestException as e:
            log.error(e)
            log.error("获取百科 Class ID 失败，请检查配置文件与网络连接")
            exit(1)
        r = re.findall(r'class\/(\d+)', res.text)
        r_name = re.findall(r'\((.+?\)?)\)', res.text)
        if len(r) > 0 and (len(r_name) == 0 or r_name[-1] == name):
            log.info(f"获取百科 Class ID: {res.text}")
            # key = input() # 鉴于结果不准确的二次验证
            # if key == '':
            #     return r[0]
            # else:
            #     return key
            return r[0]
        else:
            log.error(f"未找到 {name} 的 mc百科 classID，请手动输入")
            class_id = input()
            Classid[name] = int(class_id)
            with open('id.yml', 'w', encoding='utf-8') as f:
                yaml.dump(yml, f)
            return class_id

def upload(cookie, file, classID, mcverList, platformList, apiList, tagList):
    start = time.time()
    url = 'https://modfile.mcmod.cn/action/upload/'
    headers = { 'Cookie': cookie }
    file1 = open('mods/'+file, 'rb')
    form = {
        'file1': file1,
        'classID': (None, classID),
        'mcverList': (None, mcverList),
        'platformList': (None, platformList),
        'apiList': (None, apiList),
        'tagList': (None, tagList)
    }
    response = requests.post(url, headers=headers, files=form)
    msg = json.loads(response.text[3:])
    try:
        if msg['success']['upload']:
            log.info(f"文件 {file} 上传成功，{time.time()-start:.1f} s")
        elif msg['success']['update']:
            log.info(f"文件 {file} 覆盖成功，{time.time()-start:.1f} s")
        else:
            log.error(f"文件 {file} 上传失败，服务器返回信息如下：")
            log.error(str(msg))
    except KeyError:
        log.error(f"文件 {file} 上传失败，服务器返回信息如下：")
        log.error(str(msg))
        if str(msg) == "{'state': 101}":
            log.error("请检查 cookie 是否过期，程序即将退出...")
            exit(1)
    file1.close()
    # os.unlink('mods/'+file)

def getCookie(username, password):
    url = "https://www.mcmod.cn/action/doLogin/"
    payload = rf"data=%7B%22username%22%3A%22{username}%22%2C%22password%22%3A%22{password}%22%2C%22remember%22%3A0%2C%22captcha%22%3A%22%22%7D"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.mcmod.cn/"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    cookies = response.headers['Set-Cookie']
    match = re.search(r"_uuid=[\w-]+", cookies)
    if match:
        return match.group(0)
    else:
        return None