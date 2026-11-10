"""Opt-in validation of the shipped procedure with Snowflake's SQL parser."""

import json
import os
from pathlib import Path
import uuid

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get('NATIVE_APPS_TEST_CONNECTION'),
    reason='Set NATIVE_APPS_TEST_CONNECTION to a disposable test account',
)


@pytest.fixture(scope='module')
def database():
    import snowflake.connector

    connection = snowflake.connector.connect(
        connection_name=os.environ['NATIVE_APPS_TEST_CONNECTION']
    )
    cursor = connection.cursor()
    name = 'NA_SECURITY_' + uuid.uuid4().hex[:12].upper()
    try:
        cursor.execute('CREATE TRANSIENT DATABASE ' + name)
        cursor.execute('CREATE SCHEMA ENRICHIP')
        cursor.execute('CREATE FUNCTION ENRICHIP.ip2data(ip VARCHAR) RETURNS OBJECT AS $$ SELECT OBJECT_CONSTRUCT(\'ip\', ip) $$')
        source = (Path(__file__).resolve().parents[1] / 'app/setup_script.sql').read_text()
        procedure = 'CREATE OR REPLACE PROCEDURE ENRICHIP.enrich_ip_data' + source.split(
            'CREATE OR REPLACE PROCEDURE ENRICHIP.enrich_ip_data', 1
        )[1]
        # The Native App reference requires an installed app. Substitute only the
        # target with a disposable table, leaving its identifier handling intact.
        procedure = procedure.replace("REFERENCE(''tabletouse'')", 'ENRICHIP.bound_table')
        cursor.execute(procedure)
        yield cursor
    finally:
        cursor.execute('DROP DATABASE IF EXISTS ' + name)
        connection.close()


@pytest.mark.parametrize('input_column', [
    'IP_ADDRESS', 'Mixed Case', 'column.with.dots', "quote'and\"double", 'IP\") -- comment',
])
@pytest.mark.parametrize('result_column', ['ENRICHED', 'result\" --', 'result.with.dots'])
def test_procedure_treats_each_name_as_one_identifier(database, input_column, result_column):
    quote = lambda name: '"' + name.replace('"', '""') + '"'
    database.execute(
        f'CREATE OR REPLACE TABLE ENRICHIP.bound_table ({quote(input_column)} VARCHAR, '
        f'{quote(result_column)} VARIANT, untouched VARCHAR)'
    )
    database.execute("INSERT INTO ENRICHIP.bound_table VALUES ('1.2.3.4', NULL, 'keep')")
    database.execute('CALL ENRICHIP.enrich_ip_data(%s, %s)', (input_column, result_column))
    row = database.execute('SELECT * FROM ENRICHIP.bound_table').fetchone()
    assert row[0] == '1.2.3.4'
    assert json.loads(row[1]) == {'ip': '1.2.3.4'}
    assert row[2] == 'keep'
