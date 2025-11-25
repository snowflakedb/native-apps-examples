# Cortex API REST Call App

A Snowflake Native App with an SPCS service that exposes an endpoint to call the Snowflake Cortex LLM inference REST API.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SPCS Native App                          │
├─────────────────────────────────────────────────────────────┤
│  Backend Service (Compute Pool)                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Container (Flask)                                   │   │
│  │  - /health         → Health check                    │   │
│  │  - /cortex/complete → Calls Cortex REST API          │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  Service Function: v1.cortex_complete(prompt, model)        │
│                          │                                  │
│                          ▼                                  │
│  Cortex REST API: /api/v2/cortex/inference:complete         │
└─────────────────────────────────────────────────────────────┘
```

## Features

- Call Cortex LLM models via REST API from within Snowflake
- Uses OAuth token authentication from SPCS (`/snowflake/session/token`)
- Exposed as SQL service functions for easy integration
- Supports multiple models: llama3.1-8b, llama3.1-70b, mistral-large2, etc.

## Prerequisites

- Docker installed
- Snowflake CLI (`snow`) installed
- Connection configured in `~/.snowflake/config.toml`

## Deployment

```bash
# 1. Set your Snowflake connection
export SNOWFLAKE_DEFAULT_CONNECTION_NAME=<your_connection>

# 2. Run setup (creates resources, builds/pushes Docker image)
./setup.sh

# 3. Deploy the application
./deploy.sh

# 4. In Snowsight:
#    - Click 'Grant' to grant account privileges
#    - Click 'Activate' to create compute pools and start services
#    - Wait for the service to be READY
```

## Usage

### Via Service Function

```sql
-- With default model (llama3.1-8b)
SELECT cortex_api_rest_call_app_instance.v1.cortex_complete('What is Snowflake?');

-- With specific model
SELECT cortex_api_rest_call_app_instance.v1.cortex_complete('Explain machine learning', 'mistral-large2');
```

### Via REST Endpoint

Get the endpoint URL:

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

| Model | Description |
|-------|-------------|
| `llama3.1-8b` | Default, fast responses |
| `llama3.1-70b` | More capable |
| `llama3.1-405b` | Most capable Llama model |
| `mistral-large2` | Mistral's large model |
| `snowflake-arctic` | Snowflake's Arctic model |

## Troubleshooting

### Check Service Status

```sql
SELECT SYSTEM$GET_SERVICE_STATUS('cortex_api_rest_call_app_instance.app_public.backend');
```

### View Service Logs

```sql
CALL cortex_api_rest_call_app_instance.app_public.get_service_logs('app_public.backend', 0, 'cortex-backend', 100);
```

### Get App URL

```sql
CALL cortex_api_rest_call_app_instance.v1.app_url();
```

## Project Structure

```
cortex_api_rest_call_app/
├── app/                          # Deployed to Snowflake
│   ├── manifest.yml              # Privileges, endpoints, callbacks
│   ├── setup.sql                 # Roles, procedures, service functions
│   ├── support.sql               # Debug procedures
│   └── README.md                 # Shown in Snowsight
├── backend/
│   ├── Dockerfile
│   └── src/
│       ├── app.py                # Flask app with Cortex API integration
│       ├── entrypoint.sh
│       └── requirements.txt
├── prepare/
│   ├── provider_setup.sql        # Provider roles/resources
│   └── consumer_setup.sql        # Consumer roles
├── scripts/
│   └── setup_shared_content.sql
├── snowflake.yml                 # CLI project definition
├── Makefile.template
├── backend.yaml.template
├── setup.sh
└── deploy.sh
```

## Cleanup

```bash
snow app teardown
```

