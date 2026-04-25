# mscp/common_utils/logging_config.py

# Standard python modules
from __future__ import annotations

import os
import sys
from pathlib import Path

import loguru

# Local python modules
from .logger_instance import logger
from .paths import source_project_root, user_config_root

verbose_logging: bool = False


def function_filter(record):
    """
    This function checks if the current module should be included in the logs
    based on the MSCP_DEV_FILTER environment variable.
    Example: export MSCP_DEV_FILTER=guidance_support
    """
    filter = os.environ.get("MSCP_DEV_FILTER", "")
    return filter in record["module"].lower()


def set_logger(debug: bool = False, verbosity: int = 0) -> loguru.Logger:
    global verbose_logging
    verbose_logging = verbosity > 0 or debug
    log_level: str = "ERROR"

    if verbosity == 1:
        log_level = "INFO"
    elif verbosity > 1 or debug:
        log_level = "DEBUG"

    # formatter = LoguruFormatter()
    logger.enable("mscp")
    logger.enable("src.mscp")
    logger.remove()
    log_dir = (source_project_root() or user_config_root()) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "level": log_level,
                "filter": function_filter,
            },
            {
                "sink": Path(log_dir, "mscp.log"),
                "level": "DEBUG",
                "encoding": "utf-8",
                "enqueue": True,
                "serialize": True,
                "rotation": "1 hour",
                "retention": 5,
            },
        ]
    )

    return logger
