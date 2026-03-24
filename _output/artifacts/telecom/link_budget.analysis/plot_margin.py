"""
Link Margin Plot — Phobos Sample Return X-band Downlink
Reads link_margin_summary.json and generates margin-vs-distance plot.
Generated from plot_margin.py.j2 by VVERDAD template engine.
"""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Load results
# ---------------------------------------------------------------------------

with open("link_margin_summary.json", "r") as f:
    data = json.load(f)

sweep = data["distance_sweep"]
params = data["parameters"]
required_margin = params["required_margin_db"]

distances = [pt["distance_au"] for pt in sweep]
margins = [pt["margin_db"] for pt in sweep]

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(distances, margins, "b-", linewidth=2, label="HGA downlink margin (100 kbps)")
ax.axhline(y=required_margin, color="r", linestyle="--", linewidth=1.5,
           label=f"Required margin ({required_margin:.0f} dB)")
ax.axhline(y=0, color="k", linestyle="-", linewidth=0.5, alpha=0.3)

# Mark key distances
key = data["key_distances"]
for label, entry in key.items():
    d = entry["distance_au"]
    m = entry["margin_db"]
    ax.plot(d, m, "ko", markersize=6)
    ax.annotate(f"{m:.1f} dB\n({d:.1f} AU)",
                xy=(d, m), xytext=(0, 12),
                textcoords="offset points", ha="center", fontsize=8,
                bbox=dict(boxstyle="round,pad=0.2", fc="lightyellow", ec="gray", alpha=0.8))

# Shade the operational distance range
ax.axvspan(1.0, 2.7, alpha=0.08, color="blue", label="Operational range (1.0-2.7 AU)")

ax.set_xlabel("Earth-Spacecraft Distance (AU)", fontsize=12)
ax.set_ylabel("Link Margin (dB)", fontsize=12)
ax.set_title("Phobos Sample Return — X-band HGA Downlink Margin vs Distance\n"
             f"TX {params['tx_power_dbw']:.1f} dBW | HGA {params['hga_gain_dbi']:.1f} dBi | "
             f"DSN 34m BWG | {params['nominal_data_rate_bps']/1e3:.0f} kbps | "
             f"Turbo 1/2",
             fontsize=11)
ax.legend(loc="upper right", fontsize=10)
ax.set_xlim(0.5, 3.0)
ax.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig("link_margin_plot.png", dpi=150)
plt.close(fig)

print("Saved link_margin_plot.png")