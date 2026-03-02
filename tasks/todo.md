# Phobos Sample Return — Build Tasks

## Step 0: Scaffold
- [x] Create directory structure
- [x] Create `.gitignore`
- [ ] Initial commit

## Step 1: Phase 1 — Subsystem Data Files (parallel agents)
- [x] Mission Design agent → `mission/`
- [x] Propulsion agent → `propulsion/`
- [x] Power agent → `power/`
- [x] Telecom agent → `telecom/`
- [x] C&DH agent → `cdh/`
- [x] Thermal agent → `thermal/`
- [x] ADCS agent → `adcs/`
- [x] Payload agent → `payload/`
- [x] Spacecraft/Structures agent → `spacecraft/`

## Step 2: Phase 2 — Systems Engineering
- [x] Systems Engineering agent → `systems/`

## Step 3: Phase 3 — Report Templates
- [x] Reports agent → `reports/`

## Step 4: Review and Validate
- [x] Parse-check all YAML/TOML/JSON/CSV files — all 21 data files parse clean
- [x] Validate RON manifests — both trajectory and link_budget manifests valid
- [x] Cross-subsystem consistency check — mass/power values match between subsystem files and budgets
- [x] Verify template data paths — all 4 report templates + 3 analysis templates render without errors
- [x] Run `vv` against the project — processes successfully (Docker warnings expected, no errors)

## Review

### Summary
All 31 project files created across 11 directories. VVERDAD processes the project cleanly. 13 output files generated in `_output/`.

### Files by format
- **YAML (8)**: mission (3), propulsion (3), systems (2)
- **TOML (7)**: power (2), cdh (1), thermal (1), adcs (1), spacecraft (2)
- **JSON (6)**: telecom (3), payload (3)
- **CSV (2)**: systems/mass_budget.csv, systems/power_budget.csv
- **RON (2)**: trajectory.analysis/manifest.ron, link_budget.analysis/manifest.ron
- **Templates (6)**: reports (4), trajectory.analysis (1), link_budget.analysis (2)
- **Static (1)**: link_budget.analysis/run.sh

### VVERDAD features exercised
All features from the plan are tested: YAML/TOML/JSON/CSV parsing, quantity strings, epoch strings (with `| to_utc`), unit filters (`| value()`), analysis bundles with manifests, template rendering, cross-subsystem data access, analysis chaining (link budget declares trajectory output as input).

### Known limitation found
**Compound unit display**: VVERDAD's `Unit::multiply()`/`Unit::divide()` produce units with empty `symbol` and `name = "derived"`. Any quantity with compound units (`m/s`, `km/s`, `W/m^2`, `N*m*s`, etc.) renders as `"<value> derived"` instead of `"<value> <unit>"` in templates. This affects:
- Delta-V values showing as "2831 derived" instead of "2831 m/s" in reports
- The `| value()` filter can't re-parse these strings
- **Workaround applied**: Values used with `| value()` in analysis templates (C3, V-infinity, gravitational parameters) stored as plain numbers in `constraints.yaml`
- **Root cause**: `Unit::divide()`/`Unit::multiply()` in `units/unit.rs` always set `symbol: ""`, `name: "derived"` — they should preserve or reconstruct the compound unit symbol string
