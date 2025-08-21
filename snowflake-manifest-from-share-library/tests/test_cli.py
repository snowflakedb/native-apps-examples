"""Tests for CLI functionality."""

import pytest
from unittest.mock import Mock, patch, mock_open
from snowflake_manifest_from_share.cli import get_connection_from_args, main
import argparse
import sys
import io


class TestCLI:
    """Test cases for CLI functionality."""

    def test_get_connection_from_args_basic(self):
        """Test getting connection from basic args."""
        args = argparse.Namespace(
            account='myaccount',
            host=None,
            user='testuser',
            password='testpass',
            private_key_path=None,
            private_key_passphrase=None,
            authenticator='snowflake',
            warehouse=None,
            database=None,
            schema=None,
            role=None
        )

        connection = get_connection_from_args(args)

        assert connection.connection_params['account'] == 'myaccount'
        assert connection.connection_params['user'] == 'testuser'
        assert connection.connection_params['password'] == 'testpass'
        assert connection.connection_params['authenticator'] == 'snowflake'

    def test_get_connection_from_args_with_url(self):
        """Test getting connection from args with Snowflake URL."""
        args = argparse.Namespace(
            account='https://myaccount.snowflakecomputing.com',
            host=None,
            user='testuser',
            password='testpass',
            private_key_path=None,
            private_key_passphrase=None,
            authenticator='snowflake',
            warehouse='TEST_WH',
            database='TEST_DB',
            schema='TEST_SCHEMA',
            role='TEST_ROLE'
        )

        connection = get_connection_from_args(args)

        assert connection.connection_params['account'] == 'myaccount'
        assert connection.connection_params['warehouse'] == 'TEST_WH'
        assert connection.connection_params['database'] == 'TEST_DB'
        assert connection.connection_params['schema'] == 'TEST_SCHEMA'
        assert connection.connection_params['role'] == 'TEST_ROLE'

    def test_get_connection_from_args_with_host(self):
        """Test getting connection from args with host parameter."""
        args = argparse.Namespace(
            account=None,
            host='myaccount.region.cloud.snowflakecomputing.com',
            user='testuser',
            password='testpass',
            private_key_path=None,
            private_key_passphrase=None,
            authenticator='snowflake',
            warehouse=None,
            database=None,
            schema=None,
            role=None
        )

        connection = get_connection_from_args(args)

        assert connection.connection_params['account'] == 'myaccount.region.cloud'
        assert connection.connection_params['user'] == 'testuser'
        assert connection.connection_params['password'] == 'testpass'

    def test_get_connection_from_args_host_preferred_over_account(self):
        """Test that host parameter is preferred over account when both are provided."""
        args = argparse.Namespace(
            account='shouldnotbeused',
            host='myaccount.region.cloud.snowflakecomputing.com',
            user='testuser',
            password='testpass',
            private_key_path=None,
            private_key_passphrase=None,
            authenticator='snowflake',
            warehouse=None,
            database=None,
            schema=None,
            role=None
        )

        connection = get_connection_from_args(args)

        assert connection.connection_params['account'] == 'myaccount.region.cloud'

    def test_get_connection_from_args_neither_account_nor_host(self):
        """Test error when neither account nor host is provided."""
        args = argparse.Namespace(
            account=None,
            host=None,
            user='testuser',
            password='testpass',
            private_key_path=None,
            private_key_passphrase=None,
            authenticator='snowflake',
            warehouse=None,
            database=None,
            schema=None,
            role=None
        )

        with pytest.raises(SystemExit):
            get_connection_from_args(args)

    def test_get_connection_from_args_with_private_key(self):
        """Test getting connection from args with private key."""
        mock_private_key = b"-----BEGIN PRIVATE KEY-----\ntest_key_content\n-----END PRIVATE KEY-----"
        
        args = argparse.Namespace(
            account='myaccount',
            host=None,
            user='testuser',
            password=None,
            private_key_path='/path/to/key.pem',
            private_key_passphrase='test_passphrase',
            authenticator='snowflake',
            warehouse=None,
            database=None,
            schema=None,
            role=None
        )

        with patch('os.path.exists', return_value=True), \
             patch('os.stat'), \
             patch('builtins.open', mock_open(read_data=mock_private_key)):
            connection = get_connection_from_args(args)

        assert connection.connection_params['private_key'] == mock_private_key
        assert connection.connection_params['private_key_passphrase'] == 'test_passphrase'
        assert 'password' not in connection.connection_params

    def test_get_connection_from_args_private_key_file_not_found(self):
        """Test error handling when private key file is not found."""
        args = argparse.Namespace(
            account='myaccount',
            host=None,
            user='testuser',
            password=None,
            private_key_path='/nonexistent/key.pem',
            private_key_passphrase=None,
            authenticator='snowflake',
            warehouse=None,
            database=None,
            schema=None,
            role=None
        )

        with patch('builtins.open', side_effect=FileNotFoundError()):
            with pytest.raises(SystemExit):
                get_connection_from_args(args)

    @patch('snowflake_manifest_from_share.cli.ShareManifestGenerator')
    @patch('snowflake_manifest_from_share.cli.get_connection_from_args')
    @patch('snowflake_manifest_from_share.cli.YAMLFormatter')
    def test_main_success_stdout(self, mock_formatter_class, mock_get_connection, mock_generator_class):
        """Test successful main execution with stdout output."""
        # Mock args
        test_args = [
            'snowflake-manifest-from-share',
            '--account', 'myaccount',
            '--user', 'testuser',
            '--password', 'testpass',
            '--share', 'TEST_SHARE'
        ]

        # Mock objects
        mock_connection = Mock()
        mock_generator = Mock()
        mock_formatter = Mock()
        
        mock_get_connection.return_value = mock_connection
        mock_generator_class.return_value = mock_generator
        mock_formatter_class.return_value = mock_formatter
        
        # Mock return values
        test_result = {'manifest_version': 2, 'test': 'data'}
        mock_generator.analyze_share.return_value = test_result
        mock_formatter.format_manifest.return_value = 'yaml: output'

        # Capture stdout
        captured_output = io.StringIO()
        
        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', captured_output):
                with patch('sys.exit'):
                    main()

        # Verify calls
        mock_generator_class.assert_called_once_with(mock_connection)
        mock_generator.analyze_share.assert_called_once_with('TEST_SHARE')
        mock_formatter.format_manifest.assert_called_once_with(test_result)
        mock_connection.close.assert_called_once()

        # Verify output
        output = captured_output.getvalue()
        assert 'yaml: output' in output

    @patch('snowflake_manifest_from_share.cli.ShareManifestGenerator')
    @patch('snowflake_manifest_from_share.cli.get_connection_from_args')
    @patch('snowflake_manifest_from_share.cli.YAMLFormatter')
    def test_main_success_file_output(self, mock_formatter_class, mock_get_connection, mock_generator_class):
        """Test successful main execution with file output."""
        test_args = [
            'snowflake-manifest-from-share',
            '--account', 'myaccount',
            '--user', 'testuser',
            '--password', 'testpass',
            '--share', 'TEST_SHARE',
            '--output', 'manifest.yml'
        ]

        # Mock objects
        mock_connection = Mock()
        mock_generator = Mock()
        mock_formatter = Mock()
        
        mock_get_connection.return_value = mock_connection
        mock_generator_class.return_value = mock_generator
        mock_formatter_class.return_value = mock_formatter
        
        test_result = {'manifest_version': 2, 'test': 'data'}
        mock_generator.analyze_share.return_value = test_result

        with patch.object(sys, 'argv', test_args):
            with patch('sys.exit'):
                main()

        # Verify file save was called
        mock_formatter.save_to_file.assert_called_once_with(test_result, 'manifest.yml')

    def test_main_missing_auth_params(self):
        """Test main with missing authentication parameters."""
        test_args = [
            'snowflake-manifest-from-share',
            '--account', 'myaccount',
            '--user', 'testuser',
            '--share', 'TEST_SHARE'
            # Missing password or private key
        ]

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()

    @patch('snowflake_manifest_from_share.cli.ShareManifestGenerator')
    @patch('snowflake_manifest_from_share.cli.get_connection_from_args')
    def test_main_connection_error(self, mock_get_connection, mock_generator_class):
        """Test main with connection error."""
        test_args = [
            'snowflake-manifest-from-share',
            '--account', 'myaccount',
            '--user', 'testuser',
            '--password', 'testpass',
            '--share', 'TEST_SHARE'
        ]

        mock_connection = Mock()
        mock_generator = Mock()
        mock_get_connection.return_value = mock_connection
        mock_generator_class.return_value = mock_generator
        
        # Mock connection error
        mock_generator.analyze_share.side_effect = Exception("Connection failed")

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()

    def test_main_keyboard_interrupt(self):
        """Test main with keyboard interrupt."""
        test_args = [
            'snowflake-manifest-from-share',
            '--account', 'myaccount',
            '--user', 'testuser',
            '--password', 'testpass',
            '--share', 'TEST_SHARE'
        ]

        with patch('snowflake_manifest_from_share.cli.get_connection_from_args', side_effect=KeyboardInterrupt()):
            with patch.object(sys, 'argv', test_args):
                with pytest.raises(SystemExit):
                    main()