# -*- coding: utf-8 -*-
"""
DVB.py  —  NEKOPARA 风格 MP4 播放器
后端：PyAV (FFmpeg) + sounddevice (音频)
界面：PyQt5
"""

import sys
import os
import time
import threading

import numpy as np
import av
import sounddevice as sd

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog, QListWidget,
    QFrame, QMenuBar, QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QImage, QPixmap, QDesktopServices


# ============================================================
# 语言表
# ============================================================
LANG = {
    "zh": {
        "title":        "大聪明播放器 - Kirikiri 风格",
        "menu_file":    "档案",
        "menu_open":    "打开文件...",
        "menu_add":     "添加到播放列表...",
        "menu_exit":    "退出",
        "menu_screen":  "画面",
        "menu_full":    "全屏",
        "menu_size":    "窗口",
        "menu_ratio":   "宽高比",
        "menu_lang":    "语言",
        "menu_lang_zh": "简体中文",
        "menu_lang_en": "English",
        "menu_tools":   "工具",
        "menu_setting": "设置",
        "menu_hotkey":  "快捷键",
        "menu_help":    "说明",
        "menu_about":   "关于",
        "menu_home":    "作者主页",
        "menu_bili":    "B站主页",
        "menu_github":  "GitHub",
        "btn_open":     "打开文件",
        "btn_play":     "播放",
        "btn_pause":    "暂停",
        "btn_stop":     "停止",
        "btn_add":      "添加文件",
        "btn_clear":    "清空列表",
        "list_title":   "播放列表",
        "status_ready": "就绪 (PyAV 后端)",
        "status_loaded":"已加载: {}",
        "status_adding": "已添加 {} 个文件",
        "status_playing":"正在播放: {}",
        "about_text":   "大聪明播放器 (PyAV 后端)\nKIRIKIRI风格\n基于 DeepSeek Tongyi Qianwen 编写",
        "setting_title":      "设置",
        "setting_vol_up":     "增大音量",
        "setting_vol_down":   "减小音量",
        "setting_vol_cur":    "当前音量: {}%",
        "setting_disable_hk": "禁用快捷键",
        "setting_enable_hk":  "启用快捷键",
        "setting_hk_enabled": "快捷键已启用",
        "setting_hk_disabled":"快捷键已禁用",
        "hotkey_title":       "快捷键说明",
        "hotkey_play":        "播放",
        "hotkey_pause":       "暂停",
        "hotkey_mute":        "静音",
        "hotkey_vol_up":      "音量增大",
        "hotkey_vol_down":    "音量减小",
        "ratio_43":           "4:3",
        "ratio_169":          "16:9",
        "msg_ratio_set":      "宽高比已切换为: {}",
        "msg_muted":          "已静音",
        "msg_unmuted":        "已取消静音",
        "msg_vol_up":         "音量增大: {}%",
        "msg_vol_down":       "音量减小: {}%",
        "file_filter":        "视频文件 (*.mp4 *.avi *.mkv);;音频文件 (*.flac *.ogg *.mp3);;所有文件 (*.*)",
    },
    "en": {
        "title":        "Smart Player - Kirikiri Style",
        "menu_file":    "File",
        "menu_open":    "Open File...",
        "menu_add":     "Add to Playlist...",
        "menu_exit":    "Exit",
        "menu_screen":  "Screen",
        "menu_full":    "Fullscreen",
        "menu_size":    "Window",
        "menu_ratio":   "Aspect Ratio",
        "menu_lang":    "Text Language",
        "menu_lang_zh": "简体中文",
        "menu_lang_en": "English",
        "menu_tools":   "Tools",
        "menu_setting": "Settings",
        "menu_hotkey":  "Hotkeys",
        "menu_help":    "Help",
        "menu_about":   "About",
        "menu_home":    "Author Home",
        "menu_bili":    "Bilibili",
        "menu_github":  "GitHub",
        "btn_open":     "Open",
        "btn_play":     "Play",
        "btn_pause":    "Pause",
        "btn_stop":     "Stop",
        "btn_add":      "Add",
        "btn_clear":    "Clear",
        "list_title":   "Playlist",
        "status_ready": "Ready (PyAV backend)",
        "status_loaded":"Loaded: {}",
        "status_adding": "Added {} file(s)",
        "status_playing":"Playing: {}",
        "about_text":   "Smart Player (PyAV backend)\nKIRIKIRI style\nBased on DeepSeek Tongyi Qianwen",
        "setting_title":      "Settings",
        "setting_vol_up":     "Volume Up",
        "setting_vol_down":   "Volume Down",
        "setting_vol_cur":    "Current Volume: {}%",
        "setting_disable_hk": "Disable Hotkeys",
        "setting_enable_hk":  "Enable Hotkeys",
        "setting_hk_enabled": "Hotkeys enabled",
        "setting_hk_disabled":"Hotkeys disabled",
        "hotkey_title":       "Hotkey Reference",
        "hotkey_play":        "Play",
        "hotkey_pause":       "Pause",
        "hotkey_mute":        "Mute",
        "hotkey_vol_up":      "Volume Up",
        "hotkey_vol_down":    "Volume Down",
        "ratio_43":           "4:3",
        "ratio_169":          "16:9",
        "msg_ratio_set":      "Aspect ratio set to: {}",
        "msg_muted":          "Muted",
        "msg_unmuted":        "Unmuted",
        "msg_vol_up":         "Volume up: {}%",
        "msg_vol_down":       "Volume down: {}%",
        "file_filter":        "Video (*.mp4 *.avi *.mkv);;Audio (*.flac *.ogg *.mp3);;All Files (*.*)",
    },
}

AUTHOR_HOME = "https://space.bilibili.com/1685065897"
PLACEHOLDER_LINKS = {
    "bili":   "https://space.bilibili.com/1685065897",
    "github": "https://github.com/bii20081Aztec/Pyav-Kirikiri",
}


# ============================================================
# 音频播放线程（sounddevice 是阻塞写，放独立线程里）
# ============================================================
class AudioPlayer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.stream = None
        self.buffer = []
        self.lock = threading.Lock()
        self.running = True
        self.volume = 0.8
        self.paused = False
        self._start_stream()

    def _start_stream(self):
        # 先用默认采样率开一个流，拿到实际参数后再改
        self.stream = sd.OutputStream(
            samplerate=48000, channels=2, dtype='float32',
            callback=self._callback, blocksize=1024
        )
        self.stream.start()

    def _callback(self, outdata, frames, time_info, status):
        with self.lock:
            if self.paused or len(self.buffer) == 0:
                outdata.fill(0)
                return
            # 从 buffer 里取数据
            need = frames
            chunk = []
            while need > 0 and self.buffer:
                buf = self.buffer[0]
                if len(buf) <= need:
                    chunk.append(buf)
                    need -= len(buf)
                    self.buffer.pop(0)
                else:
                    chunk.append(buf[:need])
                    self.buffer[0] = buf[need:]
                    need = 0
            if chunk:
                data = np.concatenate(chunk, axis=0)
            else:
                data = np.zeros((frames, 2), dtype='float32')

            # 补齐 / 截断到 frames
            if len(data) < frames:
                pad = np.zeros((frames - len(data), 2), dtype='float32')
                data = np.concatenate([data, pad], axis=0)
            elif len(data) > frames:
                data = data[:frames]

            outdata[:] = np.clip(data * self.volume, -1.0, 1.0)

    def push(self, samples):
        """samples: numpy float32 形状 (N, 2)"""
        samples = np.ascontiguousarray(samples, dtype=np.float32)
        with self.lock:
            # 缓冲满时丢最旧块(滑动窗口), 保证音频连续; 不能整块丢弃新数据, 否则会造成爆裂/撕裂声
            while len(self.buffer) > 240:  # 大约 5 秒音频
                self.buffer.pop(0)
            self.buffer.append(samples)

    def set_volume(self, v):
        self.volume = max(0.0, min(5.0, v))

    def set_pause(self, p):
        self.paused = p

    def clear(self):
        with self.lock:
            self.buffer.clear()

    def stop(self):
        self.running = False
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass


# ============================================================
# 主窗口
# ============================================================
class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.lang = "zh"
        self.current_file = None
        self.is_playing = False
        self.volume = 80
        self.start_time = 0.0
        self.pause_time = 0.0
        self.duration = 0.0
        self.audio = AudioPlayer()
        self.muted = False
        self._prev_volume = self.volume
        self.aspect_ratio = None        # None = 自适应, "4:3", "16:9"
        self.hotkeys_enabled = True     # 快捷键默认启用
        self.decode_thread = None
        self.decode_stop = threading.Event()
        self._pending = 0           # 已解码但还没显示的帧数
        self._pending_lock = threading.Lock()
        self._max_pending = 60       # 最多领先主线程 2 帧

        self.setGeometry(100, 100, 1000, 700)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(self.get_win32_style())

        self.setup_menu()
        self.setup_ui()
        self.apply_language()

        # 画面刷新定时器
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._poll_frame)
        self.frame_timer.start(30)

        # 进度条定时器
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(200)

    # --------------------------------------------------------
    def get_win32_style(self):
        return """
            QMainWindow { background-color: #ECE9D8; }
            QPushButton {
                background-color: #F0F0F0;
                border: 1px solid #A0A0A0;
                padding: 5px 10px;
                min-width: 60px;
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 11px;
            }
            QPushButton:hover   { background-color: #E5E5E5; }
            QPushButton:pressed { background-color: #C0C0C0; }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 6px;
                background: #E0E0E0;
            }
            QSlider::handle:horizontal {
                background: #C0C0C0;
                border: 1px solid #5c5c5c;
                width: 12px;
                margin: -4px 0;
            }
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #A0A0A0;
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 11px;
            }
            QListWidget::item:selected {
                background-color: #C0C0C0;
                color: black;
            }
            QLabel {
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 11px;
            }
            QMenuBar {
                background-color: #F0F0F0;
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 12px;
            }
            QMenuBar::item:selected { background-color: #C0C0C0; }
            QMenu {
                background-color: #F0F0F0;
                border: 1px solid #A0A0A0;
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 12px;
            }
            QMenu::item:selected { background-color: #C0C0C0; }
        """

    # --------------------------------------------------------
    def setup_menu(self):
        menubar = self.menuBar()

        self.m_file = menubar.addMenu("")
        self.a_open = QAction("", self)
        self.a_open.triggered.connect(self.open_file)
        self.m_file.addAction(self.a_open)
        self.a_add = QAction("", self)
        self.a_add.triggered.connect(self.add_to_playlist)
        self.m_file.addAction(self.a_add)
        self.m_file.addSeparator()
        self.a_exit = QAction("", self)
        self.a_exit.triggered.connect(self.close)
        self.m_file.addAction(self.a_exit)

        self.m_screen = menubar.addMenu("")
        self.a_full  = QAction("", self)
        self.a_full.triggered.connect(self.toggle_fullscreen)
        self.a_size  = QAction("", self)
        self.a_size.triggered.connect(self.set_window_mode)

        # 宽高比 → 子菜单
        self.m_ratio = QMenu("")
        self.a_ratio_43  = QAction("", self)
        self.a_ratio_43.triggered.connect(lambda: self.set_aspect_ratio("4:3"))
        self.a_ratio_169 = QAction("", self)
        self.a_ratio_169.triggered.connect(lambda: self.set_aspect_ratio("16:9"))
        self.m_ratio.addAction(self.a_ratio_43)
        self.m_ratio.addAction(self.a_ratio_169)
        self.m_screen.addAction(self.a_full)
        self.m_screen.addAction(self.a_size)
        self.m_screen.addMenu(self.m_ratio)

        self.m_lang = menubar.addMenu("")
        self.a_lang_zh = QAction("", self)
        self.a_lang_zh.triggered.connect(lambda: self.set_language("zh"))
        self.a_lang_en = QAction("", self)
        self.a_lang_en.triggered.connect(lambda: self.set_language("en"))
        self.m_lang.addAction(self.a_lang_zh)
        self.m_lang.addAction(self.a_lang_en)

        self.m_tools = menubar.addMenu("")
        self.a_setting = QAction("", self)
        self.a_setting.triggered.connect(self.show_settings)
        self.a_hotkey = QAction("", self)
        self.a_hotkey.triggered.connect(self.show_hotkeys)
        self.m_tools.addAction(self.a_setting)
        self.m_tools.addAction(self.a_hotkey)

        self.m_help = menubar.addMenu("")
        self.a_about = QAction("", self)
        self.a_about.triggered.connect(self.show_about)
        self.m_help.addAction(self.a_about)
        self.m_help.addSeparator()

        self.a_home = QAction("", self)
        self.a_home.triggered.connect(lambda: self.open_url(AUTHOR_HOME))
        self.m_help.addAction(self.a_home)
        self.m_help.addSeparator()

        self.a_bili   = QAction("", self)
        self.a_github = QAction("", self)
        self.a_bili.triggered.connect(
            lambda: self.open_url(PLACEHOLDER_LINKS["bili"]))
        self.a_github.triggered.connect(
            lambda: self.open_url(PLACEHOLDER_LINKS["github"]))
        self.m_help.addAction(self.a_bili)
        self.m_help.addAction(self.a_github)

    # --------------------------------------------------------
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(3, 3, 3, 3)
        outer.setSpacing(0)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # 左：播放列表
        left_panel = QWidget()
        left_panel.setMaximumWidth(250)
        left_layout = QVBoxLayout(left_panel)

        self.list_label = QLabel("")
        self.list_label.setAlignment(Qt.AlignCenter)
        self.list_label.setStyleSheet(
            "font-weight: bold; padding: 5px; background-color: #D4D0C8;")

        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_selected)

        self.btn_add   = QPushButton("")
        self.btn_clear = QPushButton("")
        self.btn_add.clicked.connect(self.add_to_playlist)
        self.btn_clear.clicked.connect(self.playlist.clear)

        left_layout.addWidget(self.list_label)
        left_layout.addWidget(self.playlist, 1)
        left_layout.addWidget(self.btn_add)
        left_layout.addWidget(self.btn_clear)

        # 右：视频 + 控制
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.video_label = QLabel()
        self.video_label.setStyleSheet(
            "background-color: black; border: 1px solid #A0A0A0;")
        self.video_label.setMinimumHeight(400)
        self.video_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.video_label, 1)

        controls = QHBoxLayout()
        self.btn_open  = QPushButton("")
        self.btn_play  = QPushButton("")
        self.btn_pause = QPushButton("")
        self.btn_stop  = QPushButton("")
        self.btn_open.clicked.connect(self.open_file)
        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.sliderMoved.connect(self.seek)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(100)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 500)
        self.volume_slider.setValue(self.volume)
        self.volume_slider.setMaximumWidth(80)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.volume_label = QLabel("🔊")

        controls.addWidget(self.btn_open)
        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_pause)
        controls.addWidget(self.btn_stop)
        controls.addWidget(self.time_slider, 1)
        controls.addWidget(self.time_label)
        controls.addWidget(self.volume_label)
        controls.addWidget(self.volume_slider)

        right_layout.addLayout(controls)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

        outer.addLayout(main_layout, 1)

        # 底部条
        self.bottom_bar = QWidget()
        self.bottom_bar.setFixedHeight(26)
        self.bottom_bar.setStyleSheet("""
            QWidget#BottomBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #F5F5F5, stop:1 #D8D8D8);
                border-top: 1px solid #A0A0A0;
            }
            QLabel#BottomText {
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 11px;
                color: #333333;
                padding-left: 8px;
            }
        """)
        self.bottom_bar.setObjectName("BottomBar")
        bar_layout = QHBoxLayout(self.bottom_bar)
        bar_layout.setContentsMargins(0, 0, 8, 0)
        self.bottom_text = QLabel("")
        self.bottom_text.setObjectName("BottomText")
        bar_layout.addWidget(self.bottom_text)
        bar_layout.addStretch(1)

        outer.addWidget(self.bottom_bar)

    # --------------------------------------------------------
    def tr(self, key):
        return LANG.get(self.lang, LANG["zh"]).get(key, key)

    def set_language(self, lang):
        if lang in LANG:
            self.lang = lang
            self.apply_language()

    def apply_language(self):
        t = self.tr
        self.setWindowTitle(t("title"))

        # 标题 + action，用 getattr 兜底，缺哪个都不崩
        for attr, key in [
            ("m_file", "menu_file"), ("m_screen", "menu_screen"),
            ("m_lang", "menu_lang"), ("m_tools", "menu_tools"),
            ("m_help", "menu_help"),
        ]:
            obj = getattr(self, attr, None)
            if obj is not None:
                obj.setTitle(t(key))

        for attr, key in [
            ("a_open", "menu_open"), ("a_add", "menu_add"),
            ("a_exit", "menu_exit"), ("a_full", "menu_full"),
            ("a_size", "menu_size"),
            ("a_lang_zh", "menu_lang_zh"), ("a_lang_en", "menu_lang_en"),
            ("a_setting", "menu_setting"), ("a_hotkey", "menu_hotkey"),
            ("a_about", "menu_about"), ("a_home", "menu_home"),
            ("a_bili", "menu_bili"), ("a_github", "menu_github"),
        ]:
            obj = getattr(self, attr, None)
            if obj is not None:
                obj.setText(t(key))

        for attr, key in [
            ("btn_open", "btn_open"), ("btn_play", "btn_play"),
            ("btn_pause", "btn_pause"), ("btn_stop", "btn_stop"),
            ("btn_add", "btn_add"), ("btn_clear", "btn_clear"),
            ("list_label", "list_title"), ("bottom_text", "status_ready"),
        ]:
            obj = getattr(self, attr, None)
            if obj is not None:
                obj.setText(t(key))

        # 子菜单和子项
        if hasattr(self, 'm_ratio'):
            self.m_ratio.setTitle(t("menu_ratio"))
        if hasattr(self, 'a_ratio_43'):
            self.a_ratio_43.setText(t("ratio_43"))
        if hasattr(self, 'a_ratio_169'):
            self.a_ratio_169.setText(t("ratio_169"))

    # --------------------------------------------------------
    # 播放核心
    # --------------------------------------------------------
    def _stop_decode(self):
        self.decode_stop.set()
        if self.decode_thread and self.decode_thread.is_alive():
            self.decode_thread.join(timeout=1.0)
        self.decode_thread = None
        self.audio.clear()
        with self._pending_lock:
            self._pending = 0

    def _start_decode(self, file_path, start_time=0.0):
        self._stop_decode()
        self.decode_stop.clear()

        # 读元信息
        try:
            container = av.open(file_path)
            v_stream = container.streams.video[0]
            v_stream.thread_type = 'AUTO'
            a_stream = container.streams.audio[0] if container.streams.audio else None
            self.duration = float(container.duration) / av.time_base if container.duration else 0.0
            self.fps = float(v_stream.average_rate) if v_stream.average_rate else 25.0
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开失败:\n{e}")
            return

        self.start_time = time.time() - start_time
        self.is_playing = True
        self.audio.set_pause(False)
        self.audio.clear()

        self.decode_thread = threading.Thread(
            target=self._decode_loop,
            args=(file_path, start_time),
            daemon=True
        )
        self.decode_thread.start()

    def _decode_loop(self, file_path, start_time):
        try:
            container = av.open(file_path)
            v_stream = container.streams.video[0]
            v_stream.thread_type = 'AUTO'
            a_stream = container.streams.audio[0] if container.streams.audio else None

            # seek
            if start_time > 0:
                offset = int(start_time * av.time_base)
                container.seek(offset, backward=True)

            # 音频重采样器
            resampler = None
            if a_stream is not None:
                resampler = av.AudioResampler(
                    format='fltp', layout='stereo', rate=48000)

            # 视频帧率控制
            frame_interval = 1.0 / self.fps
            last_frame_time = 0.0

            for packet in container.demux(v_stream, a_stream):
                if self.decode_stop.is_set():
                    break

                # 跳过不在本次 decode 里的流
                if a_stream and packet.stream == a_stream:
                    for frame in packet.decode():
                        if resampler:
                            for rframe in resampler.resample(frame):
                                arr = rframe.to_ndarray()  # fltp 平面布局: (channels, N)
                                if arr.ndim == 1:                   # 兼容单声道 (N,)
                                    arr = arr.reshape(-1, 1)
                                if arr.shape[0] in (1, 2) and arr.shape[1] not in (1, 2):
                                    arr = arr.T                     # 平面 (C,N) -> 交织 (N,C)
                                if arr.shape[1] == 1:               # 单声道补成双声道
                                    arr = np.repeat(arr, 2, axis=1)
                                arr = np.clip(arr, -1.0, 1.0)       # 限幅: 消除溢出削顶造成的爆音
                                arr = np.ascontiguousarray(arr, dtype=np.float32)
                                self.audio.push(arr)
                    continue
                if packet.stream != v_stream:
                 continue
                for frame in packet.decode():
                    if self.decode_stop.is_set():
                        return

                    # === 限流：如果主线程还没消费掉上一帧，就等 ===
                    while True:
                        with self._pending_lock:
                            if self._pending < self._max_pending:
                                break
                        if self.decode_stop.is_set():
                            return
                        time.sleep(0.005)

                    img = frame.to_ndarray(format='rgb24')
                    with self._pending_lock:
                        self._pending += 1
                    self._current_frame = (img, frame.width, frame.height)

                    # 按 PTS 等一等，让画面节奏对
                    target = self.start_time + (frame.pts * float(v_stream.time_base) if frame.pts else 0)
                    now = time.time()
                    sleep = target - now
                    if sleep > 0:
                        time.sleep(min(sleep, 0.05))

            # 播放结束
            while not self.decode_stop.is_set():
                if not self.audio.buffer:
                    break
                time.sleep(0.1)

            if not self.decode_stop.is_set():
                QTimer.singleShot(0, self.on_media_end)

        except Exception as e:
            print("解码异常:", e, flush=True)

    def _poll_frame(self):
        if not hasattr(self, "_current_frame") or self._current_frame is None:
            return
        if not self.is_playing:
            return
        img, w, h = self._current_frame

        # === 通知解码线程：我消费掉一帧了 ===
        with self._pending_lock:
            if self._pending > 0:
                self._pending -= 1
        qimg = QImage(img.data, w, h, 3 * w, QImage.Format_RGB888)
        label_size = self.video_label.size()

        if self.aspect_ratio == "4:3":
            # 按 4:3 裁切显示区域
            target_w = label_size.height() * 4 // 3
            target_h = label_size.height()
            if target_w > label_size.width():
                target_w = label_size.width()
                target_h = label_size.width() * 3 // 4
        elif self.aspect_ratio == "16:9":
            # 按 16:9 裁切显示区域
            target_w = label_size.height() * 16 // 9
            target_h = label_size.height()
            if target_w > label_size.width():
                target_w = label_size.width()
                target_h = label_size.width() * 9 // 16
        else:
            # 自适应：保持原始比例
            pix = QPixmap.fromImage(qimg).scaled(
                label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(pix)
            return

        from PyQt5.QtCore import QSize
        pix = QPixmap.fromImage(qimg).scaled(
            QSize(target_w, target_h),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(pix)

    # --------------------------------------------------------
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.tr("menu_open"), "",
            self.tr("file_filter"))
        if file_path:
            self.current_file = file_path
            self._start_decode(file_path, 0.0)
            self.bottom_text.setText(
                self.tr("status_loaded").format(os.path.basename(file_path)))
            items = [self.playlist.item(i).text()
                     for i in range(self.playlist.count())]
            if file_path not in items:
                self.playlist.addItem(file_path)

    def add_to_playlist(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, self.tr("menu_add"), "",
            self.tr("file_filter"))
        for f in files:
            self.playlist.addItem(f)
        self.bottom_text.setText(
            self.tr("status_adding").format(len(files)))

    def play_selected(self, item):
        file_path = item.text()
        if os.path.exists(file_path):
            self.current_file = file_path
            self._start_decode(file_path, 0.0)
            self.bottom_text.setText(
                self.tr("status_playing").format(os.path.basename(file_path)))

    def play(self):
        if self.current_file and not self.is_playing:
            self.is_playing = True
            self.audio.set_pause(False)
            self.start_time = time.time() - self.pause_time

    def pause(self):
        if self.is_playing:
            self.is_playing = False
            self.pause_time = time.time() - self.start_time
            self.audio.set_pause(True)

    def stop(self):
        self.is_playing = False
        self._stop_decode()
        self.video_label.clear()
        self.time_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")

    def seek(self, value):
        if not self.current_file or self.duration <= 0:
            return
        target = self.duration * value / 1000.0
        self._start_decode(self.current_file, target)

    def set_volume(self, value):
        self.volume = value
        self.audio.set_volume(value / 100.0)
        if self.muted and value > 0:
            self.muted = False
        self.volume_label.setText("🔊" if value > 0 else "🔇")

    # --------------------------------------------------------
    def update_progress(self):
        if not self.is_playing or self.duration <= 0:
            return
        elapsed = time.time() - self.start_time
        if elapsed < 0:
            elapsed = 0
        if elapsed > self.duration:
            elapsed = self.duration
        self.time_slider.setValue(int(elapsed / self.duration * 1000))
        cur = f"{int(elapsed)//60:02d}:{int(elapsed)%60:02d}"
        tot = f"{int(self.duration)//60:02d}:{int(self.duration)%60:02d}"
        self.time_label.setText(f"{cur} / {tot}")

    def on_media_end(self):
        row = self.playlist.currentRow()
        if 0 <= row < self.playlist.count() - 1:
            next_item = self.playlist.item(row + 1)
            self.playlist.setCurrentRow(row + 1)
            self.play_selected(next_item)

    # --------------------------------------------------------
    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))

    def show_about(self):
        QMessageBox.information(self, self.tr("menu_about"),
                                self.tr("about_text"))

    def dummy_action(self):
        self.bottom_text.setText("TODO")

    # --------------------------------------------------------
    # 全屏 / 窗口 / 宽高比
    # --------------------------------------------------------
    def toggle_fullscreen(self):
        """切换到全屏模式"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def set_window_mode(self):
        """切换到窗口模式"""
        if self.isFullScreen():
            self.showNormal()

    def set_aspect_ratio(self, ratio):
        """切换宽高比 (4:3 / 16:9)"""
        self.aspect_ratio = ratio
        self.bottom_text.setText(self.tr("msg_ratio_set").format(ratio))

    # --------------------------------------------------------
    # 设置弹窗
    # --------------------------------------------------------
    def show_settings(self):
        """显示设置对话框：禁用/启用快捷键、增大/减小音量"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel

        dlg = QDialog(self)
        dlg.setWindowTitle(self.tr("setting_title"))
        dlg.setFixedSize(320, 260)
        layout = QVBoxLayout(dlg)

        vol_display = QLabel(self.tr("setting_vol_cur").format(self.volume))
        vol_display.setAlignment(Qt.AlignCenter)
        vol_display.setStyleSheet("font-size: 14px; padding: 6px;")
        layout.addWidget(vol_display)

        btn_style = "font-size: 13px; padding: 8px; min-width: 200px;"

        # 禁用快捷键
        btn_disable = QPushButton(self.tr("setting_disable_hk"))
        btn_disable.setStyleSheet(btn_style)
        def on_disable_hk():
            self.hotkeys_enabled = False
            self.bottom_text.setText(self.tr("setting_hk_disabled"))
        btn_disable.clicked.connect(on_disable_hk)
        layout.addWidget(btn_disable, alignment=Qt.AlignCenter)

        # 启用快捷键
        btn_enable = QPushButton(self.tr("setting_enable_hk"))
        btn_enable.setStyleSheet(btn_style)
        def on_enable_hk():
            self.hotkeys_enabled = True
            self.bottom_text.setText(self.tr("setting_hk_enabled"))
        btn_enable.clicked.connect(on_enable_hk)
        layout.addWidget(btn_enable, alignment=Qt.AlignCenter)

        # 增大音量
        btn_vol_up = QPushButton(self.tr("setting_vol_up"))
        btn_vol_up.setStyleSheet(btn_style)
        def on_vol_up():
            self.volume = min(500, self.volume + 50)
            self.audio.set_volume(self.volume / 100.0)
            self.volume_slider.setValue(self.volume)
            vol_display.setText(self.tr("setting_vol_cur").format(self.volume))
            self.bottom_text.setText(self.tr("msg_vol_up").format(self.volume))
        btn_vol_up.clicked.connect(on_vol_up)
        layout.addWidget(btn_vol_up, alignment=Qt.AlignCenter)

        # 减小音量
        btn_vol_down = QPushButton(self.tr("setting_vol_down"))
        btn_vol_down.setStyleSheet(btn_style)
        def on_vol_down():
            self.volume = max(0, self.volume - 50)
            self.audio.set_volume(self.volume / 100.0)
            self.volume_slider.setValue(self.volume)
            vol_display.setText(self.tr("setting_vol_cur").format(self.volume))
            self.bottom_text.setText(self.tr("msg_vol_down").format(self.volume))
        btn_vol_down.clicked.connect(on_vol_down)
        layout.addWidget(btn_vol_down, alignment=Qt.AlignCenter)

        # 关闭按钮
        btn_close = QPushButton("OK")
        btn_close.clicked.connect(dlg.close)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)

        dlg.exec_()

    # --------------------------------------------------------
    # 快捷键弹窗
    # --------------------------------------------------------
    def show_hotkeys(self):
        """显示快捷键说明对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

        dlg = QDialog(self)
        dlg.setWindowTitle(self.tr("hotkey_title"))
        dlg.setFixedSize(340, 280)
        layout = QVBoxLayout(dlg)

        shortcuts = [
            ("P", self.tr("hotkey_play")),
            ("S", self.tr("hotkey_pause")),
            ("M", self.tr("hotkey_mute")),
            ("U", self.tr("hotkey_vol_up")),
            ("D", self.tr("hotkey_vol_down")),
        ]

        title_label = QLabel(self.tr("hotkey_title"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 15px; font-weight: bold; padding: 8px;")
        layout.addWidget(title_label)

        for key, desc in shortcuts:
            row = QLabel(f"  {key}    —    {desc}")
            row.setStyleSheet(
                "font-size: 13px; padding: 4px 12px; "
                "font-family: 'Consolas', 'Microsoft YaHei';")
            layout.addWidget(row)

        layout.addSpacing(10)
        btn_close = QPushButton("OK")
        btn_close.clicked.connect(dlg.close)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)

        dlg.exec_()

    # --------------------------------------------------------
    # 键盘快捷键
    # --------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        if self.hotkeys_enabled:
            if key == Qt.Key_P:
                self.play()
                return
            elif key == Qt.Key_S:
                self.pause()
                return
            elif key == Qt.Key_M:
                self.toggle_mute()
                return
            elif key == Qt.Key_U:
                self.volume_up()
                return
            elif key == Qt.Key_D:
                self.volume_down()
                return
        # Esc 始终可用：退出全屏
        if key == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
            return
        super().keyPressEvent(event)

    def toggle_mute(self):
        """切换静音"""
        if self.muted:
            self.muted = False
            self.volume = self._prev_volume
            self.audio.set_volume(self.volume / 100.0)
            self.volume_slider.setValue(self.volume)
            self.volume_label.setText("🔊")
            self.bottom_text.setText(self.tr("msg_unmuted"))
        else:
            self._prev_volume = self.volume
            self.muted = True
            self.audio.set_volume(0.0)
            self.volume_slider.setValue(0)
            self.volume_label.setText("🔇")
            self.bottom_text.setText(self.tr("msg_muted"))

    def volume_up(self):
        """音量增大（+10%）"""
        if self.muted:
            self.toggle_mute()
        self.volume = min(500, self.volume + 10)
        self.audio.set_volume(self.volume / 100.0)
        self.volume_slider.setValue(self.volume)
        self.volume_label.setText("🔊")

    def volume_down(self):
        """音量减小（-10%）"""
        if self.muted:
            self.toggle_mute()
        self.volume = max(0, self.volume - 10)
        self.audio.set_volume(self.volume / 100.0)
        self.volume_slider.setValue(self.volume)
        self.volume_label.setText("🔊" if self.volume > 0 else "🔇")
        if self.volume == 0:
            self.bottom_text.setText(self.tr("msg_muted"))

    def closeEvent(self, event):
        self.frame_timer.stop()
        self.progress_timer.stop()
        self._stop_decode()
        self.audio.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MediaPlayer()
    window.show()
    sys.exit(app.exec_())
