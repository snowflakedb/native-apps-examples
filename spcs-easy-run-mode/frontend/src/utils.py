import streamlit as st
import os
import json
import uuid
import spcs_helpers
import json
import traceback
from snowflake.snowpark.functions import col


def basic_setup():
    st.markdown(
        """
    <style>
    #MainMenu, header:not([data-testid="stNavSectionHeader"]), footer {visibility: hidden;}
    body {
        background-color: #f4f7fc; /* Snowflake's light background */
        color: #2e3c47; /* Snowflake's dark text color */
        font-family: Arial, sans-serif; /* Use Arial as the default font */
        font-size: 20px; /* Set the default font size to 16px */
    }
    .stSidebar {
        background-color: #ffffff; /* White sidebar */
    }
    .block-container {
        padding: 2rem 3rem; /* Add spacing to the layout */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2e3c47;
        font-family: Arial, sans-serif;
    }
    p, body {
        weight: 500;
        font-size: 16px;
    }
    code {
        background-color: #eaf6fc; /* Light blue background */
        color: #1b9de7; /* Snowflake blue for text */
        padding: 2px 6px; /* Add padding for better readability */
        border-radius: 4px; /* Rounded corners */
        font-size: 90%; /* Slightly smaller font size */
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    ## var initialization

    if "env_vars" not in st.session_state:
        st.session_state.env_vars = """{
    "SERVER_PORT": 8000
}"""
    if "service_name" not in st.session_state:
        st.session_state.service_name = ""

    if "endpoints" not in st.session_state:
        st.session_state.endpoints = ["ui"]

    if "endpoint_port" not in st.session_state:
        st.session_state.endpoint_port = 8000

    if "udfs" not in st.session_state:
        st.session_state.udfs = [
            {
                "name": "my_udf",
                "input": ["VARCHAR"],
                "output": "VARCHAR",
                "path": "echo",
            },
            {
                "name": "my_udf2",
                "input": ["VARCHAR", "NUMBER"],
                "output": "VARCHAR",
                "path": "echo2",
            },
        ]

    if "base_image" not in st.session_state:
        st.session_state.base_image = "python:3.10-slim-buster"


def put_to_stage(session, stage, filename, content):
    try:
        local_path = "/tmp"
        local_file = os.path.join(local_path, filename)
        f = open(local_file, "w")
        f.write(content)
        f.close()
        session.file.put(local_file, "@" + stage, auto_compress=False, overwrite=True)
        return "saved file " + filename + " in stage " + stage
    except Exception as e:
        st.write(f"Error: {e}")


def upload_variable_to_stage(session, stage, variable_name, variable_value):
    if not variable_value:
        return None
    put_to_stage(session, stage, variable_name, variable_value)


def create_compute_pool(
    session, compute_pool_name, instance_family, min_nodes=1, max_nodes=4
):
    create_compute_pool_query = f"""CREATE COMPUTE POOL IF NOT EXISTS {compute_pool_name}
    MIN_NODES = {min_nodes}
    MAX_NODES = {max_nodes}
    INSTANCE_FAMILY = {instance_family}
    """
    session.sql(create_compute_pool_query).collect()
    return f"Created the compute pool {compute_pool_name}"


def create_tmp_repo(session, repo_name):
    create_repo_query = f"CREATE OR REPLACE IMAGE REPOSITORY service_schema.{repo_name}"
    result = session.sql(create_repo_query).collect()
    return f"Created the repository {repo_name}"


def create_stage_and_upload_files(session, stage, service_code, requirements, ui_code):
    create_stage_query = (
        f"CREATE OR REPLACE STAGE {stage} ENCRYPTION = (type = 'SNOWFLAKE_SSE')"
    )
    result = session.sql(create_stage_query).collect()
    upload_variable_to_stage(session, stage, "service.py", service_code)
    upload_variable_to_stage(session, stage, "requirements.txt", requirements)
    upload_variable_to_stage(session, stage + "/templates", "ui.html", ui_code)
    return f"Created the stage {stage} and uploaded the files"


def create_stage_and_upload_all_files(session, stage, code_files):
    create_stage_query = (
        f"CREATE OR REPLACE STAGE {stage} ENCRYPTION = (type = 'SNOWFLAKE_SSE')"
    )
    result = session.sql(create_stage_query).collect()
    for code_file in code_files:
        parent_dir = os.path.dirname(code_file["name"])
        file_name = os.path.basename(code_file["name"])
        upload_variable_to_stage(
            session, stage + "/" + parent_dir, file_name, code_file["content"]
        )
    return f"Created the stage {stage} and uploaded the files"


def get_registry_url(session, db_name, schema_name, repo_name):
    registry_query = f"show image repositories in {db_name}.{schema_name}"
    result = session.sql(registry_query).collect()
    return (
        session.sql(f"show image repositories in {db_name}.service_schema")
        .filter(col('"name"') == repo_name.upper())
        .select(col('"repository_url"'))
        .first()[0]
    )


def convert_dev_to_local_url(dev_url):
    return (dev_url.split(".")[0] + ".registry-local.snowflakecomputing.com").lower()


def create_kaniko_job(
    session,
    kaniko_job_name,
    stage,
    database_name,
    repo_name,
    base_image,
    service_image_name,
    compute_pool_name,
    db_name,
):
    registry_url = get_registry_url(session, database_name, "service_schema", repo_name)
    registry_local_url = f"{convert_dev_to_local_url(registry_url)}/{database_name}/service_schema/{repo_name}"
    registry_local_url = f'"{registry_local_url.lower()}"'
    base_image = f'"{base_image.lower()}"'
    service_image_name = f'"{service_image_name.lower()}"'
    stage = f'"@{stage}"'
    result = session.call(
        db_name + ".public.create_kaniko_job",
        compute_pool_name,
        kaniko_job_name,
        registry_local_url,
        base_image,
        service_image_name,
        stage,
    )
    return result


def clean_up(
    session,
    stage,
    repo_name,
    kaniko_job_name,
    service_name,
    db_name,
    udf_name,
    input_type,
):
    my_progress = st.progress(0, "Starting cleanup")
    kaniko_drop_query = f"DROP SERVICE IF EXISTS {db_name}.public.{kaniko_job_name}"
    service_drop_query = (
        f"DROP SERVICE IF EXISTS {db_name}.service_schema.{service_name}"
    )
    stage_drop_query = f"DROP STAGE  IF EXISTS {stage}"
    repo_drop_query = (
        f"DROP IMAGE REPOSITORY IF EXISTS {db_name}.service_schema.{repo_name}"
    )
    udf_drop_query = (
        f"DROP FUNCTION IF EXISTS {db_name}.udf_schema.{udf_name}({input_type})"
    )
    session.sql(kaniko_drop_query).collect()
    my_progress.progress(25, "Dropped the kaniko job")
    session.sql(service_drop_query).collect()
    my_progress.progress(50, "Dropped the service")
    session.sql(stage_drop_query).collect()
    my_progress.progress(75, "Dropped the stage")
    session.sql(repo_drop_query).collect()
    my_progress.progress(90, "Dropped the repo")
    session.sql(udf_drop_query).collect()
    my_progress.progress(100, "Dropped the UDF")

    st.write("🚿 Finished cleanup")


def start_service(
    session,
    service_name,
    db_name,
    repo_name,
    service_image_name,
    compute_pool_name,
    env_vars={"SERVICE_PORT": 8000},
    port=8000,
):
    image_path = f"/{db_name}/service_schema/{repo_name}/{service_image_name}"
    env_vars = "\n                  ".join(
        [f"{key}: {value}" for key, value in env_vars.items()]
    )
    start_service_query = f"""CREATE SERVICE service_schema.{service_name}
        IN COMPUTE POOL {compute_pool_name}
        external_access_integrations = (reference('external_access_reference'))
        FROM SPECIFICATION $$
            spec:
              containers:
              - name: main
                image: "{image_path.lower()}"
                env:
                  {env_vars}
              endpoints:
              - name: mainendpoint
                port: {port}
                public: true
       MIN_INSTANCES=1
       MAX_INSTANCES=1
    $$;
    """
    session.sql(start_service_query).collect()
    # grant usage
    session.sql(
        f"grant usage on service service_schema.{service_name} to application role app_public"
    ).collect()
    session.sql(
        f"grant service role service_schema.{service_name}!all_endpoints_usage to application role app_public"
    ).collect()
    return f"Started the service {service_name}"


def bound_udf(session, udf_name, input_types, return_type, service_name, db_name, path):
    create_udf_query = f"""CREATE OR REPLACE FUNCTION {db_name}.udf_schema.{udf_name}({', '.join([f"INPUTTEXT{i} {input_type}" for i, input_type in enumerate(input_types)])})
    RETURNS {return_type}
    SERVICE= {db_name}.service_schema.{service_name}
    ENDPOINT= mainendpoint
    AS '/{path}';
    """
    result = session.sql(create_udf_query).collect()
    session.sql(
        f"grant usage on function {db_name}.udf_schema.{udf_name}({', '.join(input_types)}) to application role app_public"
    ).collect()
    return result


def ingress_url(session, service_name, db_name, path):
    domain = (
        session.sql(
            f"show endpoints in service {db_name}.service_schema.{service_name}"
        )
        .select(col('"ingress_url"'))
        .collect()[0][0]
    )
    return f"https://{domain}/{path}"


def run_easy_run_mode():
    repo_name = "repo_" + str(uuid.uuid4()).replace("-", "_")
    stage = "public.stage_" + str(uuid.uuid4()).replace("-", "_")
    kaniko_job_name = "kaniko_job_" + str(uuid.uuid4()).replace("-", "_")
    service_image_name = "service_image_" + str(uuid.uuid4()).replace("-", "_")

    if "session" not in st.session_state:
        st.session_state.session = spcs_helpers.session()
    session = st.session_state.session

    with st.spinner("Creating the Service"):
        try:
            my_bar = st.progress(
                10, text=":material/database_upload: Creating the image repo"
            )
            create_tmp_repo(session, repo_name)

            my_bar.progress(
                20,
                text=":material/upload_file: Creating the temp stage and uploading all code files",
            )
            create_stage_and_upload_all_files(
                session, stage, st.session_state.code_files
            )

            my_bar.progress(40, text=":material/build: Build the service image")
            create_kaniko_job(
                session,
                kaniko_job_name,
                stage,
                st.session_state.db_name,
                repo_name,
                st.session_state.base_image,
                service_image_name,
                st.session_state.compute_pool_name,
                st.session_state.db_name,
            )

            my_bar.progress(80, text=":material/launch: Launch the service")
            env_vars = json.loads(st.session_state.env_vars)
            start_service(
                session,
                st.session_state.service_name,
                st.session_state.db_name,
                repo_name,
                service_image_name,
                st.session_state.compute_pool_name,
                env_vars=env_vars,
                port=st.session_state.endpoint_port,
            )

            my_bar.progress(90, text=":material/commit: Create the UDF")
            for udf in st.session_state.udfs:
                bound_udf(
                    session,
                    udf["name"],
                    udf["input"],
                    udf["output"],
                    st.session_state.service_name,
                    st.session_state.db_name,
                    udf["path"],
                )

            my_bar.progress(
                100, text=":material/check: Service is created successfully"
            )
            for endpoint in st.session_state.endpoints:
                url = ingress_url(
                    session,
                    st.session_state.service_name,
                    st.session_state.db_name,
                    endpoint,
                )
                st.markdown(f"🌐 Service is started at: [{url}]({url})")
        except Exception as e:
            st.error(f"Error: {e}", icon=":material/close:")
            traceback.print_exc()
