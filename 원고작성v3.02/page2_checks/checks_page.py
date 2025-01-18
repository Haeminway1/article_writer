import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QSplitter, QPushButton, QLineEdit, QMessageBox, QTextEdit, QTableWidget, QTableWidgetItem, QHBoxLayout, QFormLayout, QListView, QAbstractItemView, QAction, QInputDialog, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, QStringListModel
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    

from page1_model.model_functions import load_model_settings, save_model_settings

class ChecksPage(QWidget):
    def __init__(self, model_name="default_model", parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(5, 5, 5, 5)

        self.rewrite_list_label = QLabel("Rewrite Scripts")
        self.rewrite_list_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.left_layout.addWidget(self.rewrite_list_label)

        self.rewrite_list_widget = QListWidget()
        self.rewrite_list_widget.itemClicked.connect(self.on_rewrite_item_clicked)
        self.left_layout.addWidget(self.rewrite_list_widget)
        self.load_rewrite_scripts()

        self.splitter.addWidget(self.left_widget)

        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)
        self.center_layout.setContentsMargins(5, 5, 5, 5)

        self.revision_list_label = QLabel("Revision Scripts")
        self.revision_list_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.center_layout.addWidget(self.revision_list_label)

        self.revision_list_widget = QListWidget()
        self.revision_list_widget.itemClicked.connect(self.on_revision_item_clicked)
        self.center_layout.addWidget(self.revision_list_widget)
        self.load_revision_scripts()

        self.splitter.addWidget(self.center_widget)

        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(5, 5, 5, 5)

        # Add input fields for character count settings
        self.char_count_form = QFormLayout()
        self.min_length_edit = QLineEdit()
        self.max_length_edit = QLineEdit()
        self.char_count_form.addRow("Min Length", self.min_length_edit)
        self.char_count_form.addRow("Max Length", self.max_length_edit)
        self.save_char_count_button = QPushButton("Save Character Count Settings")
        self.save_char_count_button.clicked.connect(self.save_char_count_settings)
        self.char_count_form.addRow(self.save_char_count_button)
        self.right_layout.addLayout(self.char_count_form)

        self.forbidden_words_model = QStringListModel()
        self.forbidden_words_view = QListView()
        self.forbidden_words_view.setModel(self.forbidden_words_model)
        self.forbidden_words_view.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.forbidden_words_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.right_layout.addWidget(self.forbidden_words_view)

        self.forbidden_words_buttons_layout = QHBoxLayout()
        self.add_word_button = QPushButton("Add Forbidden Word")
        self.add_word_button.clicked.connect(self.add_forbidden_word)
        self.delete_word_button = QPushButton("Delete Selected Word")
        self.delete_word_button.clicked.connect(self.delete_selected_word)
        self.save_words_button = QPushButton("Save Forbidden Words")
        self.save_words_button.clicked.connect(self.save_forbidden_words)

        self.forbidden_words_buttons_layout.addWidget(self.add_word_button)
        self.forbidden_words_buttons_layout.addWidget(self.delete_word_button)
        self.forbidden_words_buttons_layout.addWidget(self.save_words_button)

        self.right_layout.addLayout(self.forbidden_words_buttons_layout)

        # Add table for substitution pairs
        self.substitution_table = QTableWidget(10, 2)  # 기본적으로 10개의 빈 줄을 제공
        self.substitution_table.setHorizontalHeaderLabels(["원래 단어", "대체 단어"])
        self.right_layout.addWidget(self.substitution_table)

        self.substitution_buttons_layout = QHBoxLayout()
        self.add_pair_button = QPushButton("Add Empty Pair")
        self.add_pair_button.clicked.connect(self.add_empty_substitution_pair)
        self.save_pairs_button = QPushButton("Save Substitution Pairs")
        self.save_pairs_button.clicked.connect(self.save_substitution_pairs)

        self.substitution_buttons_layout.addWidget(self.add_pair_button)
        self.substitution_buttons_layout.addWidget(self.save_pairs_button)
        self.right_layout.addLayout(self.substitution_buttons_layout)

        self.run_button = QPushButton("Run script")
        self.run_button.clicked.connect(self.run_scripts)
        self.right_layout.addWidget(self.run_button)

        self.progress_label = QLabel("진행 상황: 대기 중")
        self.right_layout.addWidget(self.progress_label)

        self.progress_text_edit = QTextEdit()
        self.progress_text_edit.setReadOnly(True)
        self.right_layout.addWidget(self.progress_text_edit)

        self.splitter.addWidget(self.right_widget)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setStretchFactor(2, 1)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

        self.load_initial_settings()

    def set_model_name(self, model_name):
        self.model_name = model_name
        self.load_initial_settings()
        self.load_rewrite_scripts()
        self.load_revision_scripts()

    def load_rewrite_scripts(self):
        self.rewrite_list_widget.clear()
        rewrite_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'page2_checks', 'rewrite_scripts')
        for script_name in os.listdir(rewrite_dir):
            if script_name.endswith('.py'):
                item = QListWidgetItem(script_name)
                self.rewrite_list_widget.addItem(item)

    def load_revision_scripts(self):
        self.revision_list_widget.clear()
        revision_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'page2_checks', 'revision_scripts')
        for script_name in os.listdir(revision_dir):
            if script_name.endswith('.py'):
                item = QListWidgetItem(script_name)
                self.revision_list_widget.addItem(item)

    def on_rewrite_item_clicked(self, item):
        script_name = item.text()
        self.load_script_settings(script_name, "rewrite_scripts")

    def on_revision_item_clicked(self, item):
        script_name = item.text()
        self.load_script_settings(script_name, "revision_scripts")

    def load_script_settings(self, script_name, script_type):
        # Load script settings if needed
        pass

    def load_initial_settings(self):
        model_settings = load_model_settings(self.model_name)['check_list_settings']

        char_count_settings = model_settings.get("char_count_check", {})
        self.min_length_edit.setText(str(char_count_settings.get("min_length", "")))
        self.max_length_edit.setText(str(char_count_settings.get("max_length", "")))

        forbidden_words = model_settings.get("forbidden_words_check", {}).get("forbidden_words", [])
        self.forbidden_words_model.setStringList(forbidden_words)

        substitution_pairs = model_settings.get("substitution_pairs", {}).get("substitution_list", [])
        self.substitution_table.clearContents()
        self.substitution_table.setRowCount(max(len(substitution_pairs), 10))  # 최소 10개의 빈 줄을 유지
        for row, pair in enumerate(substitution_pairs):
            for original, replacement in pair.items():
                self.substitution_table.setItem(row, 0, QTableWidgetItem(original))
                self.substitution_table.setItem(row, 1, QTableWidgetItem(replacement))

        # 나머지 빈 행 처리
        for row in range(len(substitution_pairs), self.substitution_table.rowCount()):
            self.substitution_table.setItem(row, 0, QTableWidgetItem(""))
            self.substitution_table.setItem(row, 1, QTableWidgetItem(""))

        print(f"Loaded settings for model: {self.model_name}")
        print(f"Substitution pairs: {substitution_pairs}")

    def save_char_count_settings(self):
        min_length = int(self.min_length_edit.text())
        max_length = int(self.max_length_edit.text())
        self.save_model_setting("char_count_check", "min_length", min_length)
        self.save_model_setting("char_count_check", "max_length", max_length)
        QMessageBox.information(self, "Success", "Character count settings saved successfully.")

    def save_model_setting(self, settings_type, key, value):
        model_settings = load_model_settings(self.model_name)['check_list_settings']
        if settings_type not in model_settings:
            model_settings[settings_type] = {}
        model_settings[settings_type][key] = value
        save_model_settings(self.model_name, check_list_settings=model_settings)

    def add_forbidden_word(self):
        word, ok = QInputDialog.getText(self, "Add Forbidden Word", "Enter a new forbidden word:")
        if ok and word:
            forbidden_words = self.forbidden_words_model.stringList()
            forbidden_words.append(word)
            self.forbidden_words_model.setStringList(forbidden_words)

    def delete_selected_word(self):
        selected_indexes = self.forbidden_words_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            forbidden_words = self.forbidden_words_model.stringList()
            del forbidden_words[index.row()]
            self.forbidden_words_model.setStringList(forbidden_words)

    def save_forbidden_words(self):
        forbidden_words = self.forbidden_words_model.stringList()
        self.save_model_setting("forbidden_words_check", "forbidden_words", forbidden_words)
        QMessageBox.information(self, "Success", "Forbidden words saved successfully.")

    def add_empty_substitution_pair(self):
        row_count = self.substitution_table.rowCount()
        self.substitution_table.insertRow(row_count)
        self.substitution_table.setItem(row_count, 0, QTableWidgetItem(""))
        self.substitution_table.setItem(row_count, 1, QTableWidgetItem(""))

    def save_substitution_pairs(self):
        substitution_pairs = []
        for row in range(self.substitution_table.rowCount()):
            original = self.substitution_table.item(row, 0).text() if self.substitution_table.item(row, 0) else ""
            replacement = self.substitution_table.item(row, 1).text() if self.substitution_table.item(row, 1) else ""
            if original and replacement:
                substitution_pairs.append({original: replacement})
        self.save_model_setting("substitution_pairs", "substitution_list", substitution_pairs)
        QMessageBox.information(self, "Success", "Substitution pairs saved successfully.")

    def run_scripts(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        writing_sequence_script = os.path.join(base_dir, "scripts", "writing_sequence.py")
        progress_file = os.path.join(base_dir, "data", "progress.txt")

        if os.path.exists(progress_file):
            os.remove(progress_file)

        self.progress_label.setText("진행 상황: 실행 중")
        self.progress_text_edit.clear()

        process = subprocess.Popen(['python', writing_sequence_script, self.model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='cp949')

        timer = QTimer(self)
        timer.timeout.connect(lambda: self.update_progress(process, progress_file))
        timer.start(1000)

        def on_finished():
            timer.stop()
            self.update_progress(process, progress_file, True)
            self.progress_label.setText("진행 상황: 완료")

        process.wait()
        on_finished()

    def update_progress(self, process, progress_file, final_update=False):
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='cp949') as f:
                content = f.read()
                self.progress_text_edit.setPlainText(content)
                if final_update:
                    self.progress_text_edit.append("작업 완료!")

        if final_update:
            stdout, stderr = process.communicate()
            if stdout:
                self.progress_text_edit.append(stdout)
            if stderr:
                self.progress_text_edit.append(stderr)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    model_name = "default_model"  # 또는 적절한 모델 이름
    window = ChecksPage(model_name)
    window.show()
    sys.exit(app.exec_())