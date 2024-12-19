import streamlit as st
import spcs_helpers

if "session" not in st.session_state:
    st.session_state.session = spcs_helpers.session()

session = st.session_state.session

if "db_name" not in st.session_state:
    st.session_state.db_name = eval(session.get_current_database())

st.title("🚀 Running Services")

st.markdown(
    "This page lists all running services created by SPCS easy run mode app. You can drop a service by selecting it from the list."
)

query_sql = f"show services in {st.session_state.db_name}.service_schema"
services = session.sql(query_sql).collect()


def drop_service(service_names):
    # drop the service
    for service_name in service_names:
        with st.spinner(f"Dropping service `{service_name}`..."):
            try:
                result = session.sql(
                    f"drop service {st.session_state.db_name}.service_schema.{service_name}"
                ).collect()
                st.toast(
                    f"Service `{service_name}` dropped successfully",
                    icon=":material/check:",
                )
            except Exception as e:
                st.error(f"Error: {e}", icon=":material/close:")


def show_logs(service_name):
    # show logs for the service
    with st.spinner(f"Fetching logs for service `{service_name}`..."):
        try:
            # logs = session.call("system$get_service_logs", "service_schema."+service_name, 0, "main", 100)
            logs = session.sql(
                f"call system$get_service_logs('{st.session_state.db_name}.service_schema.{service_name}', 0, 'main')"
            ).collect()[0][0]
            st.code(logs, language="txt")
        except Exception as e:
            st.error(f"Error: {e}", icon=":material/close:")


@st.dialog("Service logs", width="large")
def show_logs_dialog(service_names):
    for service_name in service_names:
        with st.expander(f"Logs for service `{service_name}`"):
            show_logs(service_name)


cols = st.columns([2, 2, 2])
with cols[0]:
    if st.button("", icon=":material/refresh:"):
        services = session.sql(query_sql).collect()
with cols[1]:
    if st.button("", icon=":material/visibility:"):
        selected_services = st.session_state.services_event.selection.rows
        service_names = [services[i]["name"] for i in selected_services]
        show_logs_dialog(service_names)
with cols[2]:
    if st.button("", icon=":material/delete:"):
        selected_services = st.session_state.services_event.selection.rows
        service_names = [services[i]["name"] for i in selected_services]
        drop_service(service_names)
        st.rerun()

st.session_state.services_event = st.dataframe(
    services,
    selection_mode="multi-row",
    on_select="rerun",
    use_container_width=True,
)
