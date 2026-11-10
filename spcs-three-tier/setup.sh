#!/usr/bin/env bash
set -euo pipefail
snow sql -f "prepare/provider_setup.sql"
snow sql -f "prepare/consumer_setup.sql"

repository_url=$(snow spcs image-repository url img_repo --database spcs_app --schema napp)
python3 - "$repository_url" <<'PYTHON'
from pathlib import Path
import sys
Path('Makefile').write_text(Path('Makefile.template').read_text().replace('<<REPOSITORY>>', sys.argv[1]))
PYTHON
make all
# Render only after successful pushes, using the local images' pushed digests.
python3 scripts/render_image_specs.py --repository "$repository_url"
