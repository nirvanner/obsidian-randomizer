import sys
import os
import random
import re
import subprocess
import winreg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextBrowser, QFrame, QMessageBox, QDialog, QCheckBox, QSlider, QSpinBox, QFileDialog, QGroupBox, QFormLayout
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
import json

DEFAULT_VAULT_PATH = os.path.expanduser("~/Documents/Obsidian Vault")
CONFIG_FILE = "obsidian_randomizer_config.json"
IMG_FOLDER = "png-files"

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"vault_path": DEFAULT_VAULT_PATH}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass

def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "Obsidian Randomizer")
        winreg.CloseKey(key)
        return True
    except:
        return False

def enable_autostart():
    try:
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        exe_path = os.path.join(script_dir, 'dist', 'obsidian_randomizer.exe')
        
        if not os.path.exists(exe_path):
            exe_path = os.path.join(script_dir, 'obsidian_randomizer.exe')
        
        if not os.path.exists(exe_path):
            exe_path = os.path.abspath(sys.argv[0])
        
        if not os.path.exists(exe_path):
            return False
            
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "Obsidian Randomizer", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        return True
    except:
        return False

def disable_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
        winreg.DeleteValue(key, "Obsidian Randomizer")
        winreg.CloseKey(key)
        return True
    except:
        return True

def parse_markdown(text, vault_path):
    text = re.sub(r'^#{1,6}\s+(.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{2,6}\s+(.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{3,6}\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{4,6}\s+(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{5,6}\s+(.+)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{6}\s+(.+)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
    
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    text = re.sub(r"==(.+?)==", r"<span style='background-color:#555555; color:#fff; padding:2px;'>\1</span>", text)
    
    def img_repl(match):
        img_name = match.group(1)
        img_path = os.path.join(vault_path, IMG_FOLDER, img_name)
        if os.path.exists(img_path):
            return f"<img src='{img_path.replace(os.sep, '/')}' style='width:100%; height:auto; max-width:100%;'/><br>"
        return f"<span style='color:#f55;'>[Нет изображения: {img_name}]</span>"
    text = re.sub(r"!\[\[(.+?)\]\]", img_repl, text)
    text = re.sub(r"(?<!\!)\[\[([^\]]*)\]\]", r"\1", text)
    return text.replace('\n', '<br>')

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Настройки Obsidian Randomizer")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(25, 26, 30))
        palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
        palette.setColor(QPalette.Base, QColor(35, 37, 41))
        palette.setColor(QPalette.Text, QColor(230, 230, 230))
        palette.setColor(QPalette.Button, QColor(45, 47, 51))
        palette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        autostart_group = QGroupBox("Автозапуск")
        autostart_group.setStyleSheet("QGroupBox { font-weight: bold; color: #fff; font-family: 'Segoe UI', sans-serif; font-size: 13px; }")
        autostart_layout = QVBoxLayout()
        
        self.autostart_checkbox = QCheckBox("Запускать при старте Windows")
        self.autostart_checkbox.setChecked(is_autostart_enabled())
        self.autostart_checkbox.setStyleSheet("QCheckBox { color: #ddd; font-family: 'Segoe UI', sans-serif; } QCheckBox::indicator { width: 16px; height: 16px; }")
        autostart_layout.addWidget(self.autostart_checkbox)
        autostart_group.setLayout(autostart_layout)
        
        display_group = QGroupBox("Отображение")
        display_group.setStyleSheet("QGroupBox { font-weight: bold; color: #fff; font-family: 'Segoe UI', sans-serif; font-size: 13px; }")
        display_layout = QFormLayout()
        
        self.always_on_top_checkbox = QCheckBox("Всегда поверх других окон")
        self.always_on_top_checkbox.setChecked(self.parent.always_on_top if self.parent else False)
        self.always_on_top_checkbox.setStyleSheet("QCheckBox { color: #ddd; font-family: 'Segoe UI', sans-serif; } QCheckBox::indicator { width: 16px; height: 16px; }")
        
        pin_label = QLabel("Закрепить окно:")
        pin_label.setStyleSheet("color: #fff; font-weight: bold; font-family: 'Segoe UI', sans-serif;")
        display_layout.addRow(pin_label, self.always_on_top_checkbox)
        
        display_group.setLayout(display_layout)
        
        vault_group = QGroupBox("Хранилище Obsidian")
        vault_group.setStyleSheet("QGroupBox { font-weight: bold; color: #fff; font-family: 'Segoe UI', sans-serif; font-size: 13px; }")
        vault_layout = QVBoxLayout()
        
        config = load_config()
        self.vault_path_label = QLabel(self.parent.vault_path if self.parent else config.get("vault_path", DEFAULT_VAULT_PATH))
        self.vault_path_label.setStyleSheet("color: #999; font-size: 10px; padding: 6px; background: #404244; border: 1px solid #555; border-radius: 3px; font-family: 'Segoe UI', sans-serif;")
        self.vault_path_label.setWordWrap(True)
        
        self.change_vault_btn = QPushButton("Изменить путь")
        self.change_vault_btn.setStyleSheet("QPushButton{background-color:#7c3aed;color:#fff;border:1px solid #8b5cf6;border-radius:3px;font-size:12px;font-weight:bold;padding:8px;font-family:'Segoe UI',sans-serif}QPushButton:hover{background-color:#8b5cf6}QPushButton:pressed{background-color:#6d28d9}")
        self.change_vault_btn.clicked.connect(self.change_vault_path)
        
        vault_layout.addWidget(self.vault_path_label)
        vault_layout.addWidget(self.change_vault_btn)
        vault_group.setLayout(vault_layout)
        
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setStyleSheet("QPushButton{background-color:#404244;color:#ddd;border:1px solid #555;border-radius:3px;font-size:12px;font-weight:bold;padding:8px}QPushButton:hover{background-color:#505254}QPushButton:pressed{background-color:#606264}")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setStyleSheet("QPushButton{background-color:#404244;color:#ddd;border:1px solid #555;border-radius:3px;font-size:12px;font-weight:bold;padding:8px}QPushButton:hover{background-color:#505254}QPushButton:pressed{background-color:#606264}")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(autostart_group)
        layout.addWidget(display_group)
        layout.addWidget(vault_group)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def change_vault_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку Obsidian хранилища")
        if folder:
            self.vault_path_label.setText(folder)

    def save_settings(self):
        config = load_config()
        
        if self.autostart_checkbox.isChecked():
            enable_autostart()
        else:
            disable_autostart()
        
        if self.parent:
            self.parent.always_on_top = self.always_on_top_checkbox.isChecked()
            if self.always_on_top_checkbox.isChecked():
                self.parent.setWindowFlags(self.parent.windowFlags() | Qt.WindowStaysOnTopHint)
            else:
                self.parent.setWindowFlags(self.parent.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.parent.show()
        
        config["vault_path"] = self.vault_path_label.text()
        save_config(config)
        
        if self.parent:
            self.parent.vault_path = self.vault_path_label.text()
            self.parent.find_md_files()
        
        self.accept()

class ObsidianWidget(QWidget):
    def __init__(self, vault_path):
        super().__init__()
        self.vault_path = vault_path
        self.md_files = []
        self.history = []
        self.history_index = -1
        self.current_file_path = None
        self.scale_factor = 1.0
        self.always_on_top = False
        
        self.find_md_files()
        self.init_ui()
        self.show_random_note()

    def find_md_files(self):
        self.md_files = []
        if os.path.exists(self.vault_path):
            for root, dirs, files in os.walk(self.vault_path):
                for file in files:
                    if file.endswith('.md'):
                        self.md_files.append(os.path.join(root, file))

    def init_ui(self):
        self.setWindowTitle("Obsidian Randomizer")
        self.setMinimumSize(250, 150)
        self.resize(400, 300)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(25, 26, 30))
        palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(4, 4, 4, 4)
        
        top_layout = QHBoxLayout()
        
        self.path_label = QLabel("")
        self.path_label.setStyleSheet("color: #999; font-size: 10px; font-family: 'Segoe UI', sans-serif;")
        self.path_label.setWordWrap(True)
        
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(28, 28)
        settings_btn.setStyleSheet("QPushButton{background-color:#404244;color:#ddd;border:1px solid #555;border-radius:3px;font-size:16px;font-weight:bold}QPushButton:hover{background-color:#505254}QPushButton:pressed{background-color:#606264}")
        settings_btn.clicked.connect(self.open_settings)
        
        top_layout.addWidget(self.path_label)
        top_layout.addWidget(settings_btn)
        
        self.name_label = QLabel("")
        self.name_label.setStyleSheet("color: #fff; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', sans-serif; margin: 2px 0;")
        self.name_label.setWordWrap(True)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setStyleSheet("background:#232428;color:#ddd;border:none;font-size:12px;font-family:'Times New Roman',Times,serif;line-height:1.2")
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.wheelEvent = self.wheel_event
        
        nav_layout = QHBoxLayout()
        
        prev_btn = QPushButton("←")
        prev_btn.setFixedSize(30, 25)
        prev_btn.setStyleSheet("QPushButton{background-color:#404244;color:#ddd;border:1px solid #555;border-radius:3px;font-size:14px;font-weight:bold}QPushButton:hover{background-color:#505254}QPushButton:pressed{background-color:#606264}")
        prev_btn.clicked.connect(self.show_prev_note)
        
        random_btn = QPushButton("🎲")
        random_btn.setFixedSize(30, 25)
        random_btn.setStyleSheet("QPushButton{background-color:#7c3aed;color:#fff;border:1px solid #8b5cf6;border-radius:3px;font-size:14px;font-weight:bold}QPushButton:hover{background-color:#8b5cf6}QPushButton:pressed{background-color:#6d28d9}")
        random_btn.clicked.connect(self.show_random_note)
        
        next_btn = QPushButton("→")
        next_btn.setFixedSize(30, 25)
        next_btn.setStyleSheet("QPushButton{background-color:#404244;color:#ddd;border:1px solid #555;border-radius:3px;font-size:14px;font-weight:bold}QPushButton:hover{background-color:#505254}QPushButton:pressed{background-color:#606264}")
        next_btn.clicked.connect(self.show_next_note)
        
        obsidian_btn = QPushButton("Obsidian")
        obsidian_btn.setFixedSize(60, 25)
        obsidian_btn.setStyleSheet("QPushButton{background-color:#404244;color:#ddd;border:1px solid #555;border-radius:3px;font-size:10px;font-weight:bold}QPushButton:hover{background-color:#505254}QPushButton:pressed{background-color:#606264}")
        obsidian_btn.clicked.connect(self.open_in_obsidian)
        
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(random_btn)
        nav_layout.addWidget(next_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(obsidian_btn)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.name_label)
        layout.addWidget(self.text_browser)
        layout.addLayout(nav_layout)
        
        self.setLayout(layout)

    def wheel_event(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale_factor = min(self.scale_factor + 0.1, 2.0)
            else:
                self.scale_factor = max(self.scale_factor - 0.1, 0.5)
            
            if self.current_file_path:
                self.display_note(self.current_file_path)
        else:
            QTextBrowser.wheelEvent(self.text_browser, event)

    def open_in_obsidian(self):
        if not self.current_file_path:
            return
        
        rel_path = os.path.relpath(self.current_file_path, self.vault_path)
        rel_path_without_ext = os.path.splitext(rel_path)[0]
        obsidian_url = f"obsidian://open?vault=Obsidian%20Vault&file={rel_path_without_ext.replace(os.sep, '%2F')}"
        try:
            os.startfile(obsidian_url)
        except:
            try:
                subprocess.run(['cmd', '/c', 'start', obsidian_url], shell=True, check=True)
            except:
                pass

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        if self.always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def show_note_by_index(self, idx):
        if 0 <= idx < len(self.history):
            file_path = self.history[idx]
            self.display_note(file_path)
            self.history_index = idx

    def show_random_note(self):
        if not self.md_files:
            self.text_browser.setText("В хранилище нет .md файлов.")
            return
        file_path = random.choice(self.md_files)
        if self.history_index == -1 or (self.history and self.history[self.history_index] != file_path):
            self.history = self.history[:self.history_index+1]
            self.history.append(file_path)
            self.history_index += 1
        self.display_note(file_path)

    def show_next_note(self):
        if self.history_index < len(self.history) - 1:
            self.show_note_by_index(self.history_index + 1)
        else:
            self.show_random_note()

    def show_prev_note(self):
        if self.history_index > 0:
            self.show_note_by_index(self.history_index - 1)

    def display_note(self, file_path):
        self.current_file_path = file_path
        rel_path = os.path.relpath(file_path, self.vault_path)
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        path_parts = rel_path.replace(os.sep, '/').split('/')
        if path_parts[0] == "Obsidian Vault":
            path_parts = path_parts[1:]
        if path_parts and path_parts[-1].endswith('.md'):
            path_parts[-1] = os.path.splitext(path_parts[-1])[0]
        
        clean_path = '/'.join(path_parts)
        self.path_label.setText(clean_path)
        self.name_label.setText(file_name_without_ext)
        
        with open(file_path, "r", encoding="utf-8") as f:
            md_text = f.read()
        
        scaled_font_size = int(12 * self.scale_factor)
        css_styles = f"""
        background:#232428;color:#ddd;border:none;font-size:{scaled_font_size}px;font-family:'Times New Roman',Times,serif;line-height:1.2;
        h1 {{ font-size: {int(24 * self.scale_factor)}px; font-weight: bold; color: #fff; margin: 6px 0; }}
        h2 {{ font-size: {int(20 * self.scale_factor)}px; font-weight: bold; color: #fff; margin: 5px 0; }}
        h3 {{ font-size: {int(18 * self.scale_factor)}px; font-weight: bold; color: #fff; margin: 4px 0; }}
        h4 {{ font-size: {int(16 * self.scale_factor)}px; font-weight: bold; color: #fff; margin: 3px 0; }}
        h5 {{ font-size: {int(14 * self.scale_factor)}px; font-weight: bold; color: #fff; margin: 2px 0; }}
        h6 {{ font-size: {int(13 * self.scale_factor)}px; font-weight: bold; color: #fff; margin: 2px 0; }}
        """
        self.text_browser.setStyleSheet(css_styles)
        
        html = parse_markdown(md_text, self.vault_path)
        self.text_browser.setHtml(html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    icon_path = None
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "icon.ico"),
        os.path.join(os.path.dirname(__file__), "dist", "icon.ico"),
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "icon.ico"),
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "dist", "icon.ico"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            icon_path = path
            break
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))
    
    config = load_config()
    vault_path = config.get("vault_path", DEFAULT_VAULT_PATH)
    
    widget = ObsidianWidget(vault_path)
    widget.show()
    sys.exit(app.exec_())