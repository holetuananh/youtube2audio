import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QFileDialog, QStatusBar, QToolBar, QLineEdit, QLabel,
    QMessageBox,
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent

from src.core.models import VideoItem, DownloadStatus
from src.core.download_manager import DownloadManager
from src.core.url_resolver import UrlResolverWorker
from src.services.settings_service import load_settings, save_settings
from src.ui.url_input_bar import UrlInputBar
from src.ui.download_panel import DownloadPanel
from src.ui.status_panel import StatusPanel
from src.ui.settings_dialog import SettingsDialog
from src.utils.constants import (
    APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, SPLITTER_RATIO,
)
from src.utils.validators import is_valid_youtube_url, extract_urls_from_text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 500)
        self.setAcceptDrops(True)

        self._settings = load_settings()
        self._resolver_workers: list[UrlResolverWorker] = []

        # Core manager
        self._manager = DownloadManager(self)
        self._manager.set_output_dir(self._settings.output_folder)
        self._manager.set_audio_format(self._settings.audio_format)
        self._manager.set_audio_bitrate(self._settings.audio_bitrate)
        self._manager.set_max_concurrent(self._settings.max_concurrent)

        self._build_ui()
        self._connect_signals()
        self._restore_state()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # -- Toolbar --
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(toolbar)

        self._start_all_btn = QPushButton("Start All")
        self._start_all_btn.setObjectName("primaryButton")
        self._pause_all_btn = QPushButton("Pause All")
        self._cancel_all_btn = QPushButton("Cancel All")
        self._cancel_all_btn.setObjectName("dangerButton")
        self._remove_btn = QPushButton("Remove Selected")
        self._settings_btn = QPushButton("Settings")

        toolbar.addWidget(self._start_all_btn)
        toolbar.addWidget(self._pause_all_btn)
        toolbar.addWidget(self._cancel_all_btn)
        toolbar.addSeparator()
        toolbar.addWidget(self._remove_btn)
        toolbar.addSeparator()
        toolbar.addWidget(self._settings_btn)

        # -- Output folder row --
        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Output:"))
        self._folder_edit = QLineEdit()
        self._folder_edit.setReadOnly(True)
        self._folder_edit.setPlaceholderText("Select output folder...")
        self._folder_edit.setText(self._settings.output_folder)
        folder_row.addWidget(self._folder_edit, 1)
        self._browse_btn = QPushButton("Browse")
        self._browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(self._browse_btn)
        main_layout.addLayout(folder_row)

        # -- URL input --
        self._url_input = UrlInputBar()
        main_layout.addWidget(self._url_input)

        # -- Splitter: left (download panel) + right (status panel) --
        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        self._download_panel = DownloadPanel()
        self._status_panel = StatusPanel()

        self._splitter.addWidget(self._download_panel)
        self._splitter.addWidget(self._status_panel)
        self._splitter.setSizes(SPLITTER_RATIO)

        main_layout.addWidget(self._splitter, 1)

        # -- Status bar --
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._update_status_bar()

    def _connect_signals(self):
        # URL input
        self._url_input.url_submitted.connect(self._on_url_submitted)

        # Toolbar
        self._start_all_btn.clicked.connect(self._manager.start_all)
        self._pause_all_btn.clicked.connect(self._manager.pause_all)
        self._cancel_all_btn.clicked.connect(self._manager.cancel_all)
        self._remove_btn.clicked.connect(self._on_remove_selected)
        self._settings_btn.clicked.connect(self._open_settings)

        # Manager signals
        self._manager.item_updated.connect(self._on_item_updated)
        self._manager.log_message.connect(self._status_panel.append_log)
        self._manager.queue_changed.connect(self._update_status_bar)

        # Download panel
        self._download_panel.remove_requested.connect(self._on_remove_items)
        self._download_panel.retry_requested.connect(self._manager.start_item)

    def _restore_state(self):
        if self._settings.window_geometry:
            self.restoreGeometry(self._settings.window_geometry)
        else:
            self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        if self._settings.splitter_state:
            self._splitter.restoreState(self._settings.splitter_state)

    def closeEvent(self, event):
        self._settings.window_geometry = bytes(self.saveGeometry())
        self._settings.splitter_state = bytes(self._splitter.saveState())
        save_settings(self._settings)
        self._manager.cancel_all()
        super().closeEvent(event)

    # -- URL handling --
    def _on_url_submitted(self, text: str):
        urls = extract_urls_from_text(text)
        if not urls:
            if is_valid_youtube_url(text):
                urls = [text]
            else:
                self._status_panel.append_log(f"[Warning] Invalid YouTube URL: {text}")
                return

        for url in urls:
            if self._manager.has_url(url):
                self._status_panel.append_log(f"[Skip] Already in queue: {url}")
                continue
            self._resolve_url(url)

    def _resolve_url(self, url: str):
        # Add a placeholder item while resolving
        placeholder = VideoItem(url=url, title="Resolving...", status=DownloadStatus.RESOLVING)
        self._manager.add_item(placeholder)
        self._download_panel.add_item(placeholder)

        worker = UrlResolverWorker(url, self)
        worker.resolved.connect(lambda orig_url, results: self._on_resolved(placeholder.id, orig_url, results))
        worker.error.connect(lambda orig_url, err: self._on_resolve_error(placeholder.id, orig_url, err))
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._resolver_workers.append(worker)
        worker.start()

    def _on_resolved(self, placeholder_id: str, original_url: str, results: list[dict]):
        if len(results) == 1:
            # Single video — update the placeholder
            item = self._manager.get_item(placeholder_id)
            if item:
                item.title = results[0].get("title", "Unknown")
                item.duration = results[0].get("duration")
                item.url = results[0].get("url", original_url)
                item.status = DownloadStatus.QUEUED
                self._manager.item_updated.emit(item.id)
                self._download_panel.update_item(item)
                self._status_panel.append_log(f"[Resolved] {item.title}")
        else:
            # Playlist — remove placeholder, add individual items
            self._manager.remove_items([placeholder_id])
            self._download_panel.remove_items([placeholder_id])
            self._status_panel.append_log(f"[Playlist] Found {len(results)} videos")

            for meta in results:
                url = meta.get("url", original_url)
                if self._manager.has_url(url):
                    continue
                item = VideoItem(
                    url=url,
                    title=meta.get("title", "Unknown"),
                    duration=meta.get("duration"),
                    status=DownloadStatus.QUEUED,
                )
                self._manager.add_item(item)
                self._download_panel.add_item(item)

        self._update_status_bar()

    def _on_resolve_error(self, placeholder_id: str, original_url: str, error: str):
        item = self._manager.get_item(placeholder_id)
        if item:
            item.status = DownloadStatus.FAILED
            item.error_message = error
            item.title = f"Failed: {original_url[:50]}"
            self._download_panel.update_item(item)
        self._status_panel.append_log(f"[Error] Could not resolve: {error}")
        self._update_status_bar()

    def _cleanup_worker(self, worker: UrlResolverWorker):
        if worker in self._resolver_workers:
            self._resolver_workers.remove(worker)
        worker.deleteLater()

    # -- Item management --
    def _on_item_updated(self, video_id: str):
        item = self._manager.get_item(video_id)
        if item:
            self._download_panel.update_item(item)
        self._update_status_bar()

    def _on_remove_selected(self):
        selected = self._download_panel.get_selected_ids()
        if selected:
            self._on_remove_items(selected)

    def _on_remove_items(self, video_ids: list[str]):
        self._manager.remove_items(video_ids)
        self._download_panel.remove_items(video_ids)
        self._update_status_bar()

    # -- Folder --
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self._settings.output_folder
        )
        if folder:
            self._settings.output_folder = folder
            self._folder_edit.setText(folder)
            self._manager.set_output_dir(folder)
            save_settings(self._settings)

    # -- Settings --
    def _open_settings(self):
        dlg = SettingsDialog(
            current_format=self._settings.audio_format,
            current_bitrate=self._settings.audio_bitrate,
            current_concurrent=self._settings.max_concurrent,
            parent=self,
        )
        if dlg.exec():
            vals = dlg.get_values()
            self._settings.audio_format = vals["audio_format"]
            self._settings.audio_bitrate = vals["audio_bitrate"]
            self._settings.max_concurrent = vals["max_concurrent"]
            self._manager.set_audio_format(vals["audio_format"])
            self._manager.set_audio_bitrate(vals["audio_bitrate"])
            self._manager.set_max_concurrent(vals["max_concurrent"])
            save_settings(self._settings)
            self._status_panel.append_log("[Settings] Updated")

    # -- Status bar --
    def _update_status_bar(self):
        stats = self._manager.get_stats()
        parts = []
        if stats["queued"]:
            parts.append(f"{stats['queued']} queued")
        if stats["downloading"]:
            parts.append(f"{stats['downloading']} downloading")
        if stats["paused"]:
            parts.append(f"{stats['paused']} paused")
        if stats["completed"]:
            parts.append(f"{stats['completed']} completed")
        if stats["failed"]:
            parts.append(f"{stats['failed']} failed")
        self._status_bar.showMessage(" | ".join(parts) if parts else "Ready")

    # -- Drag and Drop --
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mime = event.mimeData()
        text = ""
        if mime.hasUrls():
            text = "\n".join(url.toString() for url in mime.urls())
        elif mime.hasText():
            text = mime.text()

        if text:
            self._on_url_submitted(text)
        event.acceptProposedAction()
