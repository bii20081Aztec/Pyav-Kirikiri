Pyav-Kirikiri
一个用 PyAV + NumPy 写的视频播放器，自己平时折腾着玩的。
名字里的 Kirikiri 算是致敬，FFmpeg 也是。

核心就是：PyAV 负责解码，NumPy 负责处理帧数据，剩下的就是把它跑起来。

这项目大概率不会有什么商业软件想用。
真要用的话，遵守 LGPL 就行。

功能
播放视频

PyAV 解码

NumPy 处理帧数据

功能不多，主要就是自己用。

需要什么环境
运行环境
Python 3.12

Windows 10/11

推荐 Windows，因为代码里有些地方直接写了路径，没做跨平台适配。

编译器 / 构建工具
这个项目本身是纯 Python，不需要你额外装 C/C++ 编译器。
但如果你要自己打包成 exe，需要下面这些：

Python 3.12（必须，别的版本没试过）

pip（装依赖用）

PyInstaller（打包 exe 用）

PyAV 和 NumPy（运行依赖）

PyAV 自带 FFmpeg 相关二进制，正常装 wheel 就行，不需要你自己去编译 FFmpeg。
如果你装的是源码包而不是 wheel，那才需要 C 编译器，Windows 上一般是：

Visual Studio Build Tools（勾选 “使用 C++ 的桌面开发”）

或者完整版 Visual Studio

但正常情况下，直接 pip install pyav numpy 就会装 wheel，不用管编译器。

运行和打包
1. 装依赖
powershell
python -m pip install pyav numpy
如果 Python 没加进 PATH，用完整路径，例如：

powershell
%LOCALAPPDATA%\Programs\Python\Python312\python.exe -m pip install pyav numpy
2. 装 PyInstaller
powershell
python -m pip install pyinstaller
或者：

powershell
%LOCALAPPDATA%\Programs\Python\Python312\python.exe -m pip install pyinstaller
3. 先直接跑一下
powershell
python PyavKirikiri.py
4. 打包 exe
powershell
python -m PyInstaller -F -w --clean --name "Pyav Kirikiri" PyavKirikiri.py
打包完 exe 在当前目录的 dist 里：

text
dist\Pyav Kirikiri.exe
build 文件夹和 Pyav Kirikiri.spec 是打包过程生成的，可以删。

5. 如果闪退
去掉 -w 再打包一次，留控制台看报错：

powershell
python -m PyInstaller -F --clean --name "Pyav Kirikiri" PyavKirikiri.py
已知情况
路径写死过，换机器可能要改。

没做跨平台，Windows 下最稳。

播放功能比较基础，别指望它能替代成熟播放器。

License
LGPL-2.1。

简单说：改了库的代码就按 LGPL 开源；动态链接、闭源用随便你。

完整文本见 LICENSE。

第三方依赖
依赖	协议	版权
PyAV (av)	BSD-3-Clause	Copyright (c) Mike Boers and contributors
NumPy	BSD-3-Clause	Copyright (c) 2005-2025, NumPy Developers
PyInstaller	GPL-2.0 + 商业构建例外	Copyright (c) 2013-2026, PyInstaller Development Team
FFmpeg (bundled via PyAV)	LGPL-2.1+	Copyright (c) FFmpeg developers
详细声明见 THIRD_PARTY_LICENSES.txt。

这版里已经明确写了：

纯 Python 项目，正常不需要额外 C/C++ 编译器

要打包 exe 需要 Python 3.12 + pip + PyInstaller

PyAV 正常装 wheel，不需要自己编译 FFmpeg

只有装源码包时才需要 Visual Studio Build Tools / Visual Studio
