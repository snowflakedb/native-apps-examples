import streamlit as st
import pandas as pd
import spcs_helpers
from streamlit_tags import st_tags
from annotated_text import annotated_text


param_types = [
    "ARRAY",
    "BOOLEAN",
    "DATE",
    "DOUBLE",
    "FLOAT",
    "NUMBER",
    "OBJECT",
    "VARCHAR",
]


st.title("🌐 Web Endpoint and UDF Setup")

st.markdown(
    "In this step, you are needed to specify the path in the container for web UI endpoint and User-defined functions (UDFs) to be created."
)


endpoint_tab, udf_tab = st.tabs(
    [
        ":material/captive_portal: Web UI Endpoint",
        ":material/function: User-defined Functions",
    ]
)

if "_endpoint_port" not in st.session_state:
    st.session_state._endpoint_port = st.session_state.get("endpoint_port", 8000)

with endpoint_tab:
    st.write("Set the endpoint port")
    st.number_input("Port", key="_endpoint_port", min_value=1, max_value=65535)

    if st.session_state.get("_endpoint_port"):
        st.session_state["endpoint_port"] = st.session_state.get("_endpoint_port")

    paths = st_tags(
        label="List all the UI paths that you want to access",
        text="Press enter to add a new path",
        value=st.session_state.endpoints,
    )

    cols = st.columns([1, 6, 1])
    with cols[0]:
        if st.button("", icon=":material/delete:"):
            st.session_state.endpoints = []
            st.rerun()
    with cols[2]:
        if st.button("", icon=":material/check:"):
            st.session_state.endpoints = paths
            st.rerun()


@st.dialog("Edit the UDF", width="large")
def edit_udf(udf):
    udf_name = st.text_input("UDF name", value=udf["name"])
    path = st.text_input("Path", value=udf["path"])
    return_type = st.selectbox(
        "Output type", options=param_types, index=param_types.index(udf["output"])
    )
    param_df = pd.DataFrame(
        [{"type": udf["input"][i]} for i in range(len(udf["input"]))]
    )
    type_col = st.column_config.SelectboxColumn(
        "Type", options=param_types, default="VARCHAR"
    )
    number_col = st.column_config.NumberColumn("arg #")

    st.write(
        "Input types:", help="To delete a row, select the row and press the delete key"
    )

    df = st.data_editor(
        param_df,
        key="param_df",
        use_container_width=True,
        num_rows="dynamic",
        column_config={"type": type_col, "_index": number_col},
        disabled=["_index"],
        hide_index=False,
    )

    if udf_name and path and return_type and st.button("Save", icon=":material/save:"):
        if udf_name != udf["name"] and (
            udf_name in set(u["name"] for u in st.session_state.udfs)
        ):
            st.error("UDF name already exists")
            return
        udf["name"] = udf_name
        udf["output"] = return_type
        udf["input"] = df["type"].tolist()
        udf["path"] = path
        st.rerun()


@st.dialog("Add a new UDF", width="large")
def add_udf():
    udf_name = st.text_input("UDF name", placeholder="Enter the UDF name")
    path = st.text_input("Path", placeholder="Enter the path")
    return_type = st.selectbox("Output type", options=param_types)
    param_df = pd.DataFrame(columns=["type"])
    type_col = st.column_config.SelectboxColumn(
        "Type", options=param_types, default="VARCHAR"
    )
    number_col = st.column_config.NumberColumn("arg #")

    st.write(
        "Input types:", help="To delete a row, select the row and press the delete key"
    )

    df = st.data_editor(
        param_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={"type": type_col, "_index": number_col},
        disabled=["_index"],
        hide_index=False,
    )

    if udf_name and path and return_type and st.button("Save", icon=":material/save:"):
        if udf_name in set([udf["name"] for udf in st.session_state.udfs]):
            st.error("UDF name already exists")
            return
        st.session_state.udfs.append(
            {
                "name": udf_name,
                "input": df["type"].tolist(),
                "output": return_type,
                "path": path,
            }
        )
        st.rerun()


with udf_tab:
    st.write(
        "Define your function's inputs and outputs here, don't forget to specify the bound path in the container."
    )

    tabcols = st.columns([9, 1, 1])
    with tabcols[1]:
        if st.button("Clear", icon=":material/delete:", type="primary"):
            st.session_state.udfs = []
            st.rerun()
    with tabcols[2]:
        if st.button("Add", icon=":material/add:", type="primary"):
            add_udf()
    for i, udf in enumerate(st.session_state.udfs):
        with st.container(border=True):
            cols = st.columns([3, 8, 5, 2, 2])
            with cols[0]:
                st.write(f"**UDF {i+1}**:")
            with cols[1]:
                st.write(udf["name"])
            with cols[2]:
                annotated_text((udf["path"], "path"))
            with cols[3]:
                if st.button("", key=f"edit_udf_{i}", icon=":material/edit:"):
                    edit_udf(udf)
            with cols[4]:
                if st.button("", key=f"delete_udf_{i}", icon=":material/delete:"):
                    st.session_state.udfs.pop(i)
                    st.rerun()
            text = [
                (f"arg_{i+1}: ", udf["input"][i]) for i in range(len(udf["input"]))
            ] + [" -> ", ("return", udf["output"])]

            annotated_text(text)


total_cols = st.columns([3, 4, 3])
with total_cols[1]:
    if st.button("Next", icon=":material/arrow_forward:", type="primary"):
        st.switch_page("pages/4-final_review.py")
