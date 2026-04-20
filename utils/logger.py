import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class AppLogger:
    _initialized = False
    _logger_name = "fastapi_app"

    @classmethod
    def setup(
            cls,
            level: int = logging.INFO,
            log_dir: str | None = None,
            log_filename: str = "app.log"
    ):
        if cls._initialized:
            return

        if log_dir is None:
            project_root = Path(__file__).resolve().parent.parent
            log_path = project_root / "logs"
        else:
            log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(cls._logger_name)
        logger.setLevel(level)
        logger.propagate = False

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = TimedRotatingFileHandler(
            filename=str(log_path / log_filename),
            when="midnight",
            interval=1,
            backupCount=14,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.suffix = "%Y-%m-%d"
        logger.addHandler(file_handler)

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str | None = None) -> logging.Logger:
        cls.setup()
        if not name:
            return logging.getLogger(cls._logger_name)
        return logging.getLogger(f"{cls._logger_name}.{name}")
