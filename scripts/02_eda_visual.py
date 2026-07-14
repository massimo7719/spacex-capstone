#!/usr/bin/env python3
"""EDA with data visualization - generates the 6 charts requested by the
capstone template (slides 18-23)."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_style("whitegrid")
PALETTE = {"Success": "#2E7D32", "Failure": "#C62828"}

df = pd.read_csv("/home/claude/spacex_capstone/data/spacex_launches.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year
df["OutcomeLabel"] = df["LandingSuccess"].map({1.0: "Success", 0.0: "Failure"})

IMG = "/home/claude/spacex_capstone/images"


def savefig(name):
    plt.tight_layout()
    plt.savefig(f"{IMG}/{name}", dpi=150)
    plt.close()
    print(f"salvato {name}")


# 1. Flight Number vs Launch Site --------------------------------------
plt.figure(figsize=(9, 5.5))
sns.scatterplot(data=df, x="FlightNumber", y="LaunchSite", hue="OutcomeLabel",
                 palette=PALETTE, s=45, alpha=0.8)
plt.title("Flight Number vs. Launch Site (colorato per esito atterraggio)")
plt.xlabel("Flight Number")
plt.ylabel("Launch Site")
plt.legend(title="Esito atterraggio")
savefig("01_flightnumber_vs_site.png")

# 2. Payload vs Launch Site ---------------------------------------------
plt.figure(figsize=(9, 5.5))
sns.scatterplot(data=df, x="PayloadMass", y="LaunchSite", hue="OutcomeLabel",
                 palette=PALETTE, s=45, alpha=0.8)
plt.title("Payload Mass vs. Launch Site (colorato per esito atterraggio)")
plt.xlabel("Payload Mass (kg)")
plt.ylabel("Launch Site")
plt.legend(title="Esito atterraggio")
savefig("02_payload_vs_site.png")

# 3. Success rate by orbit type ------------------------------------------
# Restrict to orbits with a statistically meaningful sample (10+ launches);
# rare orbits (n=1-3) would otherwise show a misleading 100%/0% bar.
orbit_counts = df.dropna(subset=["LandingSuccess"]).groupby("Orbit")["LandingSuccess"].count()
common_orbits = orbit_counts[orbit_counts >= 10].index
orbit_success = (df.dropna(subset=["LandingSuccess"])
                 .loc[lambda d: d["Orbit"].isin(common_orbits)]
                 .groupby("Orbit")["LandingSuccess"].mean().sort_values(ascending=False))
plt.figure(figsize=(9, 5.5))
bars = plt.bar(orbit_success.index, orbit_success.values, color="#1565C0")
plt.title("Tasso di successo atterraggio per tipo di orbita (orbite con 10+ lanci)")
plt.xlabel("Orbit")
plt.ylabel("Tasso di successo")
plt.xticks(rotation=45, ha="right")
plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
savefig("03_success_rate_by_orbit.png")

# 4. Flight Number vs Orbit type ------------------------------------------
plt.figure(figsize=(9, 5.5))
sns.scatterplot(data=df, x="FlightNumber", y="Orbit", hue="OutcomeLabel",
                 palette=PALETTE, s=45, alpha=0.8)
plt.title("Flight Number vs. Orbit Type (colorato per esito atterraggio)")
plt.xlabel("Flight Number")
plt.ylabel("Orbit")
plt.legend(title="Esito atterraggio")
savefig("04_flightnumber_vs_orbit.png")

# 5. Payload vs Orbit type -------------------------------------------------
plt.figure(figsize=(9, 5.5))
sns.scatterplot(data=df, x="PayloadMass", y="Orbit", hue="OutcomeLabel",
                 palette=PALETTE, s=45, alpha=0.8)
plt.title("Payload Mass vs. Orbit Type (colorato per esito atterraggio)")
plt.xlabel("Payload Mass (kg)")
plt.ylabel("Orbit")
plt.legend(title="Esito atterraggio")
savefig("05_payload_vs_orbit.png")

# 6. Launch success yearly trend -------------------------------------------
yearly = df.dropna(subset=["LandingSuccess"]).groupby("Year")["LandingSuccess"].mean()
plt.figure(figsize=(9, 5.5))
plt.plot(yearly.index, yearly.values, marker="o", color="#1565C0", linewidth=2)
plt.title("Tasso di successo medio di atterraggio per anno")
plt.xlabel("Anno")
plt.ylabel("Tasso di successo medio")
plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
plt.xticks(yearly.index, rotation=45)
savefig("06_yearly_success_trend.png")

print("Tutti i 6 grafici EDA generati.")
