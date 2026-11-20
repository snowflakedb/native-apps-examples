# Warehouse Whisperer: Native App-Managed Warehouse

This Native App variant creates and manages its own `WAREHOUSE_WHISPERER_APP_WH` warehouse for the embedded Warehouse Whisperer Application Service.

After installation, grant the app's `app_user` application role to permitted users and approve the requested endpoint, Cortex AI, imported `SNOWFLAKE` database, and `CREATE WAREHOUSE` privileges. The app creates an X-Small auto-resuming warehouse that suspends after 60 seconds and configures the serverless Application Service to use it.
