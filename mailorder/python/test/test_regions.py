import regions as regions
from snowflake.snowpark.session import Session
from unittest.mock import MagicMock, patch
from datetime import datetime
from common_test_fixtures import session, data

def test_record_tax_transfer(session):
    session.sql = MagicMock()

    regions.record_tax_transfer(session, data.test_region_id, data.tax_transfer_amount)

    session.sql.assert_called_once_with(
        'insert into data.tax_transfers (region_id, amount_cents) values (?, ?)',
        params=[data.test_region_id, data.tax_transfer_amount]
    )

def test_tax_balances(session):
    session.create_dataframe(data=[data.tax_transfer_1], schema=data.tax_transfers_schema).write.save_as_table('data.tax_transfers')
    session.create_dataframe(data=[data.tax_collected_per_receipt_1], schema=data.tax_collected_per_receipt_schema).write.save_as_table('ledger.tax_collected_per_receipt')
    session.create_dataframe(data=[data.region_1], schema=data.regions_schema).write.save_as_table('data.regions')

    result = regions.tax_balances(session).collect()
    assert result == session.create_dataframe([[data.test_region_id, data.collected_tax_cents - data.tax_transfer_amount]]).collect()
