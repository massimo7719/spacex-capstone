#!/usr/bin/env python3
"""
Static equivalent of the 'Build a Dashboard with Plotly Dash' lab.

plotly/dash could not be installed in this sandbox (no package-index
access), so this reproduces the same 3 required dashboard views as static
matplotlib figures instead of a live interactive app: pie chart of launch
success by site, pie chart for the best-performing site, and payload vs.
outcome scatter shown as small multiples across payload ranges (in place
of an interactive range slider).
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IMG = "/home/claude/spacex_capstone/images"
df = pd.read_csv("/home/claude/spacex_capstone/data/spacex_launches.csv")
df["OutcomeLabel"] = df["LandingSuccess"].map({1.0: "Success", 0.0: "Failure"})
dfl = df.dropna(subset=["LandingSuccess"]).copy()

# --- Screenshot 1: success count share by site (pie) --------------------
site_success_counts = dfl[dfl["LandingSuccess"] == 1]["LaunchSite"].value_counts()
plt.figure(figsize=(7, 7))
plt.pie(site_success_counts.values, labels=site_success_counts.index, autopct="%1.1f%%",
        colors=["#1565C0", "#2E7D32", "#F9A825"], startangle=90)
plt.title("Quota di atterraggi riusciti per sito di lancio")
plt.tight_layout()
plt.savefig(f"{IMG}/10_dash_success_by_site.png", dpi=150)
plt.close()
print("salvato 10_dash_success_by_site.png")

# --- Screenshot 2: pie for the site with the highest success ratio -------
site_rate = dfl.groupby("LaunchSite")["LandingSuccess"].mean()
best_site = site_rate.idxmax()
best = dfl[dfl["LaunchSite"] == best_site]
counts = best["OutcomeLabel"].value_counts()
plt.figure(figsize=(7, 7))
plt.pie(counts.values, labels=counts.index, autopct="%1.1f%%",
        colors=["#2E7D32", "#C62828"], startangle=90)
plt.title(f"Esiti di atterraggio - {best_site} (miglior rateo di successo: {site_rate.max():.1%})")
plt.tight_layout()
plt.savefig(f"{IMG}/11_dash_best_site_pie.png", dpi=150)
plt.close()
print(f"salvato 11_dash_best_site_pie.png (best site: {best_site})")

# --- Screenshot 3: payload vs outcome, small multiples by payload range --
ranges = [(0, 5000), (5000, 10000), (10000, 20000)]
fig, axes = plt.subplots(1, len(ranges), figsize=(15, 5), sharey=True)
colors = {"Success": "#2E7D32", "Failure": "#C62828"}
for ax, (lo, hi) in zip(axes, ranges):
    sub = dfl[(dfl["PayloadMass"] >= lo) & (dfl["PayloadMass"] < hi)]
    for label, color in colors.items():
        s = sub[sub["OutcomeLabel"] == label]
        ax.scatter(s["PayloadMass"], s["LaunchSite"], color=color, s=30, alpha=0.7, label=label)
    ax.set_title(f"Payload {lo}-{hi} kg (n={len(sub)})")
    ax.set_xlabel("Payload Mass (kg)")
    ax.grid(alpha=0.3)
axes[0].set_ylabel("Launch Site")
axes[0].legend(title="Esito")
fig.suptitle("Payload vs. Launch Outcome per fascia di payload\n"
             "(pannelli multipli al posto del range-slider interattivo)")
plt.tight_layout()
plt.savefig(f"{IMG}/12_dash_payload_vs_outcome.png", dpi=150)
plt.close()
print("salvato 12_dash_payload_vs_outcome.png")
