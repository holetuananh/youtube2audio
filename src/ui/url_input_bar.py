from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Signal


class UrlInputBar(QWidget):
    url_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Paste YouTube URL or playlist URL here...")
        self._input.returnPressed.connect(self._on_submit)

        self._add_btn = QPushButton("Add URL")
        self._add_btn.setObjectName("primaryButton")
        self._add_btn.clicked.connect(self._on_submit)

        layout.addWidget(self._input, 1)
        layout.addWidget(self._add_btn)

    def _on_submit(self):
        text = self._input.text().strip()
        if text:
            self.url_submitted.emit(text)
            self._input.clear()

    def set_enabled(self, enabled: bool):
        self._input.setEnabled(enabled)
        self._add_btn.setEnabled(enabled)
