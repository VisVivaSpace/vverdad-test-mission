"""
Link Budget Analysis — Phobos Sample Return X-band Downlink
Computes Eb/N0 margin as a function of Earth-spacecraft distance (1.0–2.7 AU).
Generated from link_budget.py.j2 by VVERDAD template engine.
"""

import json
import math

# ---------------------------------------------------------------------------
# Parameters pulled from the VVERDAD data tree
# ---------------------------------------------------------------------------

# Transmitter
tx_power_w = 25.0
tx_power_dbw = 10.0 * math.log10(tx_power_w)

# Spacecraft antenna gains (strings with dBi — parse the numeric part)
hga_gain_dbi = float("39.7 dBi".split()[0])
mga_gain_dbi = float("15.0 dBi".split()[0])
lga_gain_dbi = float("8.0 dBi".split()[0])

# Downlink frequency
downlink_freq_ghz = float("8.425 GHz".split()[0])
downlink_freq_hz = downlink_freq_ghz * 1.0e9
wavelength_m = 2.998e8 / downlink_freq_hz

# Coding and modulation
required_eb_n0_db = float("1.0 dB".split()[0])

# Ground station
gs_gain_dbi = float("68.2 dBi".split()[0])
sys_noise_temp_k = 20.0
gs_g_over_t_db = gs_gain_dbi - 10.0 * math.log10(sys_noise_temp_k)

# System losses (conservative estimates)
tx_circuit_loss_db = 2.0       # waveguide, switches, cabling
pointing_loss_db = 0.5         # HGA pointing error budget
atmospheric_loss_db = 0.3      # clear sky, 20 deg elevation, X-band
polarization_loss_db = 0.1     # circular-to-circular mismatch
implementation_loss_db = 1.0   # modem implementation loss

total_losses_db = (tx_circuit_loss_db + pointing_loss_db +
                   atmospheric_loss_db + polarization_loss_db +
                   implementation_loss_db)

# Data rate for margin computation (nominal high-rate science)
nominal_data_rate_bps = 100.0e3   # 100 kbps nominal science downlink
data_rate_db_hz = 10.0 * math.log10(nominal_data_rate_bps)

# Required margin
required_margin_db = 3.0

# Boltzmann constant factor: 10*log10(1/k) = 228.6 dB
boltzmann_factor = 228.6

# ---------------------------------------------------------------------------
# Distance sweep
# ---------------------------------------------------------------------------

AU_M = 1.496e11  # meters per AU

distances_au = [round(0.5 + i * 0.01, 2) for i in range(251)]  # 0.5 to 3.0 AU

results = []

for d_au in distances_au:
    d_m = d_au * AU_M

    # Free-space path loss
    fspl_db = 20.0 * math.log10(4.0 * math.pi * d_m / wavelength_m)

    # EIRP (dBW)
    eirp_dbw = tx_power_dbw + hga_gain_dbi - tx_circuit_loss_db - pointing_loss_db

    # Received C/N0 (dB-Hz)
    c_n0 = (eirp_dbw + gs_g_over_t_db - fspl_db
            - atmospheric_loss_db - polarization_loss_db
            - implementation_loss_db + boltzmann_factor)

    # Eb/N0 achieved
    eb_n0 = c_n0 - data_rate_db_hz

    # Link margin
    margin_db = eb_n0 - required_eb_n0_db

    results.append({
        "distance_au": d_au,
        "fspl_db": round(fspl_db, 2),
        "eirp_dbw": round(eirp_dbw, 2),
        "c_n0_db_hz": round(c_n0, 2),
        "eb_n0_db": round(eb_n0, 2),
        "margin_db": round(margin_db, 2),
    })

# ---------------------------------------------------------------------------
# Key distance extractions
# ---------------------------------------------------------------------------

def margin_at_distance(target_au):
    closest = min(results, key=lambda r: abs(r["distance_au"] - target_au))
    return closest

min_margin_entry = min(results, key=lambda r: r["margin_db"])

key_distances = {
    "closest_approach_1_0_au": margin_at_distance(1.0),
    "nominal_ops_1_5_au": margin_at_distance(1.5),
    "far_range_2_0_au": margin_at_distance(2.0),
    "maximum_range_2_7_au": margin_at_distance(2.7),
}

summary = {
    "description": "X-band HGA downlink margin vs distance at 100 kbps",
    "parameters": {
        "tx_power_dbw": round(tx_power_dbw, 2),
        "hga_gain_dbi": hga_gain_dbi,
        "gs_g_over_t_db": round(gs_g_over_t_db, 2),
        "downlink_freq_ghz": downlink_freq_ghz,
        "nominal_data_rate_bps": nominal_data_rate_bps,
        "required_eb_n0_db": required_eb_n0_db,
        "total_losses_db": round(total_losses_db, 2),
        "required_margin_db": required_margin_db,
    },
    "minimum_margin": {
        "margin_db": min_margin_entry["margin_db"],
        "distance_au": min_margin_entry["distance_au"],
    },
    "key_distances": key_distances,
    "distance_sweep": results,
}

with open("link_margin_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"Link budget complete. Min margin: {min_margin_entry['margin_db']:.1f} dB "
      f"at {min_margin_entry['distance_au']:.2f} AU")