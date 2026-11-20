# Warehouse Whisperer Standalone SAR

This directory contains the standalone Snowflake App Runtime project for Warehouse Whisperer.

The Next.js application asks Cortex AI to generate bounded, read-only SQL against `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`, executes it as the dedicated `WAREHOUSE_WHISPERER_EXECUTOR` role, and returns an evidence-backed answer.

Run `prepare.sql` as `ACCOUNTADMIN`, then deploy as `WAREHOUSE_WHISPERER_EXECUTOR`. Both Native App examples package the version published by this project. Do not redeploy SAR when changing only Native App packaging because every deploy publishes another artifact version.

## Run Locally

```bash
npm install
npm run dev
```

## Verify

```bash
npm test
npm run build
snow app validate --project .
```

## Deploy

```bash
snow app deploy --connection <connection> --role WAREHOUSE_WHISPERER_EXECUTOR --project .
```

Deploy only when the SAR runtime itself changes.
