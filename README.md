# SpaceX Falcon 9 Capstone - spacex-capstone

Data science capstone project (IBM/Coursera template): predicting Falcon 9
first-stage landing success from real launch history data.

Repository: https://github.com/massimo7719/spacex-capstone

## Contents

- `notebooks/` - 8 Jupyter notebooks (data collection API + scraping, data
  wrangling, EDA visualization, EDA SQL, Folium map, Plotly Dash dashboard,
  predictive analysis/classification)
- `data/` - cleaned dataset (`spacex_launches.csv`, 663 real Falcon 9
  launches, 2010-06-04 to 2026-07-11), SQL query results
  (`sql_results.md`), model results (`ml_results.json`)
- `images/` - all 16 charts/screenshots used in the presentation
- `scripts/` - the Python scripts that generated everything (source of
  truth behind each notebook)
- `SpaceX_Falcon9_Capstone_Presentation.pptx` - the completed presentation

## Data source note

The classic version of this project also pulls from SpaceX's public REST
API (`api.spacexdata.com`). That host was unreachable from the sandboxed
environment used to build this project (persistent Cloudflare 525 error,
despite the API's own status page reporting 100% uptime) - reference code
for it is included in `notebooks/01_data_collection_api.ipynb`, but the
dataset actually used for the analysis was built entirely from Wikipedia's
"List of Falcon 9 and Falcon Heavy launches" pages (main + 2010-2019,
2020-2022, 2023, 2024 archives), scraped live.

Likewise, `folium` and `plotly`/`dash` could not be installed in that
sandbox (no package-index access), so the interactive map and dashboard
labs include their normal reference code plus a static matplotlib
equivalent that was actually used to produce the presentation's
screenshots.

## Key results

- 663 real Falcon 9 launches analyzed, June 2010 - July 2026.
- Landing success rate: 0% (2010-2014) -> 99%+ (every year since 2021).
- Best classification model: Decision Tree, 96.2% test accuracy
  predicting landing success (vs. 95.4% for Logistic Regression, SVM, and
  KNN).
- Best-performing launch site: VAFB SLC-4E (97.6% landing success rate).
- Hardest orbit to land from: GTO (76.2% success) vs. SSO/LEO (97-99%).
