# Snowflake Manifest from Share

A Python library to create declarative application manifests from secure data shares.

## Features

- **Generate declarative manifests** from existing Snowflake data shares
- **Smart connection handling** with multiple authentication methods (password, private key)
- **Easy copy-paste support** for full Snowflake URLs from the UI
- **Walk through share structure**:
  - Reads databases, schemas, tables, and views from existing shares
  - Processes database roles and their permissions
  - Maps which roles provide access to each object
- **Clean YAML manifests** with hierarchical structure and flow-style role arrays
- **Robust and tested** with 93% code coverage and 51 comprehensive tests
- **Dual interfaces** - Both CLI and Python API available
- **Production ready** with proper error handling and logging

## Installation

```bash
pip3 install -r requirements.txt
pip3 install -e .
```

**Note:** Use `python3` and `pip3` commands as this library requires Python 3.6+.

## Usage

### Command Line Interface

```bash
# Using account identifier
snowflake-manifest-from-share --account myaccount.region.cloud --user myuser --password mypass --share MYSHARE

# Using host (copy-paste from Snowflake account details)
snowflake-manifest-from-share --host myaccount.region.cloud.snowflakecomputing.com --user myuser --password mypass --share MYSHARE

# Using full Snowflake URL
snowflake-manifest-from-share --account https://myaccount.snowflakecomputing.com --user myuser --password mypass --share MYSHARE

# Using private key authentication
snowflake-manifest-from-share --host myaccount.region.cloud.snowflakecomputing.com --user myuser --private-key-path /path/to/key.pem --share MYSHARE

# Save output to file
snowflake-manifest-from-share --host myaccount.region.cloud.snowflakecomputing.com --user myuser --password mypass --share MYSHARE --output manifest.yml

# With additional connection parameters
snowflake-manifest-from-share --host myaccount.region.cloud.snowflakecomputing.com --user myuser --password mypass --share MYSHARE --warehouse COMPUTE_WH --role ANALYST_ROLE
```

### Python API

```python
# Run with python3
from snowflake_manifest_from_share import SnowflakeConnection, ShareManifestGenerator, YAMLFormatter

# Create connection (using account identifier)
connection = SnowflakeConnection(
    account='myaccount',
    user='myuser',
    password='mypassword',
    warehouse='COMPUTE_WH'
)

# Or using full URL (copy-paste from Snowflake UI)
connection = SnowflakeConnection(
    account='https://myaccount.snowflakecomputing.com',
    user='myuser',
    password='mypassword',
    warehouse='COMPUTE_WH'
)

# Create manifest generator
generator = ShareManifestGenerator(connection)

# Generate manifest for share
results = generator.analyze_share('MY_DATA_SHARE')

# Format to YAML
formatter = YAMLFormatter()
yaml_output = formatter.format_manifest(results)
print(yaml_output)

# Save to file
formatter.save_to_file(results, 'manifest.yml')

# Close connection
connection.close()
```

## Output Format

The generated manifest is structured in YAML format with a hierarchical representation:

```yaml
manifest_version: 2

roles:
  - VIEWER:
      comment: "The viewer role with access to one view and one notebook"
  - ANALYST:
      comment: "The analyst role with only access to the view, the table, and both the notebooks"

shared_content:
  databases:
    - DATABASE_NAME:
        schemas:
          - SCHEMA_NAME:
              roles: [VIEWER, ANALYST]
              tables:
                - TABLE_NAME:
                    roles: [ANALYST]
              views:
                - VIEW_NAME:
                    roles: [VIEWER, ANALYST]
```

The structure includes:
- **manifest_version**: Version of the output format (2)
- **roles**: List of database roles with their comments (if available)
- **shared_content**: Root container for all shared objects
- **databases**: List of databases with USAGE privileges
- **schemas**: List of schemas within each database with USAGE privileges, including roles that provide access
- **tables**: List of tables within each schema with SELECT privileges, including roles that provide access
- **views**: List of views within each schema with SELECT privileges, including roles that provide access

## Requirements

- Python 3.6+
- snowflake-connector-python>=2.7.0
- PyYAML>=6.0

## Authentication

The library supports multiple authentication methods:

1. **Password authentication**: Provide `--password`
2. **Private key authentication**: Provide `--private-key-path` (and optionally `--private-key-passphrase`)

## Development

### Running Tests

Install development dependencies:
```bash
pip3 install -e .[dev]
```

Run tests:
```bash
# Run all tests
python3 -m pytest

# Run with coverage
python3 -m pytest --cov=snowflake_manifest_from_share

# Run specific test file
python3 -m pytest tests/test_connection.py -v
```

### Test Coverage

The test suite includes:
- **Connection tests**: URL parsing, authentication methods, connection handling
- **Manifest generation tests**: Share processing, database role handling, YAML structure generation
- **YAML formatting tests**: Flow style lists, empty values, file operations  
- **CLI tests**: Argument parsing, error handling, output formatting

Current test coverage: **51 tests with 93% code coverage**

## License

Apache License 2.0