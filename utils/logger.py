import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class AppLogger:
    _initialized = False
    _logger_name = "fastapi_app"

    @classmethod
    def setup(
            cls,
            level: int | str = logging.INFO,
            log_dir: str | None = None,
            log_filename: str = "app.log"
    ):
        # 初始化
        if cls._initialized:
            return

        # 日志目录
        if log_dir is None:
            project_root = Path(__file__).resolve().parent.parent
            log_path = project_root / "logs"
        else:
            log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # 统一日志级别类型，便于类型检查
        normalized_level: int
        if isinstance(level, str):
            parsed_level = logging.getLevelName(level.upper())
            normalized_level = parsed_level if isinstance(parsed_level, int) else logging.INFO
        else:
            normalized_level = level

        # 日志器
        logger = logging.getLogger(cls._logger_name)
        logger.setLevel(normalized_level)
        logger.propagate = False

        # 日志格式
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        # 控制台日志
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件日志
        file_handler = TimedRotatingFileHandler(
            filename=str(log_path / log_filename),
            when="midnight",
            interval=1,
            backupCount=14,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.suffix = "%Y-%m-%d"

        base_name = Path(log_filename).stem

        def _namer(default_name: str) -> str:
            # default_name 形如: app.log.2026-04-19
            file_path = Path(default_name)
            date_part = file_path.name.split(".")[-1]
            return str(file_path.with_name(f"{base_name}-{date_part}.log"))

        file_handler.namer = _namer
        logger.addHandler(file_handler)

        logger.info(
            "日志系统初始化完成: level=%s, log_dir=%s, log_file=%s",
            logging.getLevelName(normalized_level),
            str(log_path),
            log_filename
        )

        # 初始化完成
        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str | None = None) -> logging.Logger:
        cls.setup()
        if not name:
            return logging.getLogger(cls._logger_name)
        return logging.getLogger(f"{cls._logger_name}.{name}")
