# Claude Code Project Instructions

## Commit Messages
- **NEVER** add "Co-Authored-By: Claude" or any Claude attribution to commit messages
- Keep commit messages clean and professional

## Project Structure
This repository contains multiple native app examples for Snowflake.

### Snowflake Manifest From Share Library
Located in `snowflake-manifest-from-share-library/`, this library has two development branches:

1. **Core Branch**: `smohammedshamil-SNOW-2282659-add-manifest-library-core`
   - Contains core functionality without tests
   - `pytest.ini` has coverage requirements removed to prevent CI failures
   - Should not include `manifest.yml` file upstream

2. **Tests Branch**: `smohammedshamil-SNOW-2282662-add-tests-for-manifest-library`  
   - Contains full test suite with coverage requirements
   - Has complete test files: `test_cli.py`, `test_connection.py`, `test_share_manifest_generator.py`, `test_yaml_formatter.py`
   - Should not include `manifest.yml` file upstream

## CI/Build Process
- CI runs on pull request events (opened, edited, labeled, unlabeled, synchronize)
- Uses `.github/workflows/ci.yml` to run pytest on changed directories
- Automatically detects Python files and runs tests for affected directories
- Coverage requirements only apply to the tests branch

## Important Notes
- `manifest.yml` files should not be committed upstream
- Coverage requirements differ between branches intentionally
- Always check which branch you're working on before making changes