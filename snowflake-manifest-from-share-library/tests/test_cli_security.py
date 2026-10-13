"""Check credential sourcing and error paths without contacting Snowflake."""

from unittest.mock import Mock, patch
import warnings

import pytest

from snowflake_manifest_from_share import cli, connection


@pytest.fixture(autouse=True)
def isolated_credentials(monkeypatch):
    monkeypatch.delenv('SNOWFLAKE_PASSWORD', raising=False)
    monkeypatch.delenv('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE', raising=False)
    monkeypatch.setattr(cli.sys.stdin, 'isatty', lambda: False)


@pytest.mark.parametrize('argument', [
    ['--password', 'dummy-secret-value'],
    ['--password=dummy-secret-value'],
    ['--private-key-passphrase', 'dummy-secret-value'],
    ['--private-key-passphrase=dummy-secret-value'],
    ['--pass', 'dummy-secret-value'],
])
def test_legacy_secret_arguments_are_rejected_without_echo(argument, monkeypatch, capsys):
    monkeypatch.setattr(cli.sys, 'argv', [
        'manifest', '--account', 'example', '--user', 'operator', '--share', 'EXAMPLE',
    ] + argument)
    with patch.object(cli, 'get_connection_from_args') as connect:
        with pytest.raises(SystemExit) as error:
            cli.main()
    assert error.value.code == 2
    assert 'dummy-secret-value' not in capsys.readouterr().err
    connect.assert_not_called()


def test_secret_from_environment_never_prompts(monkeypatch):
    monkeypatch.setenv('SNOWFLAKE_PASSWORD', 'dummy-secret-value')
    with patch.object(cli.getpass, 'getpass') as prompt:
        assert cli._resolve_secret('SNOWFLAKE_PASSWORD', 'Password: ') == 'dummy-secret-value'
    prompt.assert_not_called()


def test_noninteractive_missing_secret_never_prompts():
    with patch.object(cli.getpass, 'getpass') as prompt:
        assert cli._resolve_secret('SNOWFLAKE_PASSWORD', 'Password: ') is None
    prompt.assert_not_called()


def test_interactive_secret_uses_hidden_prompt(monkeypatch):
    monkeypatch.setattr(cli.sys.stdin, 'isatty', lambda: True)
    with patch.object(cli.getpass, 'getpass', return_value='dummy-secret-value') as prompt:
        assert cli._resolve_secret('SNOWFLAKE_PASSWORD', 'Password: ') == 'dummy-secret-value'
    prompt.assert_called_once_with('Password: ')


def test_interactive_echo_fallback_is_refused(monkeypatch):
    monkeypatch.setattr(cli.sys.stdin, 'isatty', lambda: True)
    def unsafe_prompt(prompt):
        warnings.warn('Cannot control echo', cli.getpass.GetPassWarning)
        pytest.fail('The fallback must be stopped before reading a secret')
    with patch.object(cli.getpass, 'getpass', side_effect=unsafe_prompt):
        with pytest.raises(cli.getpass.GetPassWarning):
            cli._resolve_secret('SNOWFLAKE_PASSWORD', 'Password: ')


def test_key_auth_ignores_password_environment(monkeypatch):
    monkeypatch.setenv('SNOWFLAKE_PASSWORD', 'unrelated-password')
    monkeypatch.setenv('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE', 'key-passphrase')
    monkeypatch.setattr(cli.sys, 'argv', [
        'manifest', '--account', 'example', '--user', 'operator', '--share', 'EXAMPLE',
        '--private-key-path', '/example/key.pem',
    ])
    with patch.object(cli, 'get_connection_from_args', return_value=Mock()) as connect, \
            patch.object(cli, 'ShareManifestGenerator'), patch.object(cli, 'YAMLFormatter'):
        cli.main()
    args = connect.call_args[0][0]
    assert args.password is None
    assert args.private_key_passphrase == 'key-passphrase'


@pytest.mark.parametrize('mode', [0o644, 0o640, 0o604, 0o660, 0o666])
def test_accessible_private_key_is_refused_before_parsing(tmp_path, mode):
    key = tmp_path / 'key.pem'
    key.write_text('dummy content')
    key.chmod(mode)
    with patch.object(connection.serialization, 'load_pem_private_key') as parse:
        with pytest.raises(PermissionError):
            connection._secure_read_private_key(str(key))
    parse.assert_not_called()


def test_private_key_permission_check_uses_open_descriptor(tmp_path):
    key = tmp_path / 'key.pem'
    key.write_text('dummy content')
    key.chmod(0o600)
    parsed_key = Mock()
    parsed_key.private_bytes.return_value = b'dummy-der'
    with patch.object(connection.serialization, 'load_pem_private_key', return_value=parsed_key):
        assert connection._secure_read_private_key(str(key)) == b'dummy-der'
