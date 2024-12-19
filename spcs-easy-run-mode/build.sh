set -e

snow sql -f "prepare.sql"

repository_url=$(snow spcs image-repository url spcs_easyrun_repo --database spcs_easyrun_db --schema spcs_easyrun_schema)
stop_frontend_func="${app_name}.public.stop_frontend()"



# build and push the kaniko image
cd easy-run-kaniko \
    && docker build --platform linux/amd64 -t easy_run_kaniko_image . \
    && docker tag easy_run_kaniko_image $repository_url/easy-run-mode:latest \
    && docker push $repository_url/easy-run-mode:latest \
    && cd ..

# build and push the frontend image
cd frontend \
  && docker build --platform linux/amd64 -t frontend_image . \
  && docker tag frontend_image $repository_url/frontend:latest \
  && docker push $repository_url/frontend:latest \
  && cd ..

# stop the frontend service if exists
if snow sql -q "describe procedure ${stop_frontend_func}" ; then
  snow sql -q "call ${stop_frontend_func}"
else
  echo "Function ${stop_frontend_func} does not exist, skipping"
fi

snow app run