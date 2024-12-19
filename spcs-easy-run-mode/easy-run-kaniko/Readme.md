Also available as `/snowflake/snowflake_images/images/easy-run-mode-kaniko-starter:0.0.1`

## Usage

Use this Kaniko starter image as a runtime starter of easy-run mode. Service built from the image accepts files including `service.py` and `templates/ui` as well as environment variables `IMAGE_REGISTRY_URL`, `BASE_IMG` and `FINAL_IMAGE` as inputs:

1. Put the `service.py` and `templates/ui` (optional) code on a stage

To put the text file into the stage, we can utilize function as follows:

```sql
CREATE OR REPLACE PROCEDURE PUT_TO_STAGE(STAGE VARCHAR,FILENAME VARCHAR, CONTENT VARCHAR)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION=3.8
PACKAGES=('snowflake-snowpark-python')
HANDLER='put_to_stage'
AS $$
import io
import os

def put_to_stage(session, stage, filename, content):
    local_path = '/tmp'
    dir_path = os.path.dirname(filename)
    stage_path = os.path.join('@'+stage, dir_path)
    dir_path = os.path.join(local_path, dir_path)
    os.makedirs(dir_path, exist_ok=True)
    local_file = os.path.join(local_path, filename)
    f = open(local_file, "w")
    f.write(content)
    f.close()
    session.file.put(local_file, stage_path, auto_compress=False, overwrite=True)
    return "saved file "+filename+" in stage "+stage
$$;

-- usage example: upload the tutorial_1/dockerfile
call PUT_TO_STAGE('my_internal_stage', 'tutorial_1/Dockerfile',
$$
ARG BASE_IMAGE=python:3.10-slim-buster
FROM $BASE_IMAGE
COPY echo_service.py ./
COPY templates/ ./templates/
RUN pip install --upgrade pip && \
    pip install flask
CMD ["python3", "echo_service.py"]
$$
);
```

2. Create a service like: (make sure you have access to the destination registry)

```sql
execute job service
  in compute pool DUMMY_COMPUTE_POOL
  name=kaniko_starter
  from specification $$
  spec:
    containers:
    - name: main
      image: "/db_path/schema_path/repo_path/easy-run-kaniko:<tag>"
      env:
        BASE_IMG: "python:3.11-slim"
        IMAGE_REGISTRY_URL: "<dest_registry>/db_path/schema_path/repo_path/"
        FINAL_IMAGE: "result_image_name"
      volumeMounts:
        - name: test-volume
          mountPath: /kaniko/path/to/mount
    volumes:
      - name: test-volume
        source: "@my_internal_stage"
  $$;
```

**Note**:

If the build of the target image requires network traffic resource. For example, if using `pip install` to install packages from a mirror when building the final image, please also attach an external access integration like

```sql
CREATE OR REPLACE NETWORK RULE pypi_network_rule
MODE = EGRESS
TYPE = HOST_PORT
VALUE_LIST = ('pypi.org', 'pypi.python.org', 'pythonhosted.org',  'files.pythonhosted.org');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION pypi_access_integration
ALLOWED_NETWORK_RULES = (pypi_network_rule)
ENABLED = true;

execute job service
  in compute pool TUTORIAL_COMPUTE_POOL
  name=kaniko_starter
  EXTERNAL_ACCESS_INTEGRATIONS = (snowflake_egress_access_integration)
  ...
```
