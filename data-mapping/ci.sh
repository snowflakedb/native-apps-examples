set -e
./prepare_data.sh
snow app run
snow app teardown