import base64
import logging
import os
import pathlib
import sys
import time
import traceback
import util

# Paths
REGISTRY_CRED_PATH = "/kaniko/.docker/config.json"
SESSION_TOKEN_PATH = "/snowflake/session/token"
WORKDIR = "/app"
LIBPATH = WORKDIR + "/libs/"
TEMPLATE_PATH = "/app/docker_template"
SOURCEDIR = "/app/src" # fix it as /app/src currently, must mount @stage content to /app/src

IMAGE_REGISTRY_URL = os.getenv("IMAGE_REGISTRY_URL")
SKIP_SSL = os.getenv("SKIP_SSL")
BASE_IMG = os.getenv("BASE_IMG")
FINAL_IMAGE = os.getenv("FINAL_IMAGE")
# entrypoint command to launch the service
LAUNCH_CMD = os.getenv("LAUNCH_CMD", '["python3", "service.py"]')
# the location of the build context, please set it to the directory of the target dockerfile
BUILDDIR = os.getenv("BUILD_DIR", WORKDIR)
# default timeout to fetch the token file
TOKEN_FILE_TIMEOUT = os.getenv("TOKEN_FILE_TIMEOUT", '60')

if not os.path.exists(BUILDDIR):
    os.makedirs(BUILDDIR)

if os.path.exists(os.path.join(SOURCEDIR, "Dockerfile")):
    BUILDDIR = SOURCEDIR
# Env vars from params
SPCS_MODEL_DEPLOYMENT_IMAGE_SHA_FROM_LOGS_SEARCH_STRING = os.getenv(
    "SPCS_MODEL_DEPLOYMENT_IMAGE_SHA_FROM_LOGS_SEARCH_STRING", "SF_KANIKO_RESULT="
)
# Env vars from params
SPCS_MODEL_DEPLOYMENT_IMAGE_SHA_VALUE_FROM_LOGS_JSON_KEY = os.getenv(
    "SPCS_MODEL_DEPLOYMENT_IMAGE_SHA_VALUE_FROM_LOGS_JSON_KEY", "output_image_sha"
)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def wait_till_token_file_exists(timeout):
    start_time = time.time()

    while not os.path.exists(SESSION_TOKEN_PATH):
        if time.time() - start_time > timeout:
            logger.error(
                f"Token file '{SESSION_TOKEN_PATH}' does not show up within the {timeout} seconds timeout "
                "period."
            )
            exit(1)
        logger.info(
            f"Waiting for token file to exist. Wait time remaining: {int(timeout - (time.time() - start_time))} "
            "seconds."
        )
        time.sleep(1)


def generate_registry_cred():
    # save the auth token of the destination registry
    wait_till_token_file_exists(int(TOKEN_FILE_TIMEOUT))
    with open(SESSION_TOKEN_PATH) as file:
        token = file.read().strip()
    auth_token = base64.b64encode(f"0auth2accesstoken:{token}".encode()).decode("utf-8")
    url = IMAGE_REGISTRY_URL.split("/")[0]
    registry_cred = '{"auths":{"' + url + '":{"auth":"' + auth_token + '"}}}'
    logger.info(registry_cred)
    with open(REGISTRY_CRED_PATH, "w") as file:
        file.write(registry_cred)

def generate_dockerfile():
    # Generate the Dockerfile based on the user input passed
    context = {
        "BASE_IMG": BASE_IMG,
        "LAUNCH_CMD": LAUNCH_CMD,
    }
    dest_path = os.path.join(BUILDDIR, "Dockerfile")

    if os.path.exists(dest_path):
        # Add this mode for future usage, allowing user to upload their own Dockerfile
        logger.info(f"Dockerfile exists, skipping generation")
    else:
        # Normal mode: only generate the Dockerfile from a fixed template
        logger.info(f"Generating the Dockerfile from a template")
        util.substitute_template_values(TEMPLATE_PATH, dest_path, context)
    
    with open(dest_path, encoding="utf-8") as file:
        logger.info(f"Dockerfile content: {file.read()}")

def run_kaniko():
    logger.info(f"Context path: {BUILDDIR}")
    path = pathlib.Path(BUILDDIR)
    # List all files in the directory and subdir
    files = [file for file in path.rglob("*") if file.is_file()]
    logger.info(f"Files in directory and subdirectory: {files}")

    logger.info("Starting Kaniko command...")
    image_url = IMAGE_REGISTRY_URL
    kaniko_command = [
        "/kaniko/executor",
        "--dockerfile",
        "Dockerfile",
        "--context",
        f"dir://{BUILDDIR}",
        f"--destination={image_url}/{FINAL_IMAGE}",
        "--image-fs-extract-retry=5",
        "--compression=zstd",
        "--compression-level=1",
        "--log-timestamp",
        "--verbosity=error",
        f"--digest-file={WORKDIR}/digest",
    ]

    if SKIP_SSL:
        kaniko_command.extend(
            [
                "--insecure",
                "--skip-tls-verify",
            ]
        )
    logger.info(" ".join(kaniko_command))
    # Call the function with your command
    exit_code = util.execute_and_stream_output(kaniko_command, cwd=BUILDDIR)
    logger.info(f"Command exited with code {exit_code}")
    if exit_code != 0:
        raise Exception(f"Kaniko build failed with exit code {exit_code}")


if __name__ == "__main__":
    try:
        # Run token monitoring in a background thread or process if you need it to run concurrently with Kaniko
        # Consider using threading or multiprocessing module for parallel execution

        # Adding this logic here as chainguard docker image
        # removed the rm command and we need to remove the symlink for kaniko to work

        # check the mount stage path BUILDDIR
        
        if os.path.exists(TEMPLATE_PATH):
            logger.info(f"Template file exists: {TEMPLATE_PATH}")
            with open(TEMPLATE_PATH, encoding="utf-8") as file:
                logger.info(f"Template file content: {file.read()}")
        
        # simplfy the environment
        util.remove_path("/usr/lib/terminfo")

        # get the registry credentials
        generate_registry_cred()

        # generate the dockerfile
        generate_dockerfile()

        # use kaniko to build the image and push
        logger.info("Running Kaniko")
        run_kaniko()
        logger.info("SF Output from Kaniko digest")
        if os.path.isfile(f"{WORKDIR}/digest"):
            with open(f"{WORKDIR}/digest") as file:
                digest_value = file.read()
                output_dict = {
                    SPCS_MODEL_DEPLOYMENT_IMAGE_SHA_VALUE_FROM_LOGS_JSON_KEY: digest_value
                }
                logger.info(
                    f"{SPCS_MODEL_DEPLOYMENT_IMAGE_SHA_FROM_LOGS_SEARCH_STRING}{output_dict}"
                )
    except Exception as e:
        logger.error(f"Error running Kaniko: {e}")
        # Print the traceback
        logger.error(traceback.format_exc())
        exit(1)
