#!/usr/bin/env bash
set -euo pipefail

quarto render subsystem_summary.qmd --to html
