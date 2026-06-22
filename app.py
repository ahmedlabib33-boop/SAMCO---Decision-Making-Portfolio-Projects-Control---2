"""
app.py
=======
SAMCO – Project Intelligence Hub (Streamlit rebuild)
Created & Developed by | Engr. Ahmed Labib

Run with:   streamlit run app.py

All project data is read from CSV files under a "projects root" folder
configured in the Settings panel at the top of the page. Nothing about any
specific project is hardcoded anywhere in this codebase - see data_loader.py.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

import charts as ch
import data_loader as dl
import style as sty
from sample_data_generator import generate_sample_data

# ----------------------------------------------------------------------
# PAGE SETUP
# ----------------------------------------------------------------------

st.set_page_config(page_title="SAMCO – Project Intelligence Hub", page_icon="🏗️", layout="wide")
st.markdown(sty.CSS, unsafe_allow_html=True)
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">',
    unsafe_allow_html=True,
)

if "projects_root" not in st.session_state:
    st.session_state.projects_root = "./projects"
if "nav" not in st.session_state:
    st.session_state.nav = "decision"
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Overall Portfolio"


# ----------------------------------------------------------------------
# FORMAT HELPERS
# ----------------------------------------------------------------------

def money(v, suffix="M") -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if pd.isna(v):
        return "—"
    return f"${v / 1_000_000:,.1f}{suffix}"


def pct(v) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if pd.isna(v):
        return "—"
    return f"{v:.1f}%"


def num(v, decimals=2) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if pd.isna(v):
        return "—"
    return f"{v:.{decimals}f}"


def integer(v) -> str:
    try:
        return f"{int(float(v)):,}"
    except (TypeError, ValueError):
        return "—"


# ----------------------------------------------------------------------
# SETTINGS (replaces the old sidebar - a compact, collapsible panel)
# ----------------------------------------------------------------------

root = Path(st.session_state.projects_root)
registry_found = dl.registry_exists(root)

with st.expander("⚙️ Data Source Settings", expanded=not registry_found):
    sc1, sc2, sc3 = st.columns([3, 1, 1])
    with sc1:
        st.session_state.projects_root = st.text_input(
            "Projects root folder", value=st.session_state.projects_root,
            help=r'e.g. D:\Samco - Decision Making Portfolio & Projects Control\projects',
            label_visibility="collapsed",
        )
    with sc2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with sc3:
        if not registry_found:
            if st.button("🧪 Sample Data", use_container_width=True):
                generate_sample_data(root)
                st.cache_data.clear()
                st.rerun()
    if registry_found:
        st.caption(f"✅ Registry loaded from `{root.resolve()}`")
    else:
        st.caption(f"⚠️ No `project_registry.csv` found at `{root.resolve()}`")

root = Path(st.session_state.projects_root)
registry = dl.load_registry(str(root))

# ----------------------------------------------------------------------
# HEADER BANNER
# ----------------------------------------------------------------------

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
nav = st.session_state.nav
if nav == "decision":
    phase_text = "🧭 Decision Making Dashboard"
else:
    match = registry[registry["project_id"].astype(str) == str(nav)] if not registry.empty else pd.DataFrame()
    proj_name = match.iloc[0]["project_name"] if not match.empty else nav
    phase_text = f"📋 {proj_name}"

custom_logo = sty.load_custom_logo()
logo_html = custom_logo if custom_logo else f'<div style="width:60px;height:60px;flex-shrink:0;">{sty.SAMCO_LOGO_SVG}</div>'

st.markdown(f"""
<div class="header-banner">
  <div class="brand">
    {logo_html}
    <div>
      <div class="banner-title">SAMCO <span class="desg">– Project Intelligence Hub</span></div>
      <p class="tagline">Multi-Project Controls &amp; Decision Intelligence</p>
    </div>
  </div>
  <div class="meta">
    <p class="label">SYSTEM TIME</p>
    <p class="time">{now_str}</p>
    <span class="phase">{phase_text}</span>
  </div>
</div>
""", unsafe_allow_html=True)

if registry.empty:
    st.markdown(sty.empty_state(
        "No project data found",
        f"Open <b>Data Source Settings</b> above and point it at a folder containing "
        f"<code>project_registry.csv</code>, or click <b>Sample Data</b>.",
    ), unsafe_allow_html=True)
    st.stop()

# ----------------------------------------------------------------------
# MEETING MODE PANEL - shown first, before dashboard/project navigation.
# Lives entirely in session_state so it stays active and visible no matter
# which dashboard, project, or tab you navigate to afterward - it never
# triggers a page change, and supports any number of participants.
# ----------------------------------------------------------------------

if "meeting_active" not in st.session_state:
    st.session_state.meeting_active = False
if "meeting_participants" not in st.session_state:
    st.session_state.meeting_participants = []
if "meeting_agenda" not in st.session_state:
    st.session_state.meeting_agenda = [
        "Progress status & SPI/CPI review", "Critical path & schedule health",
        "Risks and blockers – top 5", "Delay events & responsibility",
        "Claims and contractual actions", "Decisions required from management",
    ]

scope_label = "Decision Dashboard" if nav == "decision" else phase_text.replace("📋 ", "")

with st.container(border=True):
    mh1, mh2 = st.columns([3, 1])
    with mh1:
        live_html = (
            '<span class="live-badge"><span class="pulse"></span> LIVE MEETING ROOM ACTIVE</span>'
            if st.session_state.meeting_active else
            '<span class="badge badge-gray">Inactive</span>'
        )
        st.markdown(
            f'<div class="meeting-header"><div style="display:flex;align-items:center;gap:10px;">'
            f'<i class="fas fa-video" style="color:var(--electric);"></i> '
            f'<span style="font-weight:600;color:#e2e8f0;font-size:0.85rem;">Meeting Mode</span> {live_html}</div>'
            f'<span style="font-size:0.7rem;color:#94a3b8;"><i class="fas fa-crosshairs"></i> {scope_label}</span></div>',
            unsafe_allow_html=True,
        )
    with mh2:
        btn_label = "⏹ End Meeting" if st.session_state.meeting_active else "▶ Start Meeting"
        if st.button(btn_label, use_container_width=True,
                      type="primary" if not st.session_state.meeting_active else "secondary"):
            st.session_state.meeting_active = not st.session_state.meeting_active
            st.rerun()

    if st.session_state.meeting_active:
        n = len(st.session_state.meeting_participants)
        st.markdown(
            f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--border);'
            f'font-size:0.7rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">'
            f'<i class="fas fa-users"></i> Participants <span class="participant-count">({n})</span></div>',
            unsafe_allow_html=True,
        )
        if st.session_state.meeting_participants:
            chips = "".join(f'<span class="participant-chip"><i class="fas fa-user"></i> {p}</span>'
                             for p in st.session_state.meeting_participants)
            st.markdown(f'<div style="margin:6px 0;">{chips}</div>', unsafe_allow_html=True)
        else:
            st.caption("No participants added yet — add as many as the meeting needs below.")

        pc1, pc2 = st.columns([3, 1])
        with pc1:
            with st.form("add_participant_form", clear_on_submit=True, border=False):
                fp1, fp2 = st.columns([4, 1])
                with fp1:
                    new_participant = st.text_input("Add participant", placeholder="Participant name",
                                                       label_visibility="collapsed")
                with fp2:
                    add_p = st.form_submit_button("+ Add", use_container_width=True)
                if add_p and new_participant.strip():
                    st.session_state.meeting_participants.append(new_participant.strip())
                    st.rerun()
        with pc2:
            if st.session_state.meeting_participants:
                to_remove_p = st.multiselect("Remove", st.session_state.meeting_participants,
                                               label_visibility="collapsed", placeholder="Remove…",
                                               key="rm_participants_select")
                if to_remove_p and st.button("Remove", key="rm_participants_btn", use_container_width=True):
                    st.session_state.meeting_participants = [
                        p for p in st.session_state.meeting_participants if p not in to_remove_p
                    ]
                    st.rerun()

        st.markdown(
            '<div style="margin-top:14px;padding-top:10px;border-top:1px solid var(--border);'
            'font-size:0.7rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">'
            '<i class="fas fa-list-check"></i> Agenda</div>',
            unsafe_allow_html=True,
        )
        agenda_html = "".join(
            f'<div><span class="num">{i+1}.</span> {item}</div>'
            for i, item in enumerate(st.session_state.meeting_agenda)
        )
        st.markdown(f'<div class="meeting-agenda">{agenda_html}</div>', unsafe_allow_html=True)

        ac1, ac2 = st.columns([3, 1])
        with ac1:
            with st.form("add_agenda_form", clear_on_submit=True, border=False):
                fa1, fa2 = st.columns([4, 1])
                with fa1:
                    new_item = st.text_input("Add agenda item", placeholder="Add agenda item",
                                               label_visibility="collapsed")
                with fa2:
                    add_a = st.form_submit_button("+ Add", use_container_width=True)
                if add_a and new_item.strip():
                    st.session_state.meeting_agenda.append(new_item.strip())
                    st.rerun()
        with ac2:
            if st.session_state.meeting_agenda:
                to_remove_a = st.multiselect("Remove", st.session_state.meeting_agenda,
                                               label_visibility="collapsed", placeholder="Remove…",
                                               key="rm_agenda_select")
                if to_remove_a and st.button("Remove", key="rm_agenda_btn", use_container_width=True):
                    st.session_state.meeting_agenda = [
                        a for a in st.session_state.meeting_agenda if a not in to_remove_a
                    ]
                    st.rerun()

# ----------------------------------------------------------------------
# CONTROLS BAR - unified navigation (replaces sidebar Phase/Project controls)
# ----------------------------------------------------------------------

nav_options = ["🧭 Decision Making Dashboard"] + [
    f"{row.project_name}" for row in registry.itertuples()
]
nav_ids = ["decision"] + [str(row.project_id) for row in registry.itertuples()]
current_idx = nav_ids.index(nav) if nav in nav_ids else 0

with st.container(border=True):
    cb1, cb2, cb3 = st.columns([3, 1, 2])
    with cb1:
        chosen = st.selectbox("Navigate", nav_options, index=current_idx, label_visibility="collapsed")
        st.session_state.nav = nav_ids[nav_options.index(chosen)]
    with cb2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with cb3:
        scope = "Phase: Decision Dashboard" if st.session_state.nav == "decision" else "Phase: Project Dashboard"
        st.markdown(f'<div style="text-align:right;"><span class="scope-chip"><i class="fas fa-crosshairs"></i> {scope}</span></div>',
                    unsafe_allow_html=True)

nav = st.session_state.nav


# ----------------------------------------------------------------------
# CHART BOX HELPER - bordered container matching .chart-card styling
# ----------------------------------------------------------------------

def chart_box(icon: str, title: str, fig):
    with st.container(border=True):
        st.markdown(f'<div class="chart-card-title"><i class="fas {icon} icon"></i> {title}</div>',
                     unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_table_or_empty(df: pd.DataFrame, title: str, hint: str):
    if df is None or df.empty:
        st.markdown(sty.empty_state(title, hint), unsafe_allow_html=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------
# DECISION DASHBOARD
# ----------------------------------------------------------------------

def checkbox_filter_popover(label: str, options: list, state_key: str, value_labels: dict | None = None) -> list:
    """A compact filter control: click to open a popover of checkboxes,
    pick any number, the popover closes on its own when you click away
    ('the list vanishes') and the trigger button only ever shows a count
    - it never re-fills with the chosen values as tags."""
    if state_key not in st.session_state:
        st.session_state[state_key] = []
    selected = st.session_state[state_key]
    trigger_label = f"{label} ({len(selected)})" if selected else label
    with st.popover(trigger_label, use_container_width=True):
        new_selected = list(selected)
        for opt in options:
            display = value_labels.get(opt, opt) if value_labels else opt
            checked = st.checkbox(display, value=(opt in selected), key=f"{state_key}__{opt}")
            if checked and opt not in new_selected:
                new_selected.append(opt)
            elif not checked and opt in new_selected:
                new_selected.remove(opt)
        if new_selected != selected:
            st.session_state[state_key] = new_selected
            st.rerun()
    return st.session_state[state_key]


def render_decision_dashboard(registry: pd.DataFrame, root: Path):
    # ---- view mode pills ----
    vc1, vc2, vc3, _ = st.columns([1.3, 1.2, 1.4, 5])
    with vc1:
        if st.button("📊 Overall Portfolio", use_container_width=True,
                      type="primary" if st.session_state.view_mode == "Overall Portfolio" else "secondary"):
            st.session_state.view_mode = "Overall Portfolio"
            st.rerun()
    with vc2:
        if st.button("🏭 Sector Analysis", use_container_width=True,
                      type="primary" if st.session_state.view_mode == "Sector Analysis" else "secondary"):
            st.session_state.view_mode = "Sector Analysis"
            st.rerun()
    with vc3:
        if st.button("📋 Program Comparison", use_container_width=True,
                      type="primary" if st.session_state.view_mode == "Program Comparison" else "secondary"):
            st.session_state.view_mode = "Program Comparison"
            st.rerun()
    view_mode = st.session_state.view_mode

    # ------------------------------------------------------------------
    # FILTER BAR - now placed between view mode pills and KPI grid
    # Filter visibility depends on view_mode.
    # ------------------------------------------------------------------
    sectors = sorted(registry["sector"].dropna().unique().tolist())
    programs = sorted(registry["program"].dropna().unique().tolist())
    statuses = sorted(registry["status"].dropna().unique().tolist())

    with st.container(border=True):
        # Determine which filter columns to show
        if view_mode == "Overall Portfolio":
            # Show Sector, Projects, Status, date range
            f1, f2, f3, f4, f5 = st.columns([1.2, 1.2, 1.5, 1, 1])
            with f1:
                sel_sector = checkbox_filter_popover("Sector", sectors, "filter_sector")
            with f2:
                sel_program = checkbox_filter_popover("Projects", programs, "filter_program")
            with f3:
                sel_status = checkbox_filter_popover("Status", statuses, "filter_status", sty.STATUS_LABELS)
            with f4:
                start_date = st.date_input("From", value=None, label_visibility="collapsed", format="YYYY-MM-DD")
            with f5:
                end_date = st.date_input("To", value=None, label_visibility="collapsed", format="YYYY-MM-DD")
        elif view_mode == "Sector Analysis":
            # Show only Sector, Status, date range
            f1, f2, f3, f4 = st.columns([1.2, 1.5, 1, 1])
            with f1:
                sel_sector = checkbox_filter_popover("Sector", sectors, "filter_sector")
            with f2:
                sel_status = checkbox_filter_popover("Status", statuses, "filter_status", sty.STATUS_LABELS)
            with f3:
                start_date = st.date_input("From", value=None, label_visibility="collapsed", format="YYYY-MM-DD")
            with f4:
                end_date = st.date_input("To", value=None, label_visibility="collapsed", format="YYYY-MM-DD")
            # Clear program filter when not used
            st.session_state.filter_program = []
        else:  # Program Comparison
            # Show only Projects, Status, date range
            f1, f2, f3, f4 = st.columns([1.2, 1.5, 1, 1])
            with f1:
                sel_program = checkbox_filter_popover("Projects", programs, "filter_program")
            with f2:
                sel_status = checkbox_filter_popover("Status", statuses, "filter_status", sty.STATUS_LABELS)
            with f3:
                start_date = st.date_input("From", value=None, label_visibility="collapsed", format="YYYY-MM-DD")
            with f4:
                end_date = st.date_input("To", value=None, label_visibility="collapsed", format="YYYY-MM-DD")
            # Clear sector filter when not used
            st.session_state.filter_sector = []

    # ---- Apply filters to dataframe ----
    df = registry.copy()
    # Sector filter (if present)
    if view_mode in ("Overall Portfolio", "Sector Analysis"):
        sel_sector = st.session_state.get("filter_sector", [])
        if sel_sector:
            df = df[df["sector"].isin(sel_sector)]
    # Program filter (if present)
    if view_mode in ("Overall Portfolio", "Program Comparison"):
        sel_program = st.session_state.get("filter_program", [])
        if sel_program:
            df = df[df["program"].isin(sel_program)]
    # Status filter (always present)
    sel_status = st.session_state.get("filter_status", [])
    if sel_status:
        df = df[df["status"].isin(sel_status)]
    # Date filters (always present)
    if start_date:
        df = df[df["start_date"] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df["finish_date"] <= pd.Timestamp(end_date)]

    if df.empty:
        st.markdown(sty.empty_state("No projects match these filters", "Adjust filters above."), unsafe_allow_html=True)
        return

    # ---- KPIs (icons + real, derived deltas - never fabricated) ----
    kpis = dl.compute_portfolio_kpis(df)
    spi_delta_type = "positive" if kpis["portfolioSPI"] >= 1 else "negative"
    cpi_delta_type = "positive" if kpis["portfolioCPI"] >= 1 else "negative"
    prog_delta_type = "positive" if kpis["portfolioActual"] >= kpis["portfolioPlanned"] else "negative"
    cards = [
        sty.kpi_card("Total Projects", integer(kpis["totalProjects"]), icon="fa-building",
                      delta=f'{integer(kpis["activeSectors"])} sectors', delta_type="neutral"),
        sty.kpi_card("Total Contract Value", money(kpis["totalContract"]), icon="fa-file-invoice"),
        sty.kpi_card("Total BAC", money(kpis["totalBAC"]), icon="fa-bullseye"),
        sty.kpi_card("Portfolio Planned", pct(kpis["portfolioPlanned"]), icon="fa-calendar-check"),
        sty.kpi_card("Portfolio Actual", pct(kpis["portfolioActual"]), icon="fa-hourglass-half",
                      delta=f'{kpis["portfolioActual"] - kpis["portfolioPlanned"]:+.1f}pp vs plan',
                      delta_type=prog_delta_type),
        sty.kpi_card("Portfolio SPI", num(kpis["portfolioSPI"]), icon="fa-arrow-trend-down",
                      delta=f'{(kpis["portfolioSPI"] - 1) * 100:+.0f}% vs target', delta_type=spi_delta_type),
        sty.kpi_card("Portfolio CPI", num(kpis["portfolioCPI"]), icon="fa-arrow-trend-up",
                      delta=f'{(kpis["portfolioCPI"] - 1) * 100:+.0f}% vs target', delta_type=cpi_delta_type),
        sty.kpi_card("Total Certified", money(kpis["totalCertified"]), icon="fa-stamp"),
        sty.kpi_card("Total Paid", money(kpis["totalPaid"]), icon="fa-money-bill-wave"),
        sty.kpi_card("Outstanding", money(kpis["totalOutstanding"]), icon="fa-hand-holding-dollar",
                      delta_type="negative" if kpis["totalOutstanding"] > 0 else "positive"),
        sty.kpi_card("Open Risks", integer(kpis["totalOpenRisks"]), icon="fa-shield",
                      delta_type="negative" if kpis["totalOpenRisks"] > 0 else "positive",
                      badge="risk" if kpis["totalOpenRisks"] else "", badge_type="risk"),
        sty.kpi_card("High Risks", integer(kpis["totalHighRisks"]), icon="fa-triangle-exclamation",
                      delta_type="negative" if kpis["totalHighRisks"] > 0 else "positive"),
        sty.kpi_card("Active Claims", integer(kpis["totalActiveClaims"]), icon="fa-gavel",
                      delta_type="negative" if kpis["totalActiveClaims"] > 0 else "positive",
                      badge="claims" if kpis["totalActiveClaims"] else "", badge_type="warning"),
        sty.kpi_card("Claimed Amount", money(kpis["totalClaimed"]), icon="fa-file-contract"),
        sty.kpi_card("Delay Exposure", f'{integer(kpis["totalDelay"])}d', icon="fa-clock",
                      delta_type="negative" if kpis["totalDelay"] > 0 else "positive",
                      badge="risk" if kpis["totalDelay"] else "", badge_type="risk"),
        sty.kpi_card("Avg Quality", num(kpis["avgQuality"], 1), icon="fa-star",
                      delta_type="positive" if kpis["avgQuality"] >= 85 else "negative"),
        sty.kpi_card("Avg Safety", num(kpis["avgSafety"], 1), icon="fa-helmet-safety",
                      delta_type="positive" if kpis["avgSafety"] >= 90 else "negative"),
    ]
    st.markdown(sty.kpi_grid(cards), unsafe_allow_html=True)

    # ---- sector performance cards ----
    with st.container(border=True):
        st.markdown(sty.section_header("fas fa-building", "Sector Performance", "Quick overview of all sectors"),
                    unsafe_allow_html=True)
        cards_html = []
        for sector, g in df.groupby("sector"):
            cf_value = 0.0
            for _, prow in g.iterrows():
                cf = dl.get_cashflow(root, str(prow.get("project_folder") or prow.get("project_id")))
                if not cf.empty:
                    cf_value += (cf["cash_in"] - cf["cash_out"]).sum()
            cards_html.append(sty.sector_card(
                sector=str(sector), n=len(g), value_m=g["contract_value"].sum() / 1e6,
                avg_progress=g["actual_progress"].mean(), avg_spi=g["spi"].mean(), avg_cpi=g["cpi"].mean(),
                total_risks=int(g["open_risks"].sum()), total_delay=int(g["delay_days"].sum()),
                avg_quality=g["quality_score"].mean(),
            ))
        st.markdown(f'<div class="sector-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)

    # ---- charts by view mode ----
    if view_mode == "Overall Portfolio":
        c1, c2 = st.columns(2)
        with c1:
            chart_box("fa-chart-pie", "Sector Distribution", ch.sector_distribution_donut(df))
        with c2:
            chart_box("fa-chart-bar", "Budget Allocation by Sector", ch.budget_by_sector_horizontal(df))

        c3, c4 = st.columns(2)
        with c3:
            chart_box("fa-braille", "Progress Overview (Bubble)", ch.spi_cpi_project_bubble(df))
        with c4:
            chart_box("fa-chart-pie", "Status Breakdown", ch.status_breakdown_donut(df))

        c5, c6 = st.columns(2)
        with c5:
            chart_box("fa-braille", "SPI vs CPI Quadrant", ch.spi_cpi_sector_quadrant(df))
        with c6:
            chart_box("fa-circle-notch", "Quality & Safety Radar", ch.quality_safety_radar(df))

        c7, c8 = st.columns(2)
        with c7:
            chart_box("fa-chart-bar", "EV Metrics (BAC, PV, EV, AC)", ch.ev_metrics_by_sector(df))
        with c8:
            chart_box("fa-th", "Risk Heatmap", ch.risk_heatmap(df))

    elif view_mode == "Sector Analysis":
        sel = st.selectbox("Sector to analyze", sorted(df["sector"].dropna().unique().tolist()))
        sub = df[df["sector"] == sel]
        if sub.empty:
            st.markdown(sty.empty_state("No projects in this sector under current filters", ""), unsafe_allow_html=True)
        else:
            chart_box("fa-gauge-high", f"{sel} – Progress Gauges", ch.sector_gauges(sub))
            g1, g2 = st.columns(2)
            with g1:
                chart_box("fa-coins", "Budget vs Spent per Project", ch.budget_vs_spent_bar(sub))
            with g2:
                chart_box("fa-gauge", "SPI vs CPI by Project", ch.spi_cpi_bar(sub))

    else:  # Program Comparison
        prog_summary = df.groupby("program").agg(
            projects=("project_id", "count"), contract_value=("contract_value", "sum"),
            avg_spi=("spi", "mean"), avg_cpi=("cpi", "mean"), open_risks=("open_risks", "sum"),
        ).reset_index()
        g1, g2 = st.columns(2)
        with g1:
            fig = ch.budget_vs_spent_bar(df.assign(project_name=df["program"]))
            chart_box("fa-coins", "Contract Value by Program", fig)
        with g2:
            fig2 = ch.spi_cpi_bar(df.assign(project_name=df["program"]).groupby("program", as_index=False).agg(
                project_name=("program", "first"), spi=("spi", "mean"), cpi=("cpi", "mean")))
            chart_box("fa-gauge", "Avg SPI / CPI by Program", fig2)
        with st.container(border=True):
            st.markdown(sty.section_header("fas fa-table", "Program Summary"), unsafe_allow_html=True)
            st.dataframe(prog_summary, use_container_width=True, hide_index=True)

    # ---- project table ----
    with st.container(border=True):
        st.markdown(sty.section_header("fas fa-table-list", "Project Register"), unsafe_allow_html=True)
        table_cols = ["project_id", "project_name", "sector", "status", "priority", "risk_level",
                      "actual_progress", "spi", "cpi", "contract_value", "open_risks", "active_claims", "delay_days"]
        show_cols = [c for c in table_cols if c in df.columns]
        st.dataframe(
            df[show_cols].rename(columns={
                "project_id": "ID", "project_name": "Project", "sector": "Sector", "status": "Status",
                "priority": "Priority", "risk_level": "Risk", "actual_progress": "Progress %",
                "spi": "SPI", "cpi": "CPI", "contract_value": "Contract Value", "open_risks": "Risks",
                "active_claims": "Claims", "delay_days": "Delay (d)",
            }),
            use_container_width=True, hide_index=True,
        )


# ----------------------------------------------------------------------
# PROJECT DASHBOARD
# ----------------------------------------------------------------------

def render_project_dashboard(registry: pd.DataFrame, root: Path, project_id: str):
    row_df = registry[registry["project_id"].astype(str) == str(project_id)]
    if row_df.empty:
        st.warning("Selected project not found in registry.")
        return
    row = row_df.iloc[0]
    folder = str(row.get("project_folder") or row.get("project_id"))

    st.markdown(f"### {row.get('project_name', folder)}  &nbsp; {sty.status_badge(str(row.get('status','')))}", unsafe_allow_html=True)

    cards = [
        sty.kpi_card("Contract Value", money(row.get("contract_value")), icon="fa-file-invoice"),
        sty.kpi_card("Planned Progress", pct(row.get("planned_progress")), icon="fa-calendar-check"),
        sty.kpi_card("Actual Progress", pct(row.get("actual_progress")), icon="fa-hourglass-half"),
        sty.kpi_card("SPI", num(row.get("spi")), icon="fa-arrow-trend-down",
                      delta_type="positive" if float(row.get("spi") or 0) >= 1 else "negative"),
        sty.kpi_card("CPI", num(row.get("cpi")), icon="fa-arrow-trend-up",
                      delta_type="positive" if float(row.get("cpi") or 0) >= 1 else "negative"),
        sty.kpi_card("Open Risks", integer(row.get("open_risks")), icon="fa-shield",
                      delta_type="negative" if float(row.get("open_risks") or 0) > 0 else "positive"),
        sty.kpi_card("Active Claims", integer(row.get("active_claims")), icon="fa-gavel",
                      delta_type="negative" if float(row.get("active_claims") or 0) > 0 else "positive"),
        sty.kpi_card("Delay", f'{integer(row.get("delay_days"))}d', icon="fa-clock",
                      delta_type="negative" if float(row.get("delay_days") or 0) > 0 else "positive"),
        sty.kpi_card("Quality Score", num(row.get("quality_score"), 1), icon="fa-star"),
        sty.kpi_card("Safety Score", num(row.get("safety_score"), 1), icon="fa-helmet-safety"),
    ]
    st.markdown(sty.kpi_grid(cards), unsafe_allow_html=True)

    tabs = st.tabs([
        "📊 Overview", "🧩 WBS", "📋 Activities", "📈 S-Curve", "📄 Contract", "💰 EVM",
        "✉️ Letters", "⚠️ Risks", "⏱️ Delay / TIA", "⚖️ Claims", "🖥️ Output Studio",
    ])

    # ---------------- Overview ----------------
    with tabs[0]:
        ov1, ov2 = st.columns([1.3, 1])
        with ov1:
            with st.container(border=True):
                st.markdown(sty.section_header("fas fa-circle-info", "Project Information"), unsafe_allow_html=True)

                def _date_str(v):
                    if v is None or (isinstance(v, float) and pd.isna(v)) or pd.isna(v):
                        return "—"
                    try:
                        return pd.Timestamp(v).strftime("%Y-%m-%d")
                    except (TypeError, ValueError):
                        return str(v)

                info_rows = [
                    ("Sector", row.get("sector")), ("Program", row.get("program")),
                    ("Contractor", row.get("contractor")), ("Employer", row.get("employer")),
                    ("Consultant", row.get("consultant")), ("Location", row.get("location")),
                    ("Project Manager", row.get("project_manager")), ("Planning Engineer", row.get("planning_engineer")),
                    ("Start Date", _date_str(row.get("start_date"))), ("Finish Date", _date_str(row.get("finish_date"))),
                    ("Priority", row.get("priority")), ("Risk Level", row.get("risk_level")),
                    ("Team Size", integer(row.get("team_size"))), ("Equipment Units", integer(row.get("equipment_units"))),
                ]
                info_rows = [(k, "—" if (v is None or (isinstance(v, float) and pd.isna(v))) else str(v)) for k, v in info_rows]
                info_df = pd.DataFrame(info_rows, columns=["Field", "Value"])
                st.dataframe(info_df, use_container_width=True, hide_index=True)
        with ov2:
            with st.container(border=True):
                st.markdown(sty.section_header("fas fa-flag-checkered", "Milestones"), unsafe_allow_html=True)
                total_ms = row.get("milestones_total") or 0
                done_ms = row.get("milestones_completed") or 0
                try:
                    ratio = float(done_ms) / float(total_ms) if float(total_ms) else 0
                except (TypeError, ValueError):
                    ratio = 0
                st.progress(min(max(ratio, 0.0), 1.0), text=f"{integer(done_ms)} / {integer(total_ms)} milestones complete")
            with st.container(border=True):
                st.markdown(sty.section_header("fas fa-money-bill-wave", "Financial Snapshot"), unsafe_allow_html=True)
                st.markdown(sty.kpi_grid([
                    sty.kpi_card("BAC", money(row.get("bac")), icon="fa-bullseye"),
                    sty.kpi_card("BCWP (EV)", money(row.get("bcwp")), icon="fa-chart-line"),
                    sty.kpi_card("ACWP (AC)", money(row.get("acwp")), icon="fa-money-bill-wave"),
                    sty.kpi_card("BCWS (PV)", money(row.get("bcws")), icon="fa-calendar-check"),
                ]), unsafe_allow_html=True)

    # ---------------- WBS ----------------
    with tabs[1]:
        wbs = dl.load_module(str(root), folder, "wbs")
        if wbs.empty:
            st.markdown(sty.empty_state(
                "No wbs.csv found",
                f"Expected at <code>{folder}/wbs.csv</code> with columns: wbs_code, wbs_name, schedule_pct, performance_pct",
            ), unsafe_allow_html=True)
        else:
            wk1, wk2, wk3 = st.columns(3)
            wk1.metric("WBS Items", len(wbs))
            wk2.metric("Avg Schedule %", f"{wbs['schedule_pct'].mean():.1f}%")
            wk3.metric("Avg Performance %", f"{wbs['performance_pct'].mean():.1f}%")
            chart_box("fa-sitemap", "Schedule vs Performance by WBS", ch.wbs_chart(wbs))
            st.dataframe(wbs, use_container_width=True, hide_index=True)

    # ---------------- Activities ----------------
    with tabs[2]:
        acts = dl.load_module(str(root), folder, "activities")
        if acts.empty:
            st.markdown(sty.empty_state(
                "No activities.csv found", f"Expected at <code>{folder}/activities.csv</code>",
            ), unsafe_allow_html=True)
        else:
            critical = acts[acts["is_critical"] == "Yes"] if "is_critical" in acts.columns else pd.DataFrame()
            deviated = acts[acts["actual_progress"] < acts["planned_progress"]] if {"actual_progress", "planned_progress"}.issubset(acts.columns) else pd.DataFrame()
            rft = acts[acts["activity_name"].astype(str).str.contains("RFT", case=False, na=False)] if "activity_name" in acts.columns else pd.DataFrame()

            ak1, ak2, ak3, ak4 = st.columns(4)
            ak1.metric("Total Activities", len(acts))
            ak2.metric("On Critical Path", len(critical))
            ak3.metric("Behind Schedule", len(deviated))
            ak4.metric("RFT Activities", len(rft))

            chart_box("fa-chart-column", "Planned vs Actual Progress", ch.activities_progress_chart(acts))
            chart_box("fa-clock", "Total Float by Activity", ch.activities_float_chart(acts))

            sub_t1, sub_t2, sub_t3 = st.tabs(["All Activities", "Critical Path", "Behind Schedule"])
            with sub_t1:
                st.dataframe(acts, use_container_width=True, hide_index=True)
            with sub_t2:
                render_table_or_empty(critical, "No critical activities", "No activity is flagged is_critical = Yes.")
            with sub_t3:
                render_table_or_empty(deviated, "No deviated activities", "All activities are at or ahead of plan.")

    # ---------------- S-Curve ----------------
    with tabs[3]:
        cashflow = dl.get_cashflow(root, folder)
        if cashflow.empty:
            st.markdown(sty.empty_state(
                "No s_curve.csv found",
                f"Expected at <code>{folder}/s_curve.csv</code> with columns: months, monthly_planned, monthly_actual, monthly_invoiced",
            ), unsafe_allow_html=True)
        else:
            mode = st.radio("View", ["Cumulative", "Monthly"], horizontal=True, label_visibility="collapsed")
            chart_box("fa-chart-line", f"S-Curve ({mode})", ch.s_curve_chart(cashflow, cumulative=(mode == "Cumulative")))
            st.dataframe(cashflow.rename(columns={
                "period": "Period", "cash_in": "Actual ($)", "cash_out": "Planned ($)", "cash_invoiced": "Invoiced ($)",
            }), use_container_width=True, hide_index=True)

    # ---------------- Contract ----------------
    with tabs[4]:
        contracts = dl.load_module(str(root), folder, "contracts")
        payments = dl.load_module(str(root), folder, "payments")
        sub_c, sub_p = st.tabs(["Contracts", "Payments"])
        with sub_c:
            if contracts.empty:
                st.markdown(sty.empty_state("No contracts.csv found", f"Expected at <code>{folder}/contracts.csv</code>"), unsafe_allow_html=True)
            else:
                chart_box("fa-file-contract", "Contract Value vs Paid to Date", ch.contracts_value_bar(contracts))
                st.dataframe(contracts, use_container_width=True, hide_index=True)
        with sub_p:
            if payments.empty:
                st.markdown(sty.empty_state("No payments.csv found", f"Expected at <code>{folder}/payments.csv</code>"), unsafe_allow_html=True)
            else:
                chart_box("fa-money-check-dollar", "Certified vs Paid", ch.payments_certified_vs_paid(payments))
                st.dataframe(payments, use_container_width=True, hide_index=True)

    # ---------------- EVM ----------------
    with tabs[5]:
        evm = dl.compute_evm(row)
        st.markdown(sty.kpi_grid([
            sty.kpi_card("BAC", money(evm["bac"]), icon="fa-bullseye"),
            sty.kpi_card("PV (BCWS)", money(evm["pv"]), icon="fa-calendar-check"),
            sty.kpi_card("EV (BCWP)", money(evm["ev"]), icon="fa-chart-line"),
            sty.kpi_card("AC (ACWP)", money(evm["ac"]), icon="fa-money-bill-wave"),
            sty.kpi_card("SPI", num(evm["spi"]), icon="fa-arrow-trend-down",
                          delta_type="positive" if evm["spi"] >= 1 else "negative"),
            sty.kpi_card("CPI", num(evm["cpi"]), icon="fa-arrow-trend-up",
                          delta_type="positive" if evm["cpi"] >= 1 else "negative"),
            sty.kpi_card("SV (Schedule Var.)", money(evm["sv"]), icon="fa-scale-unbalanced",
                          delta_type="positive" if evm["sv"] >= 0 else "negative"),
            sty.kpi_card("CV (Cost Var.)", money(evm["cv"]), icon="fa-scale-unbalanced",
                          delta_type="positive" if evm["cv"] >= 0 else "negative"),
            sty.kpi_card("EAC", money(evm["eac"]), icon="fa-flag-checkered"),
            sty.kpi_card("ETC", money(evm["etc"]), icon="fa-hourglass-half"),
            sty.kpi_card("VAC", money(evm["vac"]), icon="fa-coins",
                          delta_type="positive" if evm["vac"] >= 0 else "negative"),
            sty.kpi_card("TCPI", num(evm["tcpi"]), icon="fa-gauge"),
        ]), unsafe_allow_html=True)
        chart_box("fa-chart-simple", "EVM Overview", ch.evm_bar(evm))

    # ---------------- Letters Intelligence ----------------
    with tabs[6]:
        lc = dl.load_optional(str(root), folder, "letters_contractor")
        lp = dl.load_optional(str(root), folder, "letters_pmo")
        lt1, lt2 = st.tabs(["Contractor Correspondence", "PMO / Engineer Correspondence"])
        with lt1:
            render_table_or_empty(lc, "No letters_contractor.csv found",
                                   f"Add <code>{folder}/letters_contractor.csv</code> with columns: ref, date, type, subject, risk_type, delay_risk, eot_potential, claim_strength, required_actions")
        with lt2:
            render_table_or_empty(lp, "No letters_pmo.csv found",
                                   f"Add <code>{folder}/letters_pmo.csv</code> with the same column structure as letters_contractor.csv")

    # ---------------- Risks ----------------
    with tabs[7]:
        risks = dl.load_optional(str(root), folder, "risks")
        render_table_or_empty(risks, "No risks.csv found",
                               f"Add <code>{folder}/risks.csv</code> with columns: id, risk, category, severity, status, mitigation")

    # ---------------- Delay / TIA ----------------
    with tabs[8]:
        delay = dl.load_optional(str(root), folder, "delay_events")
        render_table_or_empty(delay, "No delay_events.csv found",
                               f"Add <code>{folder}/delay_events.csv</code> with columns: event, responsibility, days, critical_path, eot_potential, status")

    # ---------------- Claims Intelligence ----------------
    with tabs[9]:
        claims = dl.load_optional(str(root), folder, "claims")
        clauses = dl.load_optional(str(root), folder, "clauses")
        ct1, ct2 = st.tabs(["Claim Opportunities", "Contract Clauses"])
        with ct1:
            render_table_or_empty(claims, "No claim_opportunities.csv found",
                                   f"Add <code>{folder}/claim_opportunities.csv</code> with columns: id, source_event, event_date, event_type, description, activity, matched_clause, entitlement_basis, notice_status, evidence_status, time_impact_relevance, cost_impact_relevance, claim_strength, recommended_action")
        with ct2:
            render_table_or_empty(clauses, "No contract_clauses.csv found",
                                   f"Add <code>{folder}/contract_clauses.csv</code> with the contract clause register")

    # ---------------- Output Studio ----------------
    with tabs[10]:
        with st.container(border=True):
            st.markdown(sty.section_header("fas fa-display", "Executive Summary"), unsafe_allow_html=True)
            summary_lines = [
                f"# {row.get('project_name', folder)} — Executive Summary",
                f"Generated: {now_str}",
                "",
                f"- Sector: {row.get('sector')}  |  Program: {row.get('program')}  |  Status: {row.get('status')}",
                f"- Contract Value: {money(row.get('contract_value'))}  |  Priority: {row.get('priority')}  |  Risk Level: {row.get('risk_level')}",
                f"- Progress: Planned {pct(row.get('planned_progress'))} vs Actual {pct(row.get('actual_progress'))}",
                f"- SPI: {num(row.get('spi'))}  |  CPI: {num(row.get('cpi'))}",
                f"- Open Risks: {integer(row.get('open_risks'))}  |  Active Claims: {integer(row.get('active_claims'))}  |  Delay: {integer(row.get('delay_days'))} days",
                f"- Certified: {money(row.get('certified_amount'))}  |  Paid: {money(row.get('paid_amount'))}",
                f"- Quality Score: {num(row.get('quality_score'),1)}  |  Safety Score: {num(row.get('safety_score'),1)}",
            ]
            summary_md = "\n".join(summary_lines)
            st.markdown(summary_md)
            st.download_button("⬇️ Download Executive Summary (.md)", summary_md.encode("utf-8"),
                                file_name=f"{folder}_executive_summary.md", mime="text/markdown")

        with st.container(border=True):
            st.markdown(sty.section_header("fas fa-file-export", "Export Raw Data"), unsafe_allow_html=True)
            e1, e2, e3 = st.columns(3)
            with e1:
                if not dl.load_module(str(root), folder, "wbs").empty:
                    st.download_button("WBS CSV", dl.load_module(str(root), folder, "wbs").to_csv(index=False).encode(), f"{folder}_wbs.csv", "text/csv")
            with e2:
                if not dl.load_module(str(root), folder, "activities").empty:
                    st.download_button("Activities CSV", dl.load_module(str(root), folder, "activities").to_csv(index=False).encode(), f"{folder}_activities.csv", "text/csv")
            with e3:
                cf = dl.get_cashflow(root, folder)
                if not cf.empty:
                    st.download_button("S-Curve CSV", cf.to_csv(index=False).encode(), f"{folder}_scurve.csv", "text/csv")


# ----------------------------------------------------------------------
# ROUTE
# ----------------------------------------------------------------------

if nav == "decision":
    render_decision_dashboard(registry, root)
else:
    render_project_dashboard(registry, root, nav)


# ----------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------

st.markdown(
    '<div style="text-align:center;color:#64748b;font-size:0.7rem;padding:18px 0 6px 0;">'
    'SAMCO – Project Intelligence Hub &copy; 2026 &nbsp;|&nbsp; Created &amp; Developed by '
    '<span style="color:#94a3b8;font-weight:600;">Engr. Ahmed Labib</span></div>',
    unsafe_allow_html=True,
)
