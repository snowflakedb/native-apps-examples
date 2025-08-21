"""Tests for SnowflakeConnection class."""

import pytest
from unittest.mock import Mock, patch
from snowflake_manifest_from_share.connection import SnowflakeConnection


class TestSnowflakeConnection:
    """Test cases for SnowflakeConnection."""

    def test_parse_account_from_url_basic(self):
        """Test parsing basic Snowflake URL."""
        url = "https://myaccount.snowflakecomputing.com"
        result = SnowflakeConnection._parse_account_from_url(url)
        assert result == "myaccount"

    def test_parse_account_from_url_with_region_cloud(self):
        """Test parsing URL with region and cloud provider."""
        url = "https://myaccount.us-west-2.aws.snowflakecomputing.com"
        result = SnowflakeConnection._parse_account_from_url(url)
        assert result == "myaccount.us-west-2.aws"

    def test_parse_account_from_url_complex(self):
        """Test parsing complex URL like user's example."""
        url = "https://dinaf_consumer_pp6.preprod6.us-west-2.aws.snowflakecomputing.com"
        result = SnowflakeConnection._parse_account_from_url(url)
        assert result == "dinaf_consumer_pp6.preprod6.us-west-2.aws"

    def test_parse_account_from_url_already_account_id(self):
        """Test with account identifier (no parsing needed)."""
        account_id = "myaccount.us-west-2.aws"
        result = SnowflakeConnection._parse_account_from_url(account_id)
        assert result == "myaccount.us-west-2.aws"

    def test_parse_account_from_url_http_not_https(self):
        """Test with HTTP URL (should still work)."""
        url = "http://myaccount.snowflakecomputing.com"
        result = SnowflakeConnection._parse_account_from_url(url)
        assert result == "myaccount"

    def test_parse_account_from_url_invalid_domain(self):
        """Test with non-Snowflake URL."""
        url = "https://example.com"
        result = SnowflakeConnection._parse_account_from_url(url)
        assert result == "example.com"

    def test_parse_account_from_url_empty_string(self):
        """Test with empty string."""
        result = SnowflakeConnection._parse_account_from_url("")
        assert result == ""

    def test_init_with_url(self):
        """Test SnowflakeConnection initialization with URL."""
        url = "https://myaccount.snowflakecomputing.com"
        conn = SnowflakeConnection(
            account=url,
            user="testuser",
            password="testpass"
        )
        assert conn.connection_params['account'] == "myaccount"
        assert conn.connection_params['user'] == "testuser"
        assert conn.connection_params['password'] == "testpass"
        assert conn.connection_params['authenticator'] == "snowflake"

    def test_init_with_account_id(self):
        """Test SnowflakeConnection initialization with account ID."""
        account_id = "myaccount.us-west-2.aws"
        conn = SnowflakeConnection(
            account=account_id,
            user="testuser",
            password="testpass"
        )
        assert conn.connection_params['account'] == "myaccount.us-west-2.aws"

    def test_init_with_private_key(self):
        """Test initialization with private key authentication."""
        conn = SnowflakeConnection(
            account="myaccount",
            user="testuser",
            private_key="test_private_key",
            private_key_passphrase="test_passphrase"
        )
        assert conn.connection_params['private_key'] == b"test_private_key"
        assert conn.connection_params['private_key_passphrase'] == "test_passphrase"
        assert 'password' not in conn.connection_params

    def test_init_with_optional_params(self):
        """Test initialization with optional parameters."""
        conn = SnowflakeConnection(
            account="myaccount",
            user="testuser",
            password="testpass",
            warehouse="TEST_WH",
            database="TEST_DB",
            schema="TEST_SCHEMA",
            role="TEST_ROLE",
            authenticator="oauth"
        )
        assert conn.connection_params['warehouse'] == "TEST_WH"
        assert conn.connection_params['database'] == "TEST_DB"
        assert conn.connection_params['schema'] == "TEST_SCHEMA"
        assert conn.connection_params['role'] == "TEST_ROLE"
        assert conn.connection_params['authenticator'] == "oauth"

    @patch('snowflake_manifest_from_share.connection.snowflake')
    def test_connect_success(self, mock_snowflake):
        """Test successful connection."""
        mock_connection = Mock()
        mock_snowflake.connector.connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account="myaccount",
            user="testuser",
            password="testpass"
        )
        result = conn.connect()
        
        assert result == mock_connection
        assert conn._connection == mock_connection
        mock_snowflake.connector.connect.assert_called_once_with(
            account="myaccount",
            user="testuser",
            password="testpass",
            authenticator="snowflake"
        )

    @patch('snowflake_manifest_from_share.connection.snowflake')
    def test_connect_failure(self, mock_snowflake):
        """Test connection failure."""
        mock_snowflake.connector.connect.side_effect = Exception("Connection failed")
        
        conn = SnowflakeConnection(
            account="myaccount",
            user="testuser",
            password="testpass"
        )
        
        with pytest.raises(Exception, match="Connection failed"):
            conn.connect()

    @patch('snowflake_manifest_from_share.connection.snowflake')
    def test_execute_query(self, mock_snowflake):
        """Test query execution."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("result1",), ("result2",)]
        mock_connection.cursor.return_value = mock_cursor
        mock_snowflake.connector.connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account="myaccount",
            user="testuser",
            password="testpass"
        )
        
        result = conn.execute_query("SELECT * FROM test_table")
        
        assert result == [("result1",), ("result2",)]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")
        mock_cursor.close.assert_called_once()

    @patch('snowflake_manifest_from_share.connection.snowflake')
    def test_execute_query_dict(self, mock_snowflake):
        """Test dictionary query execution."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{"col1": "val1"}, {"col1": "val2"}]
        mock_connection.cursor.return_value = mock_cursor
        mock_snowflake.connector.connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account="myaccount",
            user="testuser",
            password="testpass"
        )
        
        result = conn.execute_query_dict("SELECT * FROM test_table")
        
        assert result == [{"col1": "val1"}, {"col1": "val2"}]
        mock_connection.cursor.assert_called_with(mock_snowflake.connector.DictCursor)

    def test_context_manager(self):
        """Test context manager functionality."""
        conn = SnowflakeConnection(
            account="myaccount",
            user="testuser",
            password="testpass"
        )
        
        with patch.object(conn, 'connect') as mock_connect:
            with patch.object(conn, 'close') as mock_close:
                mock_connect.return_value = Mock()
                
                with conn as context_conn:
                    assert context_conn == conn
                    mock_connect.assert_called_once()
                
                mock_close.assert_called_once()