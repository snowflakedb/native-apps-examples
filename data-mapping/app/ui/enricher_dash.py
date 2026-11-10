def update_table(session, input_column, result_column):
    """Pass consumer column names as values to the enrichment procedure."""
    return session.sql(
        "CALL ENRICHIP.enrich_ip_data(?, ?)",
        params=[input_column, result_column],
    ).collect()


def render(session):
    import streamlit as st

    columns = session.sql(
        "SELECT * FROM REFERENCE('tabletouse') WHERE 1=0"
    ).to_pandas().columns.values.tolist()
    if not columns:
        st.info("Choose a table with columns to enrich.")
        return

    with st.form("mapping_form"):
        st.subheader("Define Mappings")
        input_column = st.selectbox("IP ADDRESS COLUMN", options=columns)
        result_column = st.selectbox("RESULT COLUMN", options=columns)
        st.form_submit_button("Update Mappings")

    st.json({"IP ADDRESS COLUMN": input_column, "RESULT COLUMN": result_column})
    st.button(
        "UPDATE!",
        on_click=update_table,
        args=(session, input_column, result_column),
    )


if __name__ == "__main__":
    from snowflake.snowpark.context import get_active_session

    render(get_active_session())
