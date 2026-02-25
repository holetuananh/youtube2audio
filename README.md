# YouTube2Audio — YouTube to MP3 / M4A Downloader for Windows

**YouTube2Audio** is a free, open-source Windows desktop app to download YouTube videos and playlists as high-quality audio files. Convert YouTube to MP3, M4A, Opus, or WAV with a single click — no browser extensions or online converters needed.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![PySide6](https://img.shields.io/badge/GUI-PySide6-green)
![yt-dlp](https://img.shields.io/badge/Backend-yt--dlp-red)
![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Why YouTube2Audio?

- **YouTube to MP3** — download any YouTube video as an MP3 file
- **YouTube to M4A** — save audio in high-quality M4A (AAC) format
- **YouTube Playlist Downloader** — paste a playlist URL and download all tracks at once
- **Batch Audio Downloader** — queue multiple YouTube URLs and download them all
- **No Ads, No Limits** — completely free and open-source, runs locally on your PC

## Features

- **Drag & Drop** — drag YouTube URLs directly from your browser into the app
- **Playlist Support** — automatically expands YouTube playlists into individual tracks
- **Concurrent Downloads** — download multiple audio files simultaneously (configurable 1–10)
- **Real-time Progress** — progress bars, download speed, and ETA for each track
- **Pause / Resume** — pause and resume downloads at any time
- **Auto Retry** — failed downloads automatically retry up to 3 times
- **Multiple Audio Formats** — convert YouTube to MP3, M4A, Opus, or WAV
- **Bitrate Selection** — choose from 128, 192, 256, 320 kbps or best available quality
- **Dark Theme** — modern dark-themed user interface
- **Persistent Settings** — output folder, audio format, and window layout saved between sessions
- **Keyboard Shortcuts** — select and delete queued videos with Delete key

## Download

**[Download YouTube2Audio.exe](https://github.com/holetuananh/youtube2audio/releases/latest)** — portable, no installation required.

## Screenshots

| Main Window | Parsed Playlist |
|:-----------:|:---------------:|
| ![Main](screenshots/main_app.png) | ![Parsed](screenshots/main_app_with_parsed_url.png) |

| Downloading | Context Menu |
|:-----------:|:------------:|
| ![Downloading](screenshots/main_app_after_downloading_youtube.png) | ![Context Menu](screenshots/main_app_context_menu.png) |

## Requirements

- Windows 10 or Windows 11
- [ffmpeg](https://ffmpeg.org/download.html) (required for MP3 conversion, optional for M4A)

## Installation (from source)

```bash
# Clone the repository
git clone https://github.com/holetuananh/youtube2audio.git
cd youtube2audio

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## Usage

1. Launch the app — output folder defaults to your **Music** folder
2. Paste a YouTube video or playlist URL and click **Add URL**, or drag and drop from your browser
3. Click **Start All** to begin downloading audio
4. Downloaded MP3/M4A files appear in your output folder
5. Right-click completed downloads to **Open Folder** in Explorer

## Settings

Click **Settings** to configure:

| Option         | Default     | Description                                |
| -------------- | ----------- | ------------------------------------------ |
| Audio Format   | m4a         | m4a, mp3, opus, or wav                     |
| Bitrate        | Best (auto) | 128, 192, 256, 320 kbps, or best available |
| Max Concurrent | 3           | Simultaneous downloads (1–10)              |

## Build Executable

```bash
venv\Scripts\activate
build.bat
```

Output: `dist\YouTube2Audio.exe`

## Tech Stack

- **Python 3.12+** — application language
- **PySide6** — cross-platform GUI framework
- **yt-dlp** — YouTube audio/video download backend
- **PyInstaller** — packages the app into a standalone `.exe`

## Project Structure

```
youtube2audio/
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── build.bat                # Build script for .exe
├── music.ico                # App icon
├── src/
│   ├── app.py               # QApplication setup
│   ├── core/
│   │   ├── models.py        # Data models
│   │   ├── ytdlp_wrapper.py # yt-dlp integration
│   │   ├── url_resolver.py  # Async URL metadata fetcher
│   │   ├── download_worker.py   # Download thread
│   │   └── download_manager.py  # Queue and concurrency manager
│   ├── services/
│   │   └── settings_service.py  # QSettings persistence
│   └── ui/
│       ├── main_window.py       # Main window with drag-drop
│       ├── download_panel.py    # Download queue table
│       ├── status_panel.py      # Log panel
│       ├── url_input_bar.py     # URL input widget
│       ├── settings_dialog.py   # Settings modal
│       └── styles.py            # Dark theme stylesheet
```

## Keywords

youtube to mp3, youtube to m4a, youtube audio downloader, youtube playlist downloader, youtube mp3 converter, download youtube audio, youtube music downloader, yt-dlp gui, youtube to wav, batch youtube downloader, free youtube downloader windows

## License

MIT
