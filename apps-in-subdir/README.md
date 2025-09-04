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

## Create a Native Application

Execute the following command:

```bash
snow app run --app-entity-id=app_v1
```
Note that we specified the Application Entity we want to run. Application Entity `app_v1` is created from Package Entity `pkg_v1` as instructed in project definition file. All the artifacts listed in `pkg_v1` are deployed to the stage under the `stage_subdirectory`: `v1`.


Now let's do the same for the other app:

```bash
snow app run --app-entity-id=app_v2
```
The above command will create `app_v2` from Application Entity `pkg_v2`. All the artifacts listed in `pkg_v2` have been deployed to the stage under the `stage_subdirectory`: `v2`. 

## Create a Version

Execute the following command: 
```bash
snow app version create version1 --app-entity-id=app_v1
```
Above command will create a version from the artifacts for the selected Application Entity which are under `stage_subdirectory`: `v1` in the stage. 

