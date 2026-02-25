import yt_dlp
from pathlib import Path


class DownloadCancelled(Exception):
    pass


def extract_metadata(url: str) -> list[dict]:
    """Extract metadata for a URL. Returns a list of dicts (one per video, multiple for playlists)."""
    # First try flat extraction (fast — single request for playlists)
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "ignoreerrors": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info is None:
            return []

        results = []
        if "entries" in info:
            for entry in info["entries"]:
                if entry is None:
                    continue
                entry_url = entry.get("url", "")
                # Flat extraction gives video IDs — build full URL
                if entry_url and not entry_url.startswith("http"):
                    entry_url = f"https://www.youtube.com/watch?v={entry_url}"
                results.append({
                    "url": entry.get("webpage_url") or entry_url or url,
                    "title": entry.get("title", "Unknown"),
                    "duration": entry.get("duration"),
                })
        else:
            results.append({
                "url": info.get("webpage_url") or info.get("url", url),
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration"),
            })
        return results


def download_audio(
    url: str,
    output_dir: str,
    audio_format: str = "m4a",
    audio_bitrate: str = "0",
    progress_hook=None,
    cancel_flag=None,
) -> str:
    """Download audio from a URL. Returns the path of the downloaded file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outtmpl = str(output_dir / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": f"bestaudio[ext={audio_format}]/bestaudio/best",
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
        "noprogress": True,
    }

    if audio_format == "mp3":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": audio_bitrate if audio_bitrate != "0" else "0",
        }]
    elif audio_bitrate != "0":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": audio_bitrate,
        }]

    downloaded_file = None

    def _progress_hook(d):
        nonlocal downloaded_file
        if cancel_flag and cancel_flag():
            raise DownloadCancelled("Download cancelled by user")

        if d["status"] == "downloading":
            if progress_hook:
                progress_hook({
                    "status": "downloading",
                    "downloaded_bytes": d.get("downloaded_bytes", 0),
                    "total_bytes": d.get("total_bytes") or d.get("total_bytes_estimate"),
                    "speed": d.get("speed"),
                    "eta": d.get("eta"),
                })
        elif d["status"] == "finished":
            downloaded_file = d.get("filename", "")
            if progress_hook:
                progress_hook({
                    "status": "finished",
                    "filename": downloaded_file,
                })

    ydl_opts["progress_hooks"] = [_progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return downloaded_file or ""
