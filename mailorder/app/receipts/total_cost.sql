create or replace function receipts.total_cost(unit_cost integer, quantity integer)
    returns integer
    language python
    packages=('snowflake-snowpark-python')
    runtime_version=3.8
    imports=('/python/receipts.py')
    handler='receipts.total_cost';

grant usage on function receipts.total_cost(integer, integer) to application role app_admin;
grant usage on function receipts.total_cost(integer, integer) to application role app_csr;