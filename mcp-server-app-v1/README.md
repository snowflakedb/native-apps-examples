# Snowflake SPCS Native App with MCP SERVER - Development Guide

Complete reference for developing Snowflake Native Apps with SPCS and MCP SERVER support. The MCP SERVER is built with service functions as custom tools.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SPCS Native App                          │
├─────────────────────────────────────────────────────────────┤
│  Backend Service (Compute Pool)                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Container (Flask)                                   │   │
│  │  - /health → Health check                            │   │
│  │  - /echo   → Service function endpoint               │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  Service Function: v1.echo(input) → Maps SQL to HTTP        │
│                          │                                  │
│                          ▼                                  │
│  MCP SERVER: v1.echo_mcp_server → REST API (tools/list,call)│
└─────────────────────────────────────────────────────────────┘
```

**Components:**
1. **Application Package** - Distributable unit with code and config
2. **Container Services** - Docker containers in Snowflake infrastructure
3. **Compute Pools** - Managed compute resources
4. **Service Functions** - SQL functions calling container endpoints
5. **MCP SERVER** - Exposes tools via MCP REST API

## Project Structure

```
mcp-server-app-v1/
├── app/                          # Deployed to Snowflake
│   ├── manifest.yml              # Privileges, endpoints, callbacks
│   ├── setup.sql                 # Roles, procedures, MCP SERVER
│   ├── support.sql               # Debug procedures
│   └── README.md                 # Shown in Snowsight
├── backend/
│   ├── Dockerfile
│   └── src/
│       ├── app.py                # Flask with service function support
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

## Configuration Files

### snowflake.yml

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

### manifest.yml

```yaml
manifest_version: 2
version:
  name: V1
  label: "First Version"

artifacts:
  setup_script: setup.sql
  readme: README.md
  default_web_endpoint:
    service: app_public.backend
    endpoint: api
  container_services:
    images:
      - /mcp_server_app_v1/napp/img_repo/mcp_backend

lifecycle_callbacks:
  version_initializer: v1.init

privileges:
  - BIND SERVICE ENDPOINT:
      description: "Create ingress URLs"
  - CREATE COMPUTE POOL:
      description: "Enable application to create its own compute pool(s)"
```

### backend.yaml.template

```yaml
spec:
  containers:
    - name: mcp-backend
      image: <<REPOSITORY>>/mcp_backend
  endpoints:
    - name: api
      port: 8080
      public: true
```

## Service Functions & MCP SERVER

### Service Function

Maps SQL calls to HTTP endpoints:

```sql
CREATE FUNCTION v1.echo(input VARCHAR)
RETURNS VARCHAR
SERVICE = app_public.backend    -- Service name
ENDPOINT = api                   -- From backend.yaml
AS '/echo';                      -- HTTP path
```

### Backend Handler

Service functions send `{"data": [[row_num, arg1, ...], ...]}`:

```python
@app.route("/echo", methods=['POST'])
def echo():
    data = request.get_json()
    if isinstance(data, dict) and 'data' in data:
        results = []
        for row in data['data']:
            row_num, input_val = row[0], row[1] if len(row) > 1 else ''
            results.append([row_num, f"Echo: {input_val}"])
        return jsonify(data=results)
```

### MCP SERVER

```sql
CREATE MCP SERVER v1.echo_mcp_server
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
          description: "Text to echo"
          type: "string"
$$;
```

## Roles & Permissions

### Provider Role (naspcs_role)

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

### Consumer Role (nac)

```sql
CREATE ROLE IF NOT EXISTS nac;
GRANT CREATE APPLICATION ON ACCOUNT TO ROLE nac;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE nac;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE nac WITH GRANT OPTION;
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE nac WITH GRANT OPTION;
```

## Deployment

### Prerequisites
- Docker installed
- Snowflake CLI (`snow`) installed
- Connection in `~/.snowflake/config.toml`

### Steps

```bash
# 1. Set connection
export SNOWFLAKE_DEFAULT_CONNECTION_NAME=<your_connection>

# 2. Setup (creates resources, builds/pushes Docker)
./setup.sh

# 3. Deploy
./deploy.sh

# 4. In Snowsight: Grant → Activate → Launch App

# 5. Test
snow sql -q "SELECT mcp_server_app_v1_instance.v1.echo('Hello')"

# 6. For MCP REST API, grant access
snow sql -q "GRANT APPLICATION ROLE mcp_server_app_v1_instance.app_admin TO ROLE PUBLIC"
snow sql -q "GRANT USAGE ON WAREHOUSE wh_nac TO ROLE PUBLIC"
```

## MCP REST API Testing

### Authentication

Use PAT with headers:
- `Authorization: Bearer <PAT_TOKEN>`
- `X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN`

### Endpoint

```
POST https://<account>.snowflakecomputing.com/api/v2/databases/<app_instance>/schemas/v1/mcp-servers/<server_name>
```

### tools/list

```bash
curl -X POST "https://<account>.snowflakecomputing.com/api/v2/databases/mcp_server_app_v1_instance/schemas/v1/mcp-servers/echo_mcp_server" \
  -H "Authorization: Bearer <PAT>" \
  -H "X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

Response:
```json
{"jsonrpc":"2.0","id":1,"result":{"tools":[{"name":"echo","description":"Echoes back the input text","inputSchema":{"type":"object","properties":{"input":{"type":"string"}}}}]}}
```

### tools/call

```bash
curl -X POST "https://<account>.snowflakecomputing.com/api/v2/databases/mcp_server_app_v1_instance/schemas/v1/mcp-servers/echo_mcp_server" \
  -H "Authorization: Bearer <PAT>" \
  -H "X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"echo","arguments":{"input":"Hello!"}}}'
```

Response:
```json
{"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"Echo: Hello!"}],"isError":false}}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MCP API "not authorized" | `GRANT APPLICATION ROLE app.app_admin TO ROLE PUBLIC` |
| Service function parse error | Backend must return `{"data": [[row_num, result], ...]}` |
| Docker login fails | `snow spcs image-registry login` |
| Service won't start | Check: `SHOW COMPUTE POOLS;` and service logs |

### Debug Commands

```sql
-- Service status
SELECT SYSTEM$GET_SERVICE_STATUS('mcp_server_app_v1_instance.app_public.backend');

-- Service logs
CALL mcp_server_app_v1_instance.app_public.get_service_logs('app_public.backend', 0, 'mcp-backend', 100);

-- App URL
CALL mcp_server_app_v1_instance.v1.app_url();

-- Test function
SELECT mcp_server_app_v1_instance.v1.echo('test');

-- Describe MCP SERVER
DESC MCP SERVER mcp_server_app_v1_instance.v1.echo_mcp_server;
```

## Quick Reference

```bash
snow sql -q "SELECT CURRENT_ACCOUNT()"     # Check connection
snow spcs image-registry login              # Login to registry
snow app run                                # Deploy app
snow app teardown                           # Remove app
```

## Compute Pool Sizes

| Family | Use Case |
|--------|----------|
| `CPU_X64_XS` | Lightweight (default) |
| `CPU_X64_S/M/L` | Heavier workloads |
| `GPU_NV_S/M` | GPU workloads |
