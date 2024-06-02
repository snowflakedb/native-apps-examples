create or replace procedure regions.tax_balances()
  returns table (region_id text, owing_cents integer)
  language python
  runtime_version=3.8
  packages=('snowflake-snowpark-python')
  imports=('/python/regions.py')
  handler='regions.tax_balances'
  comment='Returns a table of the taxes we have yet to remit in each region.';

grant usage on procedure regions.tax_balances() to application role app_admin;
