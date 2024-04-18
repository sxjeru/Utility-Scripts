import eel
from withGUI.mail import *
from withGUI.cf import *
from withGUI.mcmod import *
from withGUI.utils import *
from ruamel.yaml import YAML

eel.init('eel', allowed_extensions=['.js', '.html'])

if not os.path.exists("mods"):
    os.makedirs("mods")
    log.info("已创建 mods 文件夹")

yaml=YAML()
try:
    with open('config.yml', 'r', encoding='utf-8') as f:
        yml = yaml.load(f)
except FileNotFoundError:
    log.error("配置文件 config.yml 不存在")
    exit(1)
checkConfig(yml) # 检查配置文件必填项

cookie = yml['cookie']
# cookie = getCookie('username', 'password')

modList = getMail(1)
eel.createTable(modList)
# i = 0 # 跳过前 i 个

@eel.expose
def main():
    log.info("==== 开始 / 继续 ====")
    global i
    i += 1
    mod = modList[i-1]
    files = getMod(mod)
    if len(files) == 0 and i < len(modList): # 无新文件，自动跳过
        log.info(f"[{i}/{len(modList)}] 自动跳过...")
        eel.update(i, len(modList), 2)
        main()
        return
    for file in reversed(files):
        log.info(str(file))
        upload(cookie, *file)
    mcmodURL = "https://modfile.mcmod.cn/admin/" + file[1] + '/'
    eel.urlRow(i, mcmodURL) # 表格添加后台链接
    # eel.mcmod(mcmodURL) # 跨域无法访问
    if i < len(modList):
        log.info(f"[{i}/{len(modList)}] 点击继续...")
        eel.update(i, len(modList), 1)
    else:
        log.info(f"[{i}/{len(modList)}] 已更新所有 mod")
        eel.update(i, len(modList), 1)
    return 

@eel.expose
def start():
    global i
    opt1 = int(eel.option()()['opt1'])
    opt2 = eel.option()()['opt2']
    i = opt1
    if opt2:
        while i < len(modList):
            main()
    else:
        main()
eel.start('index.html', mode='default')
