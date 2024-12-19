import streamlit as st
import spcs_helpers

st.session_state.session = spcs_helpers.session()

st.title("🎈 Welcome to the SPCS Easy Run Mode App")

st.markdown(
    "This is a simple app to create a **service** as well as a *UDF* with one click. All you need to do is to select some basic configurations and paste your service code. The service will be launched automatically!"
)


db_name = eval(st.session_state.session.get_current_database())
role = eval(st.session_state.session.get_current_role())
schema_name = eval(st.session_state.session.get_current_schema())
wh_name = eval(st.session_state.session.get_current_warehouse())

st.write("## Current Session Information")

st.write(f":material/database: Current database: `{db_name}`")
st.write(f":material/schema: Current schema: `{schema_name}`")
st.write(f":material/person: Current role: `{role}`")
st.write(f":material/warehouse: Current warehouse: `{wh_name}`")


st.session_state.db_name = db_name
st.session_state.schema_name = schema_name
st.session_state.wh_name = wh_name


st.write(
    "From here, this app can help you create the service step by step. You just need to follow the instructions and fill in the required information."
)
st.write("## Start with the service name")

st.write(
    f"This is the name of the service you want to create. It should be unique and descriptive. You will find your final service running in `{schema_name}.service_schema` after you complete all steps."
)

st.text_input("Enter the service name", key="_service_name")

if st.session_state.get("_service_name"):
    st.session_state["service_name"] = st.session_state.get("_service_name")
    # st.session_state.service_name = service_name
    cols = st.columns([2, 2, 2])
    with cols[-1]:
        if st.button("Start", icon=":material/arrow_forward:", type="primary"):
            st.switch_page("pages/1-compute_pool.py")
