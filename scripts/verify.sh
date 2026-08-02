#!/usr/bin/env bash
set -euo pipefail

python -m ruff check src tests scripts
python -m pytest --cov=mike --cov-report=term-missing
python scripts/check_public_repo.py
python scripts/license_inventory.py --check
python -m pip_audit
bash -n scripts/verify.sh
