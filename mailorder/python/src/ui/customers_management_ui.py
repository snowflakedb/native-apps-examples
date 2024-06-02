def run_streamlit():
    import streamlit as st
    from snowflake.snowpark import Session

    session = Session.builder.getOrCreate()
    st.title("Manage Customers")

    with st.form("addCustomer", clear_on_submit=True):
        st.header("Add Customer")
        customer_id = st.text_input("Enter customer Id, will not be visible", key='customerId')
        customer_name = st.text_input("Enter customer Name, will be visible in dropdown", key='customerName')

        if st.form_submit_button("Add Customer"):
            session.sql(
                "insert into data.customers(id, name, created_at) values (?, ?, current_timestamp())",
                params=[customer_id, customer_name]
            ).collect()

        st.header("Customers")
        customers_df = session.table("data.customers")
        st.dataframe(customers_df.to_pandas(), use_container_width=True)



if __name__ == '__main__':
    run_streamlit()
