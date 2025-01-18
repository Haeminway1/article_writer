from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QFormLayout, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt

class CheckItemWidget(QWidget):
    check_selected = pyqtSignal(str)
    check_toggled = pyqtSignal(str, bool)

    def __init__(self, check_name, parent=None):
        super().__init__(parent)
        self.check_name = check_name
        self.layout = QHBoxLayout(self)
        self.checkbox = QCheckBox()
        self.label = QLabel(check_name)
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.checkbox.stateChanged.connect(self.on_toggled)
        self.label.mousePressEvent = self.on_selected

    def on_selected(self, event):
        self.check_selected.emit(self.check_name)

    def on_toggled(self, state):
        self.check_toggled.emit(self.check_name, state == Qt.Checked)
class CheckSettingsWidget(QWidget):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        self.settings = {}

    def load_settings(self, settings):
        self.settings = settings

        # Clear existing settings
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new settings
        for key, value in settings.items():
            label = QLabel(f"{key}:")
            edit = QLineEdit(str(value))
            edit.editingFinished.connect(lambda key=key, edit=edit: self.save_setting(key, edit))
            self.form_layout.addRow(label, edit)

    def save_setting(self, key, edit):
        value = edit.text()
        self.settings[key] = value
        self.settings_changed.emit(self.settings)
