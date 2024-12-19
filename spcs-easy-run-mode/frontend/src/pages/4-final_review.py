import streamlit as st
import spcs_helpers
import pandas as pd
from utils import run_easy_run_mode

st.title("📝 Final Review")

btn = None


st.markdown(
    "In this step, you can review all the configurations you have made for the service and UDFs. If you are satisfied with the configurations, you can proceed to create the service."
)

if "service_name" not in st.session_state:
    st.session_state.service_name = ""
if "compute_pool_name" not in st.session_state:
    st.session_state.compute_pool_name = ""

with st.expander("Basic Information", expanded=True):
    if not st.session_state.service_name:
        st.error("Please start with the service name from the previous step.")
    else:
        st.write(f"**Service Name**: `{st.session_state.service_name}`")
        st.write(f"**Database**: `{st.session_state.db_name}`")
        st.write(f"**Schema**: `{st.session_state.schema_name}`")
        st.write(f"**Warehouse**: `{st.session_state.wh_name}`")
    st.page_link("pages/0-welcome.py", label="Back", icon=":material/arrow_back:")


with st.expander("Compute Pool", expanded=True):
    if not st.session_state.compute_pool_name:
        st.error("Please select a compute pool from the previous step.")
    else:
        st.write(f"**Compute Pool**: `{st.session_state.compute_pool_name}`")
    st.page_link("pages/1-compute_pool.py", label="Back", icon=":material/arrow_back:")


if "base_image" not in st.session_state:
    st.session_state.base_image = ""
if "code_files" not in st.session_state:
    st.session_state.code_files = []
if "use_github" not in st.session_state:
    st.session_state.use_github = False
if "git_repo" not in st.session_state:
    st.session_state.git_repo = ""
with st.expander("Service code", expanded=True):
    if st.session_state.use_github:
        st.write(
            f"Use GitHub: [{st.session_state.git_repo}](https://github.com/{st.session_state.git_repo})"
        )
    else:
        st.write(f"**Base Image**: `{st.session_state.base_image or 'undefined'}`")
        st.write(":material/folder_open: Files:")
        st.write(
            "\n\n".join(
                [
                    f"- :material/file_copy: {item['name']}"
                    for item in st.session_state.code_files
                ]
            )
        )

    st.write("Env Variables:")
    st.code(st.session_state.env_vars, language="json")

    st.page_link("pages/2-service_code.py", label="Back", icon=":material/arrow_back:")

with st.expander("Web Endpoint and UDF", expanded=True):
    st.write(f"**Endpoint Port**: `{st.session_state.endpoint_port}`")
    st.write(
        f"**UI Paths**: "
        + ", ".join(["`" + endpoint + "`" for endpoint in st.session_state.endpoints])
    )
    df = pd.DataFrame(st.session_state.udfs)
    st.write("**UDFs**:")
    st.dataframe(df, use_container_width=True)
    st.page_link(
        "pages/3-web_endpoint_and_udf.py", label="Back", icon=":material/arrow_back:"
    )

cols = st.columns([4, 2, 4])
with cols[1]:
    if st.session_state["service_name"] and st.session_state["compute_pool_name"]:
        btn = st.button(
            "Create Service", icon=":material/arrow_forward:", type="primary"
        )

if btn:
    run_easy_run_mode()
