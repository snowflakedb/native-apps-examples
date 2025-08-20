"""Tests for ShareManifestGenerator class."""

import pytest
from unittest.mock import Mock, patch
from snowflake_manifest_from_share.share_manifest_generator import ShareManifestGenerator
from snowflake_manifest_from_share.connection import SnowflakeConnection


class TestShareManifestGenerator:
    """Test cases for ShareManifestGenerator."""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock SnowflakeConnection."""
        return Mock(spec=SnowflakeConnection)

    @pytest.fixture
    def generator(self, mock_connection):
        """Create a ShareManifestGenerator with mocked connection."""
        return ShareManifestGenerator(mock_connection)

    def test_init(self, mock_connection):
        """Test ShareManifestGenerator initialization."""
        generator = ShareManifestGenerator(mock_connection)
        assert generator.connection == mock_connection

    def test_analyze_share_basic_structure(self, generator, mock_connection):
        """Test basic manifest generation with simple structure."""
        # Mock the share grants response
        mock_connection.execute_query_dict.side_effect = [
            # SHOW GRANTS TO SHARE response
            [
                {
                    'privilege': 'USAGE',
                    'granted_on': 'DATABASE',
                    'name': 'TEST_DB'
                },
                {
                    'privilege': 'USAGE',
                    'granted_on': 'SCHEMA',
                    'name': 'TEST_DB.PUBLIC'
                },
                {
                    'privilege': 'SELECT',
                    'granted_on': 'TABLE',
                    'name': 'TEST_DB.PUBLIC.TEST_TABLE'
                }
            ]
        ]

        result = generator.analyze_share('TEST_SHARE')

        # Verify structure
        assert result['manifest_version'] == 2
        assert 'roles' in result
        assert 'shared_content' in result
        assert 'databases' in result['shared_content']

        # Verify database structure
        databases = result['shared_content']['databases']
        assert len(databases) == 1
        assert 'TEST_DB' in databases[0]

        # Verify schema structure
        schemas = databases[0]['TEST_DB']['schemas']
        assert len(schemas) == 1
        assert 'PUBLIC' in schemas[0]

        # Verify table structure
        tables = schemas[0]['PUBLIC']['tables']
        assert len(tables) == 1
        assert 'TEST_TABLE' in tables[0]

    def test_analyze_share_with_database_role(self, generator, mock_connection):
        """Test manifest generation with database role."""
        mock_connection.execute_query_dict.side_effect = [
            # SHOW GRANTS TO SHARE response
            [
                {
                    'privilege': 'USAGE',
                    'granted_on': 'DATABASE_ROLE',
                    'name': 'TEST_DB.TEST_ROLE'
                }
            ],
            # SHOW DATABASE ROLES IN DATABASE response
            [
                {
                    'name': 'TEST_ROLE',
                    'comment': 'Test role comment'
                }
            ],
            # SHOW GRANTS TO DATABASE ROLE response
            [
                {
                    'privilege': 'USAGE',
                    'granted_on': 'DATABASE',
                    'name': 'TEST_DB'
                },
                {
                    'privilege': 'SELECT',
                    'granted_on': 'TABLE',
                    'name': 'TEST_DB.PUBLIC.ROLE_TABLE'
                }
            ]
        ]

        result = generator.analyze_share('TEST_SHARE')

        # Verify roles section
        assert len(result['roles']) == 1
        assert 'TEST_ROLE' in result['roles'][0]
        assert result['roles'][0]['TEST_ROLE']['comment'] == 'Test role comment'

        # Verify database has role
        databases = result['shared_content']['databases']
        assert 'TEST_ROLE' in databases[0]['TEST_DB']['roles'].items

    def test_analyze_share_with_views(self, generator, mock_connection):
        """Test manifest generation with views."""
        mock_connection.execute_query_dict.side_effect = [
            # SHOW GRANTS TO SHARE response
            [
                {
                    'privilege': 'USAGE',
                    'granted_on': 'DATABASE',
                    'name': 'TEST_DB'
                },
                {
                    'privilege': 'USAGE',
                    'granted_on': 'SCHEMA',
                    'name': 'TEST_DB.PUBLIC'
                },
                {
                    'privilege': 'SELECT',
                    'granted_on': 'VIEW',
                    'name': 'TEST_DB.PUBLIC.TEST_VIEW'
                }
            ]
        ]

        result = generator.analyze_share('TEST_SHARE')

        # Verify view structure
        schemas = result['shared_content']['databases'][0]['TEST_DB']['schemas']
        views = schemas[0]['PUBLIC']['views']
        assert len(views) == 1
        assert 'TEST_VIEW' in views[0]

    def test_analyze_share_empty_response(self, generator, mock_connection):
        """Test manifest generation with empty response."""
        mock_connection.execute_query_dict.return_value = []

        result = generator.analyze_share('EMPTY_SHARE')

        assert result['manifest_version'] == 2
        assert result['roles'] == []
        assert result['shared_content']['databases'] == []

    def test_get_role_info_with_comment(self, generator, mock_connection):
        """Test getting role info with comment."""
        mock_connection.execute_query_dict.return_value = [
            {
                'name': 'TEST_ROLE',
                'comment': 'This is a test role'
            }
        ]

        result = generator._get_role_info('TEST_DB.TEST_ROLE')

        assert result == {'comment': 'This is a test role'}

    def test_get_role_info_without_comment(self, generator, mock_connection):
        """Test getting role info without comment."""
        mock_connection.execute_query_dict.return_value = [
            {
                'name': 'TEST_ROLE',
                'comment': ''
            }
        ]

        result = generator._get_role_info('TEST_DB.TEST_ROLE')

        assert result == {}

    def test_get_role_info_not_found(self, generator, mock_connection):
        """Test getting role info when role not found."""
        mock_connection.execute_query_dict.return_value = []

        result = generator._get_role_info('TEST_DB.NONEXISTENT_ROLE')

        assert result == {}

    def test_get_role_info_database_error(self, generator, mock_connection):
        """Test getting role info with database error."""
        mock_connection.execute_query_dict.side_effect = Exception("Database error")

        result = generator._get_role_info('TEST_DB.TEST_ROLE')

        assert result == {}

    def test_build_shared_content_structure_complex(self, generator):
        """Test building complex shared content structure."""
        grants = [
            {
                'grant': {
                    'privilege': 'USAGE',
                    'granted_on': 'DATABASE',
                    'name': 'DB1'
                },
                'role': None
            },
            {
                'grant': {
                    'privilege': 'USAGE',
                    'granted_on': 'SCHEMA',
                    'name': 'DB1.SCHEMA1'
                },
                'role': 'ROLE1'
            },
            {
                'grant': {
                    'privilege': 'SELECT',
                    'granted_on': 'TABLE',
                    'name': 'DB1.SCHEMA1.TABLE1'
                },
                'role': 'ROLE1'
            },
            {
                'grant': {
                    'privilege': 'SELECT',
                    'granted_on': 'VIEW',
                    'name': 'DB1.SCHEMA1.VIEW1'
                },
                'role': None  # Direct grant to share
            }
        ]

        result, mappings = generator._build_shared_content_structure(grants)

        # Verify structure
        databases = result['databases']
        assert len(databases) == 1
        
        db = databases[0]['DB1']
        assert 'schemas' in db
        
        schema = db['schemas'][0]['SCHEMA1']
        assert 'roles' in schema
        assert 'ROLE1' in schema['roles'].items
        
        # Verify table has role
        table = schema['tables'][0]['TABLE1']
        assert 'ROLE1' in table['roles'].items
        
        # Verify view has no roles (direct grant)
        view = schema['views'][0]['VIEW1']
        # EmptyValue should be used for objects without roles

    def test_database_role_parsing(self, generator, mock_connection):
        """Test database role grants are properly handled."""
        mock_connection.execute_query_dict.side_effect = [
            # SHOW GRANTS TO SHARE response with DATABASE_ROLE
            [
                {
                    'privilege': 'USAGE',
                    'granted_on': 'DATABASE_ROLE',
                    'name': 'DEMO_DB.DR1'
                }
            ],
            # SHOW DATABASE ROLES IN DATABASE response
            [
                {
                    'name': 'DR1',
                    'comment': 'Demo role'
                }
            ],
            # SHOW GRANTS TO DATABASE ROLE response
            [
                {
                    'privilege': 'USAGE',
                    'granted_on': 'DATABASE',
                    'name': 'DEMO_DB'
                },
                {
                    'privilege': 'USAGE',
                    'granted_on': 'SCHEMA',
                    'name': 'DEMO_DB.ANALYTICS'
                },
                {
                    'privilege': 'SELECT',
                    'granted_on': 'TABLE',
                    'name': 'DEMO_DB.ANALYTICS.EMPLOYEES'
                }
            ]
        ]

        result = generator.analyze_share('DEMO_SHARE')

        # Verify role is in roles section
        assert len(result['roles']) == 1
        assert 'DR1' in result['roles'][0]
        assert result['roles'][0]['DR1']['comment'] == 'Demo role'

        # Verify database has DR1 role
        db = result['shared_content']['databases'][0]['DEMO_DB']
        assert 'DR1' in db['roles'].items

        # Verify schema has DR1 role  
        schema = db['schemas'][0]['ANALYTICS']
        assert 'DR1' in schema['roles'].items

        # Verify table has DR1 role
        table = schema['tables'][0]['EMPLOYEES']
        assert 'DR1' in table['roles'].items