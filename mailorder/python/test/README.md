Unit tests go in this folder.

To set up and run unit tests, please follow the steps below.

# Set up testing conda environment (First Time setup)

Go to the project's root directory where you can find `local_test_env.yml` and run the following command once to set up a conda environment with the correct packages. Please note that the version of test packages may differ from the version of packages in Snowflake, so you will need to be careful with any differences in behavior.

```sh
conda env create -f local_test_env.yml
```

This will create a conda environment with the name `mailorder-testing`.

# Run unit tests

To run unit tests, follow these steps:

## Activate conda environment

You will need to activate this conda environment once per command line session:

```sh
conda activate mailorder-testing
```

To deactivate and use your current command line session for other tasks, run the following:

```sh
conda deactivate
```

## Run Pytest

To run the example tests provided, execute the following command from the project's root:

```sh
pytest
```

Note that there is a [pytest.ini](../../pytest.ini) file specifying the location of the source code that we are testing.
