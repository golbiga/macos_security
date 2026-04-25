# mscp/common_utils/run_command.py

# Standard python modules
import shlex
import subprocess
from collections.abc import Mapping

# Local python modules
from .logger_instance import logger


def run_command(
    command: str,
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
    env: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """
    Executes a shell command and returns its output or an error message.
        result = subprocess.run(args, capture_output=True, text=True, check=True)
    Parameters:
        command (str): The command to be executed.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the command output if successful, or an error message if the command fails.
    """
    args = shlex.split(command)
    try:
        logger.info("Executing command: {}", command)

        result = subprocess.run(
            args, capture_output=capture_output, text=text, check=check, env=env
        )

        logger.success("Command executed successfully: {}", command)
        if text:
            logger.debug("Command output: {}", result.stdout.strip())

            return result.stdout.strip(), None
        else:
            return None, None

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or str(e)
        logger.error(
            "Command '{}' failed with return code {}: {}",
            command,
            e.returncode,
            error_output,
        )

        return None, f"Command failed: {error_output}"

    except OSError as e:
        logger.error("OS error when running command: {}", command)
        logger.error("OS error when running command: {}, Error: {}", command, str(e))

        return None, f"OS error occurred: {str(e)}"
