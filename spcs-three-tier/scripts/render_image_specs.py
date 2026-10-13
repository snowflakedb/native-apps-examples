"""Render deployment files from the digests of locally built, pushed images."""

import argparse
import json
from pathlib import Path
import re
import subprocess


IMAGES = {'BACKEND': 'eap_backend', 'FRONTEND': 'eap_frontend', 'ROUTER': 'eap_router'}
ROOT = Path(__file__).resolve().parents[1]


def pushed_digest(repository, image):
    reference = repository + '/' + image
    result = subprocess.run(
        ['docker', 'image', 'inspect', reference, '--format', '{{json .RepoDigests}}'],
        check=True, capture_output=True, text=True,
    )
    digests = json.loads(result.stdout)
    if not isinstance(digests, list):
        raise ValueError('Docker did not return pushed image digests')
    matches = {
        value for value in digests
        if isinstance(value, str) and re.fullmatch(
            re.escape(reference) + r'@sha256:[a-f0-9]{64}', value
        )
    }
    if len(matches) != 1:
        raise ValueError('Expected one pushed digest for ' + reference)
    # Service specs and Native App manifests use repository paths without a host.
    return '/' + matches.pop().split('/', 1)[1]


def render(repository, root=ROOT):
    repository = repository.rstrip('/').lower()
    if not re.fullmatch(r'[a-z0-9.-]+(?:/[a-z_][a-z0-9_$]*){3}', repository):
        raise ValueError('Expected a Snowflake registry host/database/schema/repository URL')
    replacements = {
        '<<' + name + '_IMAGE>>': pushed_digest(repository, image)
        for name, image in IMAGES.items()
    }
    outputs = {}
    for filename in ['backend.yaml', 'frontend.yaml', 'manifest.yml']:
        content = (root / (filename + '.template')).read_text()
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        if re.search(r'<<[^>]+>>', content):
            raise ValueError('Unresolved placeholder in ' + filename)
        outputs[root / 'app' / filename] = content
    # Validate every digest and template before replacing any deployment file.
    for path, content in outputs.items():
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(content)
        temporary.replace(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    args = parser.parse_args()
    render(args.repository)
