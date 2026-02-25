from pathlib import Path
from PySide6.QtCore import QSettings, QStandardPaths
from src.core.models import AppSettings
from src.utils.constants import APP_NAME, ORG_NAME, DEFAULT_MAX_CONCURRENT


def _default_output_folder() -> str:
    music = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation)
    if music:
        return music
    return str(Path.home() / "Music")


def load_settings() -> AppSettings:
    s = QSettings(ORG_NAME, APP_NAME)
    return AppSettings(
        output_folder=s.value("output_folder", _default_output_folder(), type=str),
        audio_format=s.value("audio_format", "m4a", type=str),
        audio_bitrate=s.value("audio_bitrate", "0", type=str),
        max_concurrent=s.value("max_concurrent", DEFAULT_MAX_CONCURRENT, type=int),
        window_geometry=s.value("window_geometry", b"", type=bytes),
        splitter_state=s.value("splitter_state", b"", type=bytes),
    )


def save_settings(settings: AppSettings):
    s = QSettings(ORG_NAME, APP_NAME)
    s.setValue("output_folder", settings.output_folder)
    s.setValue("audio_format", settings.audio_format)
    s.setValue("audio_bitrate", settings.audio_bitrate)
    s.setValue("max_concurrent", settings.max_concurrent)
    s.setValue("window_geometry", settings.window_geometry)
    s.setValue("splitter_state", settings.splitter_state)
