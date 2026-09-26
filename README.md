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
- Windows 10/11 或 Linux

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
