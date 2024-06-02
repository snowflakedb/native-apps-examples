create or replace procedure receipts.tip_percentage(receipt_id integer)
  returns numeric(8, 7)
  language python
  runtime_version=3.8
  packages=('snowflake-snowpark-python')
  imports=('/python/receipts.py')
  handler='receipts.tip_percentage'
  comment='How much did the customer tip on this (calculated by subtracting the owing amount from total payment)';

-- 4. grant appropriate privileges over these objects to your application roles. 
grant usage on procedure receipts.tip_percentage(integer) to application role app_csr;
grant usage on procedure receipts.tip_percentage(integer) to application role app_admin;
