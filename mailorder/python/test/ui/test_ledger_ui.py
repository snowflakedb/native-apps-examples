import ledger_ui
from streamlit.testing.v1 import AppTest
import numpy as n
import pytest as pytest
from common_test_fixtures import session, data
from snowflake.snowpark import Session

@pytest.fixture(autouse=True)
def set_up_tables(session: Session):
    session.create_dataframe(data=[data.outstanding_customer_1], schema=data.outstanding_customers_schema).write.save_as_table('ledger.outstanding_customers')
    session.create_dataframe(data=[data.outstanding_receipt_1], schema=data.outstanding_receipts_schema).write.save_as_table('ledger.outstanding_receipts')
    session.create_dataframe(data=[data.receipt_paid_1], schema=data.receipt_paid_schema).write.save_as_table('ledger.receipt_paid')
    session.create_dataframe(data=[data.receipt_total_1], schema=data.receipt_total_schema).write.save_as_table('ledger.receipt_total')
    session.create_dataframe(data=[data.tax_collected_per_receipt_1], schema=data.tax_collected_per_receipt_schema).write.save_as_table('ledger.tax_collected_per_receipt')

def test_ledger_ui_streamlit():
    at = AppTest.from_function(ledger_ui.run_streamlit)
    at.run()
    assert not at.exception

    # check dataframe for customers with outstanding money
    assert (at.dataframe[0].value[:].values == n.array([data.outstanding_customer_1], dtype=object)).all()

    # check dataframe for receipts with outstanding money
    assert (at.dataframe[1].value[:].values == n.array([data.outstanding_receipt_1], dtype=object)).all()

    # check dataframe for receipts paid
    assert (at.dataframe[2].value[:].values == n.array([data.receipt_paid_1], dtype=object)).all()

    # check dataframe for receipts total
    assert (at.dataframe[3].value[:].values == n.array([data.receipt_total_1], dtype=object)).all()

    # check dataframe for tax collected per receipt
    assert (at.dataframe[4].value[:].values == n.array([data.tax_collected_per_receipt_1], dtype=object)).all()

    # ensure still no exception
    assert not at.exception