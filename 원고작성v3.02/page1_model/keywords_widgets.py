import pandas as pd
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QApplication, QAbstractItemView, QAction
)
from PyQt5.QtCore import Qt

class KeywordTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.setSelectionMode(QTableWidget.ExtendedSelection)
        self.setSelectionBehavior(QTableWidget.SelectItems)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.load_keywords()
        
        # Enable context menu and set keyboard shortcuts
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.addAction(self.create_action("복사", self.copy_selection, "Ctrl+C"))
        self.addAction(self.create_action("붙여넣기", self.paste_selection, "Ctrl+V"))
        self.addAction(self.create_action("삭제", self.delete_selection, "Delete"))

        # Connect cell change signal to the save function
        self.cellChanged.connect(self.save_keywords)

    def create_action(self, name, method, shortcut):
        action = QAction(name, self)
        action.triggered.connect(method)
        action.setShortcut(shortcut)
        return action

    def load_keywords(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        keywords_path = os.path.join(base_dir, 'data', 'keywords.xlsx')
        
        try:
            df = pd.read_excel(keywords_path)
            self.setColumnCount(len(df.columns))
            self.setHorizontalHeaderLabels(df.columns)

            # Set row count to maximum of 50 or the length of the dataframe
            row_count = max(50, len(df))
            self.setRowCount(row_count)
            
            for index, row in df.iterrows():
                for col_index, value in enumerate(row):
                    self.setItem(index, col_index, QTableWidgetItem(str(value) if pd.notna(value) else ""))

            # Fill remaining rows with empty cells
            for row in range(len(df), row_count):
                for col in range(self.columnCount()):
                    self.setItem(row, col, QTableWidgetItem(""))

        except Exception as e:
            QMessageBox.critical(self, "로드 실패", str(e))

    def save_keywords(self):
        rows = []
        for row in range(self.rowCount()):
            row_data = {}
            for col in range(self.columnCount()):
                item = self.item(row, col)
                row_data[self.horizontalHeaderItem(col).text()] = item.text() if item else ""
            rows.append(row_data)
        df = pd.DataFrame(rows)
        try:
            df.to_excel(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'keywords.xlsx'), index=False)
            # QMessageBox.information(self, "저장 성공", "키워드가 성공적으로 저장되었습니다.") # 저장 성공 메시지 제거
        except Exception as e:
            QMessageBox.critical(self, "저장 실패", str(e))

    def copy_selection(self):
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        copied_data = []
        for selected_range in selected_ranges:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                row_data = []
                for col in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                    item = self.item(row, col)
                    row_data.append(item.text() if item else "")
                copied_data.append('\t'.join(row_data))
        
        clipboard = QApplication.clipboard()
        clipboard.setText('\n'.join(copied_data))

    def paste_selection(self):
        clipboard = QApplication.clipboard()
        pasted_data = clipboard.text()
        if not pasted_data:
            return

        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        start_row = selected_ranges[0].topRow()
        start_col = selected_ranges[0].leftColumn()
        
        for row_offset, row_data in enumerate(pasted_data.split('\n')):
            for col_offset, cell_data in enumerate(row_data.split('\t')):
                self.setItem(start_row + row_offset, start_col + col_offset, QTableWidgetItem(cell_data))

    def delete_selection(self):
        selected_ranges = self.selectedRanges()
        for selected_range in selected_ranges:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                for col in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                    self.setItem(row, col, QTableWidgetItem(""))

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    table_widget = KeywordTableWidget()
    layout.addWidget(table_widget)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())
