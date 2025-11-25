# Snowflake SPCS Native App with MCP SERVER - Development Guide

This guide provides a complete end-to-end reference for developing, configuring, and deploying Snowflake Native Apps with Snowpark Container Services (SPCS) and MCP SERVER support.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Key Configuration Files](#key-configuration-files)
4. [Docker Container Setup](#docker-container-setup)
5. [MCP SERVER Integration](#mcp-server-integration)
6. [Snowflake Roles and Permissions](#snowflake-roles-and-permissions)
7. [Deployment Scripts](#deployment-scripts)
8. [Step-by-Step Deployment Process](#step-by-step-deployment-process)
9. [Testing MCP REST API](#testing-mcp-rest-api)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

A Snowflake SPCS Native App with MCP SERVER consists of:

1. **Application Package** - The distributable unit containing app code and configuration
2. **Container Services** - Docker containers running in Snowflake's infrastructure
3. **Compute Pools** - Snowflake-managed compute resources for running containers
4. **Service Functions** - SQL functions that call container endpoints
5. **MCP SERVER** - Model Context Protocol server exposing tools via REST API

### Single-Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SPCS Native App                          │
├─────────────────────────────────────────────────────────────┤
│  Backend Service (Compute Pool)                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Backend Container (Flask)                           │   │
│  │  - /health      → Health check                       │   │
│  │  - /echo        → Service function endpoint          │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Service Function: v1.echo(input)                    │   │
│  │  - Maps SQL calls to HTTP endpoint                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  MCP SERVER: v1.echo_mcp_server                      │   │
│  │  - Exposes tools via REST API                        │   │
│  │  - tools/list, tools/call endpoints                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
mcp-server-app-v1/
├── app/                          # Application artifacts (deployed to Snowflake)
│   ├── manifest.yml              # App manifest - defines privileges, endpoints
│   ├── setup.sql                 # Setup script - roles, procedures, MCP SERVER
│   ├── support.sql               # Support procedures (logging, debugging)
│   └── README.md                 # App readme shown in Snowsight
│
├── backend/                      # Backend container source
│   ├── Dockerfile
│   └── src/
│       ├── app.py                # Flask application with service function support
│       ├── entrypoint.sh         # Container entrypoint script
│       └── requirements.txt      # Python dependencies
│
├── prepare/                      # SQL setup scripts
│   ├── provider_setup.sql        # Creates provider-side roles and resources
│   └── consumer_setup.sql        # Creates consumer-side roles
│
├── scripts/
│   └── setup_shared_content.sql  # Post-deploy script for shared data
│
├── snowflake.yml                 # Snowflake CLI project definition
├── Makefile.template             # Docker build/push commands template
├── backend.yaml.template         # Backend service spec template
├── setup.sh                      # Main setup script
└── deploy.sh                     # Deployment script
```

---

## Key Configuration Files

### 1. `snowflake.yml` - Project Definition

```yaml
definition_version: 1
native_app:
  name: mcp_server_app_v1
  source_stage: napp.app_stage
  artifacts:
    - src: app/*
      dest: ./
  package:
    name: mcp_server_app_v1_pkg
    role: naspcs_role
    warehouse: wh_nap
    scripts:
      - scripts/setup_shared_content.sql
  application:
    name: mcp_server_app_v1_instance
    role: nac
    warehouse: wh_nac
```

### 2. `app/manifest.yml` - Application Manifest

```yaml
manifest_version: 1
version:
  name: V1
  label: "First Version"

configuration:
  grant_callback: v1.create_services

artifacts:
  setup_script: setup.sql
  readme: README.md
  default_web_endpoint:
    service: app_public.backend
    endpoint: api
  container_services:
    images:
      - /mcp_server_app_v1/napp/img_repo/echo_backend

lifecycle_callbacks:
  version_initializer: v1.init

privileges:
  - BIND SERVICE ENDPOINT:
      description: "Ability to create ingress URLs."
      required_at_setup: true
  - CREATE COMPUTE POOL:
      required_at_setup: true
      description: "Enable application to create its own compute pool(s)"
```

### 3. `app/setup.sql` - Setup Script with MCP SERVER

Key sections:

```sql
-- Application roles
CREATE APPLICATION ROLE IF NOT EXISTS app_admin;
CREATE APPLICATION ROLE IF NOT EXISTS app_user;

-- Service function that calls the backend
CREATE OR REPLACE FUNCTION v1.echo(input VARCHAR)
RETURNS VARCHAR
SERVICE = app_public.backend
ENDPOINT = api
AS '/echo';

-- MCP SERVER with custom tool
CREATE MCP SERVER IF NOT EXISTS v1.echo_mcp_server
FROM SPECIFICATION $$
tools:
- title: "Echo Tool"
  identifier: "mcp_server_app_v1_instance.v1.echo"
  name: "echo"
  type: "GENERIC"
  description: "Echoes back the input text"
  config:
    type: "function"
    warehouse: "WH_NAC"
    input_schema:
      type: "object"
      properties:
        input:
          description: "The text to echo back"
          type: "string"
$$;
```

### 4. `backend.yaml.template` - Service Specification

```yaml
spec:
  containers:
    - name: echo-backend
      image: <<REPOSITORY>>/echo_backend
  endpoints:
    - name: api
      port: 8080
      public: true
```

---

## Docker Container Setup

### Backend Dockerfile

```dockerfile
FROM python:3.10-slim
EXPOSE 8080
WORKDIR /app
COPY src/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY src/. .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
```

### Flask App with Service Function Support

Service functions send requests in a specific JSON format:

```python
@app.route("/echo", methods=['GET', 'POST'])
def echo():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        # Service function format: {"data": [[row_num, arg1, ...], ...]}
        if isinstance(data, dict) and 'data' in data:
            results = []
            for row in data['data']:
                row_num = row[0]
                input_val = row[1] if len(row) > 1 else ''
                results.append([row_num, f"Echo: {input_val}"])
            # Response format: {"data": [[row_num, result], ...]}
            return jsonify(data=results)
    # Handle regular requests...
```

---

## MCP SERVER Integration

### Components

1. **Service Function** - SQL function that maps to HTTP endpoint
2. **MCP SERVER Object** - Defines tools available via REST API
3. **MCP REST API** - Standard MCP protocol endpoints

### Service Function

```sql
CREATE OR REPLACE FUNCTION v1.echo(input VARCHAR)
RETURNS VARCHAR
SERVICE = app_public.backend    -- Service name
ENDPOINT = api                   -- Endpoint name from backend.yaml
AS '/echo';                      -- HTTP path on the container
```

### MCP SERVER Specification

```sql
CREATE MCP SERVER IF NOT EXISTS v1.echo_mcp_server
FROM SPECIFICATION $$
tools:
- title: "Echo Tool"                              # Display name
  identifier: "app_instance.v1.echo"              # Fully qualified function
  name: "echo"                                    # Tool name for API calls
  type: "GENERIC"
  description: "Echoes back the input text"
  config:
    type: "function"
    warehouse: "WH_NAC"                           # Warehouse for execution
    input_schema:
      type: "object"
      properties:
        input:
          description: "The text to echo back"
          type: "string"
$$;
```

### Granting Access

```sql
GRANT USAGE ON FUNCTION v1.echo(VARCHAR) TO APPLICATION ROLE app_user;
GRANT USAGE ON MCP SERVER v1.echo_mcp_server TO APPLICATION ROLE app_user;

-- For PAT/REST API access, grant to broader roles
GRANT APPLICATION ROLE app_instance.app_admin TO ROLE PUBLIC;
GRANT USAGE ON WAREHOUSE wh_nac TO ROLE PUBLIC;
```

---

## Snowflake Roles and Permissions

### Provider Role (`naspcs_role`)

```sql
CREATE ROLE IF NOT EXISTS naspcs_role;
GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE naspcs_role;
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE naspcs_role;
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE naspcs_role;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE naspcs_role;
GRANT CREATE APPLICATION PACKAGE ON ACCOUNT TO ROLE naspcs_role;
GRANT CREATE APPLICATION ON ACCOUNT TO ROLE naspcs_role;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE naspcs_role;
```

### Consumer Role (`nac`)

```sql
CREATE ROLE IF NOT EXISTS nac;
GRANT CREATE APPLICATION ON ACCOUNT TO ROLE nac;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE nac;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE nac WITH GRANT OPTION;
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE nac WITH GRANT OPTION;
```

---

## Deployment Scripts

### `setup.sh` - Initial Setup

```bash
#!/bin/bash
set -e

# 1. Run provider setup SQL
snow sql -f "prepare/provider_setup.sql"

# 2. Run consumer setup SQL
snow sql -f "prepare/consumer_setup.sql"

# 3. Get image repository URL
repository_url=$(snow spcs image-repository url img_repo --database <app_db> --schema napp)

# 4. Generate config files from templates
cp Makefile.template Makefile
cp backend.yaml.template app/backend.yaml
sed -i "" "s|<<REPOSITORY>>|$repository_url|g" Makefile app/backend.yaml

# 5. Build and push Docker images
make all
```

### `deploy.sh` - Deploy Application

```bash
#!/bin/bash
set -e

snow app run

echo "Next steps:"
echo "1. Open the app in Snowsight"
echo "2. Click 'Grant' to grant account privileges"
echo "3. Click 'Activate' to create compute pools and services"
```

---

## Step-by-Step Deployment Process

### Prerequisites
1. **Docker** installed and running
2. **Snowflake CLI (`snow`)** installed
3. **Snowflake connection** configured in `~/.snowflake/config.toml`

### Deployment Steps

```bash
# 1. Set the Snowflake connection
export SNOWFLAKE_DEFAULT_CONNECTION_NAME=<your_connection>

# 2. Run setup (creates resources, builds/pushes Docker images)
./setup.sh

# 3. Deploy the application
./deploy.sh

# 4. In Snowsight UI:
#    a. Click "Grant" for account privileges
#    b. Click "Activate" to create compute pools and services
#    c. Wait for service to be READY

# 5. Test the service function
snow sql -q "SELECT app_instance.v1.echo('Hello World')"

# 6. For MCP REST API access, grant permissions
snow sql -q "
GRANT APPLICATION ROLE app_instance.app_admin TO ROLE PUBLIC;
GRANT USAGE ON WAREHOUSE wh_nac TO ROLE PUBLIC;
"
```

---

## Testing MCP REST API

### Authentication

Use a Personal Access Token (PAT) with these headers:
- `Authorization: Bearer <PAT_TOKEN>`
- `X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN`

### Endpoint URL Format

```
https://<account>.snowflakecomputing.com/api/v2/databases/<app_instance>/schemas/v1/mcp-servers/<mcp_server_name>
```

### tools/list - List Available Tools

```bash
curl -X POST "https://<account>.snowflakecomputing.com/api/v2/databases/mcp_server_app_v1_instance/schemas/v1/mcp-servers/echo_mcp_server" \
  -H "Authorization: Bearer <PAT_TOKEN>" \
  -H "X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [{
      "name": "echo",
      "description": "Echoes back the input text",
      "title": "Echo Tool",
      "inputSchema": {
        "type": "object",
        "properties": {
          "input": {
            "description": "The text to echo back",
            "type": "string"
          }
        }
      }
    }]
  }
}
```

### tools/call - Execute a Tool

```bash
curl -X POST "https://<account>.snowflakecomputing.com/api/v2/databases/mcp_server_app_v1_instance/schemas/v1/mcp-servers/echo_mcp_server" \
  -H "Authorization: Bearer <PAT_TOKEN>" \
  -H "X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"echo","arguments":{"input":"Hello from MCP!"}}}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "Echo: Hello from MCP!"
    }],
    "isError": false
  }
}
```

---

## Troubleshooting

### Common Issues

1. **MCP REST API returns "not authorized"**
   - Grant app roles to the user's role: `GRANT APPLICATION ROLE app_instance.app_admin TO ROLE PUBLIC`
   - Grant warehouse access: `GRANT USAGE ON WAREHOUSE wh_nac TO ROLE PUBLIC`

2. **Service function returns parsing error**
   - Ensure backend returns correct format: `{"data": [[row_num, result], ...]}`
   - Check service logs for errors

3. **Docker login fails**
   - Re-login: `snow spcs image-registry login`
   - Check network policy allows authentication

4. **Service fails to start**
   - Check compute pool status: `SHOW COMPUTE POOLS`
   - Check service logs: `CALL app_instance.app_public.get_service_logs(...)`

### Debugging Commands

```sql
-- Get service status
SELECT SYSTEM$GET_SERVICE_STATUS('app_instance.app_public.backend');

-- Get service logs
CALL app_instance.app_public.get_service_logs('app_public.backend', 0, 'echo-backend', 100);

-- Get app URL
CALL app_instance.v1.app_url();

-- Test service function directly
SELECT app_instance.v1.echo('test');

-- Check MCP SERVER
DESC MCP SERVER app_instance.v1.echo_mcp_server;
```

---

## Quick Reference Commands

```bash
# Check connection
snow sql -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER()"

# Get repository URL
snow spcs image-repository url img_repo --database <app_db> --schema napp

# Login to image registry
snow spcs image-registry login

# Deploy app
snow app run

# Teardown app
snow app teardown
```

