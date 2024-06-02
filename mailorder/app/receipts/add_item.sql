create or replace procedure receipts.add_item(receipt_id integer, name text, amount_cents integer, quantity integer)
  returns integer
  language python
  runtime_version=3.8
  packages=('snowflake-snowpark-python')
  imports=('/python/receipts.py')
  handler='receipts.add_item';

-- 4. grant appropriate privileges over these objects to your application roles. 
grant usage on procedure receipts.add_item(integer, text, integer, integer) to application role app_csr;
grant usage on procedure receipts.add_item(integer, text, integer, integer) to application role app_admin;
