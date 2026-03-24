#!/bin/sh
set -eu

quarto render subsystem_summary.qmd --to html
