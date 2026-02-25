from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QPushButton, QGroupBox, QFormLayout,
)
from src.utils.constants import SUPPORTED_AUDIO_FORMATS, SUPPORTED_BITRATES, DEFAULT_MAX_CONCURRENT


class SettingsDialog(QDialog):
    def __init__(self, current_format: str, current_bitrate: str,
                 current_concurrent: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        # Audio settings group
        audio_group = QGroupBox("Audio Settings")
        audio_form = QFormLayout(audio_group)

        self._format_combo = QComboBox()
        self._format_combo.addItems(SUPPORTED_AUDIO_FORMATS)
        self._format_combo.setCurrentText(current_format)
        audio_form.addRow("Format:", self._format_combo)

        self._bitrate_combo = QComboBox()
        bitrate_labels = ["Best (auto)", "128 kbps", "192 kbps", "256 kbps", "320 kbps"]
        for val, label in zip(SUPPORTED_BITRATES, bitrate_labels):
            self._bitrate_combo.addItem(label, val)
        idx = SUPPORTED_BITRATES.index(current_bitrate) if current_bitrate in SUPPORTED_BITRATES else 0
        self._bitrate_combo.setCurrentIndex(idx)
        audio_form.addRow("Bitrate:", self._bitrate_combo)

        layout.addWidget(audio_group)

        # Download settings group
        dl_group = QGroupBox("Download Settings")
        dl_form = QFormLayout(dl_group)

        self._concurrent_spin = QSpinBox()
        self._concurrent_spin.setRange(1, 10)
        self._concurrent_spin.setValue(current_concurrent)
        dl_form.addRow("Max concurrent downloads:", self._concurrent_spin)

        layout.addWidget(dl_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Save")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def get_values(self) -> dict:
        return {
            "audio_format": self._format_combo.currentText(),
            "audio_bitrate": self._bitrate_combo.currentData(),
            "max_concurrent": self._concurrent_spin.value(),
        }
