def format_duration(seconds: int | None) -> str:
    if seconds is None or seconds < 0:
        return "--:--"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_speed(bytes_per_second: float | None) -> str:
    if bytes_per_second is None or bytes_per_second <= 0:
        return "-- KB/s"
    if bytes_per_second >= 1_048_576:
        return f"{bytes_per_second / 1_048_576:.1f} MB/s"
    return f"{bytes_per_second / 1024:.0f} KB/s"


def format_size(bytes_count: int | None) -> str:
    if bytes_count is None or bytes_count <= 0:
        return "--"
    if bytes_count >= 1_073_741_824:
        return f"{bytes_count / 1_073_741_824:.1f} GB"
    if bytes_count >= 1_048_576:
        return f"{bytes_count / 1_048_576:.1f} MB"
    return f"{bytes_count / 1024:.0f} KB"


def format_eta(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "--"
    return format_duration(int(seconds))
