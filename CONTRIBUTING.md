# Continuous Integration (CI)

By default, GitHub disables any workflows (or CI/CD pipelines) when forking a repository. The forked repository contains a CI/CD workflow to deploy your data pipeline to dev and prod environments. Enable the workflows by opening your forked repository in GitHub, clicking on the `Actions` tab near the top middle of the page, and then clicking on the "I understand my workflows, go ahead and enable them" green button.

You must also add the appropriate secrets to your fork to enable integration tests; see the configuration section below.
## Python Tests Workflow (Unit Tests)

Unit tests only runs when there are changes or additions in native apps containing python files. The [pipeline](./.github/workflows/ci.yml) detects which apps were changed and only the tests for those apps are going to be executed.

If you add a new app that requires a new python package, you have to specify that in the [environment file](./shared_python_ci_env.yml) used to run python tests.

*Only apps with at least one python test are going to be tested in the pipeline. We recommend to add testing to changes/additions in order to improve the general quality*

## Integration Tests Workflow

Integration tests purpose is to do automatic integration/deployment into Snowflake by running the `snow` commands from the [Snowflake CLI](https://docs.snowflake.com/developer-guide/snowflake-cli-v2/index).

Same as *Unit Tests*, Integration Tests runs only for apps that were added/modified. Integration testing pipeline is defined in the [ci.integration.yml](./.github/workflows/ci-integration.yml) file.

### Configuration

Integration Tests depends on `Snowflake CLI` to connect to your Snowflake account; we need to set up some credentials before these tests will run. GitHub Secrets are used to securely store values/variables for use in CI/CD pipelines.

In GitHub, click on the `Settings` tab near the top of the page. From the Settings page, click on the `Secrets and variables` then `Actions` tab in the left hand navigation. The "Secrets" tab should be selected. For each secret listed below click on the green `New repository secret` and enter the name given below along with the appropriate value (adjusting as appropriate).

| Secret name | Secret value |
| --- | --- |
| SNOWFLAKE_ACCOUNT | myaccount |
| SNOWFLAKE_USER | myusername |
| SNOWFLAKE_PASSWORD | mypassword |
| SNOWFLAKE_ROLE | myrole |
| SNOWFLAKE_WAREHOUSE | mywarehouse |

Once the GitHub secrets are set, you are able to contribute in the repo.

### Usage

Integration Tests Workflow uses the [snowflake-cli-action](https://github.com/Snowflake-Labs/snowflake-cli-action), that basically installs the `Snowflake CLI` in our workflow environment.

For each modify app, we test that `snow app run` and `snow app teardown` commands run successfully, that means that we are verify that the app were deployed and removed successfully from our Snowflake account.

For apps that requieres some data before deployment, we provide a capability to define a `ci.sh` file in the root of the app, that executes all the steps required to deploy the app successfully.