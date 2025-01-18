import sys
import os
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTextEdit, 
                             QMainWindow, QProgressBar, QPushButton, QDialog)
from PyQt5.QtCore import QTimer, QProcess, QSocketNotifier, Qt, pyqtSignal, QObject

class PromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("프롬프트 상세 정보")
        self.setGeometry(300, 300, 600, 400)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def set_prompt(self, prompt):
        self.text_edit.setPlainText(prompt)

class ProgressWindow(QMainWindow):
    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
        self.prompt_dialog = PromptDialog(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('작업 진행 상황')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()

        self.model_label = QLabel(f"모델: {self.model_name}", self)
        layout.addWidget(self.model_label)

        self.stage_label = QLabel("현재 단계: 대기 중", self)
        layout.addWidget(self.stage_label)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.current_keyword_label = QLabel("현재 키워드: -", self)
        layout.addWidget(self.current_keyword_label)

        self.keywords_processed_label = QLabel("처리된 키워드: 0", self)
        layout.addWidget(self.keywords_processed_label)

        self.keywords_remaining_label = QLabel("남은 키워드: -", self)
        layout.addWidget(self.keywords_remaining_label)

        self.status_label = QLabel("상태: 대기 중", self)
        layout.addWidget(self.status_label)
        
        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(self.log_text_edit)

        self.more_button = QPushButton("더보기 (프롬프트 확인)", self)
        self.more_button.clicked.connect(self.show_prompt_dialog)
        layout.addWidget(self.more_button)

        self.close_button = QPushButton("닫기", self)
        self.close_button.clicked.connect(self.close)
        self.close_button.setVisible(False)
        layout.addWidget(self.close_button)

        central_widget.setLayout(layout)

    def update_progress(self, value, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(value)

    def update_stage(self, stage):
        self.stage_label.setText(f"현재 단계: {stage}")

    def update_current_keyword(self, keyword):
        self.current_keyword_label.setText(f"현재 키워드: {keyword}")

    def update_keywords_processed(self, processed, total):
        self.keywords_processed_label.setText(f"처리된 키워드: {processed}/{total}")

    def update_keywords_remaining(self, remaining):
        self.keywords_remaining_label.setText(f"남은 키워드: {', '.join(remaining)}")

    def update_status(self, status):
        self.status_label.setText(f"상태: {status}")

    def append_log(self, message):
        self.log_text_edit.append(message)

    def show_prompt_dialog(self):
        self.prompt_dialog.show()

    def update_prompt(self, prompt):
        self.prompt_dialog.set_prompt(prompt)

    def set_finished_state(self):
        self.close_button.setVisible(True)
        self.append_log("작업이 완료되었습니다. 창을 닫으려면 '닫기' 버튼을 클릭하세요.")

class ProgressUpdater(QObject):
    progress_updated = pyqtSignal(str)
    current_stage = pyqtSignal(str)
    total_keywords = pyqtSignal(int)
    keywords_processed = pyqtSignal(int)
    current_keyword = pyqtSignal(str)
    keywords_remaining = pyqtSignal(list)
    keywords_failed = pyqtSignal(list)
    keywords_passed = pyqtSignal(list)
    prompt_updated = pyqtSignal(str)

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.connect_signals()

    def connect_signals(self):
        self.progress_updated.connect(self.window.append_log)
        self.current_stage.connect(self.window.update_stage)
        self.current_keyword.connect(self.window.update_current_keyword)
        self.keywords_processed.connect(lambda x: self.window.update_keywords_processed(x, self.total))
        self.keywords_remaining.connect(self.window.update_keywords_remaining)
        self.total_keywords.connect(self.set_total_keywords)
        self.prompt_updated.connect(self.window.update_prompt)

    def set_total_keywords(self, total):
        self.total = total
        self.window.update_progress(0, total)

    def update_progress(self, message):
        self.progress_updated.emit(message)

    def update_stage(self, stage):
        self.current_stage.emit(stage)

    def update_total_keywords(self, total):
        self.total_keywords.emit(total)

    def update_keywords_processed(self, processed):
        self.keywords_processed.emit(processed)

    def update_current_keyword(self, keyword):
        self.current_keyword.emit(keyword)

    def update_keywords_remaining(self, remaining):
        self.keywords_remaining.emit(remaining)

    def update_keywords_failed(self, failed):
        self.keywords_failed.emit(failed)

    def update_keywords_passed(self, passed):
        self.keywords_passed.emit(passed)

    def update_prompt(self, prompt):
        self.prompt_updated.emit(prompt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    model_name = sys.argv[1] if len(sys.argv) > 1 else "default_model"
    window = ProgressWindow(model_name)
    window.show()
    sys.exit(app.exec_())