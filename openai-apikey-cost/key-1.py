# 本脚本目前不需要账号密码即可统计某个 key 在某一时段内的总 Cost。
# 可复制多个本文件以统计多个 apikey 计费，保证序号唯一。

from main import *
import datetime

headers = {"Authorization": f"Bearer sk-xxxxxx"} # 需手动填入
serial = 1 # apikey 序号

# 从 2023-10-01 至今的总 Cost
cost = get_costs(datetime.date(2023, 10, 1), datetime.datetime.now().date(), serial, headers)
if cost != None:
	cost = round(cost, 6)
	print('\n', cost)
	update_records(serial, cost)

import msvcrt
msvcrt.getch()
