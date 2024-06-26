# Snowflake Cortex

This simple Native App shows how to use Cortex Complete and make it interact with user data..

For this use case, the dataset used is rather small: only 10 entries. This is because the language model used in the Cortex function restricts input data size. You can change the language model used to a bigger / different one, according to your needs.
For more information about it please visit **[this page](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions#cost-considerations)**.

## Data preparation

To run this example first execute this command, that is going to create a database and table with information about spotify songs:
```sh
snow sql -f 'prepare/prepare_data.sql'
```
## App execution

Then run `snow app run` on your terminal.

## App and Data Deletion
To delete the database and the app run

```sh
snow sql -q 'DROP DATABASE SPOTIFY_CORTEX_DB;'
snow app teardown
```

## Further reading

For more information about the different ways to use snowflake AI capabilities visit this page:
**[Snowflake AI and ML documentation](https://docs.snowflake.com/en/guides-overview-ai-features)**