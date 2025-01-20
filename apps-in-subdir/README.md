# Apps in subdirectories

This Snowflake Native Application sample demonstrates how to utilize subdirectories to hold multiple versions of your Native Application in the same stage. This feature is only available in SnowCLI versions 3.x.x or later. 

## Getting Started

### Examine the folders structure

In this example, the application source files are organized into two folders under the root directory. Each folder contains all the source files required to create and run a Native Application.

FIX THIS: 

```
.
├── README.md
├── snowflake.yml
├── v1
│   ├── README.md
│   ├── manifest.yml
│   └── setup_script.sql
└── v2
    ├── README.md
    ├── manifest.yml
    └── setup_script.sql
```

### Project Definition File

To include multiple Native Apps in the same stage, we have to specify subdirectories for the stage that host each applications' source files. Application Package Entity definition includes a `stage_subdirectory` field for this purpose. You can set this field to the subdirectory in the stage that you wish to create an Application object or a Version from.

In this example, we have created two Application Package entities in the definition file, both of which refer to the **same** Application Package in Snowflake (same value for the `identifier` field). Each of this Package entities have a distinct `stage_subdirectory` which tells the CLI to create and manage the application source files within that subdirectory in the stage. 

For this example, we will demonstrate creating and versioning apps from distinct subdirectories in the Stage of one Application Package in snowflake using the CLI. To achieve this, we have defined two Application entities in the project definition file, each `from` one of the Application Package entities as the `target`. Notice that the `identifier` fields of the Applications are different, as to not override one another. 

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