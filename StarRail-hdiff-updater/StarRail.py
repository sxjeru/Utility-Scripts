# 1. 解压 hdiff 并覆盖游戏根目录
# 2. 确保本脚本与 hpatchz.exe 同在游戏根目录
import os, re, glob, json, hashlib, time
import msvcrt
start = time.time()

if os.path.exists("deletefiles.txt"):
    with open("deletefiles.txt", 'r') as f:
        for line in f.readlines():
            try:
                os.remove(line.strip())
            except Exception as e:
                print(f"Error: {e}")
else:
    print('"deletefiles.txt" not found!\n\nPress any key to exit...')
    msvcrt.getch()
    exit(1)
print("Delete done! ({:.2f}s)\n".format(time.time() - start))
os.remove("deletefiles.txt")

hd = []
if os.path.exists("hdifffiles.txt"): # deprecated in 3.0
    with open("hdifffiles.txt", 'r') as f:
        for line in f.readlines():
            hd.append(re.findall(r'"(.*?)"', line)[1])
    for i in hd:
        os.system("hpatchz.exe -f " + i + " " + i + ".hdiff " + i)
        os.remove(i + ".hdiff")
    print("\nPatch done! ({:.2f}s)\n".format(time.time() - start))
    os.remove("hdifffiles.txt")
    # md5 verification
    hdpath = os.path.dirname(hd[0])
    md5txt = glob.glob(os.path.join(hdpath, 'AudioV_*'))
    with open(md5txt[0], 'r') as f:
        for line in f.readlines():
            path = os.path.join(hdpath, json.loads(line)['Path'])
            with open(path, 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            if md5 != json.loads(line)['Md5']:
                print("有文件校验失败：" + path + "\n\nPress any key to exit...")
                msvcrt.getch()
                exit(1)
    print("md5 verification completed, all files are correct.\nUpdate done! ({:.2f}s)\n".format(time.time() - start))
    print("Press any key to exit...")
    msvcrt.getch()

elif os.path.exists("hdiffmap.json"):
    with open("hdiffmap.json", 'r') as f:
        t = json.load(f)
        for i in range(len(t['diff_map'])):
            hd.append(t['diff_map'][i])
    for diff in hd:
        with open(diff['source_file_name'], 'rb') as f:
            md5_1 = hashlib.md5(f.read()).hexdigest()
        if md5_1 != diff['source_file_md5']:
            print("有原始文件校验失败：" + diff['source_file_name'] + "\n\nPress any key to exit...")
            msvcrt.getch()
            exit(1)
        with open(diff['patch_file_name'], 'rb') as f:
            md5_2 = hashlib.md5(f.read()).hexdigest()
        if md5_2 != diff['patch_file_md5']:
            print("有更新文件校验失败：" + diff['patch_file_name'] + "\n\nPress any key to exit...")
            msvcrt.getch()
            exit(1)
        os.system("hpatchz.exe -f " + diff['source_file_name'] + " " + diff['patch_file_name'] + " " + diff['target_file_name'])
        os.remove(diff['patch_file_name'])
        if diff['source_file_name'] != diff['target_file_name']:
            os.remove(diff['source_file_name'])
        with open(diff['target_file_name'], 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        if md5 != diff['target_file_md5']:
            print("有最终文件校验失败：" + diff['target_file_name'] + "\n\nPress any key to exit...")
            msvcrt.getch()
            exit(1)
    print("\nPatch done!")
    os.remove("hdiffmap.json")
    print("md5 verification has been completed at the same time, all files are CORRECT.\nUpdate done! ({:.2f}s)\n".format(time.time() - start))
    print("Press any key to exit...")
    msvcrt.getch()

else:
    print("hdiff file not found!\n\nPress any key to exit...")
    msvcrt.getch()
    exit(1)
