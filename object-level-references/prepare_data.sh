# The following variable assignations are used in the Azure external table and in the AWS API
# integration respectively, to used them, uncomment the lines and replace the value with your
# corresponding platform credentials.

# This lines create a database, and a schema.
snow sql -q "
CREATE OR REPLACE DATABASE obj_reference_db;

CREATE OR REPLACE SCHEMA obj_reference_schema;
"

# Prompt user for input

read -p " Do you want to create a warehouse specifically for this Native App ? y/N " enable_wh
enable_wh=${enable_wh:-N}
if [ "$enable_wh" == "y" ]; then
    # The following command creates a warehouse for you to test the ware and try again.ouse monitor example. If you
    # already have monitor privileges on other warehouse and prefer to use that one, keep this 
    # commant commented, otherwise execute it.For the warehouse to work properly, ACCOUNTADMIN must 
    # have EXPLICIT monitor privileges, it does not work for those privileges that were inherited.

    snow sql -q "
    CREATE WAREHOUSE IF NOT EXISTS obj_reference_wh
    warehouse_size = xsmall;
    "
fi

read -p "Do you want to enable the external table example ? y/N " enable_external_table
enable_external_table=${enable_external_table:-N}
if [ "$enable_external_table" == "y" ]; then
    read -p "Please add your Azure URL path: " azure_url_path
    read -p "Please add your Azure SAS token: " azure_sas_token
    read -p "Please add your external stage folder path: " azure_stage_folder_path

    if [ -z "${azure_url_path}" ] || [ -z "${azure_sas_token}" ]; then
        # the corresponding data from azure credentials at the begining of this document.
        echo "This values cannot be empty, please insert the correct credentials and try again."
    else
        # The following commands create an external table, in this example it is setup to connect 
        # to an azure container, if you want to enable it, please reßplace the placeholders with 
        # For examples using AWS or GCP visit our documentation page.
        snow sql -q "
        CREATE OR REPLACE STAGE obj_reference_db.obj_reference_schema.my_external_stage
        URL=$azure_url_path
        CREDENTIALS=(AZURE_SAS_TOKEN=$azure_sas_token);

        CREATE OR REPLACE EXTERNAL TABLE obj_reference_db.obj_reference_schema.my_external_table(
        number_name varchar as (value:c1::varchar),
        number_value number as (value:c2::number))
        LOCATION = @my_external_stage/$azure_stage_folder_path
        AUTO_REFRESH = FALSE
        REFRESH_ON_CREATE = TRUE
        FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1);
        "
    fi
fi

read -p "Do you want to enable the API integration example ? y/N " enable_api_integration
enable_api_integration=${enable_api_integration:-N}
if [ "$enable_api_integration" == "y" ]; then
    read -p "Please add your AWS IAM role: " api_iam_role_arn
    read -p "Please add your AWS api allowed prefixes: " api_allowed_prefixes
    
    if [ -z "${api_iam_role_arn}" ] | [ -z "${api_allowed_prefixes}" ]; then
        echo "This values cannot be empty, please insert the correct credentials and try again."
    else
        # The following commands create an api integration, in this example it is setup to connect 
        # to an AWS lambda function, if you want to enable it, please replace the placeholders with 
        # the corresponding data from AWS credentials at the begining of this document.
        snow sql -q "
        CREATE OR REPLACE API INTEGRATION obj_reference_db.obj_reference_schema.my_aws_api_integration
        api_provider = aws_api_gateway
        api_aws_role_arn = '$api_iam_role_arn'
        api_allowed_prefixes = ($api_allowed_prefixes)
        enabled = true
        ;"
    fi
fi

# This line creates a table with some sample values,
# as well as a view that selects directly from the table.

snow sql -q "
# CREATE OR REPLACE TABLE obj_reference_db.obj_reference_schema.obj_reference_table(
# val integer
# );

# INSERT INTO obj_reference_table VALUES (1),(2),(3),(4);

# CREATE OR REPLACE VIEW obj_reference_db.obj_reference_schema.obj_reference_view
# AS SELECT * FROM obj_reference_table;
# "

# This lines create a function and a procedure that sum two values and return the result.
# They have the same behavior and are used as mere examples of the procedure and function usage privileges.
snow sql -q "
CREATE OR REPLACE FUNCTION obj_reference_db.obj_reference_schema.obj_reference_function(val1 INTEGER, val2 INTEGER)
returns INTEGER
language sql
as 'SELECT val1 + val2';

CREATE OR REPLACE PROCEDURE obj_reference_db.obj_reference_schema.obj_reference_procedure(val1 INTEGER, val2 INTEGER)
returns INTEGER
language sql
AS \$$
    BEGIN
        return(select :val1 + :val2);
    END
\$$;
"