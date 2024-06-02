create or replace procedure receipts.subtotal(receipt_id integer)
  returns integer
  language python
  runtime_version=3.8
  packages=('snowflake-snowpark-python')
  imports=('/python/receipts.py')
  handler='receipts.subtotal'
  comment='Bill subtotal (all items x quantities totalled up).';

-- 4. grant appropriate privileges over these objects to your application roles. 
grant usage on procedure receipts.subtotal(integer) to application role app_csr;
grant usage on procedure receipts.subtotal(integer) to application role app_admin;
