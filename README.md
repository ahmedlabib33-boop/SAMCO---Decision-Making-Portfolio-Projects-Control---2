# 🏗️ SAMCO – Project Intelligence Hub (Streamlit Rebuild)

**Created & Developed by | Engr. Ahmed Labib**

---

## 📌 Overview

A multi‑project construction project‑controls dashboard built with **Streamlit**. It provides a **Decision Making Dashboard** for portfolio oversight and **Project‑Specific Dashboards** for in‑depth analysis of individual projects.

**Zero hardcoded project data.** Every number, chart, and table is read live from CSV files on disk. There is no `projectRegistry`, `wbsDataMap`, or any other in‑code data structure — `data_loader.py` is the only place that touches your files, and it never invents a value that isn't in a CSV. If a file is missing, the UI tells you exactly which file and which columns it expected, instead of showing fake data.

---

## 📂 Data Schema

```
projects/                              <- point the sidebar at this folder
├── project_registry.csv               <- master list, one row per project
├── PROJ_A/
│   ├── wbs.csv
│   ├── activities.csv
│   ├── s_curve.csv
│   ├── contracts.csv
│   ├── payments.csv
│   ├── risks.csv                      (optional)
│   ├── letters_contractor.csv         (optional)
│   ├── letters_pmo.csv                (optional)
│   ├── delay_events.csv               (optional)
│   ├── claim_opportunities.csv        (optional)
│   └── contract_clauses.csv           (optional)
├── PROJ_B/
│   └── ... same structure
```

The `project_folder` column in the registry tells the app which subfolder holds that project's files — it does not have to match `project_id`.

### Registry Columns (`project_registry.csv`)
`project_id`, `project_name`, `project_folder`, `sector`, `contractor`, `employer`, `consultant`, `location`, `project_manager`, `planning_engineer`, `contract_value`, `start_date`, `finish_date`, `status`, `planned_progress`, `actual_progress`, `spi`, `cpi`, `bac`, `bcwp`, `acwp`, `bcws`, `open_risks`, `high_risks`, `active_claims`, `claimed_amount`, `delay_days`, `certified_amount`, `paid_amount`, `quality_score`, `safety_score`, `priority`, `risk_level`, `program`, `team_size`, `equipment_units`, `milestones_total`, `milestones_completed`

### Required Module CSVs (per project folder)
- **`wbs.csv`** – `wbs_code`, `wbs_name`, `schedule_pct`, `performance_pct`
- **`activities.csv`** – `activity_id`, `activity_name`, `wbs_id`, `planned_start`, `planned_finish`, `actual_start`, `actual_finish`, `forecast_start`, `forecast_finish`, `planned_progress`, `actual_progress`, `planned_weight`, `total_float_days`, `is_critical`, `responsible_party`
- **`s_curve.csv`** – `months`, `monthly_planned`, `monthly_actual`, `monthly_invoiced`
- **`contracts.csv`** – `contract_id`, `package`, `contractor`, `contract_type`, `original_value`, `approved_variations`, `pending_variations`, `paid_to_date`, `retention_percent`, `status`
- **`payments.csv`** – `payment_id`, `contract_id`, `invoice_no`, `invoice_date`, `certified_amount`, `paid_amount`, `payment_status`

### Optional Module CSVs (per project folder)
If these aren't present, the relevant tab shows an empty‑state with the exact filename and columns expected — nothing is fabricated.
- **`risks.csv`** – `id`, `risk`, `category`, `severity`, `status`, `mitigation`
- **`letters_contractor.csv`** / **`letters_pmo.csv`** – `ref`, `date`, `type`, `subject`, `risk_type`, `delay_risk`, `eot_potential`, `claim_strength`, `required_actions`
- **`delay_events.csv`** – `event`, `responsibility`, `days`, `critical_path`, `eot_potential`, `status`
- **`claim_opportunities.csv`** – `id`, `source_event`, `event_date`, `event_type`, `description`, `activity`, `matched_clause`, `entitlement_basis`, `notice_status`, `evidence_status`, `time_impact_relevance`, `cost_impact_relevance`, `claim_strength`, `recommended_action`
- **`contract_clauses.csv`** – your contract clause register (any columns; displayed as-is)

---

## 🔗 Data Linking & Architecture
1. **Project Registry** – loaded once per session and cached (`@st.cache_data`).
2. **Project Selection** – the selected `project_id` filters every downstream read; nothing from other projects is ever loaded into memory at the same time.
3. **Module Loading** – each tab loads its own CSV from the selected project's folder, on demand.
4. **Portfolio Aggregation** – the Decision Dashboard aggregates live across whatever rows are in the registry (weighted by `contract_value` for SPI/CPI/progress, matching standard portfolio EVM practice).
5. **Caching** – click **Refresh** in the sidebar any time you edit a CSV on disk; it clears the cache and re-reads everything.

---

## 🚀 Running It

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Point it at your data
In the sidebar, set **Projects root folder** to your real path, e.g.:
```
D:\Samco - Decision Making Portfolio & Projects Control\projects
```
The app validates this on every load and shows a green confirmation once `project_registry.csv` is found there.

### 4. First-run / empty folder behavior
If the folder you point to has no `project_registry.csv`, the sidebar shows a **🧪 Generate Sample Data (5 projects)** button. Clicking it writes a complete, realistic 5‑project sample dataset to that folder in the exact schema above — useful for exploring the UI before wiring up your real data. From that point on it's read through the exact same file pipeline as any real project; there's no separate "demo mode" code path.

### 5. Adding a new project
1. Add a new row to `project_registry.csv`.
2. Create a new folder under `projects/` (e.g. `PROJ_F`) matching that row's `project_folder` value.
3. Add the required CSVs with the schema above.
4. Click **🔄 Refresh** in the sidebar (or restart the app).

### 6. Exporting data
- **Decision Dashboard** – **⬇️ Export Filtered CSV** exports exactly the rows currently shown after your filters.
- **Project Dashboard → Output Studio** – downloads an executive summary (`.md`) plus raw WBS / Activities / S‑Curve CSVs for that project.

---

## 📁 Files in this project
| File | Purpose |
|---|---|
| `app.py` | Main Streamlit app — Meeting Mode, controls bar, Decision Dashboard, Project Dashboard, all 11 tabs |
| `data_loader.py` | The only file that reads CSVs. All KPI math (portfolio aggregation, EVM) lives here |
| `charts.py` | Plotly figure builders — every function takes a DataFrame, returns a figure |
| `style.py` | CSS theme + reusable HTML components (cards, badges, headers) matching the original design |
| `sample_data_generator.py` | Writes seed CSVs for first-run onboarding only |
| `assets/` | Drop `logo.png` / `.jpg` / `.svg` here to replace the built-in SAMCO wordmark in the header |
| `requirements.txt` | `streamlit`, `pandas`, `plotly`, `openpyxl` |

## 🎤 Meeting Mode
Sits above the dashboard/project selector so it's always visible no matter where you navigate. Click **Start Meeting** to reveal:
- **Participants** — add any number of attendees (no cap at 5), shown as chips with a live count; remove any via the dropdown next to the add box.
- **Agenda** — starts with 6 default items but is fully editable: add your own items, remove any via the dropdown.

Everything is stored in session state, so it survives switching between the Decision Dashboard and any project tab — starting or ending the meeting never navigates away from what you're looking at.

## 🔍 Filter Bar
Three checkbox-popover filters, in this order: **Sector**, **Projects** (the program field), **Status**. Click to open, check any number of boxes, click away and the popover closes on its own — the trigger button only ever shows a compact count (e.g. "Status (2)"), it never fills up with selected-item tags. Status values display as Controlled / Warning / Critical Performance rather than the raw Green/Amber/Red codes, everywhere in the app (filter, badges, project table).


---

## ✅ Tested
Every phase, all 5 sample projects, all 11 project tabs, all 3 portfolio view modes, filter combinations (including emptied multiselects), and the first‑run "Generate Sample Data" button were run end‑to‑end via Streamlit's `AppTest` framework with zero exceptions before delivery.
