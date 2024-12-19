import streamlit as st
import spcs_helpers
from datetime import datetime

# param_types = ["ARRAY", "BOOLEAN", "DATE", "DOUBLE", "FLOAT", "NUMBER", "OBJECT", "VARCHAR"]

if "session" not in st.session_state:
    st.session_state.session = spcs_helpers.session()

session = st.session_state.session

if "db_name" not in st.session_state:
    st.session_state.db_name = eval(session.get_current_database())


def parse_arguments(func_signature):
    func_signature = func_signature.strip().upper()
    words = func_signature.split("RETURN")
    return_type = words[-1].strip()
    arg_lists = words[0].split("(")[1].split(")")[0].split(",")
    return arg_lists, return_type


udfs = session.sql(
    f"show user functions in {st.session_state.db_name}.udf_schema"
).collect()

st.title("🔧 Functions")

st.markdown(
    "This page lists all user-defined functions (UDFs) created by SPCS easy run mode app. You can call a UDF by selecting it from the list."
)


cols = st.columns([2, 4, 2])


@st.dialog("Call UDF", width="large")
def call_udf(udf_name, sig):
    args, return_type = parse_arguments(sig)
    arg_values = []
    for arg in args:
        if arg == "NUMBER":
            arg_values.append(st.number_input(arg, value=0))
        else:
            arg_values.append(st.text_input(arg, value=""))
    if all([arg is not None for arg in arg_values]):
        if st.button("Call", icon=":material/check:"):
            with st.spinner(f"Calling UDF `{udf_name}`..."):
                try:
                    arg_values = [
                        f"'{arg}'" if isinstance(arg, str) else arg
                        for arg in arg_values
                    ]
                    result = session.sql(
                        f"select udf_schema.{udf_name}({','.join([str(arg) for arg in arg_values])})"
                    ).collect()
                    st.write(f"Result:")
                    st.write(result)
                except Exception as e:
                    st.error(f"Error: {e}", icon=":material/close:")


with cols[0]:
    if st.button("", icon=":material/refresh:"):
        st.rerun()
with cols[-1]:
    if st.button("", icon=":material/function:"):
        if st.session_state.udf_event.selection.rows:
            udf = udfs[st.session_state.udf_event.selection.rows[0]]
            name = udf["name"]
            sig = udf["arguments"]
            call_udf(name, sig)


st.session_state.udf_event = st.dataframe(
    udfs, use_container_width=True, selection_mode="single-row", on_select="rerun"
)
