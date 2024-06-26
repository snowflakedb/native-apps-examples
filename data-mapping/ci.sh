set -e
sh prepare_data.sh
snow app run
snow app teardown