# Pyav-Kirikiri

一个用 PyAV + NumPy 写的视频播放器，自己平时折腾着玩的。  
名字里的 Kirikiri 算是致敬，FFmpeg 也是。

> 这项目大概率不会有什么商业软件想用。  
> 真要用的话，遵守 LGPL 就行。

## Features

- 视频播放
- PyAV 解码
- NumPy 处理帧数据

## Requirements

- Python 3.12
- Windows 7/10/11 或 Linux

## Windows 7 兼容说明

虽然官方 Python 3.12 不支持 Windows 7，但本项目经过实测，可以在 Windows 7 SP1 上运行。

前提条件：
- 必须安装 VxKex（或类似的 Win7 扩展内核兼容层）
- 锁定 Python 3.12
- 使用兼容版本的 PyAV 和 NumPy
- 推荐使用 PyInstaller 打包发布

如果不使用 VxKex，Windows 7 下可能无法正常启动或解码。
Windows 下最稳，代码里有些路径没做跨平台适配。  
Linux 下也能跑，建议直接跑源码，成品限制比较多。

### 编译器 / 构建工具

项目本身是纯 Python，正常不需要额外 C/C++ 编译器。  
要打包的话需要：

- Python 3.12
- pip
- PyInstaller
- PyAV、NumPy

PyAV 正常装 wheel 即可，不需要自己编译 FFmpeg。  
只有装源码包时才需要 C 编译器：

- Windows：Visual Studio Build Tools（勾选“使用 C++ 的桌面开发”）
- Linux：`build-essential`（Debian/Ubuntu）
