# Cortex API REST Call App

This Native App provides an SPCS service that exposes an endpoint to call the Snowflake Cortex LLM inference REST API.

## Features

- Call Cortex LLM models (llama3.1-8b, mistral-large2, etc.) via REST API
- Uses OAuth token authentication from SPCS
- Exposed as a SQL service function for easy integration

## Usage

### Via Service Function

```sql
-- With default model (llama3.1-8b)
SELECT cortex_api_rest_call_app_instance.v1.cortex_complete('What is Snowflake?');

-- With specific model
SELECT cortex_api_rest_call_app_instance.v1.cortex_complete('Explain machine learning', 'mistral-large2');
```

### Via REST Endpoint

After activation, access the endpoint URL:

```sql
CALL cortex_api_rest_call_app_instance.v1.app_url();
```

Then make HTTP requests:

```bash
curl -X POST "<endpoint_url>/cortex/complete" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Snowflake?", "model": "llama3.1-8b"}'
```

## Available Models

- `llama3.1-8b` (default)
- `llama3.1-70b`
- `llama3.1-405b`
- `mistral-large2`
- `snowflake-arctic`

## Troubleshooting

Check service status:
```sql
CALL cortex_api_rest_call_app_instance.app_public.get_service_status('app_public.backend');
```

View service logs:
```sql
CALL cortex_api_rest_call_app_instance.app_public.get_service_logs('app_public.backend', 0, 'cortex-backend', 100);
```

