# Phobos Sample Return — VVERDAD Test Mission

Test data for the [VVERDAD design data engine](https://github.com/VisVivaSpace/vverdad-prototype).

This repository contains a complete CML-4 (point design) Phobos Sample Return mission, built to exercise VVERDAD's data parsing, template rendering, analysis bundle execution, and cross-subsystem integration features.

## What is VVERDAD?

VVERDAD (Vis Viva Engineering, Review, Design, and Architecture Database) is a data-oriented engineering design system. Mission design data lives in plain-text files (YAML, TOML, JSON, CSV) organized by subsystem. VVERDAD loads these into an Entity-Component-System data store, parses physical quantities and time epochs automatically, renders Jinja2 templates against the full data tree, and executes containerized analysis bundles.

See the [VVERDAD prototype repository](https://github.com/VisVivaSpace/vverdad-prototype) for the engine itself.

## Mission Overview

A NASA New Frontiers-class Phobos Sample Return mission:

- **Launch**: ~2035, Falcon Heavy expendable, direct ballistic transfer to Mars
- **Mars operations**: Orbit insertion, transfer to Phobos quasi-satellite orbit (QSO)
- **Science**: Wide-angle camera imaging + gamma-ray/neutron spectrometer (GRNS) composition mapping
- **Sample collection**: Harpoon-based touch-and-go (TAG) maneuver
- **Return**: Earth return cruise, rendezvous with lunar Gateway station (no aeroshell)

Two instruments plus a sample collection system. Heritage drawn from JAXA MMX.

## Repository Structure

```
mission/          # Mission description, timeline, constraints, trajectory analysis bundle
spacecraft/       # Bus configuration, mechanisms
propulsion/       # Biprop main engine, monoprop RCS, delta-V budget
power/            # Solar arrays, battery
telecom/          # Antennas, transponder, ground station, link budget analysis bundle
cdh/              # Flight computer
thermal/          # Hot/cold case thermal summary
adcs/             # Attitude sensors, actuators, pointing requirements
payload/          # Wide-angle camera, GRNS, harpoon sample system
systems/          # Mass budget (CSV), power budget (CSV), power modes, data budget
reports/          # Jinja2 report templates (mission summary, mass/power tables, telecom)
_output/          # Rendered reports and analysis results (gitignored)
```

## Data Formats

Each subsystem uses the format best suited to its data:

| Subsystem | Format |
|-----------|--------|
| Mission Design | YAML |
| Propulsion | YAML |
| Power | TOML |
| Telecom | JSON |
| C&DH | TOML |
| Thermal | TOML |
| ADCS | TOML |
| Payload | JSON |
| Systems Engineering | YAML + CSV |

Physical quantities include units as strings (`"400 N"`, `"321 s"`, `"850 W"`). Time epochs include timescale suffixes (`"2035-06-15T12:00:00 UTC"`). VVERDAD parses both automatically.

## VVERDAD Features Exercised

- **Multi-format parsing**: YAML, TOML, JSON, CSV
- **Quantity strings**: Unit-aware values throughout all subsystem files
- **Epoch strings**: UTC and TDB timestamps in mission timeline
- **Template rendering**: Jinja2 report templates with unit conversion and time filters
- **Analysis bundles**: Trajectory scan (Rust) and link budget (Python) with RON manifests
- **Analysis chaining**: Link budget analysis depends on trajectory analysis outputs
- **Cross-subsystem data access**: Report templates pull data from the entire directory tree

## Usage

Point the `vv` CLI at this directory:

```sh
vv run .
```

This parses all data files, renders templates, and executes analysis bundles. Outputs land in `_output/`.

## License

MIT — see [LICENSE](LICENSE).
