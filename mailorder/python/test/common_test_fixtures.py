from pytest import fixture
from unittest.mock import patch
from snowflake.snowpark.session import Session
from datetime import datetime
from snowflake import telemetry

@fixture
def session():
    session = Session.builder.config('local_testing', True).create()
    yield session
    session.close()

@fixture
def session_sql():
    with patch('snowflake.snowpark.session.Session.sql') as session_sql:
        yield session_sql

@fixture
def telemetry():
    with patch('snowflake.telemetry') as telemetry:
        yield telemetry

class data:
    test_customer_id = 'cus1'
    test_customer_name = 'John Smith'

    test_region_id = 'ont'
    test_region_name = 'Ontario'

    customers_schema = ['id', 'name', 'created_at']
    customer_1 = [test_customer_id, test_customer_name, datetime.now()]

    test_tax_percent = 0.13
    regions_schema = ['id', 'name', 'tax_amount_pct', 'created_at']
    region_1 = [test_region_id, test_region_name, test_tax_percent, datetime.now()]

    test_receipt_id = 3435
    test_item_name = 'piano'
    test_item_amount_cents = 40000
    test_item_quantity = 2
    test_payment_method = 'credit card'
    test_payment_amount = 20000

    tax_transfer_amount = 23322

    receipts_schema = ['id', 'customer_id', 'region_id', 'created_at']
    test_receipt = [test_receipt_id, test_customer_id, test_region_id, datetime.now()]

    items_schema = ['receipt_id', 'name', 'amount_cents', 'quantity', 'created_at']
    test_item_1 = [test_receipt_id, 'item1', 300, 2, datetime.now()]
    test_item_2 = [test_receipt_id, 'item2', 200, 1, datetime.now()]

    payments_schema = ['receipt_id', 'method', 'amount_cents', 'created_at']
    test_payment = [test_receipt_id, test_payment_method, test_payment_amount, datetime.now()]
    hardcoded_total_cost = 3000

    outstanding_customers_schema = ['customer_id', 'owing_cents', 'receipts_owing']
    outstanding_customer_1 = [test_customer_id, 2000, '1,3,4']

    test_owing_cents = 2011
    outstanding_receipts_schema = ['receipt_id', 'customer_id', 'paid_cents', 'total_cents', 'owing_cents']
    outstanding_receipt_1 = [test_receipt_id, test_customer_id, 1000, 3000, test_owing_cents]

    receipt_paid_schema = ['receipt_id', 'amount_cents', 'last_payment_at']
    receipt_paid_1 = [test_receipt_id, 1000, datetime.now()]

    receipt_total_schema = ['receipt_id', 'amount_cents']
    receipt_total_1 = [test_receipt_id, 1000]

    collected_tax_cents = 12000
    tax_collected_per_receipt_schema = ['receipt_id', 'region_id', 'collected_taxable_cents', 'collected_tax_cents']
    tax_collected_per_receipt_1 = [test_receipt_id, test_region_id, 10000, collected_tax_cents]

    tax_transfers_schema = ['region_id', 'amount_cents', 'created_at']
    tax_transfer_1 = [test_region_id, tax_transfer_amount, datetime.now()]
