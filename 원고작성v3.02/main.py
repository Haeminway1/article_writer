import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from page1_model.model_page import ModelPage
from page2_checks.checks_page import ChecksPage
from page3_manual_checks.manual_checks_page import ManualChecksPage
from page4_export.export_page import ExportPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Config Manager')
        self.setGeometry(100, 100, 1200, 800)  # Adjusted window size
        
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.tabs = QTabWidget()
        
        self.layout.addWidget(self.tabs)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        self.model_page = ModelPage(self)
        self.model_page.model_selected.connect(self.update_checks_page)
        
        self.checks_page = ChecksPage(model_name="default_model", parent=self)
        self.manual_checks_page = ManualChecksPage(self)
        self.export_page = ExportPage(self)
        
        self.tabs.addTab(self.model_page, "Model")
        self.tabs.addTab(self.checks_page, "Checks")
        self.tabs.addTab(self.manual_checks_page, "Manual Checks")
        self.tabs.addTab(self.export_page, "Export")

    def update_checks_page(self, model_name):
        self.checks_page.set_model_name(model_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
