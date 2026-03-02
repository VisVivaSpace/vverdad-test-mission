# Phobos Sample Return Test Repository — Agent Task Plan

## Mission Overview

A Phobos sample return mission at CML-4 maturity (point design with margins, consistent subsystem budgets, key risks identified). The spacecraft is based on JAXA/ESA MMX but simplified:

- **Launch**: Direct ballistic transfer to Mars (no SEP, no gravity assists)
- **Mars operations**: Orbit insertion, transfer to Phobos quasi-satellite orbit
- **Science**: Camera imaging, gamma-ray/neutron spectrometer (GRNS) surface composition mapping
- **Sample collection**: Harpoon-based touch-and-go (TAG) maneuver
- **Return**: Phobos departure, Earth return, capture at lunar Gateway station (no aeroshell needed)

Two instruments only: wide-angle camera and GRNS. Sample system is a harpoon fired during a TAG maneuver.

## What Is VVERDAD

VVERDAD (Vis Viva Engineering, Review, Design, and Architecture Database) is a data-oriented engineering design system. Agents building data for this test repo need to understand the following conventions.

### Data Files

Engineering data lives in plain text files: YAML, TOML, JSON, and CSV. Each file is loaded into an Entity-Component-System (ECS) data store keyed by its path in the directory tree. Templates and reports can then access any data by navigating the tree.

**Physical quantities** are expressed as strings with units and parsed automatically:

```yaml
thrust: "400 N"
specific_impulse: "321 s"
mass: "45.2 kg"
diameter: "1.6 m"
data_rate: "2.0 Mbps"
power: "850 W"
```

**Time epochs** are expressed as ISO 8601 strings with a timescale suffix and parsed automatically:

```yaml
launch_epoch: "2035-06-15T12:00:00 UTC"
arrival_epoch: "2036-01-20T00:00:00 UTC"
```

Both UTC and TDB timescales are supported. TDB is used for trajectory calculations; UTC for operations planning.

**No special tooling is required** to create these files. They are standard YAML, TOML, JSON, or CSV. VVERDAD's parser recognizes quantity strings and epoch strings at load time.

### Directory Structure

The repository is organized by subsystem. Each subsystem directory contains data files and optionally analysis bundles. An `_output/` directory (gitignored) mirrors the project structure and holds rendered templates and analysis results.

### Templates (Minijinja / Jinja2)

Template files end in `.j2` and are rendered with the full project data tree. They can access any data in the repo by path.

Available filters for templates:

- `{{ value | to("unit") }}` — convert quantity to specified unit (e.g., `{{ thrust | to("lbf") }}`)
- `{{ value | value("unit") }}` — extract numeric value in a unit
- `{{ value | unit }}` — extract unit symbol string
- `{{ value | si }}` — convert to SI base units
- `{{ epoch | to_utc }}` — convert to UTC string
- `{{ epoch | to_tdb }}` — convert to TDB string
- `{{ epoch | jd }}` — Julian Date
- `{{ epoch | mjd }}` — Modified Julian Date

Template data access uses the directory tree as the namespace. For example, if `propulsion/main_engine.yaml` contains `thrust: "400 N"`, a template accesses it as `{{ propulsion.main_engine.thrust }}`.

### Analysis Bundles

A directory with `.analysis` extension containing everything needed to run an analysis:

- `manifest.ron` — declares inputs, outputs, Docker image, entrypoint, resource limits
- Template files (`.j2`) — scripts and input files rendered with project data before execution
- Static files — copied as-is into the execution environment

Manifest structure (RON format):

```ron
Analysis(
    id: "analysis_name",
    version: "1.0.0",
    description: "What this analysis does",
    image: "python:3.11-slim",
    entrypoint: "script.py",
    inputs: [
        Input(key: "telecom.antenna.gain", required: true),
        Input(key: "telecom.transponder.power", required: true),
    ],
    outputs: [
        Output(key: "link_margin_summary.json"),
        Output(key: "link_margin_plot.png"),
    ],
    templates: [
        Template(source: "script.py.j2", destination: "script.py"),
    ],
    static_files: [],
    resources: Resources(
        cpu_cores: 1.0,
        memory_mb: 2048,
        timeout_seconds: 300,
    ),
)
```

Analysis outputs land in `_output/` in the parent directory of the `.analysis` bundle and are merged back into the data tree so downstream templates and analyses can reference them.

## Repository Structure

```
phobos-sample-return/
├── mission/
│   ├── overview.yaml                  # mission description, objectives, phases
│   ├── timeline.yaml                  # mission phase epochs and durations
│   ├── constraints.yaml               # launch vehicle, orbit constraints, C3
│   └── trajectory.analysis/           # Earth-Mars trajectory scan (Rust)
│       ├── manifest.ron
│       └── config.json.j2
├── spacecraft/
│   ├── bus.toml                       # bus dimensions, dry mass target, structure
│   └── mechanisms.toml                # deployables, separation systems
├── propulsion/
│   ├── main_engine.yaml               # biprop engine params
│   ├── rcs.yaml                       # monoprop RCS thrusters
│   └── delta_v_budget.yaml            # ΔV by mission phase with margins
├── power/
│   ├── solar_array.toml               # array config, cell type, efficiency
│   └── battery.toml                   # battery sizing
├── telecom/
│   ├── antenna.json                   # HGA/MGA/LGA parameters
│   ├── transponder.json               # radio parameters
│   ├── ground_station.json            # DSN antenna params, G/T
│   └── link_budget.analysis/          # Python link budget (agent-built)
│       ├── manifest.ron
│       ├── link_budget.py.j2
│       └── plot_margin.py.j2
├── cdh/
│   └── flight_computer.toml           # processor, memory, data bus
├── thermal/
│   └── thermal_summary.toml           # hot/cold case, heater power
├── adcs/
│   └── adcs.toml                      # sensors, actuators, pointing
├── payload/
│   ├── camera.json                    # WAC params
│   ├── grns.json                      # gamma-ray/neutron spec
│   └── sample_system.json             # harpoon + TAG params
├── systems/
│   ├── mass_budget.csv                # MEL: subsystem, CBE mass, margin %, MEV
│   ├── power_budget.csv               # power by subsystem per mode
│   ├── power_modes.yaml               # mode definitions and duty cycles
│   └── data_budget.yaml               # data volumes and downlink planning
├── reports/
│   ├── mission_summary.md.j2          # top-level mission summary report
│   ├── mass_budget_table.md.j2        # formatted MEL
│   ├── power_budget_table.md.j2       # power budget by mode
│   └── telecom_summary.md.j2          # link budget results + margin plot
└── _config/
    └── vverdad.ron                     # project-level config
```

### Format Assignments by Team

| Team | Format | Rationale |
|------|--------|-----------|
| Mission Design | YAML | Nested structures, epoch strings |
| Propulsion | YAML | Nested engine/thruster params |
| Power | TOML | Flat parameter tables |
| Telecom | JSON | Structured antenna/radio configs |
| C&DH | TOML | Flat config |
| Thermal | TOML | Flat hot/cold parameters |
| ADCS | TOML | Flat sensor/actuator list |
| Payload | JSON | Instrument parameter blocks |
| Systems Engineering | YAML + CSV | Budgets as CSV, modes as YAML |

## Agent Tasks

### 1. Mission Design Agent

**Skills**: `space-mission-design`, `basics-of-spaceflight`

**Delivers**:
- `mission/overview.yaml`
- `mission/timeline.yaml`
- `mission/constraints.yaml`
- `mission/trajectory.analysis/manifest.ron`
- `mission/trajectory.analysis/config.json.j2`

**Details**:

`overview.yaml` — Mission name, mission class (New Frontiers-class), science objectives (Phobos surface composition, sample return for laboratory analysis), mission phases list (launch, cruise, MOI, Phobos proximity ops, science mapping, TAG sample collection, Phobos departure, Earth return, Gateway rendezvous).

`timeline.yaml` — Epoch for each mission phase start/end. Use realistic dates for a ~2035 launch opportunity. Cruise ~7 months, Mars orbit ops ~18 months, return ~11 months. All epochs as UTC strings (e.g., `"2035-09-15T00:00:00 UTC"`). Include phase durations.

`constraints.yaml` — Launch vehicle class (e.g., Falcon Heavy expendable), maximum C3 (launch energy), Mars arrival V-infinity constraints, Phobos orbit parameters (semi-major axis ~9376 km, period ~7.66 hr), Gateway orbit parameters (NRHO). Keep it simple — these are the boundary conditions the trajectory analysis needs.

`trajectory.analysis/manifest.ron` — Declare inputs from `mission/constraints.yaml` and `mission/timeline.yaml`. Outputs: `trajectory_results.json` (optimal launch/arrival dates, C3, arrival V∞, ΔV breakdown) and `porkchop.csv` (grid of launch date × arrival date × C3 for plotting). Docker image for a Rust binary. Entrypoint is the compiled binary name.

`trajectory.analysis/config.json.j2` — Template that pulls launch window bounds, C3 limits, and target body parameters from the data tree and renders them into a JSON config file the Rust trajectory tool reads.

### 2. Propulsion Agent

**Skills**: `in-space-propulsion`, `basics-of-spaceflight`

**Delivers**:
- `propulsion/main_engine.yaml`
- `propulsion/rcs.yaml`
- `propulsion/delta_v_budget.yaml`

**Details**:

`main_engine.yaml` — Bipropellant engine parameters based on MMX heritage. Include: thrust, specific impulse, propellant combination (MMH/MON-3 or similar), mixture ratio, engine dry mass, number of engines. All quantities with units as strings.

`rcs.yaml` — Monopropellant (hydrazine) RCS thruster parameters. Include: thrust per thruster, Isp, number of thrusters, propellant type, thruster dry mass. These handle small maneuvers (trajectory correction, proximity ops, attitude control backup).

`delta_v_budget.yaml` — ΔV allocation by mission phase: Earth departure (C3-based, provided by launch vehicle), deep space maneuvers / TCMs, Mars orbit insertion, transfer to Phobos QSO, Phobos proximity ops and TAG, Phobos departure, Earth return, Gateway approach and rendezvous. Each entry: nominal ΔV, margin percentage, total (MEV). Include a mission total. Statistical ΔV (navigation, TCMs) separate from deterministic ΔV (MOI, departure). All values with unit strings.

### 3. Power Agent

**Skills**: `spacecraft-power`, `basics-of-spaceflight`

**Delivers**:
- `power/solar_array.toml`
- `power/battery.toml`

**Details**:

`solar_array.toml` — Solar array configuration for Mars distance (1.38–1.67 AU). Cell type (triple-junction GaAs or IMM), BOL efficiency, radiation degradation factor, array area, number of wings, sun incidence angle assumption, power output at 1 AU BOL, power output at Mars distance EOL. All quantities with unit strings.

`battery.toml` — Secondary battery for eclipse and peak power. Chemistry (Li-ion), capacity, depth of discharge limit, number of cells, bus voltage, mass. Eclipse duration at Mars for sizing context.

### 4. Telecom Agent

**Skills**: `spacecraft-telecom`, `basics-of-spaceflight`

**Delivers**:
- `telecom/antenna.json`
- `telecom/transponder.json`
- `telecom/ground_station.json`
- `telecom/link_budget.analysis/manifest.ron`
- `telecom/link_budget.analysis/link_budget.py.j2`
- `telecom/link_budget.analysis/plot_margin.py.j2`

**Details**:

`antenna.json` — HGA (parabolic, ~1.0 m, X-band, gain), MGA (medium gain, X-band), LGA (low gain, omnidirectional, for safe mode). For each: diameter or type, frequency band, gain, beamwidth, mass.

`transponder.json` — SDST-class deep space transponder. RF output power, receive sensitivity, data rates (selectable), modulation/coding scheme, mass, DC power consumption.

`ground_station.json` — DSN 34m BWG antenna parameters. System noise temperature, antenna gain at X-band, G/T. Keep simple — just the numbers the link budget calculation needs.

`link_budget.analysis/manifest.ron` — Inputs from `telecom/` data files plus `mission/trajectory.analysis` outputs (for Earth-Mars distance over time). Outputs: `link_margin_summary.json` and `link_margin_plot.png`.

`link_budget.analysis/link_budget.py.j2` — Minijinja template that renders into a Python script. The script computes downlink Eb/N0 margin as a function of Earth-spacecraft distance. Pull transmit power, antenna gains, frequency, required data rate, coding gain, system losses from the data tree via template variables. Compute free-space path loss across a range of distances (1.0–2.7 AU covers Earth-Mars range). Output a JSON with: minimum margin, distance at minimum margin, margin at key mission phases.

`link_budget.analysis/plot_margin.py.j2` — Template rendering a matplotlib script. Reads the link budget results JSON, plots margin (dB) vs distance (AU) or vs mission time. Horizontal line at 3 dB required margin. Save as PNG. This is a separate script from the link budget calculator (but runs in the same container — the entrypoint can be a wrapper or the manifest can list both).

**Note**: The link budget analysis depends on trajectory results (Earth-Mars distance profile). This tests VVERDAD's analysis chaining — trajectory analysis outputs get merged into the data tree, and the link budget templates can reference them. The manifest should declare the trajectory output as an input.

### 5. C&DH Agent

**Skills**: `spacecraft-cdh`, `basics-of-spaceflight`

**Delivers**:
- `cdh/flight_computer.toml`

**Details**:

`flight_computer.toml` — RAD750 or similar radiation-hardened processor. Clock speed, memory (SRAM, flash/MRAM for mass storage), data bus (MIL-STD-1553 and/or SpaceWire), solid-state recorder capacity, mass, power. One file is sufficient at CML-4.

### 6. Thermal Agent

**Skills**: `spacecraft-thermal`, `basics-of-spaceflight`

**Delivers**:
- `thermal/thermal_summary.toml`

**Details**:

`thermal_summary.toml` — Hot case and cold case summary. Hot case: near Mars perihelion, sun-facing, all electronics on. Cold case: eclipse or maximum Earth distance, minimum power. For each case: predicted temps for key components (battery, propellant tanks, electronics, payload). MLI coverage assumption, radiator area, heater power required (cold case). This is a summary table, not a full thermal model — CML-4 level.

### 7. ADCS Agent

**Skills**: `spacecraft-acs`, `basics-of-spaceflight`

**Delivers**:
- `adcs/adcs.toml`

**Details**:

`adcs.toml` — Attitude determination: star trackers (number, accuracy), sun sensors (number, type), IMU (type, drift rate). Attitude control: reaction wheels (number, momentum capacity, torque, mass each), RCS thrusters (reference propulsion RCS data). Pointing requirements: science mode (camera/GRNS), telecom mode (HGA Earth-pointing), TAG mode. Pointing accuracy and knowledge numbers for each mode. Safe mode attitude (sun-pointing, LGA).

### 8. Payload Agent

**Skills**: `phobos-payload`, `basics-of-spaceflight`

**Delivers**:
- `payload/camera.json`
- `payload/grns.json`
- `payload/sample_system.json`

**Details**:

`camera.json` — Wide-angle camera for Phobos surface imaging. FOV, IFOV, detector size (pixels), spectral bands, data rate per image, mass, power, operating temperature range. Based on MMX TENGOO/OROCHI heritage but simplified to one camera.

`grns.json` — Gamma-ray and neutron spectrometer for surface composition. Detector types (scintillator for gamma, He-3 or Li-glass for neutrons), energy range, FOV, integration time for usable signal at Phobos QSO altitude, data rate, mass, power.

`sample_system.json` — Harpoon-based touch-and-go sampling. Harpoon penetration depth target, sample mass target, TAG contact duration, mechanism mass (harpoon + actuator + sample container), power (deployment), number of sample attempts, sample container return capsule mass. This is the mechanism that collects and stores the sample for return.

### 9. Spacecraft / Structures Agent

**Skills**: `spacecraft-structures`, `basics-of-spaceflight`

**Delivers**:
- `spacecraft/bus.toml`
- `spacecraft/mechanisms.toml`

**Details**:

`bus.toml` — Bus configuration (box-type, similar to MMX). Dimensions, structural mass estimate, primary structure material (aluminum honeycomb), launch adapter type (e.g., 937mm or 1194mm), design load factors (quasi-static), structural mass fraction target.

`mechanisms.toml` — Solar array deployment (2-wing), HGA gimbal (2-axis), sample container transfer mechanism, launch restraints. For each: type, mass, power (deployment), heritage. Keep brief — CML-4 doesn't need detailed mechanism design.

### 10. Systems Engineering Agent

**Skills**: `nasa-systems-engineering`, `basics-of-spaceflight`

**Delivers**:
- `systems/mass_budget.csv`
- `systems/power_budget.csv`
- `systems/power_modes.yaml`
- `systems/data_budget.yaml`

**Details**:

`mass_budget.csv` — Master Equipment List in CSV. Columns: subsystem, component, CBE_mass_kg, margin_percent, MEV_mass_kg. Rows for every subsystem (structures, thermal, propulsion dry, power, telecom, C&DH, ADCS, payload, sample system, harness). Subtotals for dry mass, propellant mass, wet mass. The CBE values should be consistent with (or derived from) the subsystem data files. Include a system-level margin line (typically 30% at CML-4 for non-heritage items).

`power_budget.csv` — Power consumption by subsystem for each power mode. Columns: subsystem, component, cruise_W, science_W, comms_W, tag_W, safe_W. This is essentially the power mode matrix. Values should be consistent with subsystem files.

`power_modes.yaml` — Definition of each power mode (cruise, science_mapping, communications, TAG_maneuver, safe_mode). For each mode: description, which subsystems are active, duty cycle if applicable, duration per orbit or per day. This is the key that explains what the power budget columns mean.

`data_budget.yaml` — Data generation rates by instrument and mode, onboard storage requirement, downlink strategy (how many hours of DSN contact per day, data rate, daily data volume returned). Simple accounting showing the data budget closes.

### 11. Reports Agent

**Skills**: (needs VVERDAD template syntax — described in this document)

**Delivers**:
- `reports/mission_summary.md.j2`
- `reports/mass_budget_table.md.j2`
- `reports/power_budget_table.md.j2`
- `reports/telecom_summary.md.j2`

**Details**:

All report templates are Minijinja templates that render to Markdown.

`mission_summary.md.j2` — Top-level mission summary. Pulls mission name and objectives from `mission/overview`, launch date and timeline from `mission/timeline`, key spacecraft parameters from subsystem files (total mass, power, ΔV), instrument list from `payload/`. Should demonstrate accessing data across the full tree. Use `{{ epoch | to_utc }}` for dates and `{{ mass | to("kg") }}` for quantities where appropriate.

`mass_budget_table.md.j2` — Renders `systems/mass_budget.csv` as a formatted Markdown table. Demonstrates accessing CSV/table data in templates.

`power_budget_table.md.j2` — Renders `systems/power_budget.csv` as a formatted Markdown table with power mode columns. Can reference mode descriptions from `systems/power_modes`.

`telecom_summary.md.j2` — Summarizes telecom configuration from `telecom/` data files and references link budget analysis outputs (margin summary JSON, embeds the margin plot PNG). Demonstrates referencing analysis outputs in report templates.

## Agent Execution Order

The agents are mostly independent, but there are two ordering constraints:

1. **Mission Design** should run first (or early) because the trajectory analysis defines the mission timeline, ΔV requirements, and distance profile that other subsystems reference.
2. **Systems Engineering** should run last because it integrates mass/power/data from all subsystems.
3. **Reports** should run last because templates reference the full data tree.
4. All other agents (Propulsion, Power, Telecom, C&DH, Thermal, ADCS, Payload, Spacecraft) can run in parallel.

Practical ordering:

```
Phase 1 (parallel): Mission Design, Propulsion, Power, Telecom, C&DH,
                     Thermal, ADCS, Payload, Spacecraft/Structures
Phase 2 (after Phase 1): Systems Engineering
Phase 3 (after Phase 2): Reports
```

If full parallelism isn't possible, any serial order works so long as Systems Engineering and Reports come last.

## VVERDAD Features Exercised

| Feature | Where Tested |
|---------|-------------|
| YAML parsing | mission/, propulsion/, systems/power_modes |
| TOML parsing | power/, cdh/, thermal/, adcs/, spacecraft/ |
| JSON parsing | telecom/, payload/ |
| CSV parsing | systems/mass_budget.csv, systems/power_budget.csv |
| Quantity strings | Every subsystem data file |
| Epoch strings | mission/timeline.yaml |
| Unit conversion filters | Report templates (`\|to`, `\|value`, `\|unit`, `\|si`) |
| Time filters | Report templates (`\|to_utc`, `\|to_tdb`, `\|jd`) |
| Analysis bundle structure | trajectory.analysis/, link_budget.analysis/ |
| Manifest.ron | Both analysis bundles |
| Template rendering (.j2) | Analysis input templates + report templates |
| Docker execution | Rust container (trajectory), Python container (link budget) |
| Output merging | Trajectory outputs used by link budget templates |
| Analysis chaining | Link budget depends on trajectory distance profile |
| Cross-subsystem data access | Reports pull from all directories |
| Directory mirroring | `_output/` mirrors full project tree |

## Notes

- This is CML-4: a self-consistent point design, not a detailed design. One or two pages of data per subsystem is appropriate. Don't over-specify.
- Physical quantities MUST include units as strings (e.g., `"400 N"` not `400`). This is how VVERDAD knows it's a quantity.
- Time epochs MUST include the timescale suffix (e.g., `"2035-06-15T12:00:00 UTC"`).
- Each team uses their assigned data format. Don't mix formats within a team's deliverables (except Systems Engineering which uses both CSV and YAML).
- Values across subsystems need to be roughly consistent (e.g., power draws in subsystem files should approximately match the power budget) but don't need to be exact — that's what the integration process is for.
- Margin conventions: 30% on mass for new designs, 5-10% on heritage. Power margins per NASA/AIAA standards for the appropriate mission phase.
