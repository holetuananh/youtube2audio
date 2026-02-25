APP_NAME = "YouTube2Audio"
APP_VERSION = "1.0.0"
ORG_NAME = "YouTube2Audio"

# URL patterns
YOUTUBE_URL_PATTERNS = [
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
    r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
    r'(?:https?://)?youtu\.be/[\w-]+',
    r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
    r'(?:https?://)?music\.youtube\.com/watch\?v=[\w-]+',
]

# Audio format defaults
DEFAULT_AUDIO_FORMAT = "m4a"
SUPPORTED_AUDIO_FORMATS = ["m4a", "mp3", "opus", "wav"]
DEFAULT_AUDIO_BITRATE = "0"  # best available
SUPPORTED_BITRATES = ["0", "128", "192", "256", "320"]

# Download defaults
DEFAULT_MAX_CONCURRENT = 3
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

# UI defaults
DEFAULT_WINDOW_WIDTH = 1100
DEFAULT_WINDOW_HEIGHT = 700
SPLITTER_RATIO = [550, 550]
