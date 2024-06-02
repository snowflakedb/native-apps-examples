create or replace procedure receipts.record_payment(receipt_id integer, method text, amount_cents integer)
  returns integer
  language python
  runtime_version=3.8
  packages=('snowflake-snowpark-python')
  imports=('/python/receipts.py')
  handler='receipts.record_payment'
  comment='Returns the remaining owing amount on the receipt, or 0 if the receipt has been paid in full / overpaid (tip)';

-- 4. grant appropriate privileges over these objects to your application roles. 
grant usage on procedure receipts.record_payment(integer, text, integer) to application role app_csr;
grant usage on procedure receipts.record_payment(integer, text, integer) to application role app_admin;
