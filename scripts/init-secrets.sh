#!/usr/bin/env bash
set -e

# Install detect-secrets (if not installed) and create a baseline
python -m pip install --upgrade pip
pip install detect-secrets

# Create baseline (run locally, review before committing)
detect-secrets scan > .secrets.baseline

echo "Created .secrets.baseline. Review the file and commit it if it is correct (do NOT commit real secrets)."