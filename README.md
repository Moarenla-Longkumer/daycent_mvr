# DayCent QA/QC Dashboard

Streamlit app for browsing DayCent model QA/QC results across sites: per-site check verdicts, diagnostic plots, summary text files, and a multi-site Excel summary.

Deployed from this repo on Streamlit Community Cloud (branch: `main`).

## What the dashboard shows

- **Site selector** — pick one site from `qaqc_inventory.csv`
- **Per-site results** — SOMSC, Biomass, and N2O verdicts plus plot counts
- **QA/QC Summary tab** — row from `multi_site_qa_qc_summary_20260604.xlsx` (pipeline steps, model checks, comments)
- **SOMSC / Biomass / N2O tabs** — plots and `*_check_summary.txt` text for the selected site

## Repo layout

| Path | Purpose |
|------|---------|
| `app.py` | Streamlit dashboard |
| `qaqc_inventory.csv` | Index of all sites, result strings, and paths to plots/summaries |
| `assets/` | Bundled plot PNGs and summary text files (relative paths for cloud deploy) |
| `multi_site_qa_qc_summary_20260604.xlsx` | Multi-site pipeline + model-check summary table |
| `update_dashboard.py` | Copies local QA outputs into `assets/` and rewrites CSV paths |
| `requirements.txt` | Python dependencies |

## Prerequisites

- DayCent QA/QC outputs on your machine under:
  ```
  /Users/mac/DAYCENT/daycent_sites/sites/<site>/{somsc_check,biomass_check,n2o_check}/
  ```
- Inventory builder notebook:
  ```
  /Users/mac/DAYCENT/tools/qaqc_dashboard/qaqc_dashboard.ipynb
  ```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown in the terminal (default: http://localhost:8501).

## Update workflow

Use this sequence whenever you have new QA/QC outputs and want the live dashboard to reflect them.

### 1. Regenerate QA/QC outputs

Run your DayCent QA/QC pipeline so each site folder is updated under:

```
/Users/mac/DAYCENT/daycent_sites/sites/<site>/
```

Expected outputs include, per check folder:

- `*_check_summary.txt`
- `somsc_timeseries_spinup.png`, `somsc_timeseries_exp.png`, `observed_vs_modeled_*.png` (where applicable)

### 2. Rebuild `qaqc_inventory.csv`

1. Open `/Users/mac/DAYCENT/tools/qaqc_dashboard/qaqc_dashboard.ipynb`
2. Run the **inventory builder** cell
3. Confirm it prints something like: `Wrote N site(s) to .../qaqc_inventory.csv`
4. Copy the fresh CSV into this repo:

```bash
cp /Users/mac/DAYCENT/tools/qaqc_dashboard/qaqc_inventory.csv \
   /Users/mac/Desktop/dummy/my_app/qaqc_inventory.csv
```

The copied CSV will contain **absolute** paths (`/Users/mac/DAYCENT/...`). That is expected at this step.

### 3. Bundle files for Streamlit Cloud

From this repo folder, run:

```bash
python update_dashboard.py
```

This script:

- Reads `qaqc_inventory.csv`
- Deletes and rebuilds `assets/` from the referenced source files
- Rewrites all path columns to relative `assets/...` paths
- Prints a summary: `rows=... copied=... missing=...`

**Important:** `update_dashboard.py` only runs when the CSV still has absolute `daycent_sites/sites/` paths. If the CSV is already relativized, copy in a fresh export from the notebook first.

Missing source files are skipped; the app will show **"not found"** for those plots.

### 4. Update the Excel summary (optional)

If you have a new multi-site summary workbook:

1. Place it in this repo (or replace the existing file)
2. Update `SUMMARY_XLSX` in `app.py` if the filename changed
3. Ensure the sheet has a **`Site name`** column that matches `site` values in `qaqc_inventory.csv`

### 5. Commit and push

```bash
git add -A
git commit -m "Update QA/QC outputs"
git push origin main
```

Streamlit Community Cloud redeploys automatically when `main` is updated (usually within a minute).

## Quick reference (full refresh)

```bash
# after notebook inventory cell + cp qaqc_inventory.csv here
cd /Users/mac/Desktop/dummy/my_app
python update_dashboard.py
git add -A
git commit -m "Update QA/QC outputs"
git push origin main
```

## How data flows

```
DayCent QA runs
    → daycent_sites/sites/<site>/...
Notebook inventory builder
    → qaqc_inventory.csv (absolute paths)
update_dashboard.py
    → assets/ + qaqc_inventory.csv (relative paths)
git push → Streamlit Cloud
    → app.py reads CSV + assets/ + Excel
```

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|----------------|-----|
| Plots show "not found" on Streamlit Cloud | Absolute paths in CSV or missing `assets/` | Re-run `update_dashboard.py` from a fresh absolute-path CSV |
| `update_dashboard.py` exits immediately | CSV already has `assets/...` paths | Copy fresh `qaqc_inventory.csv` from the notebook first |
| Site missing from Excel tab | Site not in the workbook | Add row to Excel or ignore for that site |
| `Missing qaqc_inventory.csv` | CSV not in repo | Run notebook + copy CSV into repo |
| Excel tab fails to load | `openpyxl` missing | `pip install -r requirements.txt` |

## Notes

- `assets/` is large (~50+ MB). That is normal for bundled plots.
- Plot paths in the inventory index five fixed PNGs per site; extra plot folders (`summary_plots`, `livec_out`, etc.) are counted but not individually displayed.
- Revoke and rotate GitHub tokens after use; do not commit credentials.
