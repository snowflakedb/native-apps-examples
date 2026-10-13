"""Opt-in Snowflake regression tests; all objects use unique names and are removed."""

import os
from pathlib import Path
import re
import uuid

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get('NATIVE_APPS_TEST_CONNECTION'),
    reason='Set NATIVE_APPS_TEST_CONNECTION to a disposable ACCOUNTADMIN test account',
)
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def account():
    import snowflake.connector

    connection = snowflake.connector.connect(
        connection_name=os.environ['NATIVE_APPS_TEST_CONNECTION']
    )
    cursor = connection.cursor()
    prefix = 'NA_SECURITY_' + uuid.uuid4().hex[:12].upper()
    names = {name: prefix + '_' + name.upper() for name in [
        'naspcs_role', 'nac', 'spcs_app', 'wh_nap', 'wh_nac',
        'snowflake_sample_data', 'nac_test', 'owner',
    ]}
    def run(source):
        source = re.sub(
            r'\b(' + '|'.join(name for name in names if name != 'owner') + r')\b',
            lambda match: names[match.group().lower()], source, flags=re.IGNORECASE,
        )
        source = source.replace("WAREHOUSE_SIZE='XSMALL'", "WAREHOUSE_SIZE='XSMALL' INITIALLY_SUSPENDED=TRUE")
        for statement in snowflake.connector.util_text.split_statements(__import__('io').StringIO(source)):
            cursor.execute(statement[0])
    try:
        cursor.execute('USE ROLE ACCOUNTADMIN')
        yield cursor, names, run
    finally:
        cursor.execute('USE ROLE ACCOUNTADMIN')
        for name in ['spcs_app', 'snowflake_sample_data', 'nac_test']:
            cursor.execute('DROP DATABASE IF EXISTS ' + names[name])
        for name in ['wh_nap', 'wh_nac']:
            cursor.execute('DROP WAREHOUSE IF EXISTS ' + names[name])
        for name in ['naspcs_role', 'nac', 'owner']:
            cursor.execute('DROP ROLE IF EXISTS ' + names[name])
        connection.close()


def make_untrusted_role(cursor, names, role):
    cursor.execute('CREATE ROLE ' + names['owner'])
    cursor.execute('GRANT CREATE ROLE ON ACCOUNT TO ROLE ' + names['owner'])
    cursor.execute('GRANT ROLE ' + names['owner'] + ' TO ROLE ACCOUNTADMIN')
    cursor.execute('USE ROLE ' + names['owner'])
    cursor.execute('CREATE ROLE ' + names[role])
    cursor.execute('USE ROLE ACCOUNTADMIN')


@pytest.mark.parametrize('role', ['naspcs_role', 'nac'])
def test_provider_rejects_squatted_roles_before_granting(account, role):
    cursor, names, run = account
    make_untrusted_role(cursor, names, role)
    with pytest.raises(Exception, match='Demo roles must be owned'):
        run((ROOT / 'prepare/provider_setup.sql').read_text())
    for name in ['naspcs_role', 'nac']:
        grants = cursor.execute('SHOW GRANTS TO ROLE ' + names[name]).fetchall()
        assert not grants


def test_provider_rejects_role_with_unexpected_members(account):
    cursor, names, run = account
    for name in ['naspcs_role', 'owner']:
        cursor.execute('CREATE ROLE ' + names[name])
    cursor.execute('GRANT ROLE ' + names['naspcs_role'] + ' TO ROLE ' + names['owner'])
    with pytest.raises(Exception, match='Demo roles must be owned'):
        run((ROOT / 'prepare/provider_setup.sql').read_text())
    assert not cursor.execute('SHOW GRANTS TO ROLE ' + names['naspcs_role']).fetchall()


def test_consumer_rejects_squatted_role(account):
    cursor, names, run = account
    make_untrusted_role(cursor, names, 'nac')
    with pytest.raises(Exception, match='Demo roles must be owned'):
        run((ROOT / 'prepare/consumer_setup.sql').read_text())
    assert not cursor.execute('SHOW GRANTS TO ROLE ' + names['nac']).fetchall()


def test_trusted_setup_can_be_repeated(account):
    cursor, names, run = account
    run((ROOT / 'prepare/provider_setup.sql').read_text())
    run((ROOT / 'prepare/consumer_setup.sql').read_text())
    run((ROOT / 'prepare/provider_setup.sql').read_text())
    grants = cursor.execute('SHOW GRANTS TO ROLE ' + names['naspcs_role']).fetchall()
    privileges = {row[1] for row in grants}
    assert 'CREATE APPLICATION PACKAGE' in privileges
    assert 'CREATE INTEGRATION' not in privileges
    assert 'CREATE COMPUTE POOL' not in privileges
