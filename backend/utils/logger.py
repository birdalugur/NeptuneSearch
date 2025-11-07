"""
Projenin tüm logging işlemlerini merkezi olarak yönetir.
Farklı log seviyeleri ve formatları sağlar.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class LoggerSetup:
    """
    Uygulamanın farklı bölümleri için logger'lar oluşturur ve yapılandırır.
    """

    @staticmethod
    def setup_logger(
        name: str, level: int = logging.INFO, log_file: Optional[Path] = None
    ) -> logging.Logger:
        """
        Yapılandırılmış logger oluşturur.

        Args:
            name: Logger ismi (genellikle modül ismi)
            level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Log dosyası yolu (opsiyonel)

        Returns:
            Yapılandırılmış logger instance'ı
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if logger.handlers:
            return logger

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Logger instance'ı döndürür.

    Args:
        name: Logger ismi

    Returns:
        Logger instance
    """
    return LoggerSetup.setup_logger(name)
