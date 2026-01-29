import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "filename": record.filename,
            "line_number": record.lineno,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def setup_logging(log_level: str) -> None:
    """Configure application logging with JSON format."""
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)