"""
data_loader.py
================
All data access for the SAMCO Project Intelligence Hub.

ZERO hardcoded project data lives in this file or anywhere else in the app.
Everything is read from CSV files on disk under PROJECTS_ROOT:

    PROJECTS_ROOT/
        project_registry.csv
        <project_folder_1>/
            wbs.csv
            activities.csv
            s_curve.csv
            contracts.csv
            payments.csv
            risks.csv              (optional)
            letters_contractor.csv (optional)
            letters_pmo.csv        (optional)
            delay_events.csv       (optional)
            claim_opportunities.csv(optional)
            contract_clauses.csv   (optional)
        <project_folder_2>/
            ...

If a required file is missing, the loader returns an empty DataFrame and the
UI layer is responsible for showing a clear "no data" state - nothing is
ever invented to fill the gap.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------
# CANONICAL SCHEMAS
# ----------------------------------------------------------------------

REGISTRY_COLUMNS = [
    "project_id", "project_name", "project_folder", "sector", "contractor",
    "employer", "consultant", "location", "project_manager", "planning_engineer",
    "contract_value", "start_date", "finish_date", "status", "planned_progress",
    "actual_progress", "spi", "cpi", "bac", "bcwp", "acwp", "bcws",
    "open_risks", "high_risks", "active_claims", "claimed_amount", "delay_days",
    "certified_amount", "paid_amount", "quality_score", "safety_score",
    "priority", "risk_level", "program", "team_size", "equipment_units",
    "milestones_total", "milestones_completed",
]

REGISTRY_NUMERIC = [
    "contract_value", "planned_progress", "actual_progress", "spi", "cpi",
    "bac", "bcwp", "acwp", "bcws", "open_risks", "high_risks", "active_claims",
    "claimed_amount", "delay_days", "certified_amount", "paid_amount",
    "quality_score", "safety_score", "team_size", "equipment_units",
    "milestones_total", "milestones_completed",
]

MODULE_FILES = {
    "wbs": "wbs.csv",
    "activities": "activities.csv",
    "s_curve": "s_curve.csv",
    "contracts": "contracts.csv",
    "payments": "payments.csv",
}

OPTIONAL_FILES = {
    "risks": "risks.csv",
    "letters_contractor": "letters_contractor.csv",
    "letters_pmo": "letters_pmo.csv",
    "delay_events": "delay_events.csv",
    "claims": "claim_opportunities.csv",
    "clauses": "contract_clauses.csv",
}

NUMERIC_COLS_BY_MODULE = {
    "wbs": ["schedule_pct", "performance_pct"],
    "activities": ["planned_progress", "actual_progress", "planned_weight", "total_float_days"],
    "s_curve": ["monthly_planned", "monthly_actual", "monthly_invoiced"],
    "contracts": ["original_value", "approved_variations", "pending_variations",
                  "paid_to_date", "retention_percent"],
    "payments": ["certified_amount", "paid_amount"],
}


# ----------------------------------------------------------------------
# PATH RESOLUTION
# ----------------------------------------------------------------------

def get_projects_root() -> Path:
    """Resolve the projects root folder from session_state (set via sidebar)."""
    raw = st.session_state.get("projects_root", "").strip()
    if not raw:
        raw = "./projects"
    return Path(raw)


def registry_path(root: Path) -> Path:
    return root / "project_registry.csv"


def _safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or not path.is_file():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.warning(f"Could not read `{path}`: {e}")
        return pd.DataFrame()


def _coerce_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# ----------------------------------------------------------------------
# REGISTRY
# ----------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_registry(root_str: str) -> pd.DataFrame:
    root = Path(root_str)
    df = _safe_read_csv(registry_path(root))
    if df.empty:
        return df

    # Tolerate missing optional registry columns - fill with safe defaults
    for col in REGISTRY_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = _coerce_numeric(df, REGISTRY_NUMERIC)

    for c in ["project_id", "project_name", "project_folder", "sector",
              "status", "priority", "risk_level", "program"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    for c in ["start_date", "finish_date"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    return df


def registry_exists(root: Path) -> bool:
    return registry_path(root).exists()


# ----------------------------------------------------------------------
# PER-PROJECT MODULE DATA
# ----------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_module(root_str: str, project_folder: str, module: str) -> pd.DataFrame:
    """Load one of the required module CSVs (wbs, activities, s_curve,
    contracts, payments) for a given project folder."""
    root = Path(root_str)
    filename = MODULE_FILES.get(module)
    if filename is None:
        return pd.DataFrame()
    df = _safe_read_csv(root / project_folder / filename)
    if df.empty:
        return df
    df = _coerce_numeric(df, NUMERIC_COLS_BY_MODULE.get(module, []))
    return df


@st.cache_data(show_spinner=False)
def load_optional(root_str: str, project_folder: str, key: str) -> pd.DataFrame:
    """Load an optional CSV (risks, letters, delay events, claims, clauses).
    Returns an empty DataFrame (not fake data) if the file isn't present."""
    root = Path(root_str)
    filename = OPTIONAL_FILES.get(key)
    if filename is None:
        return pd.DataFrame()
    return _safe_read_csv(root / project_folder / filename)


def module_file_exists(root: Path, project_folder: str, module: str) -> bool:
    filename = MODULE_FILES.get(module) or OPTIONAL_FILES.get(module)
    if filename is None:
        return False
    return (root / project_folder / filename).exists()


# ----------------------------------------------------------------------
# PROJECT DISCOVERY / VALIDATION
# ----------------------------------------------------------------------

def list_registered_projects(root: Path) -> pd.DataFrame:
    """The registry IS the source of truth for which projects exist -
    not a folder scan. A project only appears if it has a registry row."""
    return load_registry(str(root))


def discover_unregistered_folders(root: Path, registry_df: pd.DataFrame) -> list[str]:
    """Folders on disk that contain project data but have no registry row -
    useful for surfacing 'you forgot to register this project' warnings."""
    if not root.exists():
        return []
    known = set(registry_df.get("project_folder", pd.Series(dtype=str)).astype(str))
    found = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and child.name not in known:
            if any((child / f).exists() for f in MODULE_FILES.values()):
                found.append(child.name)
    return found


def project_health_check(root: Path, row: pd.Series) -> dict[str, bool]:
    """Which required files exist for a given registered project row."""
    folder = str(row.get("project_folder", "")).strip()
    return {mod: module_file_exists(root, folder, mod) for mod in MODULE_FILES}


# ----------------------------------------------------------------------
# DERIVED / COMPUTED VALUES (computed from real loaded data only)
# ----------------------------------------------------------------------

def get_cashflow(root: Path, project_folder: str) -> pd.DataFrame:
    """Long-format cashflow built from s_curve.csv.
    cash_in = monthly_actual (in $), cash_out = monthly_planned (in $),
    consistent with the original dashboard's convention that s-curve
    monthly values are expressed in $ millions."""
    sc = load_module(str(root), project_folder, "s_curve")
    if sc.empty:
        return pd.DataFrame(columns=["period", "cash_in", "cash_out", "cash_invoiced"])

    month_col = "months" if "months" in sc.columns else (
        "month" if "month" in sc.columns else sc.columns[0]
    )
    out = pd.DataFrame()
    out["period"] = sc[month_col]
    out["cash_in"] = sc.get("monthly_actual", 0).fillna(0) * 1_000_000
    out["cash_out"] = sc.get("monthly_planned", 0).fillna(0) * 1_000_000
    out["cash_invoiced"] = sc.get("monthly_invoiced", 0).fillna(0) * 1_000_000
    return out


def compute_portfolio_kpis(projects: pd.DataFrame) -> dict:
    """Mirrors the original dashboard's getPortfolioKpis() formulas exactly,
    but sourced entirely from the live registry DataFrame."""
    empty = {
        "totalProjects": 0, "activeSectors": 0, "totalContract": 0, "totalBAC": 0,
        "totalBCWP": 0, "totalBCWS": 0, "totalACWP": 0, "portfolioPlanned": 0,
        "portfolioActual": 0, "portfolioSPI": 0, "portfolioCPI": 0,
        "totalCertified": 0, "totalPaid": 0, "totalOutstanding": 0,
        "totalOpenRisks": 0, "totalHighRisks": 0, "totalActiveClaims": 0,
        "totalClaimed": 0, "totalDelay": 0, "avgQuality": 0, "avgSafety": 0,
    }
    if projects is None or projects.empty:
        return empty

    p = projects.copy()
    for c in REGISTRY_NUMERIC:
        if c in p.columns:
            p[c] = pd.to_numeric(p[c], errors="coerce").fillna(0)
        else:
            p[c] = 0

    total_contract = float(p["contract_value"].sum())
    total_bac = float(p["bac"].sum())
    total_bcwp = float(p["bcwp"].sum())
    total_bcws = float(p["bcws"].sum())
    total_acwp = float(p["acwp"].sum())
    total_certified = float(p["certified_amount"].sum())
    total_paid = float(p["paid_amount"].sum())

    weighted_planned = float((p["planned_progress"] * p["contract_value"]).sum())
    weighted_actual = float((p["actual_progress"] * p["contract_value"]).sum())
    weighted_spi = float((p["spi"] * p["contract_value"]).sum())
    weighted_cpi = float((p["cpi"] * p["contract_value"]).sum())

    portfolio_planned = weighted_planned / total_contract if total_contract > 0 else 0
    portfolio_actual = weighted_actual / total_contract if total_contract > 0 else 0
    portfolio_spi = weighted_spi / total_contract if total_contract > 0 else 0
    portfolio_cpi = weighted_cpi / total_contract if total_contract > 0 else 0

    n = len(p)
    return {
        "totalProjects": n,
        "activeSectors": p["sector"].nunique() if "sector" in p.columns else 0,
        "totalContract": total_contract,
        "totalBAC": total_bac,
        "totalBCWP": total_bcwp,
        "totalBCWS": total_bcws,
        "totalACWP": total_acwp,
        "portfolioPlanned": portfolio_planned,
        "portfolioActual": portfolio_actual,
        "portfolioSPI": portfolio_spi,
        "portfolioCPI": portfolio_cpi,
        "totalCertified": total_certified,
        "totalPaid": total_paid,
        "totalOutstanding": total_certified - total_paid,
        "totalOpenRisks": float(p["open_risks"].sum()),
        "totalHighRisks": float(p["high_risks"].sum()),
        "totalActiveClaims": float(p["active_claims"].sum()),
        "totalClaimed": float(p["claimed_amount"].sum()),
        "totalDelay": float(p["delay_days"].sum()),
        "avgQuality": float(p["quality_score"].mean()) if n else 0,
        "avgSafety": float(p["safety_score"].mean()) if n else 0,
    }


def compute_evm(row: pd.Series) -> dict:
    """Earned Value Management metrics derived purely from registry numbers
    for a single project - no fabricated figures."""
    bac = float(row.get("bac", 0) or 0)
    pv = float(row.get("bcws", 0) or 0)
    ev = float(row.get("bcwp", 0) or 0)
    ac = float(row.get("acwp", 0) or 0)
    spi = ev / pv if pv else 0
    cpi = ev / ac if ac else 0
    sv = ev - pv
    cv = ev - ac
    eac = bac / cpi if cpi else 0
    etc = eac - ac
    vac = bac - eac
    tcpi = (bac - ev) / (bac - ac) if (bac - ac) != 0 else 0
    return {
        "bac": bac, "pv": pv, "ev": ev, "ac": ac, "spi": spi, "cpi": cpi,
        "sv": sv, "cv": cv, "eac": eac, "etc": etc, "vac": vac, "tcpi": tcpi,
    }
