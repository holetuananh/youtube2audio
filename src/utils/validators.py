import re
from src.utils.constants import YOUTUBE_URL_PATTERNS


def is_valid_youtube_url(url: str) -> bool:
    url = url.strip()
    for pattern in YOUTUBE_URL_PATTERNS:
        if re.search(pattern, url):
            return True
    return False


def extract_urls_from_text(text: str) -> list[str]:
    urls = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line and is_valid_youtube_url(line):
            urls.append(line)
    if not urls and is_valid_youtube_url(text.strip()):
        urls.append(text.strip())
    return urls
