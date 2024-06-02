def run_streamlit():
    import streamlit as st
    import pandas as pd
    from snowflake.snowpark import Session
    from snowflake import permissions

    session = Session.builder.getOrCreate()

    if permissions.get_held_account_privileges(['CREATE DATABASE']):
        session.sql("CREATE DATABASE IF NOT EXISTS MAILORDER_DB").collect()
        session.sql("CREATE SCHEMA IF NOT EXISTS MAILORDER_DB.LOGS").collect()
        session.sql("CREATE TABLE IF NOT EXISTS MAILORDER_DB.LOGS.TAX_TRANSFERS (REGION_ID VARCHAR(100), AMOUNT_CENTS NUMBER, CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP())").collect()
    else:
        st.warning('No permissions to create logging database')
        st.button('Request permissions', on_click=lambda: permissions.request_account_privileges(["CREATE DATABASE"]))

    st.title("Tax Management")

    st.header("Record tax transfer")
    regions_df = session.table("data.regions").select("id", "name")
    region_id_to_name = {}
    for record in regions_df.collect():
        region_id_to_name[list(record)[0]] = list(record)[1]
    region_id_selected = st.selectbox("Region", region_id_to_name.keys(), format_func=lambda x: region_id_to_name[x], key='regionId')

    amount_cents = st.number_input("Tax Transfer (in cents)", value=0, step=1, key="taxAmount")

    def click_button():
        session.call("regions.record_tax_transfer", region_id_selected, amount_cents)
        if permissions.get_held_account_privileges(['CREATE DATABASE']):
            session.sql("INSERT INTO MAILORDER_DB.LOGS.TAX_TRANSFERS(REGION_ID, AMOUNT_CENTS) VALUES(?, ?)", params=[region_id_selected, amount_cents]).collect()

    st.button("Transfer Tax", on_click=click_button, key='recordTaxTransfer')

    st.header("Owing balances")
    tax_balances = session.call("regions.tax_balances")
    st.dataframe(pd.DataFrame(list(map(list, tax_balances.collect()))), use_container_width=True)

if __name__ == '__main__':
    run_streamlit()
