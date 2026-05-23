# mscp/common_utils/config.py
"""Project configuration loader.

At import time this module loads ``config.yaml`` shipped under the
package's ``data/`` directory and resolves every relative path inside
it. Bundled package paths (rules, baselines, templates, etc.) are
rebased onto the package's data directory; writable paths
(``output_dir``, ``custom_dir``) are rebased onto the source checkout
when available, or the user's mSCP config directory when globally
installed. The result is exposed as the module-level `config` dict,
which most other mSCP modules import directly.

`ensure_custom_dirs` creates the custom directory tree on disk
(typically called once at CLI startup), and `set_custom_dir` rebinds
every ``custom`` entry to a new base directory after `config` is
already loaded.
"""

# Standard python modules
import os
from importlib.resources import files
from pathlib import Path

# Local python modules
from .file_handling import open_file
from .logger_instance import logger
from .paths import data_path, source_project_root, user_config_root

# Locate the data directory bundled with the package.
# Falls back to __file__-relative path when running from the source tree
# without an editable install.
try:
    _pkg_data = Path(str(files("mscp").joinpath("data")))
    if not _pkg_data.is_dir():
        raise FileNotFoundError(_pkg_data)
except Exception:
    _pkg_data = Path(__file__).parent.parent / "data"

CONFIG_PATH: Path = Path(
    os.environ.get("MSCP_CONFIG_FILE", _pkg_data / "config.yaml")
).expanduser()


def _resolve_path(path: str, base: Path) -> str:
    p = Path(path).expanduser()
    return str(p if p.is_absolute() else base / p)


def _custom_root() -> Path:
    if custom_dir := os.environ.get("MSCP_CUSTOM_DIR"):
        return Path(custom_dir).expanduser()
    if source_root := source_project_root():
        source_custom = source_root / "custom"
        if source_custom.exists():
            return source_custom
    return user_config_root() / "custom"


def _output_dir() -> str:
    if output_dir := os.environ.get("MSCP_OUTPUT_DIR"):
        return str(Path(output_dir).expanduser())
    if source_root := source_project_root():
        return str(source_root / "build")
    return str(user_config_root() / "build")


def _resolve_config_paths(raw_config: dict) -> dict:
    base = data_path()

    raw_config["output_dir"] = _output_dir()

    for key in ("includes_dir", "mscp_data"):
        if key in raw_config:
            raw_config[key] = _resolve_path(raw_config[key], base)

    bundled_dir_keys = (
        "baseline_dir",
        "documents_templates_dir",
        "images_dir",
        "locales_dir",
        "rules_dir",
        "sections_dir",
        "shell_template_dir",
        "templates_dir",
        "themes_dir",
    )
    for key in bundled_dir_keys:
        if key in raw_config:
            raw_config[key] = _resolve_path(raw_config[key], base)

    custom_root = _custom_root()
    raw_config["custom_dir"] = str(custom_root)
    raw_config["custom"] = {
        "root_dir": str(custom_root),
        "misc_dir": str(custom_root / "misc"),
    }
    defaults_only = frozenset({"locales_dir", "shell_template_dir"})
    for key in set(bundled_dir_keys) - defaults_only:
        if key in raw_config:
            config_rel_path = Path(raw_config[key]).relative_to(base)
            raw_config["custom"][key] = str(custom_root / config_rel_path)

    return raw_config

try:
    logger.info("Attempting to open config file: {}", CONFIG_PATH)
    config = _resolve_config_paths(open_file(CONFIG_PATH))
    logger.success("Config file loaded successfully")
except Exception as e:
    logger.error("An error occurred while loading the config file: {}", e)
    raise

# Custom base: now guaranteed absolute.
_custom_base: Path = Path(config["custom_dir"])


def ensure_custom_dirs() -> None:
    """Create the custom directory tree on disk if it isn't already there.

    Iterates every value in ``config["custom"]`` (resolved at import
    time from `custom_dir`) and `mkdir(parents=True, exist_ok=True)`s
    it. Safe to call repeatedly; intended to run once on CLI startup.
    """
    for path in config["custom"].values():
        Path(path).mkdir(parents=True, exist_ok=True)


def set_custom_dir(path: Path) -> None:
    """Rebase every ``config["custom"][...]`` entry onto a new directory.

    Each existing custom path's relative offset from the previous
    `_custom_base` is preserved underneath ``path``. Also updates
    ``config["custom_dir"]`` and the module-level `_custom_base` so
    subsequent calls compose correctly.

    Args:
        path (Path): New absolute base directory for custom files.
    """
    global _custom_base
    path = path.expanduser().resolve()
    for key in config.get("custom", {}):
        rel = Path(config["custom"][key]).relative_to(_custom_base)
        config["custom"][key] = str(path / rel)
    _custom_base = path
    config["custom_dir"] = str(path)
