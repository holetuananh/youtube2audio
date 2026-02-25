from PySide6.QtCore import QThread, Signal
from src.core.ytdlp_wrapper import extract_metadata


class UrlResolverWorker(QThread):
    """Resolves a URL to one or more VideoItem metadata dicts in a background thread."""
    resolved = Signal(str, list)  # (original_url, list of metadata dicts)
    error = Signal(str, str)  # (original_url, error_message)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            results = extract_metadata(self.url)
            if not results:
                self.error.emit(self.url, "No videos found at this URL")
            else:
                self.resolved.emit(self.url, results)
        except Exception as e:
            self.error.emit(self.url, str(e))
