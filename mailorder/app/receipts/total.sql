create or replace procedure receipts.total(receipt_id integer)
  returns integer
  language python
  runtime_version=3.8
  packages=('snowflake-snowpark-python')
  imports=('/python/receipts.py')
  handler='receipts.total'
  comment='Total amount, after regional tax and tip, in cents.';

-- 4. grant appropriate privileges over these objects to your application roles. 
grant usage on procedure receipts.total(integer) to application role app_csr;
grant usage on procedure receipts.total(integer) to application role app_admin;
