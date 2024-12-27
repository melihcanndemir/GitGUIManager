#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5 tabanlı basit bir Git yönetim aracı.

Bu kod, bir GUI üzerinden temel ve ileri düzey Git komutlarını
kullanabilmeyi amaçlar.
"""

import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QFileDialog,
    QMessageBox, QLineEdit, QComboBox, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor


class MaterialButton(QPushButton):
    """
    Material Design benzeri stil uygulanmış özel bir QPushButton sınıfı.
    """

    def __init__(self, text, color="#2196F3", icon=None):
        super().__init__(text)
        if icon:
            self.setIcon(icon)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, -20)};
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(color, -40)};
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                box-shadow: none;
            }}
            """
        )

    @staticmethod
    def adjust_color(color_str, amount):
        """
        Renk tonunu ayarlar. color stringini (#RRGGBB) alıp
        amount kadar daha koyu/açık hale getirir.
        """
        clr = color_str.lstrip('#')
        rgb = tuple(int(clr[i:i + 2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"


class GitGUI(QMainWindow):
    """
    Git işlemlerini kolaylaştıran bir PyQt5 arayüz sınıfı.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git GUI Manager")
        self.setMinimumSize(1000, 900)
        self.dark_mode = False
        self.current_branch = "main"  # Varsayılan branch

        # Pylint'te attribute-defined-outside-init hatalarını önlemek için
        self.remote_list = None
        self.theme_btn = None
        self.branch_label = None
        self.branch_combo = None
        self.status_label = None
        self.tabs = None

        # Bu sekmelerde kullanacağımız widget'lar
        self.remote_url_lineedit = None
        self.repo_path = None
        self.commit_msg = None
        self.output_text = None

        # Advanced sekmesiyle ilgili nitelikler
        self.new_branch_name = None
        self.delete_branch_combo = None
        self.rename_branch_combo = None
        self.new_branch_name_edit = None
        self.merge_source_combo = None
        self.merge_target_combo = None
        self.remote_name = None
        self.remote_url = None
        self.refresh_remote_btn = None
        self.branch_for_push = None
        self.force_push = None
        self.history_text = None
        self.advanced_output = None

        # Terminal sekmesiyle ilgili nitelikler
        self.terminal_output = None
        self.command_input = None

        self._setup_toolbar()
        self._setup_main_style()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        self.tabs = QTabWidget()
        self._setup_tabs()
        main_layout.addWidget(self.tabs)
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        self.init_ui()

    def _setup_toolbar(self):
        """
        Üst kısımda tema ve branch seçimi için kullanılan Toolbar ayarları.
        """
        self.toolbar = self.addToolBar("Settings")
        self.toolbar.setMovable(False)

        # Tema değiştirme butonu
        self.theme_btn = MaterialButton("🌙 Dark Mode")
        self.theme_btn.setMaximumWidth(150)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.toolbar.addWidget(self.theme_btn)

        self.toolbar.addSeparator()

        # Branch seçimi için dropdown
        self.branch_label = QLabel("Branch:")
        self.toolbar.addWidget(self.branch_label)

        self.branch_combo = QComboBox()
        self.branch_combo.addItems(["main", "master", "develop"])
        self.branch_combo.setStyleSheet(
            """
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            """
        )
        self.branch_combo.currentTextChanged.connect(self.change_branch)
        self.toolbar.addWidget(self.branch_combo)

    def _setup_main_style(self):
        """
        Ana pencere için ilk stil ayarları.
        """
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 1em;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #1976D2;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                padding: 8px;
                font-size: 14px;
            }
            """
        )

    def _setup_tabs(self):
        """
        Tab widget'ı oluşturup alt sekmeleri ekler.
        """
        basic_tab = self.create_basic_tab()
        advanced_tab = self.create_advanced_tab()
        terminal_tab = self.create_terminal_tab()
        self.tabs.addTab(basic_tab, "Basic Git Operations")
        self.tabs.addTab(advanced_tab, "Advanced Git")
        self.tabs.addTab(terminal_tab, "Live Terminal")

    def init_ui(self):
        """
        Karanlık tema paletini hazırlar (varsayılan kapalı).
        """
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def create_basic_tab(self):
        """
        'Basic Git Operations' sekmesini oluşturur.
        """
        tab = QWidget()
        layout_tab = QVBoxLayout(tab)

        # Remote repo işlemleri
        remote_group = QGroupBox("Remote Repository")
        remote_layout = QVBoxLayout()
        remote_layout.setSpacing(15)
        remote_layout.setContentsMargins(15, 20, 15, 15)

        remote_url_layout = QHBoxLayout()
        self.remote_url_lineedit = QLineEdit()
        self.remote_url_lineedit.setPlaceholderText(
            "Remote URL (e.g., https://github.com/user/repo.git)"
        )
        self.remote_url_lineedit.setMinimumHeight(40)
        remote_url_layout.addWidget(self.remote_url_lineedit)

        remote_buttons_layout = QHBoxLayout()
        remote_buttons_layout.setSpacing(10)

        add_remote_btn = MaterialButton("Add Remote", "#4CAF50")
        add_remote_btn.clicked.connect(self.add_remote)

        push_btn = MaterialButton("Push", "#2196F3")
        push_btn.clicked.connect(self.git_push)

        pull_btn = MaterialButton("Pull", "#9C27B0")
        pull_btn.clicked.connect(self.git_pull)

        remote_buttons_layout.addWidget(add_remote_btn)
        remote_buttons_layout.addWidget(push_btn)
        remote_buttons_layout.addWidget(pull_btn)

        remote_layout.addLayout(remote_url_layout)
        remote_layout.addLayout(remote_buttons_layout)
        remote_group.setLayout(remote_layout)
        layout_tab.addWidget(remote_group)

        # Repository seçimi
        repo_layout = QHBoxLayout()
        self.repo_path = QLineEdit()
        self.repo_path.setPlaceholderText("Repository path...")
        browse_btn = MaterialButton("Browse")
        browse_btn.clicked.connect(self.browse_repository)
        repo_layout.addWidget(self.repo_path)
        repo_layout.addWidget(browse_btn)
        layout_tab.addLayout(repo_layout)

        # Temel Git komutları
        init_btn = MaterialButton("Git Init")
        init_btn.clicked.connect(self.git_init)

        add_btn = MaterialButton("Git Add")
        add_btn.clicked.connect(self.git_add)

        commit_layout = QHBoxLayout()
        self.commit_msg = QLineEdit()
        self.commit_msg.setPlaceholderText("Commit message...")
        commit_btn = MaterialButton("Commit")
        commit_btn.clicked.connect(self.git_commit)
        commit_layout.addWidget(self.commit_msg)
        commit_layout.addWidget(commit_btn)

        status_btn = MaterialButton("Git Status")
        status_btn.clicked.connect(self.git_status)

        layout_tab.addWidget(init_btn)
        layout_tab.addWidget(add_btn)
        layout_tab.addLayout(commit_layout)
        layout_tab.addWidget(status_btn)

        # Çıktı alanı
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout_tab.addWidget(self.output_text)

        return tab

    def create_advanced_tab(self):
        """
        'Advanced Git' sekmesini oluşturur.
        """
        tab = QWidget()
        layout_tab = QVBoxLayout(tab)

        # Branch Yönetimi Grubu
        branch_group = QGroupBox("Branch Management")
        branch_layout = QVBoxLayout()

        # Yeni branch oluşturma
        new_branch_layout = QHBoxLayout()
        self.new_branch_name = QLineEdit()
        self.new_branch_name.setPlaceholderText("New branch name...")
        create_branch_btn = MaterialButton("Create Branch", "#4CAF50")
        create_branch_btn.clicked.connect(self.create_branch)
        new_branch_layout.addWidget(self.new_branch_name)
        new_branch_layout.addWidget(create_branch_btn)

        # Branch silme
        delete_branch_layout = QHBoxLayout()
        self.delete_branch_combo = QComboBox()
        self.delete_branch_combo.setPlaceholderText("Select branch to delete...")
        delete_branch_btn = MaterialButton("Delete Branch", "#F44336")
        delete_branch_btn.clicked.connect(self.delete_branch)
        delete_branch_layout.addWidget(self.delete_branch_combo)
        delete_branch_layout.addWidget(delete_branch_btn)

        # Branch yeniden adlandırma
        rename_layout = QHBoxLayout()
        self.rename_branch_combo = QComboBox()
        self.rename_branch_combo.setPlaceholderText("Current branch name...")
        self.new_branch_name_edit = QLineEdit()
        self.new_branch_name_edit.setPlaceholderText("New name...")
        rename_branch_btn = MaterialButton("Rename Branch", "#FF9800")
        rename_branch_btn.clicked.connect(self.rename_branch)
        rename_layout.addWidget(self.rename_branch_combo)
        rename_layout.addWidget(self.new_branch_name_edit)
        rename_layout.addWidget(rename_branch_btn)

        # Branch merge işlemleri
        merge_layout = QHBoxLayout()
        self.merge_source_combo = QComboBox()
        self.merge_source_combo.setPlaceholderText("Source branch...")
        self.merge_target_combo = QComboBox()
        self.merge_target_combo.setPlaceholderText("Target branch...")
        merge_btn = MaterialButton("Merge Branches", "#2196F3")
        merge_btn.clicked.connect(self.handle_merge_branches)
        merge_layout.addWidget(self.merge_source_combo)
        merge_layout.addWidget(QLabel("→"))
        merge_layout.addWidget(self.merge_target_combo)
        merge_layout.addWidget(merge_btn)

        branch_layout.addLayout(new_branch_layout)
        branch_layout.addLayout(delete_branch_layout)
        branch_layout.addLayout(rename_layout)
        branch_layout.addLayout(merge_layout)
        branch_group.setLayout(branch_layout)

        # Remote Yönetimi Grubu
        remote_group = QGroupBox("Remote Management")
        remote_layout = QVBoxLayout()

        # Remote ekleme
        remote_add_layout = QHBoxLayout()
        self.remote_name = QLineEdit()
        self.remote_name.setPlaceholderText("Remote name...")
        self.remote_url = QLineEdit()
        self.remote_url.setPlaceholderText("Remote URL...")
        add_remote_btn = MaterialButton("Add Remote", "#4CAF50")
        add_remote_btn.clicked.connect(self.add_remote_custom)
        remote_add_layout.addWidget(self.remote_name)
        remote_add_layout.addWidget(self.remote_url)
        remote_add_layout.addWidget(add_remote_btn)

        self.remote_list = QComboBox()
        self.refresh_remote_btn = MaterialButton("Refresh Remotes", "#2196F3")
        self.refresh_remote_btn.clicked.connect(self.refresh_remotes)

        # Push/Pull işlemleri
        push_pull_layout = QHBoxLayout()
        self.branch_for_push = QComboBox()
        self.force_push = QCheckBox("Force Push")
        push_btn = MaterialButton("Push", "#2196F3")
        pull_btn = MaterialButton("Pull", "#9C27B0")
        fetch_btn = MaterialButton("Fetch", "#FF9800")
        push_btn.clicked.connect(self.git_push_advanced)
        pull_btn.clicked.connect(self.git_pull)
        fetch_btn.clicked.connect(self.git_fetch)
        push_pull_layout.addWidget(self.branch_for_push)
        push_pull_layout.addWidget(self.force_push)
        push_pull_layout.addWidget(push_btn)
        push_pull_layout.addWidget(pull_btn)
        push_pull_layout.addWidget(fetch_btn)

        remote_layout.addLayout(remote_add_layout)
        remote_layout.addWidget(self.remote_list)
        remote_layout.addWidget(self.refresh_remote_btn)
        remote_layout.addLayout(push_pull_layout)
        remote_group.setLayout(remote_layout)

        # Branch Management grubuna refresh butonu ekle
        refresh_branches_btn = MaterialButton("Refresh Branches", "#2196F3")
        refresh_branches_btn.clicked.connect(self.refresh_branches)
        branch_layout.addWidget(refresh_branches_btn)

        # Branch geçmişi
        history_group = QGroupBox("Branch History")
        history_layout = QVBoxLayout()
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        refresh_history_btn = MaterialButton("Refresh History", "#2196F3")
        refresh_history_btn.clicked.connect(self.refresh_branch_history)
        history_layout.addWidget(self.history_text)
        history_layout.addWidget(refresh_history_btn)
        history_group.setLayout(history_layout)

        # Advanced output
        self.advanced_output = QTextEdit()
        self.advanced_output.setReadOnly(True)

        layout_tab.addWidget(branch_group)
        layout_tab.addWidget(remote_group)
        layout_tab.addWidget(history_group)
        layout_tab.addWidget(self.advanced_output)

        return tab

    def create_terminal_tab(self):
        """
        'Live Terminal' sekmesini oluşturur.
        """
        tab = QWidget()
        layout_tab = QVBoxLayout(tab)

        # Terminal emulator
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet(
            """
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: 'Courier New';
                font-size: 14px;
            }
            """
        )

        # Komut girişi
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter git command...")
        self.command_input.returnPressed.connect(self.execute_command)

        layout_tab.addWidget(self.terminal_output)
        layout_tab.addWidget(self.command_input)

        return tab

    ###################################################################
    # Temel Git Komutları
    ###################################################################

    def git_init(self):
        """
        Git deposu oluşturur.
        """
        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.output_text.append(result.stdout)
            self.status_label.setText("Repository initialized")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def git_add(self):
        """
        Tüm değişiklikleri sahneye (staging area) ekler.
        """
        try:
            subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.output_text.append("Files added to staging area")
            self.status_label.setText("Files staged")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def git_commit(self):
        """
        Değişiklikleri commit eder.
        """
        try:
            msg = self.commit_msg.text().strip()
            if not msg:
                self.show_error("Please enter a commit message")
                return

            result = subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.output_text.append(result.stdout)
            self.status_label.setText("Changes committed")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def git_push(self):
        """
        Seçili branch'i uzaktaki (remote) repoya gönderir (push).
        """
        try:
            subprocess.run(
                ["git", "push", "origin", self.current_branch],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.output_text.append("Changes pushed successfully!")
            self.status_label.setText("Changes pushed to remote")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def git_status(self):
        """
        Depo durumunu gösterir.
        """
        try:
            result = subprocess.run(
                ["git", "status"],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.output_text.append(result.stdout)
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    ###################################################################
    # Advanced Git Komutları
    ###################################################################

    def create_branch(self):
        """
        Yeni bir branch oluşturup ona geçiş yapar (checkout -b).
        """
        try:
            branch = self.new_branch_name.text().strip()
            if not branch:
                self.show_error("Please enter a branch name")
                return

            result = subprocess.run(
                ["git", "checkout", "-b", branch],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.advanced_output.append(result.stdout)
            self.status_label.setText(
                f"Created and switched to branch: {branch}"
            )
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def delete_branch(self):
        """
        Seçili branch'i siler.
        """
        try:
            branch = self.delete_branch_combo.currentText()
            if not branch:
                self.show_error("Please select a branch to delete")
                return

            result = subprocess.run(
                ["git", "branch", "-d", branch],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.advanced_output.append(result.stdout)
            self.status_label.setText(f"Deleted branch: {branch}")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def rename_branch(self):
        """
        Branch'i yeniden adlandırır.
        """
        try:
            old_branch = self.rename_branch_combo.currentText().strip()
            new_branch = self.new_branch_name_edit.text().strip()
            if not old_branch or not new_branch:
                self.show_error("Current or new branch name cannot be empty.")
                return

            result = subprocess.run(
                ["git", "branch", "-m", old_branch, new_branch],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.advanced_output.append(result.stdout)
            self.status_label.setText(
                f"Branch '{old_branch}' renamed to '{new_branch}'."
            )
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def refresh_branches(self):
        """
        Tüm branch listelerini günceller.
        """
        try:
            if not self.repo_path.text().strip():
                return

            # Git branch komutunu çalıştır
            result = subprocess.run(
                ["git", "branch", "--list"],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )

            # Branch listesini temizle ve yeniden doldur
            branches = []
            for branch in result.stdout.split('\n'):
                branch = branch.replace('*', '').strip()
                if branch:  # Boş string değilse
                    branches.append(branch)

            # Tüm branch combobox'larını güncelle
            self.merge_source_combo.clear()
            self.merge_target_combo.clear()
            self.delete_branch_combo.clear()
            self.rename_branch_combo.clear()
            self.branch_for_push.clear()

            # Branch'leri combobox'lara ekle
            for branch in branches:
                self.merge_source_combo.addItem(branch)
                self.merge_target_combo.addItem(branch)
                self.delete_branch_combo.addItem(branch)
                self.rename_branch_combo.addItem(branch)
                self.branch_for_push.addItem(branch)

        except subprocess.CalledProcessError as err:
            self.show_error(f"Failed to refresh branches: {str(err)}")
        except Exception as err:
            self.show_error(f"Unexpected error while refreshing branches: {str(err)}")

    def handle_merge_branches(self):
        """
        Kaynak ve hedef branch bilgilerini comboBox'lardan alarak merge yapar.
        """
        try:
            source_branch = self.merge_source_combo.currentText().strip()
            target_branch = self.merge_target_combo.currentText().strip()
            if not source_branch or not target_branch:
                self.show_error("Please select source and target branches.")
                return

            # Önce hedef branch'e checkout yapalım
            subprocess.run(
                ["git", "checkout", target_branch],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )

            # Ardından merge
            result_merge = subprocess.run(
                ["git", "merge", source_branch],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.advanced_output.append(result_merge.stdout)
            self.status_label.setText(
                f"Branch '{source_branch}' merged into '{target_branch}'."
            )
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def git_fetch(self):
        """
        Uzaktaki (remote) repodan güncellemeleri yerel repoya çeker (fetch).
        """
        try:
            result = subprocess.run(
                ["git", "fetch"],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.advanced_output.append(result.stdout)
            self.status_label.setText("Fetched latest updates from remote")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def refresh_branch_history(self):
        """
        Mevcut branch'in commit geçmişini gösterir.
        """
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--graph", "--all"],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.history_text.clear()
            self.history_text.append(result.stdout)
            self.status_label.setText("Branch history refreshed.")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    ###################################################################
    # Remote Yönetimi
    ###################################################################

    def add_remote(self):
        """
        'origin' adıyla remote ekler. Basic sekmede kullanılan kısayol.
        """
        try:
            url = self.remote_url_lineedit.text().strip()
            if not url:
                self.show_error("Please enter remote repository URL")
                return

            subprocess.run(
                ["git", "remote", "add", "origin", url],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.output_text.append("Remote repository added successfully.")
            self.status_label.setText("Remote added")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def add_remote_custom(self):
        """
        Gelişmiş sekmedeki 'Remote name' ve 'Remote URL' alanından okur,
        custom isimli remote ekler.
        """
        try:
            r_name = self.remote_name.text().strip()
            r_url = self.remote_url.text().strip()
            if not r_name or not r_url:
                self.show_error("Please enter remote name and URL")
                return

            result = subprocess.run(
                ["git", "remote", "add", r_name, r_url],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.advanced_output.append(result.stdout)
            self.status_label.setText(f"Remote '{r_name}' added.")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def refresh_remotes(self):
        """
        Remoteları listeler ve comboBox'a ekler.
        """
        try:
            result = subprocess.run(
                ["git", "remote"],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            remote_names = result.stdout.split()
            self.remote_list.clear()
            for r_name in remote_names:
                self.remote_list.addItem(r_name)

            branch_list_result = subprocess.run(
                ["git", "branch", "--list"],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.branch_for_push.clear()
            for br_line in branch_list_result.stdout.split('\n'):
                br = br_line.replace('*', '').strip()
                if br:
                    self.branch_for_push.addItem(br)

            self.advanced_output.append("Remote list refreshed.")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def git_push_advanced(self):
        """
        Gelişmiş sekmedeki remote ve branch seçimine göre push işlemi yapar.
        Force push kutusu işaretliyse --force eklenir.
        """
        try:
            branch = self.branch_for_push.currentText().strip()
            if not branch:
                self.show_error("No branch selected for push")
                return

            args = ["git", "push", "origin", branch]
            if self.force_push.isChecked():
                # Force push
                args = ["git", "push", "origin", "--force", branch]

            result = subprocess.run(
                args,
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.advanced_output.append(result.stdout)
            self.status_label.setText(f"Pushed to remote (branch: {branch})")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def git_pull(self):
        """
        Uzaktaki (remote) repodan güncellemeleri yerel branch'e alır (pull).
        """
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            self.output_text.append(result.stdout)
            self.advanced_output.append(result.stdout)
            self.status_label.setText("Changes pulled from remote")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    ###################################################################
    # Ortak Yardımcı Fonksiyonlar
    ###################################################################

    def change_branch(self, branch_name):
        """
        Toolbar'daki branch seçicisinden gelen isimle branch değiştirir
        (yoksa oluşturur).
        """
        try:
            self.current_branch = branch_name
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path.text(),
                capture_output=True,
                text=True,
                check=True
            )
            if result.returncode != 0:
                # Eğer branch zaten varsa, sadece geçiş yap
                subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=self.repo_path.text(),
                    capture_output=True,
                    text=True,
                    check=True
                )
            self.status_label.setText(f"Switched to branch: {branch_name}")
        except subprocess.CalledProcessError as err:
            self.show_error(str(err))

    def browse_repository(self):
        """
        Depo klasörünü seçmek için dosya diyalogu açar.
        """
        repo_path = QFileDialog.getExistingDirectory(self, "Select Repository")
        if repo_path:
            self.repo_path.setText(repo_path)

    def execute_command(self):
        """
        Terminal sekmesinde kullanıcıdan gelen komutları (yalnızca git)
        çalıştırır.
        """
        command = self.command_input.text().strip()
        repo_path = self.repo_path.text().strip()

        # Repo yolu kontrolü
        if not repo_path:
            self.show_error("Please select a repository path first")
            return           
        
        # Sadece git komutlarına izin ver
        if not command.startswith("git"):
            self.show_error("Only git commands are allowed")
            return
    
        try:
            # Komutu liste olarak hazırla ve çalıştır
            command_list = command.split()
            result = subprocess.run(
                command_list,
                cwd=repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',  # Encoding'i açıkça belirt
                check=True
            )
            self.terminal_output.append(f"$ {command}\n{result.stdout}")
            
        except subprocess.CalledProcessError as err:
            self.show_error(f"Command failed: {str(err)}")
        except OSError as err:
            self.show_error(f"System error: {str(err)}")
        except Exception as err:
            self.show_error(f"Unexpected error: {str(err)}")
            
        self.command_input.clear()

    def toggle_theme(self):
        """
        Karanlık ve aydınlık tema arasında geçiş yapar.
        """
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.theme_btn.setText("☀️ Light Mode")
            self.setStyleSheet(
                """
                QMainWindow, QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QToolBar {
                    background-color: #2d2d2d;
                    border-bottom: 1px solid #333333;
                    spacing: 10px;
                    padding: 5px;
                }
                QTabWidget::pane {
                    border: 1px solid #333333;
                    background: #1e1e1e;
                }
                QTabBar::tab {
                    background: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #333333;
                    padding: 8px 12px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #1e1e1e;
                    border-bottom: 2px solid #2196F3;
                }
                QTabBar::tab:hover {
                    background: #383838;
                }
                QGroupBox {
                    border: 2px solid #333333;
                    border-radius: 8px;
                    margin-top: 1em;
                    font-weight: bold;
                    color: #ffffff;
                }
                QGroupBox::title {
                    color: #64B5F6;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #2d2d2d;
                    border: 2px solid #333333;
                    color: #ffffff;
                    border-radius: 4px;
                    padding: 8px;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 2px solid #64B5F6;
                }
                """
            )
        else:
            self.theme_btn.setText("🌙 Dark Mode")
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QMenuBar {
                    background-color: #ffffff;
                }
                QToolBar {
                    background-color: #ffffff;
                    border-bottom: 1px solid #e0e0e0;
                    spacing: 10px;
                    padding: 5px;
                }
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    background: #ffffff;
                }
                QTabBar::tab {
                    background: #f5f5f5;
                    border: 1px solid #e0e0e0;
                    padding: 8px 12px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                    border-bottom: 2px solid #2196F3;
                }
                QTabBar::tab:hover {
                    background: #e0e0e0;
                }
                QGroupBox {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    margin-top: 1em;
                    font-weight: bold;
                }
                QGroupBox::title {
                    color: #1976D2;
                }
                QLineEdit, QTextEdit, QComboBox {
                    padding: 8px;
                    border: 2px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: white;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 2px solid #2196F3;
                }
                """
            )

    def show_error(self, message):
        """
        Hata mesajlarını kullanıcıya gösterir.
        """
        QMessageBox.critical(self, "Error", message)


def main():
    """
    Uygulamayı başlatmak için ana fonksiyon.
    """
    app = QApplication(sys.argv)
    window = GitGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
