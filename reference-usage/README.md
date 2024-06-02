# Reference Usage

This Snowflake Native Application sample demonstrates how to share a provider table with a native application whose data is replicated to any consumer in the data cloud.

## Getting Started

In this application, you will see how to add readonly access to a provider table using the [shared-content.sql](scripts/shared-content.sql) of a package script by using an intermediate view. For more information, see "How does the package script work?" below.

### Prepare objects in account

Make sure you already have a warehouse and it is used in the current connection. If not, you can create one with the following command, then set it in your `connections.toml` file:

```sql
CREATE WAREHOUSE IF NOT EXISTS provider_warehouse;
```

Execute the [setup.sql](prepare/setup.sql) file as the `ACCOUNTADMIN` role. This script sets up the table that is going to be shared:

```bash
snow sql -f 'prepare/provider.sql'
```

### Installation

Execute the following command, which deploys the application package, runs the package script, then creates an instance of the application in your configured Snowflake account:

```bash
snow app run
```

### Test the app

When you are inside the app, you will see a dataframe with the values of the provider table that were inserted before installing the application. You can modify the table's data as desired, and the changes will be reflected here. If you were to list this application on the Snowflake Marketplace, changes will also reflect in application objects installed in consumer accounts!

### How does the package script work?

As mentioned previously, the package script works by creating an intermediate view in a schema that exists on the application package, then sharing that schema and view "through" the application object. By doing so, the schema and view are available to the running application and its setup script. In [shared-content.sql](scripts/shared-content.sql), we have the following to create the view:

```sql
create view if not exists package_shared.view_shared
  as select * from reference_usage_app_sample.provider_schema.provider_table;
```

After the view has been created, we share it in the application package:

```sql
grant select on view package_shared.view_shared
  to share in application package {{ package_name }};
```

To work, this "package script" must be referenced by the [snowflake.yml](snowflake.yml) file. This file uses Jinja templating to interpolate in the resolved name of the application package object that Snowflake CLI creates when you deploy the app.

The script is then run every time you (re-)deploy your application, meaning it is important that it is written in an idempotent fashion. Avoid constructs like `CREATE OR REPLACE`!

### Additional Resources

- [Add shared data content to an application package](https://docs.snowflake.com/en/developer-guide/native-apps/preparing-data-content)