# Mail-order

This Snowflake Native Application sample demonstrates how to implement the business operations
of an imaginary mail-order business within a native application using Snowpark.

## Summary

We model the following:

- customers
- regions we operate in and must collect tax on behalf of
- receipts for specific customers

After creating some regions and customers, a typical session might look like:

1. (`app_csr`) create a new receipt for a customer (`receipts.create_new`)
2. (`app_csr`) add items to the receipt (`receipts.add_item`)
3. (`app_csr`) let the customer know how much is owed (`receipts.total`) after tax
4. (`app_csr`) collect payment for the receipt, perhaps with an additional tip on top (`receipts.record_payment`)
5. (`app_admin`) see if there are any tax transfers (to government agencies) necessary now that we've collected tax on thier behalf (`regions.tax_balances`)
6. (`app_admin`) record tax transfers to agencies (`regions.record_tax_transfer`)

## Development

### Setting up / Updating the Environment

Run the following command to create or update Conda environment. This includes tools like Snowflake CLI and testing packages:

```sh
conda env update -f local_test_env.yml
```
To activate the environment, run the following command:

```sh
conda activate mailorder-testing
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
