import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from src.utils.constants import APP_NAME, ORG_NAME
from src.ui.main_window import MainWindow


def run() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)

    # Set app icon from music.ico (supports PyInstaller bundled path)
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, "music.ico")
    app.setWindowIcon(QIcon(icon_path))

    from src.ui.styles import DARK_STYLESHEET
    app.setStyleSheet(DARK_STYLESHEET)

    window = MainWindow()
    window.show()
    return app.exec()
