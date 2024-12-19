import streamlit as st
import spcs_helpers
import time
from utils import basic_setup, create_compute_pool
from snowflake.snowpark.functions import col

st.title("💻 Compute Pool Setup")

st.markdown(
    "In this step, You need to select a **compute pool** to run your service. You can either select an existing compute pool or create a new one."
)

if "session" not in st.session_state:
    st.session_state.session = spcs_helpers.session()

session = st.session_state.session


@st.dialog("Create a new compute pool")
def create_compute_pool_dialog():
    compute_pool_name = st.text_input(
        "Enter the compute pool name to create the service", value="TEST_COMPUTE5"
    )
    instance_family = st.selectbox(
        "Select the instance family",
        options=["CPU_X64_XS", "CPU_X64_S", "CPU_X64_M", "CPU_X64_L", "GPU_NV_S"],
    )
    min_nodes = st.number_input("Minimum number of nodes", value=1, min_value=1)
    max_nodes = st.number_input("Maximum number of nodes", value=1, min_value=1)
    sub_cols = st.columns([1, 2, 2, 1])
    with sub_cols[1]:
        if st.button("Create", icon=":material/check:"):
            if compute_pool_name and instance_family and min_nodes <= max_nodes:
                with st.spinner("Creating compute pool..."):
                    create_compute_pool(
                        session,
                        compute_pool_name,
                        instance_family,
                        min_nodes,
                        max_nodes,
                    )
                    st.toast(
                        f"Compute pool `{compute_pool_name}` created successfully",
                        icon=":material/check:",
                    )
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("Please fill in all fields with valid values")
    with sub_cols[2]:
        if st.button("Cancel", icon=":material/close:"):
            st.rerun()


cols = st.columns([4, 2, 1, 1])
with cols[0]:
    st.markdown("### Select a compute pool")
with cols[2]:
    refresh_button = st.button("", icon=":material/refresh:")
    if refresh_button:
        compute_pools = (
            session.sql("show compute pools")
            .filter(col('"name"') != "frontend_pool".upper())
            .collect()
        )
with cols[3]:
    add_button = st.button("", icon=":material/add:")
    if add_button:
        create_compute_pool_dialog()

compute_pools = (
    session.sql("show compute pools")
    .filter(col('"name"') != "frontend_pool".upper())
    .collect()
)


event = st.dataframe(
    compute_pools, hide_index=True, on_select="rerun", selection_mode="single-row"
)

if event.selection.rows:
    st.session_state.compute_pool_name = compute_pools[event.selection.rows[0]].name
    st.session_state.use_gpu = (
        compute_pools[event.selection.rows[0]].instance_family == "GPU_NV_S"
    )
    st.success(
        f"You have selected compute pool `{st.session_state.compute_pool_name}`",
        icon=":material/check:",
    )
    bottom_cols = st.columns([1, 1, 1, 1])
    with bottom_cols[-1]:
        if st.button(
            "Save and Next Step", icon=":material/arrow_forward:", type="primary"
        ):
            st.switch_page("pages/2-service_code.py")
else:
    st.error(
        "No compute pool selected, please select a compute pool",
        icon=":material/error:",
    )
