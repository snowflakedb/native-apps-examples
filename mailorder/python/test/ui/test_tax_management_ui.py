import tax_management_ui
import regions as regions
from snowflake.snowpark import Session
from streamlit.testing.v1 import AppTest
import numpy as n
import pytest as pytest
from common_test_fixtures import session, session_sql, data

test_tax_amount = 33300

@pytest.fixture(autouse=True)
def set_up_tables(session: Session):
    session.create_dataframe(data=[data.region_1], schema=data.regions_schema).write.save_as_table('data.regions')
    session.create_dataframe(data=[data.tax_transfer_1], schema=data.tax_transfers_schema).write.save_as_table('data.tax_transfers')
    session.create_dataframe(data=[data.tax_collected_per_receipt_1], schema=data.tax_collected_per_receipt_schema).write.save_as_table('ledger.tax_collected_per_receipt')
    session.sproc.register(regions.tax_balances, name='regions.tax_balances')
    session.sproc.register(regions.record_tax_transfer, name='regions.record_tax_transfer')

def test_tax_management_ui_streamlit(session_sql):
    at = AppTest.from_function(tax_management_ui.run_streamlit)
    at.run()
    assert not at.exception

    # check current tax balances dataframe
    assert (at.dataframe[0].value[:].values == n.array([[data.test_region_id, data.collected_tax_cents - data.tax_transfer_amount]], dtype=object)).all()

    # test record tax transfer
    at.number_input('taxAmount').set_value(test_tax_amount).run()
    at.selectbox('regionId').select(data.test_region_id).run()

    at.button('recordTaxTransfer').click().run()
    session_sql.assert_called_once_with('insert into data.tax_transfers (region_id, amount_cents) values (?, ?)', params=[data.test_region_id, test_tax_amount])
    session_sql.reset_mock()

    # ensure still no exception
    assert not at.exception