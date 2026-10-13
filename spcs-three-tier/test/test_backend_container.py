"""Run the built backend with dummy data and exercise the hash enforcement."""

import os
import subprocess

import pytest


IMAGE = os.environ.get('NATIVE_APPS_BACKEND_IMAGE')
pytestmark = pytest.mark.skipif(not IMAGE, reason='Set NATIVE_APPS_BACKEND_IMAGE after building the backend')


def run(script):
    result = subprocess.run(
        ['docker', 'run', '--rm', '--entrypoint', 'python', IMAGE, '-c', script],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_non_root_runtime_and_http_routes():
    run('''
import os, sys, types
import flask, pandas, numpy, snowflake.connector, snowflake.snowpark
assert os.getuid() == 10001
class Row:
    def as_dict(self): return {'O_CLERK': 'example', 'CLERK_TOTAL': 42}
class DataFrame:
    def __getattr__(self, name): return lambda *args, **kwargs: self
    def to_local_iterator(self): return iter([Row()])
helpers = types.ModuleType('spcs_helpers')
helpers.session = lambda: DataFrame()
sys.modules['spcs_helpers'] = helpers
import app
client = app.app.test_client()
assert client.get('/').status_code == 200
assert client.get('/snowpark/top_clerks?topn=invalid').status_code == 400
response = client.get('/snowpark/top_clerks')
assert response.status_code == 200, response.data
assert response.get_json() == [{'O_CLERK': 'example', 'CLERK_TOTAL': 42}]
''')


def test_tampered_package_hash_is_refused():
    run('''
from pathlib import Path
import subprocess, sys, tempfile
with tempfile.TemporaryDirectory() as directory:
    lock = Path(directory) / 'requirements.txt'
    lock.write_text('flask==3.1.3 --hash=sha256:' + '0' * 64 + '\\n')
    result = subprocess.run([sys.executable, '-m', 'pip', 'download', '--no-deps',
        '--no-cache-dir', '--require-hashes', '--only-binary=:all:', '-r', str(lock),
        '--dest', directory], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'DO NOT MATCH THE HASHES' in result.stderr, result.stderr
''')


def test_locked_amd64_wheels_are_available_and_verified():
    run('''
import subprocess, sys, tempfile
with tempfile.TemporaryDirectory() as directory:
    subprocess.run([sys.executable, '-m', 'pip', 'download', '--require-hashes',
        '--only-binary=:all:', '--python-version', '310', '--implementation', 'cp',
        '--abi', 'cp310', '--abi', 'abi3', '--abi', 'none',
        '--platform', 'manylinux2014_x86_64', '--platform', 'manylinux_2_34_x86_64',
        '--platform', 'manylinux_2_28_x86_64', '--platform', 'manylinux_2_17_x86_64',
        '--platform', 'any', '-r', '/app/requirements.txt', '--dest', directory], check=True)
''')
