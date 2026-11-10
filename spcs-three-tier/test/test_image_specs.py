"""Check that deployment follows pushed content, independent of mutable tags."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from unittest.mock import Mock

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('image_specs', ROOT / 'scripts/render_image_specs.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
REPOSITORY = 'example.registry.snowflakecomputing.com/spcs_app/napp/img_repo'


@pytest.fixture
def project(tmp_path):
    (tmp_path / 'app').mkdir()
    for filename in ['backend.yaml.template', 'frontend.yaml.template', 'manifest.yml.template']:
        shutil.copyfile(ROOT / filename, tmp_path / filename)
    return tmp_path


def mock_inspect(monkeypatch, values):
    def inspect(arguments, **kwargs):
        image = arguments[3].split('/')[-1]
        return Mock(stdout=json.dumps(values[image]))
    monkeypatch.setattr(renderer.subprocess, 'run', inspect)


def test_service_specs_and_manifest_share_pushed_digests(project, monkeypatch):
    values = {
        image: [REPOSITORY + '/' + image + '@sha256:' + character * 64]
        for image, character in zip(renderer.IMAGES.values(), 'abc')
    }
    mock_inspect(monkeypatch, values)
    renderer.render(REPOSITORY, project)
    service_images = []
    for filename in ['backend.yaml', 'frontend.yaml']:
        service = yaml.safe_load((project / 'app' / filename).read_text())
        service_images.extend(item['image'] for item in service['spec']['containers'])
    manifest = yaml.safe_load((project / 'app/manifest.yml').read_text())
    assert set(service_images) == set(manifest['artifacts']['container_services']['images'])
    assert all('@sha256:' in image for image in service_images)
    assert all(':latest' not in image for image in service_images)


@pytest.mark.parametrize('digests', [
    [], None,
    ['other.registry/db/schema/repo/eap_backend@sha256:' + 'a' * 64],
    [REPOSITORY + '/eap_backend:latest'],
    [REPOSITORY + '/eap_backend@sha256:bad'],
    [REPOSITORY + '/eap_backend@sha256:' + char * 64 for char in 'ab'],
])
def test_missing_or_ambiguous_digest_preserves_existing_files(project, monkeypatch, digests):
    output = project / 'app/backend.yaml'
    output.write_text('previous deployment')
    mock_inspect(monkeypatch, {'eap_backend': digests})
    with pytest.raises(ValueError):
        renderer.render(REPOSITORY, project)
    assert output.read_text() == 'previous deployment'
    assert not (project / 'app/manifest.yml').exists()


def test_inspect_failure_aborts_rendering(project, monkeypatch):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0])
    monkeypatch.setattr(renderer.subprocess, 'run', fail)
    with pytest.raises(subprocess.CalledProcessError):
        renderer.render(REPOSITORY, project)
    assert not list((project / 'app').iterdir())


def test_last_image_failure_does_not_partially_replace_specs(project, monkeypatch):
    output = project / 'app/backend.yaml'
    output.write_text('previous deployment')
    values = {
        image: [REPOSITORY + '/' + image + '@sha256:' + 'a' * 64]
        for image in renderer.IMAGES.values()
    }
    values['eap_router'] = []
    mock_inspect(monkeypatch, values)
    with pytest.raises(ValueError):
        renderer.render(REPOSITORY, project)
    assert output.read_text() == 'previous deployment'


def test_unknown_template_placeholder_does_not_replace_specs(project, monkeypatch):
    output = project / 'app/backend.yaml'
    output.write_text('previous deployment')
    with (project / 'manifest.yml.template').open('a') as template:
        template.write('\nunknown: <<UNEXPECTED>>\n')
    values = {
        image: [REPOSITORY + '/' + image + '@sha256:' + 'a' * 64]
        for image in renderer.IMAGES.values()
    }
    mock_inspect(monkeypatch, values)
    with pytest.raises(ValueError):
        renderer.render(REPOSITORY, project)
    assert output.read_text() == 'previous deployment'


@pytest.mark.parametrize('repository', ['https://' + REPOSITORY, REPOSITORY + ';command', '/db/schema/repo', 'host/db/schema'])
def test_invalid_repository_is_rejected_before_docker(project, monkeypatch, repository):
    docker = Mock()
    monkeypatch.setattr(renderer.subprocess, 'run', docker)
    with pytest.raises(ValueError):
        renderer.render(repository, project)
    docker.assert_not_called()
