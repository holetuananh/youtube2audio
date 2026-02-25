from PySide6.QtCore import QThread, Signal
from src.core.ytdlp_wrapper import download_audio, DownloadCancelled


class DownloadWorker(QThread):
    """Downloads a single video's audio in a background thread."""
    progress_updated = Signal(str, dict)  # (video_id, progress_data)
    download_completed = Signal(str, str)  # (video_id, file_path)
    download_failed = Signal(str, str)  # (video_id, error_message)

    def __init__(self, video_id: str, url: str, output_dir: str,
                 audio_format: str = "m4a", audio_bitrate: str = "0",
                 parent=None):
        super().__init__(parent)
        self.video_id = video_id
        self.url = url
        self.output_dir = output_dir
        self.audio_format = audio_format
        self.audio_bitrate = audio_bitrate
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            def on_progress(data):
                self.progress_updated.emit(self.video_id, data)

            file_path = download_audio(
                url=self.url,
                output_dir=self.output_dir,
                audio_format=self.audio_format,
                audio_bitrate=self.audio_bitrate,
                progress_hook=on_progress,
                cancel_flag=lambda: self._cancelled,
            )
            if self._cancelled:
                self.download_failed.emit(self.video_id, "Cancelled")
            else:
                self.download_completed.emit(self.video_id, file_path)
        except DownloadCancelled:
            self.download_failed.emit(self.video_id, "Cancelled")
        except Exception as e:
            self.download_failed.emit(self.video_id, str(e))
