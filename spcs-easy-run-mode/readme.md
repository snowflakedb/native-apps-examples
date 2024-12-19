# SPCS EASY RUN MODE

This app provides an easy-to-use UI that helps users start their SPCS service in a few clicks after they have completed the onboarding process.

## Setup

**Prerequisites**: Install [SnowCLI](https://docs.snowflake.com/en/user-guide/snowsql-install-config.html) and [Docker](https://docs.docker.com/get-docker/).

Config your SnowCLI connection and specify it for deployment:

```
export APP_NAME=<enter-your-app-name>
export SNOWFLAKE_DEFAULT_CONNECTION_NAME=<connection-name>
```

Run the setup script:

```
./build.sh
```

Go to the app page given by the running results and grant all privileges it needs, click "activate" to wait it ready for launching.

Once the app launchs, Click and login, then follow the instructions in the app.

## File Structure

- `app/`: Files to create and deploy the app
- `easy-run-kaniko/`: Files to build the easy-run kaniko starter image, the image built by it can also be found in Snowflake's built-in image as `/snowflake/snowflake_images/images/easy-run-mode-kaniko-starter:0.0.1`
- `frontend/`: The app is running in the browser as a web app using SPCS, the files to build the frontend service are provided here, based on [Streamlit](https://streamlit.io/).

By running `./build.sh`, an image repo is first created to store the kaniko-starter and frontend images, then the images are built and pushed to the repo. The app is then deployed to your Snowflake account.

## Known Limitations

Currently,

1. not support the GitHub repo link in "service code" section.
2. can't be used in consumer's account after publishing, as it can't access the image created in the app. Don't publish it if you want to use it in another account, just fork it and deploy it in your account.
