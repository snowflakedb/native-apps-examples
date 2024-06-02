def run_streamlit():
    import streamlit as st
    from snowflake.snowpark.functions import col, call_udf
    from snowflake import telemetry
    from snowflake.snowpark import Session

    session = Session.builder.getOrCreate()

    st.header("Manage a receipt")
    receipts_df = session.table("data.receipts").select("id")
    all_receipt_ids = [list(record)[0] for record in receipts_df.collect()]
    receipt_id = st.selectbox("Receipt Id", all_receipt_ids)

    st.subheader("Current Items in Receipt")
    items_df = session.table("data.items").filter(col("receipt_id") == receipt_id).with_column("total cost", call_udf("receipts.total_cost", col("amount_cents"), col("quantity")))
    st.dataframe(items_df.to_pandas(), use_container_width=True)

    st.subheader("Add Item")

    item_name = st.text_input("Item Name", key='itemName')
    amount_cents = st.number_input("Amount in cents", value=0, key='amountCents')
    item_quantity = st.number_input("Quantity", value=1, key='itemQuantity')

    def add_item_button():
        telemetry.add_event("item-added", {"receipt_id": receipt_id, "item_name": item_name, "amount_cents": amount_cents, "item_quantity": item_quantity})
        session.call("receipts.add_item", receipt_id, item_name, amount_cents, item_quantity)

    st.button("Add Item", key='addItem', on_click=add_item_button)

    st.subheader("Current Payments for Receipt")
    payments_df = session.table("data.payments").filter(col("receipt_id") == receipt_id)
    st.dataframe(payments_df.to_pandas(), use_container_width=True)

    st.subheader("Add Payment")
    payment_method = st.text_input("Payment Method", key='paymentMethod')
    payment_amount_cents = st.number_input("Payment amount in cents", value=0, key='paymentAmount')
    def add_payment_button():
        session.call("receipts.record_payment", receipt_id, payment_method, payment_amount_cents)

    st.button("Add Payment", on_click=add_payment_button, key='addPayment')

    st.header("Add New Receipt")
    new_receipt_id = st.number_input("Enter receipt_id", key='receiptId')

    customers_df = session.table("data.customers").select("id", "name")
    customer_id_to_name = {}
    for record in customers_df.collect():
        customer_id_to_name[list(record)[0]] = list(record)[1]
    customer_id = st.selectbox("Customer", customer_id_to_name.keys(), format_func=lambda x: customer_id_to_name[x], key='customerId')

    regions_df = session.table("data.regions").select("id", "name")
    region_id_to_name = {}
    for record in regions_df.collect():
        region_id_to_name[list(record)[0]] = list(record)[1]
    region_id = st.selectbox("Region", region_id_to_name.keys(), format_func=lambda x: region_id_to_name[x], key='regionId')

    def add_receipt_button():
        session.sql(
            "insert into data.receipts(id, customer_id, region_id, created_at) values (?, ?, ?, current_timestamp())",
            params=[new_receipt_id, customer_id, region_id]
        ).collect()

    st.button("Add Receipt", on_click=add_receipt_button, key='addReceipt')

if __name__ == '__main__':
    run_streamlit()
