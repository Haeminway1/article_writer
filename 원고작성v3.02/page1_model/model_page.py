from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSplitter, QLineEdit, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal
from .model_widgets import ModelListWidget, ModelSettingsWidget
from .keywords_widgets import KeywordTableWidget
from .model_functions import add_new_model, delete_model, copy_model, rename_model

class ModelPage(QWidget):
    model_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)

        # Left Column
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(5, 5, 5, 5)  # 마진 조정

        self.model_list_label = QLabel("모델 리스트")
        self.model_list_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.left_layout.addWidget(self.model_list_label)

        self.button_layout = QHBoxLayout()
        self.add_model_input = QLineEdit()
        self.add_model_input.setPlaceholderText("모델 이름 입력")
        self.add_model_button = QPushButton("모델 추가")
        self.delete_model_button = QPushButton("모델 삭제")
        self.copy_model_button = QPushButton("모델 복사")
        self.add_model_button.clicked.connect(self.add_model)
        self.delete_model_button.clicked.connect(self.delete_model)
        self.copy_model_button.clicked.connect(self.copy_model)
        self.button_layout.addWidget(self.add_model_input)
        self.button_layout.addWidget(self.add_model_button)
        self.button_layout.addWidget(self.delete_model_button)
        self.button_layout.addWidget(self.copy_model_button)
        self.left_layout.addLayout(self.button_layout)

        self.model_list_widget = ModelListWidget(self)
        self.left_layout.addWidget(self.model_list_widget)

        self.splitter.addWidget(self.left_widget)

        # Center Column
        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)
        self.center_layout.setContentsMargins(0, 0, 0, 0)  # 마진 제거
        self.center_layout.setSpacing(0)  # 위젯 간 간격 조정

        self.model_settings_label = QLabel("모델 설정")
        self.model_settings_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.center_layout.addWidget(self.model_settings_label)

        self.model_settings_widget = ModelSettingsWidget(self, self.model_list_widget)
        self.center_layout.addWidget(self.model_settings_widget, 1)  # 적당한 크기로 설정

        self.splitter.addWidget(self.center_widget)

        # Right Column with Keyword Table
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(5, 5, 5, 5)  # 마진 조정

        self.keyword_table_widget = KeywordTableWidget(self)
        self.right_layout.addWidget(self.keyword_table_widget)

        self.splitter.addWidget(self.right_widget)

        # Adjust the stretch factors to show the keyword table fully
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 6)  # 중앙열의 가로 길이 살짝 줄임
        self.splitter.setStretchFactor(2, 3)  # 우측 키워드 테이블 가로 길이 늘림

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

        self.model_list_widget.model_selected.connect(self.model_settings_widget.load_model_settings)
        self.model_list_widget.model_selected.connect(self.emit_model_selected)

    def emit_model_selected(self, model_name):
        self.model_selected.emit(model_name)

    def add_model(self):
        model_name = self.add_model_input.text().strip()
        if model_name:
            try:
                add_new_model(model_name)
                self.model_list_widget.load_models()
                self.add_model_input.clear()
            except FileExistsError:
                QMessageBox.warning(self, "Error", f"The model '{model_name}' already exists.")

    def delete_model(self):
        model_name = self.model_list_widget.current_model()
        if model_name:
            delete_model(model_name)
            self.model_list_widget.load_models()

    def copy_model(self):
        model_name = self.model_list_widget.current_model()
        if model_name:
            new_model_name, ok = QInputDialog.getText(self, "모델 복사", "새 모델 이름을 입력하세요:")
            if ok and new_model_name:
                try:
                    copy_model(model_name, new_model_name)
                    self.model_list_widget.load_models()
                except FileExistsError:
                    QMessageBox.warning(self, "Error", f"The model '{new_model_name}' already exists.")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ModelPage()
    window.show()
    sys.exit(app.exec_())
