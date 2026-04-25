# mscp/common_utils/paths.py

# Standard python modules
import os
import sys
from importlib import resources
from pathlib import Path


def source_project_root() -> Path | None:
    """Return the project root when running from a source checkout."""
    for parent in Path(__file__).resolve().parents:
        if (
            (parent / "pyproject.toml").is_file()
            and (parent / "config" / "config.yaml").is_file()
            and (parent / "src" / "mscp").is_dir()
        ):
            return parent
    return None


def package_root() -> Path:
    return Path(str(resources.files("mscp")))


def resource_base() -> Path:
    return source_project_root() or package_root()


def resource_path(*parts: str) -> Path:
    return resource_base().joinpath(*parts)


def user_config_root() -> Path:
    if config_dir := os.environ.get("MSCP_CONFIG_DIR"):
        return Path(config_dir).expanduser()

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "mscp"

    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "mscp"
