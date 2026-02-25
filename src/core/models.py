from dataclasses import dataclass, field
from enum import Enum
import uuid


class DownloadStatus(Enum):
    QUEUED = "Queued"
    RESOLVING = "Resolving..."
    DOWNLOADING = "Downloading"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


@dataclass
class VideoItem:
    url: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    duration: int | None = None
    status: DownloadStatus = DownloadStatus.QUEUED
    progress: float = 0.0
    speed: float | None = None
    eta: float | None = None
    downloaded_bytes: int = 0
    total_bytes: int | None = None
    error_message: str = ""
    retry_count: int = 0
    file_path: str = ""


@dataclass
class AppSettings:
    output_folder: str = ""
    audio_format: str = "m4a"
    audio_bitrate: str = "0"
    max_concurrent: int = 3
    window_geometry: bytes = b""
    splitter_state: bytes = b""
