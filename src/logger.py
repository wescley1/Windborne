import logging
import os
from datetime import datetime
from logging import StreamHandler, FileHandler

_configured = False
_log_file = None


def _make_log_filename(prefix: str = "windborne") -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    fname = f"{prefix}_{ts}.log"
    return os.path.join("logs", fname)


def setup_logging(level: str = None, json_format: bool = False):
    global _configured, _log_file
    if _configured:
        return _log_file

    level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    os.makedirs("logs", exist_ok=True)
    _log_file = os.getenv("LOG_FILE") or _make_log_filename()

    root = logging.getLogger()
    root.setLevel(level)

    # Console handler
    ch = StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(ch)

    # File handler (unique file per process invocation)
    fh = FileHandler(_log_file, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s [%(module)s:%(lineno)d] %(message)s"))
    root.addHandler(fh)

    _configured = True
    return _log_file


def get_logger(name: str = None) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)


__all__ = ["get_logger", "setup_logging"]
