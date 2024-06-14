from datetime import datetime, timedelta, timezone
import requests, os, hashlib, re, msvcrt
from urllib.parse import unquote
from .log import log
from .mcmod import yaml
from collections import OrderedDict

with open('config.yml', 'r', encoding='utf-8') as f:
    yml = yaml.load(f)

def withinHours(time_str):
    formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]
    for fmt in formats:
        try:
            time = datetime.strptime(time_str, fmt)
            break
        except ValueError:
            pass
    diff = datetime.now(timezone.utc).replace(tzinfo=None) - time
    return diff < timedelta(hours=16 + 24 * yml['mail-id']) # 40 h + n days

def download(file_url, proxy):
    filename = unquote(os.path.basename(file_url))
    if os.path.exists('mods/'+filename):
        log.info(f"{filename} 本地已存在，将被覆盖")
    try:
        log.info(f'{filename} 开始下载')
        response = requests.get(file_url, proxies=proxy)
        if response.status_code == 200:
            with open('mods/'+filename, 'wb') as file:
                file.write(response.content)
            log.debug(f"{filename} 下载完成")
        else:
            log.error(f"{filename} 下载时出错，状态码：{response.status_code}")
    except Exception as e:
        # log.error(f"{filename} 下载时出错：{e}")
        raise Exception(f"{filename} 下载时出错：{e}")

def dlRetry(file_url, proxy, max_retries=3):
    for i in range(max_retries):
        try:
            download(file_url, proxy)
            break
        except Exception as e:
            log.error(f"下载失败，第 {i+1} 次重试...")
            if i == max_retries-1:
                raise Exception(f"{file_url} 下载失败：{e}")

def md5(filename, md5):
    md5_hash = hashlib.md5()
    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest() == md5

def sha512(filename, sha512):
    sha512_hash = hashlib.sha512()
    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha512_hash.update(chunk)
    return sha512_hash.hexdigest() == sha512

def getInfo(file, class_id):
    isSnap = 0
    lst = []
    lst.append(file['fileName'])
    lst.append(class_id)
    ver, snap = [], []
    for item in file['gameVersions']:
        if re.match(r"^\d.+", item):
            if item.find('Snapshot') != -1: # 处理快照版本号
                snap.append(snapVer(file, item))
                isSnap = 1
            else:
                ver.append(item)
    versions = trimVer(ver, snap)
    if not versions:
        lst.append('版本号为空')
    else:
        lst.append(versions)
    lst.append(trimVer(ver, snap))
    lst.append(1) # 平台默认JAVA版
    lst.append(getAPI(file['gameVersions']))
    lst.append(getTag(file, isSnap))
    return lst

def trimVer(vers, snap):
    def sort_key(version):
        return [int(part) for part in version.split('.')]
    vers = sorted(vers, key=sort_key)
    r = ''

    def repeat(vers):
        repeat = [0] * 30 # 支持到 1.29.x
        for ver in vers:
            repeat[int(ver.split('.')[1])] += 1
        return repeat

    rep = [0, 0,0,0,0,0, 0,0,0,5,3, 3,3,3,5,3, 6,2,3,5,7, 0] 
    # 如第一个5，从头(0)开始数为第9个，即 1.9 共有5个版本，即读到5个 1.9.x 版本后自动合并为一个 “1.9.x”

    def mergeVer(lst, ver):
        mid = ver.split('.')[1]
        vers = [f"1.{mid}"]
        for i in range(1, rep[int(mid)]):
            vers.append(f"1.{mid}.{i}")
        for ver in vers:
            if ver in lst:
                lst.remove(ver)
        return f"1.{mid}.x", lst

    lst_rep = repeat(vers)
    # while True:
    #     if len(vers) == 0:
    #         break
    #     for ver in vers:
    while len(vers) > 0:
        ver = vers[0]
        mid = int(ver.split('.')[1])
        if lst_rep[mid] == rep[mid]:
            t, vers = mergeVer(vers, ver)
            r += f"{t}/"
            # break
        else:
            r += f"{ver}/"
            vers.remove(ver)

    r_lst = r.split('/')
    r_lst = list(OrderedDict.fromkeys(r_lst)) # 去重
    r = "/".join(r_lst)

    for ver in snap:
        if ver != '':
            r += f"{ver}/"
    return r[:-1]

def snapVer(file, snap): # 手动适配快照, 注意 displayName 与 fileName 差异
    modid = file['modId']
    if modid == 349239: # Carpet v1.4.114 for 23w32a
        return file['displayName'].split(" ")[-1]
    if modid == 306612: # [1.20.2-rc1/2] Fabric API 0.88.5+1.20.2
        r = re.search(r"\[(.+)\]", file['displayName']) # match 匹配开头，如果开头有空格的话...
        return r.group(1)
    if modid == 419699: # [Fabric 23w40a] v11.0.1 (Architectury API)
        return file['displayName'].split(" ")[1][:-1]
    if modid == 538881: # 13.6 (for 20w14infinite)
        return file['displayName'].split(" ")[-1][:-1]
    # if
    else:
        log.error(f"{file['displayName']} | {snap} 请手动填入快照版本")
        return input()

def purgeAPI(info):
    if 'Client' in info:
        info.remove('Client')
    if 'Server' in info:
        info.remove('Server')
    pattern = re.compile(r'^\d+.*')
    info[:] = [item for item in info if not pattern.match(item)]
    return info

def getAPI(info):
    info = purgeAPI(info)
    r = ''
    if 'Forge' in info:
        r += '1,'
        info.remove('Forge')
    if 'Fabric' in info:
        r += '2,'
        info.remove('Fabric')
    if 'Quilt' in info:
        r += '11,'
        info.remove('Quilt')
    if 'NeoForge' in info:
        r += '13,'
        info.remove('NeoForge')
    if 'Rift' in info:
        r += '3,'
        info.remove('Rift')
    if 'LiteLoader' in info:
        r += '4,'
        info.remove('LiteLoader')
    if len(info) > 0:
        log.error(f"{info} 请手动填入'运作方式'")
        r = r + input() + ','
    return r[:-1]

def getTag(file, isSnap):
    r = ''
    if file['releaseType'] in [2, 3]: # 2 - beta, 3 - alpha
        if isSnap:
            r += 'snapshot,'
        else:
            r += 'beta,'
    if 'Client' in file['gameVersions']:
        if 'Server' not in file['gameVersions']:
            r += 'client,'
    elif 'Server' in file['gameVersions']:
        r += 'server,'
    return r[:-1]

def checkConfig(yml, required_fields=["cookie", "cf-api-key", "mail-pop-server", "mail-username", "mail-password", "mail-id"]):
    for field in required_fields:
        if field not in yml or not yml[field]:
            log.error("配置文件不完整，请前往 config.yml 确认。按任意键退出程序...")
            msvcrt.getch()
            exit(1)
    hash_object = hashlib.sha256(yml["mcmod-api"].encode('utf-8'))
    if hash_object.hexdigest() != "aaa065afa21ab95d050bac43c1dae768d3ade7b7746df1b093fe84862004c306":
        log.error("请填写正确的 mcmod 搜索 API")
        msvcrt.getch()
        exit(1)
