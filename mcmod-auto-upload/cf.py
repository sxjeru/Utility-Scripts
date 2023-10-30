import requests
import time
from utils import *
from log import log
from mcmod import getClassid, yaml

headers = { 'x-api-key': 'XXXXXXXXXXXXX' } # https://docs.curseforge.com/#authentication
proxy = { 'http': 'http://localhost:1080', 'https': 'http://localhost:1080' }

with open('id.yml', 'r', encoding='utf-8') as f:
    yml = yaml.load(f)

def getModid(name):
    if name in yml['projectID']:
        return str(yml['projectID'][name])

    url = "https://api.curseforge.com/v1/mods/search"
    # slug = name.lower().replace(" ", "-")
    slug = name
    # TODO: slug 还可从邮件直接获取 (已实现)
    params = { 'gameId': 432, "sortOrder": "desc", 'slug': slug, 'classId': 6 }
    response = requests.get(url, params=params, headers=headers, proxies=proxy).json()
    if len(response['data']) > 0:
        # if response['data'][0]['name'].strip() == name:
        if response['data'][0]['slug'].strip() == slug:
            pjid = response['data'][0]['id']
        else:
            log.debug(f"slug 无解，尝试按名称搜索")
    else:
        log.debug(f"slug 无解，尝试按名称搜索")
    name = response['data'][0]['name'].strip()
    return pjid, name # 一般 slug 必有解，后续基本可省略 (有空再改)

    rename = name.replace(" ", "%2520") # 空格处理
    params = { 
        'gameId': 432, "sortOrder": "desc", 
        'searchFilter': rename, 
        # 'slug': slug, # 建议换用 slug
        'classId': 6 }
    response = requests.get(url, params=params, headers=headers, proxies=proxy).json()
    for i in range(len(response['data'])):
        # if response['data'][i]['name'].strip() == name:
        if response['data'][i]['slug'].strip() == slug:
            return response['data'][i]['id']
    
    log.error(f"未找到 {name} 的 CurseForge ProjectID，请手动输入")
    pjid = input()
    yml['projectID'][name] = int(pjid)
    with open('id.yml', 'w', encoding='utf-8') as f:
        yaml.dump(yml, f)
    return pjid

def getMod(name):
    modid, name = getModid(name)
    log.debug(f"{name} 开始下载")
    start = time.time()
    url = f"https://api.curseforge.com/v1/mods/{modid}/files"
    res = requests.get(url, headers=headers, proxies=proxy).json()['data']
    redownload = dl_sum = 0
    flag = 1
    files = []
    class_id = getClassid(name)
    sameVers = [] # 同版本文件只取最新
    for i in range(len(res)):
        file = res[i]
        if not within30h(file['fileDate']):
            if flag:
                log.info(f"{name} 无新文件，已跳过")
            else:
                spend_time = time.time() - start
                log.info(f"{name} 共下载 {dl_sum} 个文件，{spend_time:.1f} s")
            break
        if file['gameVersions'] in sameVers:
            log.info(f"有相同版本存在，{file['fileName']} 已忽略")
            continue
        else:
            sameVers.append(file['gameVersions'].copy()) # 注意列表可变，需复制
        flag = 0
        if file['downloadUrl'] == None:
            file_id = str(file['id'])
            dl_url = f"https://edge.forgecdn.net/files/{file_id[:4]}/{file_id[-3:]}/{file['fileName']}"
            download(dl_url, proxy)
        else:
            download(file['downloadUrl'], proxy)
        # if not md5('mods/'+file['fileName'], file['hashes'][1]['value']):
        #     redownload += 1
        #     if redownload > 3:
        #         log.error(f"{file['fileName']} 多次尝试仍校验失败，已跳过")
        #         continue
        #     log.error(f"{file['fileName']} 校验失败，第 {redownload} 次重试...")
        #     i -= 1
        #     continue
        # redownload = 0
        log.debug(f"{file['fileName']} 校验成功")
        uploadInfo = getInfo(file, class_id)
        files.append(uploadInfo)
        dl_sum += 1
    return files