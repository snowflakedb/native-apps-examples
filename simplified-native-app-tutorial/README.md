# Simplified Native Application Framework

This is a tutorial on how to build simplified native applications.

For more information about it please visit **[this page](https://docs.snowflake.com/)**.

## Data preparation

To run this example first execute this command, that is going to create databases, tables, and views with information about country populations:
```sh
snow sql -f 'scripts/provider_data.sql'
```

Upload data from csv to stage

```sh
snow stage copy data/population.csv @SNAF_POPULATION_DB.DATA_SCHEMA.RAW_DATA
```

Load csv to table
```sh
snow sql -f 'scripts/provider_load_csv.sql'
```

## Create Version 1 of the Application
Manifest with only one view shared but not the underlying table. 

```yml
manifest_version: 2

shared_content:
  databases:
    - SNAF_POPULATION_DB:
        schemas:
          - DATA_SCHEMA:
              views:
                - COUNTRY_POP_BY_YEAR_2000:
```

Run the following sql script
```sh
snow sql -f 'scripts/provider_snaf_package_v1.sql'
```

Test V1 of the application with local instance
```sh
snow sql -f 'scripts/consumer_test_app_v1.sql'
```

## Create Version 2 of the Application
Introduce roles to the application and share multiple tables and views 

```yml
manifest_version: 2

roles:
  - VIEWER:
      comment: "The viewer role with access to only one view"
  - ANALYST:
      comment: "The analyst role with access to both the view and the table"

shared_content:
  databases:
    - SNAF_POPULATION_DB:
        schemas:
          - DATA_SCHEMA:
              roles: [VIEWER, ANALYST]
              tables:
                - COUNTRY_POP_BY_YEAR:
                    roles: [ANALYST]
              views:
                - COUNTRY_POP_BY_YEAR_2000:
                    roles: [VIEWER, ANALYST]

```

Run the following sql script
```sh
snow sql -f 'scripts/provider_snaf_package_v2.sql'
```

Test V2 of the application with local instance
```sh
snow sql -f 'scripts/consumer_test_app_v2.sql'
```

## Create Version 3 of the Application
Add multiple notebooks to application package to share with consumer
``` yml
manifest_version: 2

roles:
  - VIEWER:
      comment: "The viewer role with only access to one view"
  - ANALYST:
      comment: "The analyst role with only access to both view and table"

shared_content:
  databases:
    - SNAF_POPULATION_DB:
        schemas:
          - DATA_SCHEMA:
              roles: [VIEWER, ANALYST]
              tables:
                - COUNTRY_POP_BY_YEAR:
                    roles: [ANALYST]
              views:
                - COUNTRY_POP_BY_YEAR_2000:
                    roles: [VIEWER, ANALYST]

application_content:
  notebooks:
      - intro_notebook:
          roles: [VIEWER, ANALYST]
          main_file: INTRO_NB.ipynb
      - analyst_notebook:
          roles: [ANALYST]
          main_file: ANALYST_NB.ipynb
```

Run the following sql script
```sh
snow sql -f 'scripts/provider_snaf_package_v3.sql'
```

Test V3 of the application with local instance
```sh
snow sql -f 'scripts/consumer_test_app_v3.sql'
```

## Teardown
To delete the database and packages

```sh
snow sql -f 'scripts/teardown.sql'
```

## Further reading
To test the application with a consumer account, create a private listing with SNAF_POPULATION_PACKAGE as the data product. 
https://other-docs.snowflake.com/en/collaboration/provider-listings-creating-publishing