# 建议事先将每日更新邮件转发到非常用邮箱，既保证隐私安全，又可避免 Gmail 的【邮件过长折叠】。

import poplib
from email import parser
import re, time
from collections import OrderedDict
from .log import log
from .mcmod import yaml
from .utils import getMailDate
import quopri # 解码 MIME

with open('config.yml', 'r', encoding='utf-8') as f:
    yml = yaml.load(f)

def getMail(tpe):
    pop_server = yml['mail-pop-server']
    username = yml['mail-username']
    password = yml['mail-password']
    start = time.time()
    pop_conn = poplib.POP3_SSL(pop_server)
    pop_conn.user(username)
    pop_conn.pass_(password)
    num_emails = len(pop_conn.list()[1])

    emails = []
    for i in range(num_emails, 0, -1): # num_emails-1 则解析第二封 (实际是全局第二封，逻辑上有误)
        lines = pop_conn.retr(i)[1]
        msg = b'\n'.join(lines).decode('utf-8')
        msg = parser.Parser().parsestr(msg)
        sj = "What's been happening at CurseForge"
        # sj = "Fwd: What's been happening at CurseForge"
        if msg['subject'] == sj:
            emails.append(msg)
            if len(emails) == yml['mail-id']:
                break

    modNames = []
    for email in emails[-1:]: # TODO: 批量解析前几封邮件，目前只解析第 n 封
        body = email.get_payload()[tpe] # 0: plain text, 1: html
        body = quopri.decodestring(str(body)).decode('utf-8')

        # with open('email.txt', 'w+', encoding='utf-8') as file:
        #     file.write(body)
        # exit()

        if tpe == 0: # 得到 mod 名称
            match = re.findall(r'There are new files in (.+)\.', body)
        elif tpe == 1: # 得到 slug
            match = re.findall(r'new files in <a href="https:\/\/www\.curseforge\.com\/minecraft\/mc-mods\/(.+?)"', body) # 2024.1.16 之前为 legacy
        modNames.extend(match)
        modNames = list(OrderedDict.fromkeys(modNames)) # 去重
    pop_conn.quit()
    log.info(f"解析邮件成功，共 {len(modNames)} 个 mod，{time.time()-start:.1f} s")
    match = re.findall(r'<h2 style="text-decoration: underline;">(.+)</h2>', body)
    log.info(f"邮件日期：{getMailDate(match)}")
    log.debug(modNames)
    return modNames
