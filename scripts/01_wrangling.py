#!/usr/bin/env python3
"""
Data collection (web scraping) + data wrangling for the SpaceX Falcon 9
capstone project.

Source: Wikipedia "List of Falcon 9 and Falcon Heavy launches" page,
fetched live on 2026-07-14 (saved locally as /tmp/wiki_falcon9.html).

NOTE ON THE SPACEX REST API: the classic version of this lab also pulls
data from api.spacexdata.com. That host returned a persistent Cloudflare
525 error from this sandboxed environment (its own network egress is
locked down to an allowlist, and the SpaceX API's edge appears to reject
the sandbox's requests) even though the API's own public status page
reports it as fully operational. The API-calling code is preserved in
notebook 01 for reference/completeness, but the dataset used for the rest
of this project comes from the Wikipedia scrape below, which was reachable
and gave complete, current data.
"""
import re
import json
import pandas as pd
import numpy as np

WIKI_SOURCES = [
    "/tmp/wiki_falcon9_2010_2019.html",
    "/tmp/wiki_falcon9_2020_2022.html",
    "/tmp/wiki_falcon9_2023.html",
    "/tmp/wiki_falcon9_2024.html",
    "/tmp/wiki_falcon9.html",  # main page: 2025-2026 (+ upcoming manifest, filtered out later)
]
OUT_CSV = "/home/claude/spacex_capstone/data/spacex_launches.csv"

VALID_SITES = ["Cape Canaveral", "Kennedy", "Vandenberg"]


def is_real_row(row):
    site = str(row["Launch site"])
    return any(site.startswith(v) for v in VALID_SITES)


def parse_payload_mass(x):
    if pd.isna(x):
        return np.nan
    s = str(x)
    s = s.replace("~", "")
    m = re.search(r"([\d,]+)\s*kg", s)
    if m:
        return float(m.group(1).replace(",", ""))
    return np.nan


def parse_date(x):
    s = str(x)
    s = re.sub(r"\[\d+\]", "", s)  # strip footnote refs like [251]
    s = s.strip()
    try:
        return pd.to_datetime(s, errors="coerce", utc=False)
    except Exception:
        return pd.NaT


def parse_booster_landing(x):
    """Returns (landing_class, landing_type) e.g. (1, 'drone ship') or (0, 'ground pad')."""
    if pd.isna(x):
        return np.nan, np.nan
    s = str(x)
    s_low = s.lower()
    if "no attempt" in s_low or s.strip() in ("", "—", "-", "N/A"):
        return np.nan, "No attempt"
    success = 1 if s_low.startswith("success") else 0
    s_norm = s_low.replace("‑", "-").replace("–", "-")  # normalize non-breaking/en dashes
    landing_type = np.nan
    drone_ship_names = ("drone ship", "asog", "jrti", "ocisly", "octagrabber", "just read",
                         "of course i still love you", "a shortfall of gravitas")
    ground_pad_names = ("ground pad", "lz-1", "lz-2", "lz-4", "landing zone")
    if any(k in s_norm for k in drone_ship_names):
        landing_type = "Drone ship"
    elif any(k in s_norm for k in ground_pad_names):
        landing_type = "Ground pad"
    elif "ocean" in s_norm:
        landing_type = "Ocean"
    elif "parachute" in s_norm:
        landing_type = "Parachute"
    else:
        landing_type = "Other"
    return success, landing_type


def strip_footnotes(x):
    if pd.isna(x):
        return x
    s = str(x)
    s = re.sub(r"\[\d+\]", "", s)  # strip [123] footnote refs
    return s.strip()


def clean_site(x):
    s = str(x).strip()
    if s.startswith("Cape Canaveral"):
        return "CCAFS SLC-40"
    if s.startswith("Kennedy"):
        return "KSC LC-39A"
    if s.startswith("Vandenberg"):
        return "VAFB SLC-4E"
    return s


def main():
    canonical = ["Flight No.", "Date and time (UTC)", "Version, booster[j]", "Launch site",
                 "Payload[k]", "Payload mass", "Orbit", "Customer", "Launch outcome", "Booster landing"]

    frames = []
    for src in WIKI_SOURCES:
        tables = pd.read_html(src)
        for t in tables:
            cols = list(t.columns)
            # Match tables with the same *shape* of launch-record header regardless
            # of the exact wiki footnote markers (e.g. "Version, booster[a]" vs "[j]").
            if (len(cols) >= 10 and cols[0] == "Flight No." and cols[1] == "Date and time (UTC)"
                    and str(cols[8]) == "Launch outcome" and str(cols[9]) == "Booster landing"):
                sub = t.iloc[:, :10].copy()
                sub.columns = canonical
                frames.append(sub)
        print(f"  {src}: {len(frames)} tabelle valide finora (cumulativo)")

    past = pd.concat(frames, ignore_index=True, sort=False)
    past = past[past.apply(is_real_row, axis=1)].copy()

    # Keep Falcon 9 only (exclude Falcon Heavy triple-core missions) to match
    # the classic "Falcon 9 first stage landing prediction" capstone scope.
    past = past[past["Version, booster[j]"].astype(str).str.startswith("F9")].copy()

    df = pd.DataFrame()
    df["FlightNumber"] = pd.to_numeric(past["Flight No."], errors="coerce")
    df["Date"] = past["Date and time (UTC)"].apply(parse_date)
    df["BoosterVersion"] = (past["Version, booster[j]"].apply(strip_footnotes)
                             .str.replace("‑", "-", regex=False))
    df["LaunchSite"] = past["Launch site"].apply(clean_site)
    df["Payload"] = past["Payload[k]"].apply(strip_footnotes)
    df["PayloadMass"] = past["Payload mass"].apply(parse_payload_mass)
    df["Orbit"] = past["Orbit"].apply(strip_footnotes)
    df["Customer"] = past["Customer"].apply(strip_footnotes)
    df["LaunchOutcome"] = past["Launch outcome"].apply(strip_footnotes)
    df["LaunchOutcome"] = df["LaunchOutcome"].replace({
        "Successful simulated failure": "Success",  # CASSIOPE (flight 8): mission success,
                                                       # intentional 1st-stage soft ocean landing test
    })

    landing = past["Booster landing"].apply(parse_booster_landing)
    df["LandingSuccess"] = [t[0] for t in landing]
    df["LandingType"] = [t[1] for t in landing]

    # Drop rows with no usable flight number (residual notes rows) and dedupe
    df = df.dropna(subset=["FlightNumber"]).copy()
    df["FlightNumber"] = df["FlightNumber"].astype(int)
    df = df.drop_duplicates(subset=["FlightNumber", "Date"]).sort_values("FlightNumber").reset_index(drop=True)

    # Site coordinates (public, well-known launch complex coordinates)
    site_coords = {
        "CCAFS SLC-40": (28.5623, -80.5774),
        "KSC LC-39A": (28.6080, -80.6041),
        "VAFB SLC-4E": (34.6321, -120.6108),
    }
    df["Lat"] = df["LaunchSite"].map(lambda s: site_coords.get(s, (np.nan, np.nan))[0])
    df["Long"] = df["LaunchSite"].map(lambda s: site_coords.get(s, (np.nan, np.nan))[1])

    df.to_csv(OUT_CSV, index=False)

    print(f"Righe totali dopo pulizia: {len(df)}")
    print(f"Intervallo date: {df['Date'].min()} -> {df['Date'].max()}")
    print(f"Intervallo flight number: {df['FlightNumber'].min()} -> {df['FlightNumber'].max()}")
    print("Conteggio per sito:")
    print(df["LaunchSite"].value_counts())
    print("Valori mancanti per colonna:")
    print(df.isna().sum())
    print(f"\nSalvato in: {OUT_CSV}")


if __name__ == "__main__":
    main()
