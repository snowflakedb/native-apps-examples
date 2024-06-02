# Account Privileges

This Snowflake Native Application sample demonstrates how to add account privileges to an object reference within a native application.

## Getting Started

### Prepare objects in account

Before start, ensure there is an existing warehouse used in the current connection. You can use the following command to create a new warehouse:

```sql
CREATE WAREHOUSE IF NOT EXISTS consumer_warehouse;
```

Execute the [references.sql](prepare/references.sql) file as the `ACCOUNTADMIN` role. This script sets up the table, view, function and procedure that will be binded inside the application:

```bash
snow sql -f 'prepare/references.sql'
```

### Installation

Execute the following command:

```bash
snow app run
```

> [!CAUTION]
> Note that objects with references are being created within stored procedures in [setup_script.sql](app/setup_script.sql), rather than inside user-defined functions. Because UDFs are resolved at build-time, we cannot create a UDF that uses a reference until that reference is bound.

### First-time setup

The first time you run the app (e.g. `snow app open`), you will be prompted to bind some references and add privileges before proceeding to the application's main functionality:

   - *table_reference*: `consumer_database.consumer_schema.table_reference`.

   - *view_reference*: You must choose `consumer_database.consumer_schema.view_reference`.

   - *procedure_reference*: You must choose `consumer_database.consumer_schema.procedure_reference`.

   - *function_reference*: You must choose `consumer_database.consumer_schema.function_reference`.

> These references and privileges are defined in [manifest.yml](app/manifest.yml).

Once references are set, the UI will let you proceed to the main application.

### Test the app

When you are inside the app, you will see three different buttons:

- *Call Udf reference*: Calls the user defined function you bound previously.

- *Call Procedure reference*: Calls the stored procedure previously binded in the setup.

- *Insert rows*: Insert a new row into the table previously binded in the setup. The dataframe is populated with the binded view.

### Additional Resources

- [Request references and object-level privileges from consumers](https://docs.snowflake.com/en/developer-guide/native-apps/requesting-refs)
- [Create a user interface to request privileges and references](https://docs.snowflake.com/en/developer-guide/native-apps/requesting-ui)
- [Access control privileges](https://docs.snowflake.com/en/user-guide/security-access-control-privileges)