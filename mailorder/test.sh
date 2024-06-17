VAR1=".github/workflows"
VAR2="."
VAR3="mailorder/app/data"

BASE_DIRECTORY=$(echo "$VAR1" | cut -d "/" -f2)
echo "#$BASE_DIRECTORY#";