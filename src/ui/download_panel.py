from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QMenu, QAbstractItemView, QLabel,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QDesktopServices, QKeyEvent, QShortcut, QKeySequence
from PySide6.QtCore import QUrl
import webbrowser

from src.core.models import VideoItem, DownloadStatus
from src.utils.formatters import format_duration, format_speed, format_eta


COL_TITLE = 0
COL_DURATION = 1
COL_STATUS = 2
COL_PROGRESS = 3
COL_SPEED = 4
COL_ETA = 5
COLUMN_COUNT = 6


class DownloadPanel(QWidget):
    remove_requested = Signal(list)  # list of video_ids
    retry_requested = Signal(str)  # video_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._video_ids: list[str] = []  # row index -> video_id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Download Queue")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self._table = QTableWidget(0, COLUMN_COUNT)
        self._table.setHorizontalHeaderLabels([
            "Title", "Duration", "Status", "Progress", "Speed", "ETA"
        ])
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(COL_TITLE, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(COL_DURATION, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(COL_STATUS, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(COL_PROGRESS, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(COL_SPEED, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(COL_ETA, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setColumnWidth(COL_PROGRESS, 160)

        self._table.keyPressEvent = self._table_key_press
        layout.addWidget(self._table)

        # Store URL and file path mappings for context menu
        self._url_map: dict[str, str] = {}
        self._file_map: dict[str, str] = {}  # video_id -> downloaded file path

    def add_item(self, item: VideoItem):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._video_ids.append(item.id)
        self._url_map[item.id] = item.url

        self._table.setItem(row, COL_TITLE, QTableWidgetItem(item.title or "Resolving..."))
        self._table.setItem(row, COL_DURATION, QTableWidgetItem(format_duration(item.duration)))
        self._table.setItem(row, COL_STATUS, self._status_item(item.status))

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(item.progress))
        self._table.setCellWidget(row, COL_PROGRESS, progress_bar)

        self._table.setItem(row, COL_SPEED, QTableWidgetItem(""))
        self._table.setItem(row, COL_ETA, QTableWidgetItem(""))

    def update_item(self, item: VideoItem):
        row = self._get_row(item.id)
        if row < 0:
            return

        title_item = self._table.item(row, COL_TITLE)
        if title_item and title_item.text() != item.title and item.title:
            title_item.setText(item.title)

        duration_item = self._table.item(row, COL_DURATION)
        if duration_item:
            duration_item.setText(format_duration(item.duration))

        self._table.setItem(row, COL_STATUS, self._status_item(item.status))

        progress_bar = self._table.cellWidget(row, COL_PROGRESS)
        if isinstance(progress_bar, QProgressBar):
            progress_bar.setValue(int(item.progress))

        speed_item = self._table.item(row, COL_SPEED)
        if speed_item:
            speed_item.setText(format_speed(item.speed) if item.status == DownloadStatus.DOWNLOADING else "")

        eta_item = self._table.item(row, COL_ETA)
        if eta_item:
            eta_item.setText(format_eta(item.eta) if item.status == DownloadStatus.DOWNLOADING else "")

        self._url_map[item.id] = item.url
        if item.file_path:
            self._file_map[item.id] = item.file_path

    def remove_items(self, video_ids: list[str]):
        for vid in sorted(video_ids, key=lambda v: self._get_row(v), reverse=True):
            row = self._get_row(vid)
            if row >= 0:
                self._table.removeRow(row)
                self._video_ids.remove(vid)
                self._url_map.pop(vid, None)
                self._file_map.pop(vid, None)

    def get_selected_ids(self) -> list[str]:
        rows = set()
        for idx in self._table.selectedIndexes():
            rows.add(idx.row())
        return [self._video_ids[r] for r in sorted(rows) if r < len(self._video_ids)]

    def _get_row(self, video_id: str) -> int:
        try:
            return self._video_ids.index(video_id)
        except ValueError:
            return -1

    def _status_item(self, status: DownloadStatus) -> QTableWidgetItem:
        item = QTableWidgetItem(status.value)
        colors = {
            DownloadStatus.QUEUED: "#a6adc8",
            DownloadStatus.RESOLVING: "#f9e2af",
            DownloadStatus.DOWNLOADING: "#89b4fa",
            DownloadStatus.PAUSED: "#fab387",
            DownloadStatus.COMPLETED: "#a6e3a1",
            DownloadStatus.FAILED: "#f38ba8",
            DownloadStatus.CANCELLED: "#6c7086",
        }
        from PySide6.QtGui import QColor
        item.setForeground(QColor(colors.get(status, "#cdd6f4")))
        return item

    def _show_context_menu(self, pos):
        selected = self.get_selected_ids()
        if not selected:
            return

        menu = QMenu(self)

        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(lambda: self.remove_requested.emit(selected))
        menu.addAction(remove_action)

        if len(selected) == 1:
            url = self._url_map.get(selected[0], "")
            if url:
                copy_action = QAction("Copy URL", self)
                copy_action.triggered.connect(lambda: self._copy_url(url))
                menu.addAction(copy_action)

                open_action = QAction("Open in Browser", self)
                open_action.triggered.connect(lambda: webbrowser.open(url))
                menu.addAction(open_action)

            file_path = self._file_map.get(selected[0], "")
            if file_path:
                open_folder_action = QAction("Open Folder", self)
                open_folder_action.triggered.connect(lambda: self._open_folder(file_path))
                menu.addAction(open_folder_action)

            menu.addSeparator()
            retry_action = QAction("Retry", self)
            retry_action.triggered.connect(lambda: self.retry_requested.emit(selected[0]))
            menu.addAction(retry_action)

        menu.exec(self._table.mapToGlobal(pos))

    def _table_key_press(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            selected = self.get_selected_ids()
            if selected:
                self.remove_requested.emit(selected)
        else:
            QTableWidget.keyPressEvent(self._table, event)

    def _open_folder(self, file_path: str):
        import subprocess, os
        folder = os.path.dirname(file_path)
        if os.path.isfile(file_path):
            # Select the file in Explorer
            subprocess.Popen(["explorer", "/select,", os.path.normpath(file_path)])
        elif os.path.isdir(folder):
            os.startfile(folder)

    def _copy_url(self, url: str):
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(url)
