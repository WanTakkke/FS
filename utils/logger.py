# app/utils/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str = "my_fastapi_app", level: int = logging.INFO) -> logging.Logger:
    """
    配置并返回一个日志记录器。
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False # 防止日志消息传播到父级记录器

    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)

    # 控制台输出格式化器
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # 文件输出格式化器 (包含文件路径和行号)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s - %(lineno)d"
    )

    # 控制台输出处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件输出处理器 (使用轮转文件处理器，防止日志文件过大)
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10
    )
    file_handler.setLevel(logging.ERROR) # 文件中主要记录错误及以上级别的日志
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger