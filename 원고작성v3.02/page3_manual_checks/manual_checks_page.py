from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPlainTextEdit, QLabel, QPushButton, QMessageBox, QSplitter, QFrame, QLineEdit, QGroupBox, QListWidgetItem
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QTimer, QFileSystemWatcher
import os
from .manual_checks_functions import get_document_info, save_text_to_docx, load_text_from_docx

class ManualChecksPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        # Main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)

        # 1st column: Files list widget
        self.files_list_widget = QListWidget()
        self.files_list_widget.setFont(QFont('Arial', 12))
        self.files_list_widget.itemClicked.connect(self.load_file_content)

        # 2nd column: Files content edit
        self.files_content_edit = QPlainTextEdit()
        self.files_content_edit.setFont(QFont('Arial', 16))  # Set font size to 16 for better readability

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setFont(QFont('Arial', 14))
        self.save_button.clicked.connect(self.save_file_content)

        # 3rd column: File info display
        self.info_splitter = QSplitter(Qt.Vertical)
        
        # Character count section
        self.char_count_group = QGroupBox("Character Count")
        self.char_count_layout = QVBoxLayout()
        self.char_count_label = QLineEdit()
        self.char_count_label.setReadOnly(True)  # Make it read-only
        self.char_count_label.setFont(QFont('Arial', 14))
        self.char_count_layout.addWidget(self.char_count_label)
        self.char_count_group.setLayout(self.char_count_layout)
        
        # Frequent words section
        self.frequent_words_group = QGroupBox("Frequent Words")
        self.frequent_words_layout = QVBoxLayout()
        
        self.min_count_input = QLineEdit()
        self.min_count_input.setPlaceholderText("Enter min count")
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_min_count)
        
        self.frequent_words_list = QListWidget()
        self.frequent_words_list.setFont(QFont('Arial', 14))
        self.frequent_words_list.itemClicked.connect(self.highlight_word)

        self.frequent_words_layout.addWidget(self.min_count_input)
        self.frequent_words_layout.addWidget(self.apply_button)
        self.frequent_words_layout.addWidget(self.frequent_words_list)
        self.frequent_words_group.setLayout(self.frequent_words_layout)

        self.info_splitter.addWidget(self.char_count_group)
        self.info_splitter.addWidget(self.frequent_words_group)
        self.info_splitter.setSizes([100, 900])  # Set initial sizes

        self.info_container = QFrame()
        self.info_layout = QVBoxLayout(self.info_container)
        self.info_layout.addWidget(self.info_splitter)
        self.info_layout.addWidget(self.save_button)

        # Add widgets to the main splitter
        self.main_splitter.addWidget(self.files_list_widget)
        self.main_splitter.addWidget(self.files_content_edit)
        self.main_splitter.addWidget(self.info_container)

        # Set the stretch factor for each widget to control their sizes
        self.main_splitter.setStretchFactor(0, 2)
        self.main_splitter.setStretchFactor(1, 6)
        self.main_splitter.setStretchFactor(2, 2)

        self.layout.addWidget(self.main_splitter)

        # Initialize file system watcher
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(self.get_workbench_dir())
        self.file_watcher.directoryChanged.connect(self.load_files_in_workbench)

        # Initialize word positions
        self.word_positions = {}

        # Initial Files Load
        self.load_files_in_workbench()

        # Set initial sizes for the splitters using QTimer
        QTimer.singleShot(0, self.set_initial_splitter_sizes)

        # Track the current file being edited
        self.current_file_path = None

    def set_initial_splitter_sizes(self):
        self.main_splitter.setSizes([200, 600, 200])

    def get_workbench_dir(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "../data/작업대")

    def load_files_in_workbench(self):
        self.files_list_widget.clear()
        workbench_dir = self.get_workbench_dir()
        if not os.path.exists(workbench_dir):
            QMessageBox.critical(self, "Error", "The '작업대' directory does not exist.")
            return

        try:
            workbench_files = os.listdir(workbench_dir)
            for workbench_file in workbench_files:
                self.files_list_widget.addItem(workbench_file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load files from '작업대': {str(e)}")

    def load_file_content(self, item):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        workbench_dir = os.path.join(base_dir, "../data/작업대")
        file_path = os.path.join(workbench_dir, item.text())
        try:
            text_content = load_text_from_docx(file_path)
            self.files_content_edit.setPlainText(text_content)
            self.update_file_info(file_path)
            self.word_positions = self.get_word_positions(text_content)  # Update word positions
            self.current_file_path = file_path  # Track the current file path
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def delete_file_content(self):
        current_item = self.files_list_widget.currentItem()
        if not current_item or current_item.text().startswith("Files in 작업대"):
            QMessageBox.warning(self, "No Selection", "Please select a file from the list.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        workbench_dir = os.path.join(base_dir, "../data/작업대")
        file_path = os.path.join(workbench_dir, current_item.text())

        reply = QMessageBox.question(self, 'Delete File', f"Are you sure you want to delete {current_item.text()}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
                QMessageBox.information(self, "Success", "File deleted successfully.")
                self.load_files_in_workbench()  # Refresh the file list
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete file: {str(e)}")

    def save_file_content(self):
        if not self.current_file_path:
            return  # If no file is currently loaded, do nothing
        try:
            file_content = self.files_content_edit.toPlainText()
            save_text_to_docx(self.current_file_path, file_content)
            QMessageBox.information(self, "Success", "File saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def update_file_info(self, file_path):
        try:
            min_count = int(self.min_count_input.text()) if self.min_count_input.text().isdigit() else 2
            char_count, frequent_words = get_document_info(file_path, min_count)
            self.char_count_label.setText(f"Character count: {char_count}")
            self.frequent_words_list.clear()
            for word, count in frequent_words:
                item = QListWidgetItem(f"{word}: {count}")
                item.setData(Qt.UserRole, word)  # Store the word itself for highlighting
                self.frequent_words_list.addItem(item)
        except Exception as e:
            self.char_count_label.setText(f"Error: {str(e)}")
            self.frequent_words_list.clear()

    def apply_min_count(self):
        current_item = self.files_list_widget.currentItem()
        if current_item:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            workbench_dir = os.path.join(base_dir, "../data/작업대")
            file_path = os.path.join(workbench_dir, current_item.text())
            self.update_file_info(file_path)

    def highlight_word(self, item):
        word = item.data(Qt.UserRole)
        cursor = self.files_content_edit.textCursor()
        format = QTextCharFormat()
        format.setBackground(QColor("yellow"))

        # Clear existing highlights
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.endEditBlock()

        # Highlight the base word at the given positions
        positions = self.get_word_positions(self.files_content_edit.toPlainText()).get(word, [])
        for pos in positions:
            cursor.setPosition(pos)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(word))
            cursor.mergeCharFormat(format)

    def get_word_positions(self, text):
        words = text.split()
        positions = {}
        start = 0
        for word in words:
            start = text.find(word, start)
            if word not in positions:
                positions[word] = []
            positions[word].append(start)
            start += len(word)
        return positions
