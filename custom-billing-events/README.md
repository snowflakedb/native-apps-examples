# Custom Billing Events

This Snowflake Native Application sample demonstrates how to bill costs from the provider side by adding a billing event to a procedure call.

## Getting Started

In this example, we are going to focus on `setup_script` and `module-billing/src/billing.py` files.

In the `billing.py` file, we have two methods:

   - A helper method that executes the `SYSTEM$CREATE_BILLING_EVENT` function, who is responsible of creating the billing event that tracks the consumer usage in the installed application.

   - The bill method that adds the billing event to the `core.increment_by_one` procedure call.

In the `setup_script.sql` file, you will find a procedure definition that adds the custom event to the procedure call:

```sql
CREATE OR REPLACE PROCEDURE core.billing_event()
   RETURNS STRING
   LANGUAGE PYTHON
   RUNTIME_VERSION = 3.8
   PACKAGES = ('snowflake-snowpark-python')
   IMPORTS=('/module-billing/billing.py')
   HANDLER = 'billing.bill';
```

## Installation

Execute the following command:

```bash
snow app run
```

## Test the app

 > You need two different accounts to test the application (provider and consumer).

### Provider side

In the provider account, make sure the app package was installed successfully. Once it is installed, you would create an initial version of the package.
For this, go through `Projects/App Packages`, click the `+ App Package` button on the top right corner and make sure you select the package you have deployed before.

Once the app package is ready to be shared, you should create and publish a [listing](https://other-docs.snowflake.com/en/collaboration/provider-listings-creating-publishing#share-data-or-apps-with-specific-consumers-using-a-private-listing) with the package and [add the billing event](https://other-docs.snowflake.com/en/collaboration/provider-listings-pricing-model#configure-your-listing-for-custom-event-billing).

### Consumer side

When the app package is listed, you should sign in to the consumer account and go through `Data Products/Private Sharing` and search for the app package that was shared with your account before and install the app.

To make sure the `billing event` is successfull, click over the `Test Billing Event` button to call the procedure with the event. If a success message appears, you billing event is working!

To validate the custom event billing pricing plan, you should execute the following command:

> The [MARKETPLACE_PAID_USAGE_DAILY](https://other-docs.snowflake.com/en/collaboration/views/marketplace-paid-usage-daily-ds) view is only available in production accounts.

```sql
SELECT listing_global_name,
   listing_display_name,
   charge_type,
   charge
FROM SNOWFLAKE.DATA_SHARING_USAGE.MARKETPLACE_PAID_USAGE_DAILY
WHERE charge_type='MONETIZABLE_BILLING_EVENTS'
      AND PROVIDER_ACCOUNT_NAME = <account_name>
      AND PROVIDER_ORGANIZATION_NAME= <organization_name>;
```

Make sure `<account_name>` and `<organization_name>` fields are replaced with the current provider values.

## Additional Resources

- [Add billable events to an application package](https://docs.snowflake.com/en/developer-guide/native-apps/adding-custom-event-billing)
- [Creating and publishing a listing](https://other-docs.snowflake.com/en/collaboration/provider-listings-creating-publishing)
- [Add Custom Event Billing to your listing](https://other-docs.snowflake.com/en/collaboration/provider-listings-pricing-model#add-custom-event-billing-to-your-listing)
