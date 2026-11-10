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
        cursor.execute('USE SECONDARY ROLES NONE')
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
    cursor.execute('GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE ' + names['naspcs_role'])
    with pytest.raises(Exception, match='Demo roles must be owned'):
        run((ROOT / 'prepare/provider_setup.sql').read_text())
    grants = cursor.execute('SHOW GRANTS TO ROLE ' + names['naspcs_role']).fetchall()
    assert {grant[1] for grant in grants} == {'CREATE INTEGRATION'}


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
    assert_consumer_can_delegate_warehouse(cursor, names)


def assert_consumer_can_delegate_warehouse(cursor, names):
    cursor.execute('USE ROLE ACCOUNTADMIN')
    cursor.execute('CREATE ROLE ' + names['owner'])
    cursor.execute('USE ROLE ' + names['nac'])
    # Test the deployment grant without help from ACCOUNTADMIN secondary roles.
    cursor.execute('USE SECONDARY ROLES NONE')
    cursor.execute('GRANT USAGE ON WAREHOUSE ' + names['wh_nac'] + ' TO ROLE ' + names['owner'])
    cursor.execute('USE ROLE ACCOUNTADMIN')
    grants = role_grants(cursor, names['owner'])
    assert any(grant['privilege'] == 'USAGE' and grant['name'] == names['wh_nac']
               and grant['granted_by'] == names['nac'] for grant in grants)


def role_grants(cursor, role):
    cursor.execute('SHOW GRANTS TO ROLE ' + role)
    columns = [column[0].lower() for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def test_upgrade_removes_obsolete_demo_grants(account):
    cursor, names, run = account
    provider = (ROOT / 'prepare/provider_setup.sql').read_text()
    consumer = (ROOT / 'prepare/consumer_setup.sql').read_text()
    run(provider)
    run(consumer)

    # Reproduce every excess grant made by the original setup scripts.
    obsolete = {
        'CREATE INTEGRATION', 'CREATE COMPUTE POOL', 'CREATE WAREHOUSE',
        'CREATE APPLICATION', 'BIND SERVICE ENDPOINT',
    }
    cursor.execute('USE ROLE ACCOUNTADMIN')
    for privilege in sorted(obsolete):
        cursor.execute(f'GRANT {privilege} ON ACCOUNT TO ROLE ' + names['naspcs_role'])
    cursor.execute('GRANT ALL ON WAREHOUSE ' + names['wh_nap'] + ' TO ROLE ' + names['naspcs_role'])
    cursor.execute('GRANT USAGE ON WAREHOUSE ' + names['wh_nac'] + ' TO ROLE ' + names['nac'] + ' WITH GRANT OPTION')
    cursor.execute('GRANT ALL ON TABLE ' + names['snowflake_sample_data'] + '.tpch_sf10.orders TO ROLE ' + names['nac'])

    prior = role_grants(cursor, names['naspcs_role'])
    assert obsolete <= {grant['privilege'] for grant in prior}
    assert any(grant['privilege'] == 'OPERATE' and grant['name'] == names['wh_nap'] for grant in prior)
    prior_consumer = role_grants(cursor, names['nac'])
    assert any(grant['name'] == names['wh_nac'] and grant['grant_option'] == 'true' for grant in prior_consumer)

    # Keep an unrelated grant to prove the migration only changes demo grants.
    cursor.execute('GRANT MONITOR USAGE ON ACCOUNT TO ROLE ' + names['naspcs_role'])
    run(provider)
    run(consumer)
    run(provider)
    run(consumer)

    provider_grants = role_grants(cursor, names['naspcs_role'])
    account_privileges = {grant['privilege'] for grant in provider_grants if grant['granted_on'] == 'ACCOUNT'}
    assert account_privileges == {'CREATE DATABASE', 'CREATE APPLICATION PACKAGE', 'MONITOR USAGE'}
    warehouse_grants = [grant for grant in provider_grants if grant['name'] == names['wh_nap']]
    assert {grant['privilege'] for grant in warehouse_grants} == {'USAGE'}
    assert all(grant['grant_option'] == 'false' for grant in warehouse_grants)

    consumer_grants = role_grants(cursor, names['nac'])
    warehouse_grants = [grant for grant in consumer_grants if grant['name'] == names['wh_nac']]
    assert {grant['privilege'] for grant in warehouse_grants} == {'USAGE'}
    assert all(grant['grant_option'] == 'true' for grant in warehouse_grants)
    table_grants = [grant for grant in consumer_grants if grant['name'] == names['snowflake_sample_data'] + '.TPCH_SF10.ORDERS']
    assert {grant['privilege'] for grant in table_grants} == {'SELECT'}
    for privilege in ['CREATE COMPUTE POOL', 'BIND SERVICE ENDPOINT']:
        assert any(grant['privilege'] == privilege and grant['grant_option'] == 'true' for grant in consumer_grants)
    assert_consumer_can_delegate_warehouse(cursor, names)
