# mscp/common_utils/config.py

# Standard python modules
import os
from pathlib import Path

# Local python modules
from .file_handling import open_file
from .logger_instance import logger
from .paths import resource_path, source_project_root, user_config_root

# Additional python modules

CONFIG_ROOT = resource_path("config")
CONFIG_PATH: Path = Path(
    os.environ.get("MSCP_CONFIG_FILE", CONFIG_ROOT / "config.yaml")
).expanduser()


def _resolve_path(path: str, base: Path) -> str:
    p = Path(path).expanduser()
    return str(p if p.is_absolute() else base / p)


def _custom_root() -> Path:
    if custom_dir := os.environ.get("MSCP_CUSTOM_DIR"):
        return Path(custom_dir).expanduser()
    if source_root := source_project_root():
        source_custom = source_root / "config" / "custom"
        if source_custom.exists():
            return source_custom
    return user_config_root() / "custom"


def _resolve_custom_path(path: str, custom_root: Path) -> str:
    p = Path(path).expanduser()
    if p.is_absolute():
        return str(p)
    try:
        return str(custom_root / p.relative_to("config/custom"))
    except ValueError:
        return str(custom_root / p)


def _prepare_custom_dirs(custom_config: dict[str, str]) -> None:
    for value in custom_config.values():
        path = Path(value)
        if not path.suffix:
            path.mkdir(parents=True, exist_ok=True)


def _output_dir() -> str:
    if output_dir := os.environ.get("MSCP_OUTPUT_DIR"):
        return str(Path(output_dir).expanduser())
    if source_root := source_project_root():
        return str(source_root / "build")
    return str(user_config_root() / "build")


def _resolve_config_paths(raw_config: dict) -> dict:
    base = resource_path()

    raw_config["output_dir"] = _output_dir()

    for key in ("logging_config", "includes_dir", "mscp_data", "shell_template_dir"):
        if key in raw_config:
            raw_config[key] = _resolve_path(raw_config[key], base)

    for key in ("defaults",):
        for nested_key, value in raw_config.get(key, {}).items():
            raw_config[key][nested_key] = _resolve_path(value, base)

    custom_root = _custom_root()
    for nested_key, value in raw_config.get("custom", {}).items():
        raw_config["custom"][nested_key] = _resolve_custom_path(value, custom_root)
    if "custom" in raw_config:
        raw_config["custom"]["root_dir"] = str(custom_root)
        _prepare_custom_dirs(raw_config["custom"])

    return raw_config

try:
    logger.info("Attempting to open config file: {}", CONFIG_PATH)
    config = _resolve_config_paths(open_file(CONFIG_PATH))
    logger.success("Config file loaded successfully")
except Exception as e:
    logger.error("An error occurred while loading the config file: {}", e)
    raise
