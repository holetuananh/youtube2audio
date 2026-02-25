from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from PySide6.QtCore import Qt
from datetime import datetime


class StatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Download Log")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self._info_label = QLabel("Ready")
        self._info_label.setWordWrap(True)
        layout.addWidget(self._info_label)

        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(1000)
        layout.addWidget(self._log, 1)

    def append_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log.appendPlainText(f"[{timestamp}] {message}")

    def set_info(self, text: str):
        self._info_label.setText(text)

    def clear_log(self):
        self._log.clear()
