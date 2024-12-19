import streamlit as st
from streamlit_monaco_code_editor import monaco_code_editor

languages = {
    "py": "python",
    "sql": "sql",
    "html": "html",
    "css": "css",
}

st.title("📦 Service Container Setup")

suggested_base_images = [
    "python:3.10-slim-buster",
    "python:3.9-slim-buster",
    "python:3.8-slim-buster",
]

st.markdown(
    "In this step, you are required to upload **all the necessary files** and code to create the service container. You can also select the base image for the service container."
)

# st.markdown("---")

st.markdown(
    "### Select the base image",
    help="If you select to upload a Dockerfile, you can just ignore this step.",
)

st.markdown(
    "You can write the `image_name:tag` of the base image if it is already available on the Docker Hub, and the full imahe path like `gcr.io/my-project/my-image:latest` if it is available on Google Container Registry."
)

cols = st.columns([4] + [3] * len(suggested_base_images))

if "_base_image" not in st.session_state:
    st.session_state._base_image = st.session_state.get("base_image", "")

with cols[0]:
    st.write("Try one of the suggested base images:")
for i, image in enumerate(suggested_base_images):
    with cols[i + 1]:
        if st.button(image, on_click=st.rerun):
            st.session_state._base_image = image
            st.rerun()

st.text_input("Or enter the image name manually", key="_base_image")

if st.session_state.get("_base_image"):
    st.session_state.base_image = st.session_state.get("_base_image")

st.write(f"Selected base image: `{st.session_state.base_image}`")

if "code_files" not in st.session_state:
    st.session_state.code_files = []


def use_llm_example():
    st.session_state.code_files = [
        {"name": "service.py", "content": open("llm-example/service.py").read()},
        {
            "name": "requirements.txt",
            "content": open("llm-example/requirements.txt").read(),
        },
        {
            "name": "templates/index.html",
            "content": open("llm-example/templates/index.html").read(),
        },
        {
            "name": "static/styles.css",
            "content": open("llm-example/static/styles.css").read(),
        },
    ]
    st.session_state.env_vars = open("llm-example/env_vars.json").read()
    st.rerun()


def use_echo_example():
    st.session_state.code_files = [
        {"name": "service.py", "content": open("echo-example/service.py").read()},
        {
            "name": "requirements.txt",
            "content": open("echo-example/requirements.txt").read(),
        },
        {
            "name": "templates/ui.html",
            "content": open("echo-example/templates/ui.html").read(),
        },
    ]
    st.rerun()


@st.dialog("Upload a new file", width="large")
def upload_new_file():
    name = st.text_input(":material/folder_open: File Path")
    path_parts = name.split(".")
    if len(path_parts) > 1:
        ext = languages.get(path_parts[-1], "txt")
    else:
        ext = "txt"
    st.write(":material/code: Code")
    content = monaco_code_editor(
        key="code_editor_" + name,
        value="",
        language=ext,
    )
    if st.button("Upload", icon=":material/cloud_upload:", type="primary"):
        if not name:
            st.error("Please provide the file path")
            return
        st.session_state.code_files.append({"name": name, "content": content})
        st.rerun()


st.markdown("### Code Files")

st.markdown(
    "Upload the code and other necessary to build your service container. If you don't upload a `Dockerfile`, the service will be built using the base image you selected, install the python modules from the upload `requirements.txt` file, and run the `service.py` file."
)

st.markdown(
    "You can choose either to upload the files by hand or use a GitHub repository for the service code."
)

st.markdown(
    'If you click *"Use Echo Example"*, it will use [this example](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/tutorials/tutorial-1#download-the-service-code) in the :material/description: Snowflake documentation as a starting point.'
)

upload_tab, github_tab, env_tab = st.tabs(
    [
        ":material/upload_file: Upload",
        ":material/code: GitHub",
        ":material/data_object: Environment Variables (Optional)",
    ]
)

with upload_tab:
    subcols = st.columns([2, 2, 2, 2])
    with subcols[0]:
        if st.button("Use Echo Example", icon=":material/file_open:", type="primary"):
            use_echo_example()

    with subcols[1]:
        if st.button("Use LLM Example", icon=":material/file_copy:", type="primary"):
            use_llm_example()
    with subcols[2]:
        if st.button(
            "Create a New File", icon=":material/cloud_upload:", type="primary"
        ):
            upload_new_file()
    with subcols[-1]:
        if st.button("Clear", icon=":material/delete:", type="primary"):
            st.session_state.code_files = []
            st.rerun()

    @st.dialog("Edit the code", width="large")
    def edit_code_file(code_file):

        name = st.text_input(
            ":material/folder_open: File Path", value=code_file["name"]
        )
        path_parts = name.split(".")
        if len(path_parts) > 1:
            ext = languages.get(path_parts[-1], "txt")
        else:
            ext = "txt"
        st.write(":material/code: Code")
        content = monaco_code_editor(
            key="code_editor_" + name,
            value=code_file["content"],
            language=ext,
        )
        if st.button("Save", icon=":material/save:", type="primary"):
            code_file["name"] = name
            code_file["content"] = content
            st.rerun()

    for i, code_file in enumerate(st.session_state.code_files):
        cols = st.columns([4, 1, 1])
        with cols[0]:
            st.write(f":material/description: {code_file['name']}")
        with cols[1]:
            if st.button("", icon=":material/edit:", key="edit_code_file_" + str(i)):
                edit_code_file(code_file)
        with cols[2]:
            if st.button(
                "", icon=":material/delete:", key="delete_code_file_" + str(i)
            ):
                st.session_state.code_files.pop(i)
                st.rerun()
    tab_cols = st.columns([6, 1])
    with tab_cols[1]:
        if st.button(
            "Next", icon=":material/arrow_forward:", type="primary", key="next"
        ):
            st.session_state.use_github = False
            st.switch_page("pages/3-web_endpoint_and_udf.py")

with github_tab:
    git_repo = st.text_input(
        "Enter the GitHub repository URL :material/add_link:",
        help="Use a public GitHub repository URL with the `Dockerfile`",
    )
    if git_repo:
        tab_cols = st.columns([6, 1])
        with tab_cols[1]:
            if st.button(
                "Next",
                icon=":material/arrow_forward:",
                type="primary",
                key="github_next",
            ):
                st.session_state.git_repo = git_repo
                st.session_state.use_github = True
                st.switch_page("pages/3-web_endpoint_and_udf.py")

with env_tab:
    st.write("Environment Variables (write in the format of JSON)")

    env_vars = monaco_code_editor(language="json", value=st.session_state.env_vars)
    rab_cols = st.columns([1, 6, 1])
    with rab_cols[0]:
        if st.button("Save", icon=":material/save:", type="primary", key="save_env"):
            st.session_state.env_vars = env_vars
            st.rerun()
    with rab_cols[2]:
        if st.button("Next", icon=":material/arrow_forward:", type="primary"):
            st.session_state.env_vars = env_vars
            st.switch_page("pages/3-web_endpoint_and_udf.py")
