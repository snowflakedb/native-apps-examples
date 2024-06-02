create or replace procedure regions.record_tax_transfer(region_id text, amount_cents integer)
  returns integer
  language python
  runtime_version=3.8
  packages=('snowflake-snowpark-python')
  imports=('/python/regions.py')
  handler='regions.record_tax_transfer'
  comment='Records a remittance of tax collected on behalf of local governments back to the region.';

grant usage on procedure regions.record_tax_transfer(text, integer) to application role app_admin;
