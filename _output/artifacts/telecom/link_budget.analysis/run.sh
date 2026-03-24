#!/usr/bin/env bash
set -euo pipefail

pip install --quiet matplotlib numpy
python link_budget.py
python plot_margin.py
