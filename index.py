import sys
import subprocess
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie, QCursor
from PyQt5.QtCore import Qt, QPoint
import keyboard
import random
import math

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class UpdateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.progress = 0
        self.time_elapsed = 0
        self.kill_explorer()
        self.initUI()
        # 添加一个变量来跟踪退出组合键序列（严格按照组合键的顺序）
        self.exit_sequence = []
        self.required_sequence = ["ctrl", "shift", "alt", "esc"]
        
    def kill_explorer(self):
        try:
            # 关闭资源管理器
            subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'])
        except Exception as e:
            print(f"无法关闭 explorer.exe: {e}")
            
    def restore_explorer(self):
        try:
            # 恢复资源管理器
            subprocess.Popen(['explorer.exe'])
        except Exception as e:
            print(f"无法启动 explorer.exe: {e}")
            
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        self.setWindowOpacity(1.0)
        
        # 禁用常见系统快捷键
        if is_admin():
            try:
                keyboard.block_key('tab')
                keyboard.block_key('windows')
                keyboard.block_key('ctrl+alt+esc')
                keyboard.block_key('alt+esc')
                keyboard.block_key('alt+space')
                keyboard.block_key('alt+enter')
                keyboard.block_key('alt+prtsc')
                keyboard.block_key('alt+end')
                keyboard.block_key('alt+home')
                keyboard.block_key('alt+insert')
                keyboard.block_key('alt+delete')
                keyboard.block_key('alt+pageup')
                keyboard.block_key('alt+pagedown')
                keyboard.block_key('alt+left')
                keyboard.block_key('alt+right')
                keyboard.block_key('alt+up')
                keyboard.block_key('alt+down')
            except Exception as e:
                print(f"无法屏蔽系统快捷键: {e}")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 80)
        
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(20)
        
        self.loading_label = QLabel()
        self.loading_label.setFixedSize(159, 95)
        self.movie = QMovie("./static/images/loading.gif")
        self.movie.setScaledSize(self.loading_label.size())
        self.loading_label.setMovie(self.movie)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setContentsMargins(80, 0, 0, 0)
        
        self.movie.start()
        
        self.text_label = QLabel("正在进行更新 0%\n请保持计算机打开状态。")
        self.text_label.setStyleSheet("color: white; font-size: 24px; font-family: 'Microsoft YaHei', 'SimHei';")
        self.text_label.setAlignment(Qt.AlignCenter)
        
        container_layout.addWidget(self.loading_label)
        container_layout.addWidget(self.text_label)
        
        main_layout.addStretch(1)
        main_layout.addWidget(container_widget, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)
        
        self.bottom_label = QLabel("计算机可能会重启几次")
        self.bottom_label.setStyleSheet("color: white; font-size: 22px; font-family: 'Microsoft YaHei', 'SimHei';")
        self.bottom_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(self.bottom_label)
        
        # 隐藏鼠标
        self.setCursor(QCursor(Qt.BlankCursor))
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateProgress)
        # self.timer.start(random.randint(3000, 10000))     # 随机3-10更新
        self.timer.start(1000)  # 每秒更新一次
        
        # 设置退出快捷键
        keyboard.add_hotkey('ctrl+alt+esc', self.close)
        
        # 替换简单的热键设置，改用更严格的按键检测
        # keyboard.on_press(self.check_exit_key)
        
    def updateProgress(self):
        if self.progress < 99:
            self.time_elapsed += 1
            # 使用对数函数来减缓进度增长速度
            progress_increment = max(0.1, 1.0 / (1 + math.log(self.time_elapsed + 1, 2)))
            self.progress = min(99, self.progress + progress_increment)
            self.text_label.setText(f"正在进行更新 {int(self.progress)}%\n请保持计算机打开状态。")
            
            # 随机暂停一段时间
            if random.random() < 0.1:  # 10% 的概率
                self.timer.setInterval(random.randint(3000, 8000))
            else:
                self.timer.setInterval(1000)
                
    def closeEvent(self, event):
        if is_admin():
            try:
                keyboard.unblock_all()
            except Exception as e:
                print(f"无法恢复系统快捷键: {e}")
        self.restore_explorer()
        event.accept()
        
    def keyPressEvent(self, event):
        event.ignore()
        return
            
    def check_exit_key(self, event):
        key = event.name.lower()
        if key in ["ctrl", "shift", "alt", "esc"]:
            expected_key = self.required_sequence[len(self.exit_sequence)] if len(self.exit_sequence) < len(self.required_sequence) else None
            
            if key == expected_key:
                self.exit_sequence.append(key)
                # 如果完成了整个序列，关闭应用
                if self.exit_sequence == self.required_sequence:
                    self.close()
            else:
                # 如果按键顺序错误，重置序列
                self.exit_sequence = []
                if key == self.required_sequence[0]:
                    self.exit_sequence.append(key)
        else:
            # 如果按下了其他键，重置序列
            self.exit_sequence = []
            
if __name__ == '__main__':
    if not is_admin():
        # 如果不是管理员权限，则请求管理员权限重新运行
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    app = QApplication(sys.argv)
    window = UpdateWindow()
    sys.exit(app.exec_())
