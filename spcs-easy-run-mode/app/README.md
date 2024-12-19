# 🎈 SPCS Easy Run Mode

## Motivation

**Why we need Easy-run mode for SPCS?**

As it requires a lot of steps to try SPCS, particularly:

- Setup a image repository and a compute pool 🤔
- **Write a `Dockerfile`** (which can including many works to set up all dependencies for services) 🤯
- **Build the docker image and push it to the image repository** (auth of the registry can also be annoying 😡)
- Write Spec function to create the service and wait (even need to check `SYSTEM$GET_SERVICE_LOGS` over and over again until the service starts) 😫
- Execute the function definition query carefully ⚠️
- Check where it builds the endpoint and then access the web UI 🤷‍♀️
- ...

Now with **SPCS easy-run mode**, you can stay in Snowflake ❄️ web portal (*SnowSight UI*) without any extra effort above, launch the service by just **one click**!

## Implementation

Generally, we wrap all those queries behind into a **Native App**, which will be published in Snowflake app marketplace.

1. Build the UI using *streamlit* to take some basic information as input
2. Store the customer's code files in stage
3. Execute [Kaniko](https://github.com/GoogleContainerTools/kaniko) job service to build and publish the container image from the stored files

## Demo

Code files:

- `templates/ui.html`
- `requirements.txt`
- `service.py`

We use the [echo service example](https://docs.snowflake.com/en/_downloads/c3a8f6109048f2ecca7734c7fd3b0b3b/SnowparkContainerServices-Tutorials.zip) in [SPCS official tutorial 1](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/tutorials/tutorial-1#download-the-service-code) to show how the easy-run mode works in the following demo

**What we expect to see**

1. The Echo service `ECHO_TEST` is running. `SELECT SYSTEM$GET_SERVICE_STATUS('ECHO_TEST')`
2. Web UI (after login)
3. Service function `MY_UDF` `show functions like 'MY_UDF';`


## WIP features

1. Arbitary numbers of parameters in service function
2. Arbitary numbers and paths of code files
3. Metrics and Monitoring
4. Distribute the app in public Marketplace