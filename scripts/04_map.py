#!/usr/bin/env python3
"""
Static equivalent of the 'Build an Interactive Map with Folium' lab.

The sandbox this session runs in cannot install new pip packages (folium
included) and has no network access to map tile servers, so a genuinely
interactive Folium map isn't possible here. This script produces three
static, real-data-driven map images that cover the same three requirements
as the original lab:
  1. All launch site locations on a world map
  2. Launch outcomes color-coded on the map (site-level, jittered to
     approximate the visual effect of Folium's MarkerCluster on overlapping
     points)
  3. Proximity of a selected site to nearby geographic features (coastline,
     highway, railway), with distances computed via the haversine formula
"""
import json
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

IMG = "/home/claude/spacex_capstone/images"
df = pd.read_csv("/home/claude/spacex_capstone/data/spacex_launches.csv")
df["OutcomeLabel"] = df["LandingSuccess"].map({1.0: "Success", 0.0: "Failure"}).fillna("No attempt")

with open("/tmp/world.geojson") as f:
    world = json.load(f)


def add_world_basemap(ax, extent=None):
    patches = []
    for feat in world["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ring = poly[0]
            patches.append(MplPolygon(ring, closed=True))
    pc = PatchCollection(patches, facecolor="#dfe6e9", edgecolor="#95a5a6", linewidths=0.4, zorder=1)
    ax.add_collection(pc)
    if extent:
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
    else:
        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 85)
    ax.set_facecolor("#aed6f1")
    ax.set_xlabel("Longitudine")
    ax.set_ylabel("Latitudine")


sites = df.drop_duplicates("LaunchSite")[["LaunchSite", "Lat", "Long"]]

# --- Screenshot 1: world map with all launch site markers -------------
fig, ax = plt.subplots(figsize=(11, 6))
add_world_basemap(ax, extent=(-130, -60, 15, 45))
# CCAFS SLC-40 and KSC LC-39A are only ~5 km apart, so on a world-scale map
# their labels would overlap; offset them to opposite sides of the shared marker.
label_offsets = {
    "CCAFS SLC-40": (10, -16),
    "KSC LC-39A": (10, 10),
    "VAFB SLC-4E": (10, 8),
}
for _, row in sites.iterrows():
    ax.scatter(row["Long"], row["Lat"], s=180, color="#C0392B", edgecolor="white",
               linewidth=1.5, zorder=3)
    dx, dy = label_offsets.get(row["LaunchSite"], (8, 8))
    ax.annotate(row["LaunchSite"], (row["Long"], row["Lat"]), xytext=(dx, dy),
                textcoords="offset points", fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))
ax.set_title("Siti di lancio Falcon 9 (Screenshot mappa 1)")
plt.tight_layout()
plt.savefig(f"{IMG}/07_map_launch_sites.png", dpi=150)
plt.close()
print("salvato 07_map_launch_sites.png")

# --- Screenshot 2: outcomes color-coded, jittered around each site -----
rng = np.random.default_rng(42)
colors = {"Success": "#2E7D32", "Failure": "#C62828", "No attempt": "#7f8c8d"}
fig, ax = plt.subplots(figsize=(11, 6))
add_world_basemap(ax, extent=(-125, -78, 26, 37))
for outcome, color in colors.items():
    sub = df[df["OutcomeLabel"] == outcome]
    jitter_lat = sub["Lat"] + rng.normal(0, 0.12, len(sub))
    jitter_long = sub["Long"] + rng.normal(0, 0.12, len(sub))
    ax.scatter(jitter_long, jitter_lat, s=14, alpha=0.65, color=color, label=f"{outcome} (n={len(sub)})")
for _, row in sites.iterrows():
    ax.scatter(row["Long"], row["Lat"], s=60, marker="*", color="black", zorder=5)
ax.legend(title="Esito atterraggio", loc="upper left")
ax.set_title("Esiti di atterraggio per sito, colorati (Screenshot mappa 2)\n"
             "(punti dispersi casualmente attorno al sito reale, come in un MarkerCluster, per visibilita')")
plt.tight_layout()
plt.savefig(f"{IMG}/08_map_outcomes_colored.png", dpi=150)
plt.close()
print("salvato 08_map_outcomes_colored.png")


# --- Screenshot 3: proximity analysis for CCAFS SLC-40 -----------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


site_lat, site_lon = 28.5623, -80.5774  # CCAFS SLC-40
landmarks = {
    "Costa atlantica": (28.5721, -80.5674),
    "Autostrada (SR-401)": (28.5449, -80.5814),
    "Ferrovia (Florida East Coast Railway)": (28.5567, -80.6083),
    "Citta' piu' vicina (Cape Canaveral, FL)": (28.4058, -80.6048),
}

fig, ax = plt.subplots(figsize=(9, 7))
ax.scatter(site_lon, site_lat, s=250, color="#C0392B", marker="*", zorder=5, label="CCAFS SLC-40")
for name, (lat, lon) in landmarks.items():
    d = haversine_km(site_lat, site_lon, lat, lon)
    ax.scatter(lon, lat, s=90, color="#1565C0", zorder=4)
    ax.plot([site_lon, lon], [site_lat, lat], linestyle="--", color="#1565C0", linewidth=1, zorder=3)
    mid_lon, mid_lat = (site_lon + lon) / 2, (site_lat + lat) / 2
    ax.annotate(f"{name}\n{d:.2f} km", (mid_lon, mid_lat), fontsize=8.5,
                ha="center", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#1565C0", alpha=0.9))
ax.set_xlim(-80.68, -80.45)
ax.set_ylim(28.35, 28.63)
ax.set_title("Analisi di prossimita' - CCAFS SLC-40 (Screenshot mappa 3)\n"
             "Distanze approssimate calcolate con formula dell'emisenoverso (haversine) da coordinate note")
ax.set_xlabel("Longitudine")
ax.set_ylabel("Latitudine")
ax.legend(loc="lower left")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{IMG}/09_map_proximity.png", dpi=150)
plt.close()
print("salvato 09_map_proximity.png")
