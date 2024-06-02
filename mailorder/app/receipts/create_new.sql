create or replace procedure receipts.create_new(customer_id text, region text)
  returns integer
  language python
  runtime_version=3.8
  packages=('snowflake-snowpark-python')
  imports=('/python/receipts.py')
  handler='receipts.create_new'
  comment='Creates a new receipt for a given customer';

-- 4. grant appropriate privileges over these objects to your application roles. 
grant usage on procedure receipts.create_new(text, text) to application role app_csr;
grant usage on procedure receipts.create_new(text, text) to application role app_admin;
