# ChatGPT 模型锁定器

Windows 上的小型悬浮工具，为 **Chat / 聊天**和 **Work / 工作**分别保存模型与思考程度，并通过 Edge 扩展检测和纠正网页选择。

## 安装与更新

在 [GitHub Releases](https://github.com/UNO1742/chatgpt-model-keeper/releases/latest) 下载 `ModelKeeper-Setup.exe`，安装后会显示可拖动的小圆球。点击圆球打开设置；设置中的“检查更新”读取本仓库的最新稳定 Release，下载后校验 GitHub 提供的 SHA-256，再运行安装程序。

- Windows 10/11 x64；安装针对当前用户，无需管理员权限。
- 首次安装默认登录自启；更新保留已有的开关选择。
- 首次显示原始球体需要下载约 134 KiB 的版本固定渲染资源；校验后本地缓存。后续可离线显示。
- 当前构建使用 Qt WebEngine 实时运行原始 Horizon 控制器，不使用预录动画或定时回放；保留原始时间推进、纹理和 WebGL 着色器。球体处于等待状态，不接入或采集麦克风音量。
- 安装包包含浏览器渲染引擎，体积较旧版增大。

## “浏览器扩展安装”是什么？

浏览器安全限制下，桌面程序需要配套扩展来操作普通网页标签页。**仅运行悬浮球并不能调整网页模型。**

首次点击设置中的“浏览器扩展安装”，按向导执行：

1. 在 Edge 打开 `edge://extensions`。
2. 开启开发人员模式，选择“加载解压缩的扩展”。
3. 使用向导提供的“复制扩展路径”或“打开文件夹”，选择含 `manifest.json` 的 `extension` 文件夹。
4. 刷新 ChatGPT。连接后，设置中的状态会显示“已连接”。

**安装成功后不需要反复打开文件夹。** 这是首次加载和排障入口，与软件更新分开。此版本未上架 Edge 商店，不会静默强制安装浏览器扩展；企业策略若禁止开发人员扩展，需要管理员按组织政策部署。

## 使用

点击圆球，在带滑动过渡的聊天／工作标签中分别设置模型和思考程度，点击“保存设置”。模型必须与对应模式菜单里的完整名称匹配。中英文强度均适配；“极高 / Extra high”和单独显示的“Max”分别处理。

扩展约每 3 秒读取设置，等待用户空闲后检查当前可见页面；稳定情况下每 60 秒复核。用户输入、生成回复或打开菜单时会推迟。无法确认模式、模型不可用或档位不支持时会显示原因，不能解锁套餐权限。程序不会发送消息，也不会改变已发出的消息使用的模型。

## 数据与权限

配置、悬浮位置、状态及图形资源缓存在本机安装目录。Native Messaging 接口只允许固定的配套扩展 ID。扩展不上传聊天内容、Cookie 或浏览历史；更新检查不需要 GitHub 账户或 Token。

桌面渲染页面由仅绑定 `127.0.0.1` 的随机本地端口提供，使用随机路径、Host 校验和文件白名单；没有外部监听。该页面只承载本机 UI 和绘制资源，不加载 ChatGPT 登录页。浏览器与本机程序的模型控制仍走 Native Messaging。

原始图形资源不发布进本仓库或安装包，不适用本项目 MIT 许可证。来源和固定摘要见 `runtime_manifest.json`，组件说明见 [THIRD_PARTY.md](THIRD_PARTY.md)。本项目与 OpenAI 无隶属关系。

## 构建

需要 Windows x64、Python 3.13、Inno Setup 6/7。

```powershell
python -m pip install -r requirements-build.txt
./build.ps1 -InnoCompiler 'C:/Program Files (x86)/Inno Setup 6/ISCC.exe'
```

输出为 `release/ModelKeeper-Setup.exe` 和 `release/SHA256SUMS.txt`。Native Messaging 主机是单独的小型程序，不会每次连接都加载或解压浏览器引擎。

推送 `v*` 标签后，GitHub Actions 会构建并发布安装程序。发布版本号需要同步更新 `app.py` 与 `installer.iss`。

开发验证：`python -m unittest discover -s tests -p test_services.py`；网页适配验证需要安装 Playwright 与 Chromium 后运行 `python tests/test_adapter.py`。GUI 可用 `python app.py --gui-smoke <报告路径>` 验证实时绘制计数和截图。发布前还应执行独立 Windows 用户的安装、Native Messaging 与跨电脑验收。
