set -e
snow sql -f "prepare/provider_setup.sql"
snow sql -f "prepare/consumer_setup.sql"

# Gets the image repository url.
repository_url=$(snow spcs image-repository url img_repo --database spcs_app --schema napp)

# Paths to the files
makefile="./Makefile"
frontend_yaml_template="./frontend.yaml.template"
backend_yaml_template="./backend.yaml.template"
frontend_yaml="./app/frontend.yaml"
backend_yaml="./app/backend.yaml"

# Copy files
cp $makefile.template $makefile
cp $frontend_yaml_template $frontend_yaml
cp $backend_yaml_template $backend_yaml

# Replace placeholders in Makefile file using | as delimiter
sed -i "" "s|<<REPOSITORY>>|$repository_url|g" $makefile
sed -i "" "s|<<REPOSITORY>>|$repository_url|g" $frontend_yaml
sed -i "" "s|<<REPOSITORY>>|$repository_url|g" $backend_yaml

make all