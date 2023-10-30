from cf import *
from mcmod import *
from utils import *
from mail import *

if not os.path.exists("mods"):
    os.makedirs("mods")
    log.info("已创建 mods 文件夹")

cookie = 'XXXXXX'
# cookie = getCookie('username', 'password')

modList = getMail(1)
# modList = []

i = 0

for mod in modList:
    i += 1
    if i <= 0: # 跳过前 i 个 mod
        continue
    files = getMod(mod)
    if len(files) == 0 and i < len(modList): # 无新文件，自动跳过
        print(f"[{i}/{len(modList)}] 继续更新...")
        continue
    for file in reversed(files):
        log.info(file)
        upload(cookie, *file)
    if i < len(modList):
        input(f"[{i}/{len(modList)}] 按回车继续...") # 单步
    else:
        print(f"[{i}/{len(modList)}] 已更新所有 mod")
        import msvcrt
        msvcrt.getch() # 任意键退出
