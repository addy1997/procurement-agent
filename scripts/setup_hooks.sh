#!/usr/bin/env bash
# Run once after cloning: bash scripts/setup_hooks.sh
set -euo pipefail
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
echo "✓ Git hooks installed (.githooks/pre-commit active)"
