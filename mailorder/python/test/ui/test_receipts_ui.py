import receipts_ui
from streamlit.testing.v1 import AppTest
import pytest as pytest
from common_test_fixtures import session, session_sql, telemetry, data
import receipts
from snowflake.snowpark import Session

@pytest.fixture(autouse=True)
def set_up_tables(session: Session):
    session.create_dataframe(data=[data.customer_1], schema=data.customers_schema).write.save_as_table('data.customers')
    session.create_dataframe(data=[data.region_1], schema=data.regions_schema).write.save_as_table('data.regions')
    session.create_dataframe(data=[data.test_receipt], schema=data.receipts_schema).write.save_as_table('data.receipts')
    session.create_dataframe(data=[data.test_item_1, data.test_item_2], schema=data.items_schema).write.save_as_table('data.items')
    session.create_dataframe(data=[data.test_payment], schema=data.payments_schema).write.save_as_table('data.payments')
    session.create_dataframe(data=[data.outstanding_receipt_1], schema=data.outstanding_receipts_schema).write.save_as_table('ledger.outstanding_receipts')
    session.udf.register(receipts.total_cost, name='receipts.total_cost')
    session.sproc.register(receipts.add_item, name='receipts.add_item')
    session.sproc.register(receipts.record_payment, name='receipts.record_payment')
    
def test_receipts_ui_streamlit(session_sql, telemetry):
    at = AppTest.from_function(receipts_ui.run_streamlit)
    at.run()
    assert not at.exception

    # check current items dataframe
    assert (at.dataframe[0].value[:].values == [
        [*data.test_item_1, data.test_item_1[2] * data.test_item_1[3]],
        [*data.test_item_2, data.test_item_2[2] * data.test_item_2[3]]
    ]).all()

    # check payments dataframe
    assert (at.dataframe[1].value[:].values == [data.test_payment]).all()

    new_item_name = 'new item'
    new_amount = 250
    new_qty = 3
    # test adding new item
    at.text_input('itemName').set_value(new_item_name).run()
    at.number_input('amountCents').set_value(new_amount).run()
    at.number_input('itemQuantity').set_value(new_qty).run()

    at.button('addItem').click().run()
    session_sql.assert_called_once_with('insert into data.items (receipt_id, name, amount_cents, quantity) values (?, ?, ?, ?)', params=[data.test_receipt_id, new_item_name, new_amount, new_qty])
    session_sql.reset_mock()
    telemetry.add_event.assert_called_once_with('item-added', {'receipt_id': data.test_receipt_id, 'item_name': new_item_name, 'amount_cents': new_amount, 'item_quantity': new_qty})

    # test adding a payment
    payment_method = 'credit card'
    payment_amount = 43400
    at.text_input('paymentMethod').set_value(payment_method).run()
    at.number_input('paymentAmount').set_value(payment_amount).run()

    at.button('addPayment').click().run()
    session_sql.assert_called_once_with('insert into data.payments (receipt_id, method, amount_cents) values (?, ?, ?)', params=[data.test_receipt_id, payment_method, payment_amount])
    session_sql.reset_mock()

    # test adding a new receipt
    new_receipt_id = 328
    at.number_input('receiptId').set_value(new_receipt_id).run()
    at.selectbox('customerId').select(data.test_customer_id).run()
    at.selectbox('regionId').select(data.test_region_id).run()
    at.button('addReceipt').click().run()

    session_sql.assert_called_once_with('insert into data.receipts(id, customer_id, region_id, created_at) values (?, ?, ?, current_timestamp())', params=[new_receipt_id, data.test_customer_id, data.test_region_id])
    session_sql.reset_mock()

    # ensure still no exception
    assert not at.exception