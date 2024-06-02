import receipts as receipts
from snowflake.snowpark.session import Session
from unittest.mock import MagicMock, patch
from datetime import datetime
import pytest as pytest
from common_test_fixtures import session, data

EPSILON = 0.000001

@pytest.fixture(autouse=True)
def set_up_tables(session):
    session.create_dataframe(data=[data.customer_1], schema=data.customers_schema).write.save_as_table('data.customers')
    session.create_dataframe(data=[data.region_1], schema=data.regions_schema).write.save_as_table('data.regions')
    session.create_dataframe(data=[data.test_receipt], schema=data.receipts_schema).write.save_as_table('data.receipts')

def test_total_cost():
    assert receipts.total_cost(8, 3) == 24

@patch('snowflake.snowpark.session.Session.sql')
def test_create_new(session_sql, session):
    new_receipt_id = data.test_receipt_id + 5
    session_sql.return_value = session.create_dataframe([[new_receipt_id]], schema=['ID'])

    result = receipts.create_new(session, data.test_customer_id, data.test_region_id)

    assert result == new_receipt_id
    session_sql.assert_called_once_with('insert into data.receipts (customer_id, region_id) values (?, ?) returning id', params=[data.test_customer_id, data.test_region_id])

@patch('snowflake.snowpark.session.Session.sql')
def test_add_item(session_sql, session):
    receipts.add_item(session, data.test_receipt_id, data.test_item_name, data.test_item_amount_cents, data.test_item_quantity)

    session_sql.assert_called_once_with('insert into data.items (receipt_id, name, amount_cents, quantity) values (?, ?, ?, ?)', params=[data.test_receipt_id, data.test_item_name, data.test_item_amount_cents, data.test_item_quantity])

@patch('snowflake.snowpark.session.Session.sql')
def test_record_payment(session_sql, session):
    session.create_dataframe(data=[data.outstanding_receipt_1], schema=data.outstanding_receipts_schema).write.save_as_table('ledger.outstanding_receipts')

    result = receipts.record_payment(session, data.test_receipt_id, data.test_payment_method, data.test_payment_amount)

    assert result == data.test_owing_cents
    session_sql.assert_called_once_with('insert into data.payments (receipt_id, method, amount_cents) values (?, ?, ?)', params=[data.test_receipt_id, data.test_payment_method, data.test_payment_amount])

def test_subtotal(session):
    session.create_dataframe(data=[data.test_item_1, data.test_item_2], schema=data.items_schema).write.save_as_table('data.items')

    result = receipts.subtotal(session, data.test_receipt_id)

    assert result == data.test_item_1[2] * data.test_item_1[3] + data.test_item_2[2] * data.test_item_2[3]

def test_total(session):
    session.create_dataframe(data=[data.test_item_1, data.test_item_2], schema=data.items_schema).write.save_as_table('data.items')

    result = receipts.total(session, data.test_receipt_id)

    subtotal = data.test_item_1[2] * data.test_item_1[3] + data.test_item_2[2] * data.test_item_2[3]
    subtotal_after_tax = round(subtotal + subtotal * data.test_tax_percent)
    assert result == subtotal_after_tax

def test_tip_percentage(session):
    session.create_dataframe(data=[data.test_item_1, data.test_item_2], schema=data.items_schema).write.save_as_table('data.items')
    subtotal = data.test_item_1[2] * data.test_item_1[3] + data.test_item_2[2] * data.test_item_2[3]
    total = round(subtotal + subtotal * data.test_tax_percent)
    test_tip_percentage = 0.11
    payment_amount_with_tips = total + total * test_tip_percentage
    payment_row = [data.test_receipt_id, data.test_payment_method, payment_amount_with_tips, datetime.now()]
    session.create_dataframe(data=[payment_row], schema=data.payments_schema).write.save_as_table('data.payments')

    result = receipts.tip_percentage(session, data.test_receipt_id)

    assert abs(result - test_tip_percentage) <= EPSILON
