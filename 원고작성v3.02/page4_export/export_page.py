import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, 
    QMessageBox, QApplication, QGridLayout
)
from docx import Document
import shutil  # For archiving files

class ExportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)  # Reduce padding around the layout
        self.layout.setSpacing(5)  # Reduce space between widgets

        # Setup a grid layout for inputs and buttons
        grid_layout = QGridLayout()

        # Input fields and labels
        self.prefix_input = QLineEdit()
        self.suffix_input = QLineEdit()
        self.prefix_label = QLabel("접두사:")
        self.suffix_label = QLabel("접미사:")
        self.file_example_label = QLabel("변환될 파일명 예시:")
        self.update_example_label()

        # Buttons to perform conversion, renaming and archiving
        self.process_button = QPushButton("파일 변환 및 이름 변경")
        self.process_button.clicked.connect(self.convert_and_rename_files)
        
        self.archive_button = QPushButton("결과물 압축하기")
        self.archive_button.clicked.connect(self.archive_files)

        # Add widgets to the grid layout
        grid_layout.addWidget(self.prefix_label, 0, 0)
        grid_layout.addWidget(self.prefix_input, 0, 1)
        grid_layout.addWidget(self.suffix_label, 1, 0)
        grid_layout.addWidget(self.suffix_input, 1, 1)
        grid_layout.addWidget(self.file_example_label, 2, 0, 1, 2)
        grid_layout.addWidget(self.process_button, 3, 0, 1, 2)
        grid_layout.addWidget(self.archive_button, 4, 0, 1, 2)

        # Setup text change listeners
        self.prefix_input.textChanged.connect(self.update_example_label)
        self.suffix_input.textChanged.connect(self.update_example_label)

        # Add grid layout to main layout
        self.layout.addLayout(grid_layout)

    def update_example_label(self):
        example_filename = "examplefile.docx"
        prefix = self.prefix_input.text()
        suffix = self.suffix_input.text()
        new_name = f"{prefix}{example_filename[:-5]}{suffix}.txt"
        self.file_example_label.setText(f"변환될 파일명 예시: {new_name}")

    def convert_and_rename_files(self):
        source_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', '작업대')
        target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', '최종결과물')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        for filename in os.listdir(source_dir):
            if filename.endswith(".docx"):
                docx_path = os.path.join(source_dir, filename)
                new_filename = f"{self.prefix_input.text()}{filename[:-5]}{self.suffix_input.text()}.txt"
                txt_path = os.path.join(target_dir, new_filename)
                self.convert_docx_to_txt(docx_path, txt_path)

        QMessageBox.information(self, "완료", "모든 파일이 변환되고 이름이 변경되었습니다.")

    def archive_files(self):
        target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', '최종결과물')
        archive_path = os.path.join(os.path.dirname(target_dir), '최종결과물.zip')
        shutil.make_archive(archive_path[:-4], 'zip', target_dir)
        QMessageBox.information(self, "완료", "파일이 압축되었습니다.")

    def convert_docx_to_txt(self, docx_path, txt_path):
        doc = Document(docx_path)
        with open(txt_path, 'w', encoding='utf-8') as file:
            for paragraph in doc.paragraphs:
                file.write(paragraph.text + '\n')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExportPage()
    window.show()
    sys.exit(app.exec_())
