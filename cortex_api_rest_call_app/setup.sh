#!/bin/bash
set -e

echo "=== Running provider setup SQL ==="
snow sql -f "prepare/provider_setup.sql"

echo "=== Running consumer setup SQL ==="
snow sql -f "prepare/consumer_setup.sql"

echo "=== Getting image repository URL ==="
repository_url=$(snow spcs image-repository url img_repo --database cortex_api_rest_call_app --schema napp 2>/dev/null | head -n 1 | tr -d '\r')
echo "Repository URL: $repository_url"

# Escape characters that are special in sed replacement
safe_repository_url=$(printf '%s' "$repository_url" | sed -e 's/[&|\\]/\\&/g')

# Paths to the files
makefile="./Makefile"
backend_yaml_template="./backend.yaml.template"
backend_yaml="./app/backend.yaml"

echo "=== Generating config files from templates ==="
cp $makefile.template $makefile
cp $backend_yaml_template $backend_yaml

# Replace placeholders
sed -i "" "s|<<REPOSITORY>>|$safe_repository_url|g" $makefile
sed -i "" "s|<<REPOSITORY>>|$safe_repository_url|g" $backend_yaml

echo "=== Building and pushing Docker images ==="
make all

echo "=== Setup complete! ==="
echo "Run ./deploy.sh to deploy the application"

