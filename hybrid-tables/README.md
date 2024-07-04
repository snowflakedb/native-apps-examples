# Hybrid Tables

This Snowflake Native Application sample demonstrates how to use hybrid tables when user needs to enforce a primary key constraint.

The `internal.dictionary` table simulates the behavior of a `Dictionary/Hash Table` data structure by allowing users add just key/value pairs that don't exist yet in the table.

```sql
CREATE HYBRID TABLE IF NOT EXISTS internal.dictionary
(
    key VARCHAR,
    value VARCHAR,
    CONSTRAINT pkey PRIMARY KEY (key)
);
```

To add new values in the `dictionary` table, there is a Stored Procedure that returns an `OK` status if the columns where added successfully or a json with the error if the new row could not be added.

```sql
CREATE OR REPLACE PROCEDURE core.add_key_value(KEY VARCHAR, VALUE VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO internal.dictionary VALUES (:KEY, :VALUE);
    RETURN OBJECT_CONSTRUCT('STATUS', 'OK');
    EXCEPTION
        WHEN STATEMENT_ERROR THEN
            RETURN OBJECT_CONSTRUCT('STATUS', 'FAILED',
                                    'SQLCODE', SQLCODE,
                                    'SQLERRM', SQLERRM,
                                    'SQLSTATE', SQLSTATE);
END;
$$;
```

## Development

### Setting up / Updating the Environment

Run the following command to create or update Conda environment. This includes tools like Snowflake CLI and testing packages:

```sh
conda env update -f local_test_env.yml
```
To activate the environment, run the following command:

```sh
conda activate hybrid-tables-testing
```

### Automated Testing

With the conda environment activated, you can test the app as follows:

```sh
pytest
```

### Manual Testing / Deployment to Snowflake

You can deploy the application in dev mode as follows:

```sh
snow app run
```

## Additional Resources

- [Hybrid Tables](https://docs.snowflake.com/en/user-guide/tables-hybrid)