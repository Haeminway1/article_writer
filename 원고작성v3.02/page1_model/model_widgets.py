from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QLineEdit, QFormLayout, QHBoxLayout, QPushButton, QMessageBox, QInputDialog, QScrollArea, QCheckBox, QTextEdit, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt
from .model_functions import load_model_list, load_model_settings, save_model_settings, rename_model

class ModelListWidget(QWidget):
    model_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.model_list = QListWidget()
        
        self.layout.addWidget(self.model_list)
        self.setLayout(self.layout)
        
        self.model_list.itemSelectionChanged.connect(self.emit_model_selected)
        self.load_models()
    
    def load_models(self):
        models = load_model_list()
        self.model_list.clear()
        self.model_list.addItems(models)
    
    def emit_model_selected(self):
        selected_items = self.model_list.selectedItems()
        if selected_items:
            model_name = selected_items[0].text()
            self.model_selected.emit(model_name)

    def current_model(self):
        selected_items = self.model_list.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

class ModelSettingsWidget(QWidget):
    def __init__(self, parent=None, model_list_widget=None):
        super().__init__(parent)
        self.model_list_widget = model_list_widget
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # 마진 제거
        self.layout.setSpacing(0)  # 위젯 간 간격 조정

        self.settings_form = QFormLayout()
        self.settings_form.setContentsMargins(0, 0, 0, 0)  # 마진 제거
        self.settings_form.setSpacing(0)  # 위젯 간 간격 조정

        self.model_name_label = QLabel("Model Name:")
        self.model_name_label.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
        self.model_name = QLineEdit()
        self.model_name.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
        self.rename_button = QPushButton("이름 수정")
        self.rename_button.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
        self.rename_button.clicked.connect(self.rename_model)
        
        self.layout.addWidget(self.model_name_label)
        self.layout.addWidget(self.model_name)
        self.layout.addWidget(self.rename_button)
        self.layout.addLayout(self.settings_form)

        self.prompts_label = QLabel("Prompts")
        self.prompts_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.prompts_label.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.prompts_label)

        self.prompts_scroll = QScrollArea()
        self.prompts_scroll.setWidgetResizable(True)
        self.prompts_widget = QWidget()
        self.prompts_layout = QVBoxLayout(self.prompts_widget)
        self.prompts_layout.setContentsMargins(0, 0, 0, 0)  # 마진 제거
        self.prompts_layout.setSpacing(5)  # 위젯 간 간격 조정
        self.prompts_scroll.setWidget(self.prompts_widget)
        self.layout.addWidget(self.prompts_scroll)

        self.new_prompt_input = QTextEdit()
        self.new_prompt_input.setPlaceholderText("새 프롬트 입력")
        self.new_prompt_input.setFixedHeight(200)  # 세로 길이 두 배로 늘림
        self.new_prompt_input.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
        self.layout.addWidget(self.new_prompt_input)

        # Add keyword buttons below the new prompt input
        self.keyword_buttons_layout = QHBoxLayout()
        self.keyword_button1 = QPushButton("'{키워드1}'")
        self.keyword_button1.clicked.connect(lambda: self.insert_keyword("'{키워드1}'"))
        self.keyword_button2 = QPushButton("'{키워드2}'")
        self.keyword_button2.clicked.connect(lambda: self.insert_keyword("'{키워드2}'"))
        self.keyword_button3 = QPushButton("'{키워드3}'")
        self.keyword_button3.clicked.connect(lambda: self.insert_keyword("'{키워드3}'"))

        self.keyword_buttons_layout.addWidget(self.keyword_button1)
        self.keyword_buttons_layout.addWidget(self.keyword_button2)
        self.keyword_buttons_layout.addWidget(self.keyword_button3)

        self.layout.addLayout(self.keyword_buttons_layout)

        self.save_prompts_button = QPushButton("프롬트 저장")
        self.save_prompts_button.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
        self.save_prompts_button.clicked.connect(self.save_prompts)
        self.layout.addWidget(self.save_prompts_button)

        self.delete_prompts_button = QPushButton("선택한 프롬트 삭제")
        self.delete_prompts_button.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
        self.delete_prompts_button.clicked.connect(self.delete_selected_prompts)
        self.layout.addWidget(self.delete_prompts_button)

        self.setLayout(self.layout)

        # 모델 세팅값 항목을 미리 표시
        self.set_initial_settings()

    def set_initial_settings(self):
        initial_settings = {"temperature": "", "max_tokens": "", "top_p": "", "frequency_penalty": "", "presence_penalty": ""}
        for key in initial_settings:
            label = QLabel(f"{key}:")
            label.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
            edit = QLineEdit(initial_settings[key])
            edit.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
            edit.editingFinished.connect(lambda key=key, edit=edit: self.save_config(key, edit))
            self.settings_form.addRow(label, edit)

    def load_model_settings(self, model_name):
        self.model_name.setText(model_name)
        try:
            settings = load_model_settings(model_name)

            # Clear previous settings and prompts
            while self.settings_form.count():
                item = self.settings_form.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            while self.prompts_layout.count():
                item = self.prompts_layout.takeAt(0)
                if item.layout():
                    while item.layout().count():
                        sub_item = item.layout().takeAt(0)
                        if sub_item.widget():
                            sub_item.widget().deleteLater()

            # Load settings
            for key, value in settings['config'].items():
                label = QLabel(f"{key}:")
                label.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
                edit = QLineEdit(str(value))
                edit.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
                edit.editingFinished.connect(lambda key=key, edit=edit: self.save_config(key, edit))
                self.settings_form.addRow(label, edit)

            # Load prompts
            for prompt in settings['prompts']:
                prompt_layout = QHBoxLayout()
                checkbox = QCheckBox()
                edit = QTextEdit(prompt)
                edit.setFixedHeight(200)  # 세로 길이 두 배로 늘림
                edit.setStyleSheet("font-size: 16px;")  # 글씨 크기 설정
                edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
                prompt_layout.addWidget(checkbox)
                prompt_layout.addWidget(edit)
                self.prompts_layout.addLayout(prompt_layout)
                
        except FileNotFoundError as e:
            print(e)
    
    def save_config(self, key, edit):
        model_name = self.model_name.text()
        value = edit.text()
        save_model_settings(model_name, config={key: value})
    
    def save_prompts(self):
        model_name = self.model_name.text()
        prompts = []
        for i in range(self.prompts_layout.count()):
            layout = self.prompts_layout.itemAt(i).layout()
            if layout:
                edit = layout.itemAt(1).widget()
                prompts.append(edit.toPlainText())
        new_prompt = self.new_prompt_input.toPlainText().strip()
        if new_prompt:
            prompts.append(new_prompt)
        save_model_settings(model_name, prompts=prompts)
        self.new_prompt_input.clear()
        self.load_model_settings(model_name)

    def delete_selected_prompts(self):
        to_delete = []
        for i in range(self.prompts_layout.count()):
            layout = self.prompts_layout.itemAt(i).layout()
            checkbox = layout.itemAt(0).widget()
            if checkbox.isChecked():
                to_delete.append(i)
        for i in reversed(to_delete):
            item = self.prompts_layout.takeAt(i)
            if item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
        self.save_prompts()
    
    def rename_model(self):
        current_name = self.model_name.text()
        new_name, ok = QInputDialog.getText(self, "이름 수정", "새 모델 이름을 입력하세요:", text=current_name)
        if ok and new_name:
            try:
                rename_model(current_name, new_name)
                self.model_name.setText(new_name)
                self.model_list_widget.load_models()
            except FileExistsError:
                QMessageBox.warning(self, "Error", f"The model '{new_name}' already exists.")
            except FileNotFoundError:
                QMessageBox.warning(self, "Error", f"The model '{current_name}' does not exist.")

    def insert_keyword(self, keyword):
        cursor = self.new_prompt_input.textCursor()
        cursor.insertText(keyword)


