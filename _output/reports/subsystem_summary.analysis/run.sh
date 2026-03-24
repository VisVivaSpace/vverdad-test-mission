#!/bin/sh
set -eu

# Install Quarto CLI
apt-get update -qq && apt-get install -y -qq curl >/dev/null 2>&1
curl -sL https://github.com/quarto-dev/quarto-cli/releases/download/v1.6.42/quarto-1.6.42-linux-amd64.deb -o quarto.deb
dpkg -i quarto.deb >/dev/null 2>&1
rm quarto.deb

# Install jupyter for Quarto's Python kernel
pip install -q jupyter

# Render
quarto render subsystem_summary.qmd --to html
