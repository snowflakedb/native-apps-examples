This Native App examplifies how to implement the Cortex Complete and to make it interact with user data.

For this use case, the dataset used is rather small: only 10 entries. This is because the language model used in the Cortex function restricts input data size. You can change the language model used to a bigger / different one, according to your needs.
For more information about it please visit **[this page](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions#cost-considerations)**.

To run this example first execute this command:
```sh
snow sql -f 'prepare/prepare_data.sql'
```

Then run `snow app run` on your terminal.

To delete the database and the app run

```sh
snow sql -q 'DROP DATABASE SPOTIFY_CORTEX_DB;'
snow app teardown
```