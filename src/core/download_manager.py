from PySide6.QtCore import QObject, Signal, QTimer
from src.core.models import VideoItem, DownloadStatus
from src.core.download_worker import DownloadWorker
from src.utils.constants import DEFAULT_MAX_CONCURRENT, MAX_RETRIES, RETRY_DELAY_SECONDS


class DownloadManager(QObject):
    """Orchestrates download queue, concurrency, and retry logic."""
    item_updated = Signal(str)  # video_id — emitted whenever a VideoItem changes
    log_message = Signal(str)  # log text for the status panel
    queue_changed = Signal()  # emitted when items added/removed

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: dict[str, VideoItem] = {}
        self._order: list[str] = []  # maintains insertion order
        self._workers: dict[str, DownloadWorker] = {}
        self._output_dir: str = ""
        self._audio_format: str = "m4a"
        self._audio_bitrate: str = "0"
        self._max_concurrent: int = DEFAULT_MAX_CONCURRENT
        self._retry_timers: dict[str, QTimer] = {}

    # -- Configuration --
    def set_output_dir(self, path: str):
        self._output_dir = path

    def set_audio_format(self, fmt: str):
        self._audio_format = fmt

    def set_audio_bitrate(self, bitrate: str):
        self._audio_bitrate = bitrate

    def set_max_concurrent(self, n: int):
        self._max_concurrent = max(1, n)
        self._try_start_next()

    # -- Item management --
    def add_item(self, item: VideoItem) -> bool:
        """Add a video item. Returns False if duplicate URL."""
        for existing in self._items.values():
            if existing.url == item.url and existing.status not in (
                DownloadStatus.COMPLETED, DownloadStatus.CANCELLED, DownloadStatus.FAILED
            ):
                return False
        self._items[item.id] = item
        self._order.append(item.id)
        self.queue_changed.emit()
        return True

    def get_item(self, video_id: str) -> VideoItem | None:
        return self._items.get(video_id)

    def get_all_items(self) -> list[VideoItem]:
        return [self._items[vid] for vid in self._order if vid in self._items]

    def remove_items(self, video_ids: list[str]):
        for vid in video_ids:
            if vid in self._workers:
                self._workers[vid].cancel()
                self._workers[vid].wait(2000)
                del self._workers[vid]
            if vid in self._retry_timers:
                self._retry_timers[vid].stop()
                del self._retry_timers[vid]
            self._items.pop(vid, None)
            if vid in self._order:
                self._order.remove(vid)
        self.queue_changed.emit()

    def has_url(self, url: str) -> bool:
        for item in self._items.values():
            if item.url == url and item.status not in (
                DownloadStatus.COMPLETED, DownloadStatus.CANCELLED, DownloadStatus.FAILED
            ):
                return True
        return False

    # -- Download control --
    def start_all(self):
        for vid in self._order:
            item = self._items.get(vid)
            if item and item.status in (DownloadStatus.QUEUED, DownloadStatus.PAUSED, DownloadStatus.FAILED):
                item.status = DownloadStatus.QUEUED
                item.error_message = ""
                self.item_updated.emit(vid)
        self._try_start_next()

    def pause_all(self):
        for vid, worker in list(self._workers.items()):
            worker.cancel()
        for vid in self._order:
            item = self._items.get(vid)
            if item and item.status == DownloadStatus.QUEUED:
                item.status = DownloadStatus.PAUSED
                self.item_updated.emit(vid)

    def cancel_all(self):
        for vid, worker in list(self._workers.items()):
            worker.cancel()
        for vid in self._order:
            item = self._items.get(vid)
            if item and item.status in (DownloadStatus.QUEUED, DownloadStatus.DOWNLOADING, DownloadStatus.PAUSED):
                item.status = DownloadStatus.CANCELLED
                self.item_updated.emit(vid)

    def start_item(self, video_id: str):
        item = self._items.get(video_id)
        if not item:
            return
        item.status = DownloadStatus.QUEUED
        item.error_message = ""
        item.progress = 0.0
        self.item_updated.emit(video_id)
        self._try_start_next()

    def cancel_item(self, video_id: str):
        if video_id in self._workers:
            self._workers[video_id].cancel()
        item = self._items.get(video_id)
        if item:
            item.status = DownloadStatus.CANCELLED
            self.item_updated.emit(video_id)

    # -- Internal --
    def _active_count(self) -> int:
        return len(self._workers)

    def _try_start_next(self):
        while self._active_count() < self._max_concurrent:
            next_item = None
            for vid in self._order:
                item = self._items.get(vid)
                if item and item.status == DownloadStatus.QUEUED and vid not in self._workers:
                    next_item = item
                    break
            if not next_item:
                break
            self._start_download(next_item)

    def _start_download(self, item: VideoItem):
        if not self._output_dir:
            item.status = DownloadStatus.FAILED
            item.error_message = "No output folder selected"
            self.item_updated.emit(item.id)
            self.log_message.emit(f"[Error] {item.title}: No output folder selected")
            return

        item.status = DownloadStatus.DOWNLOADING
        item.progress = 0.0
        item.speed = None
        item.eta = None
        self.item_updated.emit(item.id)
        self.log_message.emit(f"[Start] {item.title}")

        worker = DownloadWorker(
            video_id=item.id,
            url=item.url,
            output_dir=self._output_dir,
            audio_format=self._audio_format,
            audio_bitrate=self._audio_bitrate,
        )
        worker.progress_updated.connect(self._on_progress)
        worker.download_completed.connect(self._on_completed)
        worker.download_failed.connect(self._on_failed)
        self._workers[item.id] = worker
        worker.start()

    def _on_progress(self, video_id: str, data: dict):
        item = self._items.get(video_id)
        if not item:
            return
        if data.get("status") == "downloading":
            total = data.get("total_bytes")
            downloaded = data.get("downloaded_bytes", 0)
            if total and total > 0:
                item.progress = (downloaded / total) * 100
            item.total_bytes = total
            item.downloaded_bytes = downloaded
            item.speed = data.get("speed")
            item.eta = data.get("eta")
            self.item_updated.emit(video_id)

    def _on_completed(self, video_id: str, file_path: str):
        self._workers.pop(video_id, None)
        item = self._items.get(video_id)
        if item:
            item.status = DownloadStatus.COMPLETED
            item.progress = 100.0
            item.file_path = file_path
            item.speed = None
            item.eta = None
            self.item_updated.emit(video_id)
            self.log_message.emit(f"[Done] {item.title}")
        self.queue_changed.emit()
        self._try_start_next()

    def _on_failed(self, video_id: str, error: str):
        self._workers.pop(video_id, None)
        item = self._items.get(video_id)
        if not item:
            self._try_start_next()
            return

        if error == "Cancelled":
            if item.status != DownloadStatus.CANCELLED:
                item.status = DownloadStatus.PAUSED
            self.item_updated.emit(video_id)
            self.log_message.emit(f"[Paused] {item.title}")
        elif item.retry_count < MAX_RETRIES:
            item.retry_count += 1
            item.status = DownloadStatus.QUEUED
            item.error_message = f"Retry {item.retry_count}/{MAX_RETRIES}: {error}"
            self.item_updated.emit(video_id)
            self.log_message.emit(
                f"[Retry {item.retry_count}/{MAX_RETRIES}] {item.title}: {error}"
            )
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._on_retry_timer(video_id))
            self._retry_timers[video_id] = timer
            timer.start(RETRY_DELAY_SECONDS * 1000)
        else:
            item.status = DownloadStatus.FAILED
            item.error_message = error
            self.item_updated.emit(video_id)
            self.log_message.emit(f"[Failed] {item.title}: {error}")

        self.queue_changed.emit()
        self._try_start_next()

    def _on_retry_timer(self, video_id: str):
        self._retry_timers.pop(video_id, None)
        self._try_start_next()

    # -- Stats --
    def get_stats(self) -> dict:
        stats = {"queued": 0, "downloading": 0, "completed": 0, "failed": 0, "paused": 0}
        for item in self._items.values():
            if item.status == DownloadStatus.QUEUED:
                stats["queued"] += 1
            elif item.status == DownloadStatus.DOWNLOADING:
                stats["downloading"] += 1
            elif item.status == DownloadStatus.COMPLETED:
                stats["completed"] += 1
            elif item.status == DownloadStatus.FAILED:
                stats["failed"] += 1
            elif item.status == DownloadStatus.PAUSED:
                stats["paused"] += 1
        return stats
