from utils.DownloadError import DownloadError


def retry(max_attempts: int, func: callable, *args, **kwargs) -> any:
    for attempt in range(max_attempts):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            pass
    raise DownloadError("Exceeded maximum number of attempts")
