### mc百科 文件自动更新

本脚本实现自动从 CurseForge 获取当日更新并上传至 mc百科。

请前往 [Releases](https://github.com/sxjeru/Utility-Scripts/releases/tag/1.0) 下载。

用法：
1. `config.yml` 补全配置文件；
2. 运行 `main-gui.py`，自动在浏览器中打开网页 GUI；
3. 单击“开始”按钮，待右侧mod上传，依次确认文件上传情况，从而完成更新。

- 若取消勾选“自动遍历”，则需手动点击“继续”按钮；
- 日志会输出到网页、控制台以及目录中的 `app.log` 文件。

每次mod更新完毕，请务必前往该mod后台检查文件信息是否正确，并手动排序。

TODO: 支持 Modrinth，支持新mod上传，支持自动排序。

## mc百科部分 API

也可以参考 [mcmod.py](https://github.com/sxjeru/Utility-Scripts/blob/main/mcmod-auto-upload/mcmod.py)，即 API 在 Python 下的一种实现方式。

### 文件上传
- Cookie 有效期 30天，可从下面的登录 API 获取，或直接从已登录百科的浏览器复制。
- 可一次上传多个文件，按 file1、file2 的顺序。
- xxxList 的值中**逗号前后不得有空格**。
- classID，即 mod 在百科的编号。
- mcverList 会将原始文本直接上传。
- platformList，支持平台，1 = JAVA版，2 = 基岩版。
- apiList，运作方式，1=Forge，2=Fabric，11=Quilt，13=Neo Forge，3=Rift，4=LiteLoader……
- tagList，文件标签，可选 snapshot，beta，client，server，dev，lite.

```Shell
curl --request POST \
  --url https://modfile-dl.mcmod.cn/action/upload/ \
  --header 'Content-Type: multipart/form-data' \
  --header 'Cookie: _uuid=xxxxxx' \
  --form 'file1=@C:\Users\Eru\Desktop\mods\appleskin-fabric-mc1.16.5-2.5.1.jar' \
  --form classID=2 \
  --form mcverList=1.99.1/1.126.1 \
  --form platformList=1 \
  --form 'apiList=1,3' \
  --form 'tagList=beta,client'
```

### 登录
注意 mc百科存在多设备登录限制，为避免顶掉浏览器端登录状态，可前往“个人中心 -> 设置 -> 安全设置”修改。

需要的 Cookie 为 _uuid.

若短时间密码错误次数超过 3 次，会要求验证码，大概等待 30 分钟后可再次尝试。

```Shell
curl --request POST \
  --url https://www.mcmod.cn/action/doLogin/ \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --header 'Referer: https://www.mcmod.cn/' \
  --data 'data={"username":"admin","password":"admin","remember":0,"captcha":""}'
```
