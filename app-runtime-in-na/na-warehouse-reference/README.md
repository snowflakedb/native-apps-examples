# Warehouse Whisperer

Warehouse Whisperer is a serverless Snowflake Native App that answers natural-language questions about `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`.

It generates constrained read-only SQL, executes with Restricted Caller's Rights, and shows the SQL and supporting rows with every answer. Queries are restricted to the last 90 days and at most 200 result rows. Account Usage timestamps are UTC and can lag by up to 45 minutes.

After installation, grant the app's `app_user` application role to permitted users and approve the requested endpoint and Cortex AI permissions. Grant the requested `IMPORTED PRIVILEGES` on the `SNOWFLAKE` database, then bind a warehouse with `USAGE` to the `QUERY_WAREHOUSE` reference.
