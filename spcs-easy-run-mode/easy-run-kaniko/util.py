import logging
import os
import shutil
import signal
import string
import subprocess
import traceback

logger = logging.getLogger(__name__)


def substitute_template_values(template_path, output_path, context):
    """
    Reads a template file, substitutes template values, and writes to a new file.

    Args:
        template_path: Path to the template file.
        output_path: Path where the output file should be written.
        context: Dictionary with template variable names and their substitution values.
    """
    # Read the template file
    with open(template_path, encoding="utf-8") as file:
        template_content = file.read()

    # Create a Template object and substitute values
    template = string.Template(template_content)
    substituted_content = template.substitute(context)

    # Write the substituted content to the output file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(substituted_content)


def execute_and_stream_output(command, cwd=None):
    """
    Executes a command and streams its output (stdout and stderr).

    Args:
        command: Command to execute as a list of strings.

    Returns:
        Exit code.
    """
    # Start the subprocess
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd
    )

    def cleanup():
        logger.info("Stopping file monitoring job...")
        process.terminate()

    signal.signal(signal.SIGTERM, cleanup)

    # Stream the output
    while True:
        # Read one line at a time
        output = process.stdout.readline()

        # If the output is empty and the process has terminated, break the loop
        if output == "" and process.poll() is not None:
            break

        # Log the output line
        if output:
            logger.info(output.strip())

    # Wait for the process to finish and get the exit code
    rc = process.poll()
    return rc


def remove_path(path):
    try:
        if os.path.islink(path):
            # Remove symbolic link
            os.unlink(path)
            logger.debug(f"Symbolic link '{path}' removed successfully")
        elif os.path.isfile(path):
            # Remove file
            os.remove(path)
            logger.debug(f"File '{path}' removed successfully")
        elif os.path.isdir(path):
            # Remove directory and all its contents
            shutil.rmtree(path)
            logger.debug(
                f"Directory '{path}' and all its contents removed successfully"
            )
        else:
            logger.debug(
                f"Path '{path}' does not exist or is not a file, directory, or symbolic link"
            )
    except OSError as e:
        logger.error(f"Error: {e.strerror}")
        logger.error(traceback.format_exc())
