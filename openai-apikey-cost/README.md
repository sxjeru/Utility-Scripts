- 由于按天查询计费 API 存在访问速率限制，本脚本会生成一个 "cost id.json" 文件用来记录历史日期的 Cost；
- 本脚本还会给出一个 "records.csv" 用以记录每次查询的 key序号、总费用、查询时间；
- 如果需要使用 HTTP 代理，请记得修改 "main.py" 行 28-29 端口号。

https://github.com/sxjeru/Utility-Scripts/blob/4d2202c2eb9d005b3772d417df8bc54395bea39e/openai-apikey-cost/main.py#L27-L30
