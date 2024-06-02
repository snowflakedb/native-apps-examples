
def run_streamlit():
    import streamlit as st
    from snowflake.snowpark import Session

    session = Session.builder.getOrCreate()

    st.header("Customers with outstanding money")
    outstanding_customers_df = session.table("ledger.outstanding_customers")
    st.dataframe(outstanding_customers_df.to_pandas(), use_container_width=True)

    st.header("Receipts with outstanding money")
    outstanding_receipts_df = session.table("ledger.outstanding_receipts")
    st.dataframe(outstanding_receipts_df.to_pandas(), use_container_width=True)

    st.header("Receipts Paid")
    receipts_paid_df = session.table("ledger.receipt_paid")
    st.dataframe(receipts_paid_df.to_pandas(), use_container_width=True)

    st.header("Receipts Total")
    receipts_total_df = session.table("ledger.receipt_total")
    st.dataframe(receipts_total_df.to_pandas(), use_container_width=True)

    st.header("Tax collected per receipt")
    tax_collected_df = session.table("ledger.tax_collected_per_receipt")
    st.dataframe(tax_collected_df.to_pandas(), use_container_width=True)

if __name__ == '__main__':
    run_streamlit()
