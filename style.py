"""
style.py
=========
Visual theme + reusable HTML snippet builders, ported 1:1 from the original
design tokens (colors, gradients, radii, badges) of the SAMCO Intelligence
Hub HTML. No data lives here - purely presentation.
"""

SECTOR_COLORS = {
    "Road Sector": "#3b82f6",
    "Bridges Sector": "#8b5cf6",
    "Building & Finishing": "#f59e0b",
    "Maintenance": "#10b981",
    "Tunnels": "#ec4899",
}
DEFAULT_SECTOR_COLOR = "#94a3b8"

STATUS_COLORS = {"Green": "#22c55e", "Amber": "#f59e0b", "Red": "#ef4444"}
DEFAULT_STATUS_COLOR = "#94a3b8"

STATUS_LABELS = {
    "Green": "Controlled Performance",
    "Amber": "Warning Performance",
    "Red": "Critical Performance",
}

BADGE_CLASS = {"Green": "badge-green", "Amber": "badge-amber", "Red": "badge-red"}

PRIORITY_COLORS = {"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#22c55e"}
RISK_COLORS = {"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#22c55e"}


def sector_color(sector: str) -> str:
    return SECTOR_COLORS.get(sector, DEFAULT_SECTOR_COLOR)


def status_color(status: str) -> str:
    return STATUS_COLORS.get(status, DEFAULT_STATUS_COLOR)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700;14..32,800;14..32,900&display=swap');

:root {
    --navy: #0F172A; --deep-blue: #1E3A8A; --electric: #2563EB; --cyan: #06B6D4;
    --teal: #14B8A6; --white: #FFFFFF; --bg: #0a0e1a; --card-bg: rgba(30, 41, 59, 0.4);
    --border: rgba(148, 163, 184, 0.1); --muted: #94a3b8; --amber: #F59E0B;
    --red: #DC2626; --green: #059669; --radius: 16px; --radius-lg: 24px;
    --shadow: 0 8px 32px rgba(0, 0, 0, 0.08); --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.12);
    --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

.stApp { background: var(--bg); color: #e2e8f0; }
section[data-testid="stSidebar"] { background: #0d1322; border-right: 1px solid var(--border); }
#MainMenu, footer { visibility: hidden; }

.header-banner {
    background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.08));
    border-radius: var(--radius-lg); padding: 20px 32px; margin-bottom: 18px;
    border: 1px solid rgba(59,130,246,0.15); display: flex; justify-content: space-between;
    align-items: center; flex-wrap: wrap; gap: 16px;
}
.header-banner .brand { display: flex; align-items: center; gap: 14px; }
.header-banner .custom-logo { height: 42px; width: auto; max-width: 140px; object-fit: contain; flex-shrink: 0; }
.header-banner .banner-title {
    font-size: 1.32rem; font-weight: 900; margin: 0; letter-spacing: -0.4px; line-height: 1.2;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.header-banner .banner-title .desg { font-size: 0.85rem; font-weight: 400; color: #94a3b8; -webkit-text-fill-color: #94a3b8; }
.header-banner .tagline { color: #94a3b8; font-size: 0.72rem; margin: 2px 0 0 0; font-weight: 500; }
.header-banner .meta { text-align: right; }
.header-banner .meta .label { color: #64748b; font-size: 0.7rem; margin: 0; }
.header-banner .meta .time { color: #e2e8f0; font-size: 0.95rem; font-weight: 600; margin: 2px 0 0 0; }
.header-banner .meta .phase {
    display: inline-block; font-size: 0.65rem; font-weight: 600; padding: 3px 12px;
    border-radius: 20px; background: rgba(245,158,11,0.15); color: var(--amber);
    border: 1px solid rgba(245,158,11,0.2); margin-top: 4px;
}

.kpi-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 12px; margin-bottom: 18px; }
.kpi-card {
    background: linear-gradient(145deg, rgba(30,41,59,0.7), rgba(15,23,42,0.8));
    border-radius: var(--radius); padding: 16px 18px 14px 18px; border-left: 4px solid var(--electric);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15); position: relative; overflow: hidden;
    transition: var(--transition);
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,0.25); }
.kpi-card .kpi-label { font-size: 0.65rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.6px; display: flex; align-items: center; gap: 5px; }
.kpi-card .kpi-label i { font-size: 0.7rem; color: #64748b; }
.kpi-card .kpi-value {
    font-size: 1.6rem; font-weight: 800; line-height: 1.2; margin-top: 2px;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kpi-card .kpi-delta { font-size: 0.65rem; font-weight: 600; padding: 2px 8px; border-radius: 12px; display: inline-block; margin-top: 4px; }
.kpi-card .kpi-delta.positive { background: rgba(34,197,94,0.15); color: #4ade80; }
.kpi-card .kpi-delta.negative { background: rgba(239,68,68,0.15); color: #f87171; }
.kpi-card .kpi-delta.neutral { background: rgba(148,163,184,0.1); color: #94a3b8; }
.kpi-card .kpi-badge {
    position: absolute; top: 10px; right: 10px; font-size: 0.5rem; font-weight: 700;
    padding: 2px 8px; border-radius: 12px; text-transform: uppercase; letter-spacing: 0.4px;
}
.kpi-card .kpi-badge.risk { background: rgba(239,68,68,0.15); color: #f87171; }
.kpi-card .kpi-badge.warning { background: rgba(251,191,36,0.15); color: #fbbf24; }
.kpi-card .kpi-badge.success { background: rgba(34,197,94,0.15); color: #4ade80; }

.section-card { background: var(--card-bg); border-radius: var(--radius); padding: 18px 22px 22px 22px; margin-bottom: 18px; border: 1px solid var(--border); }
.section-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.section-desc { font-size: 0.75rem; color: #94a3b8; margin-bottom: 12px; }

.controls-bar { background: var(--card-bg); border-radius: var(--radius); padding: 10px 18px; margin-bottom: 14px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
.scope-chip { font-size: 0.65rem; font-weight: 600; padding: 3px 12px; border-radius: 20px; background: rgba(245,158,11,0.12); color: var(--amber); border: 1px solid rgba(245,158,11,0.2); white-space: nowrap; display: inline-block; }
.filter-bar-label { font-size: 0.62rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 2px; }

.chart-card-title { font-size: 0.78rem; font-weight: 600; color: #e2e8f0; margin-bottom: 2px; display: flex; align-items: center; gap: 6px; }
.chart-card-title .icon { color: #60a5fa; }

div[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(30,41,59,0.3) !important; border-radius: var(--radius) !important; border-color: var(--border) !important; }

div[data-testid="stButton"] > button[kind="primary"] { background: var(--electric); border-color: var(--electric); color: #fff; font-weight: 500; }
div[data-testid="stButton"] > button[kind="secondary"] { background: rgba(148,163,184,0.08); border-color: rgba(148,163,184,0.15); color: #94a3b8; font-weight: 500; }
div[data-testid="stButton"] > button { border-radius: 8px; padding: 4px 14px; font-size: 0.78rem; }

.sector-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 12px; }
.sector-card { background: linear-gradient(145deg, rgba(30,41,59,0.5), rgba(15,23,42,0.6)); border-radius: var(--radius); padding: 14px 16px; border-left: 4px solid var(--electric); position: relative; transition: var(--transition); cursor: pointer; }
.sector-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
div[data-testid="stVerticalBlockBorderWrapper"] { transition: var(--transition); }

.meeting-panel { background: var(--card-bg); border-radius: var(--radius); padding: 12px 18px; margin-bottom: 14px; border: 1px solid var(--border); }
.meeting-panel.active { border-color: rgba(239,68,68,0.2); }
.meeting-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.live-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(239,68,68,0.15); color: #f87171; font-size: 0.7rem; font-weight: 700; padding: 3px 14px 3px 10px; border-radius: 20px; border: 1px solid rgba(239,68,68,0.2); }
.live-badge .pulse { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--red); animation: pulse-red 1.2s ease-in-out infinite; }
@keyframes pulse-red { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.35; transform: scale(0.8); } }
.meeting-agenda { display: grid; grid-template-columns: 1fr 1fr; gap: 3px 16px; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); font-size: 0.7rem; color: #94a3b8; }
.meeting-agenda .num { color: #64748b; }
.participant-chip { display: inline-flex; align-items: center; gap: 5px; background: rgba(96,165,250,0.12); color: #93c5fd; font-size: 0.68rem; font-weight: 600; padding: 3px 10px; border-radius: 14px; border: 1px solid rgba(96,165,250,0.2); margin: 2px 4px 2px 0; }
.participant-count { font-size: 0.65rem; color: #64748b; margin-left: 4px; }
.sector-card .sector-name { font-size: 0.85rem; font-weight: 700; color: #f1f5f9; }
.sector-card .sector-meta { display: flex; flex-wrap: wrap; gap: 3px 10px; margin-top: 5px; font-size: 0.65rem; color: #94a3b8; }
.sector-card .sector-meta .item { display: inline-flex; align-items: center; gap: 3px; }
.sector-card .sector-meta .val { font-weight: 600; color: #e2e8f0; }
.sector-card .sector-status { position: absolute; top: 8px; right: 10px; font-size: 0.55rem; font-weight: 600; padding: 2px 8px; border-radius: 12px; }
.sector-card .sector-status.green { background: rgba(34,197,94,0.15); color: #4ade80; }
.sector-card .sector-status.amber { background: rgba(251,191,36,0.15); color: #fbbf24; }
.sector-card .sector-status.red { background: rgba(239,68,68,0.15); color: #f87171; }

.badge { font-size: 0.65rem; font-weight: 600; padding: 2px 10px; border-radius: 12px; display: inline-block; }
.badge-green { background: rgba(34,197,94,0.15); color: #4ade80; }
.badge-amber { background: rgba(251,191,36,0.15); color: #fbbf24; }
.badge-red { background: rgba(239,68,68,0.15); color: #f87171; }
.badge-blue { background: rgba(59,130,246,0.15); color: #60a5fa; }
.badge-gray { background: rgba(148,163,184,0.12); color: #94a3b8; }

.empty-state { padding: 28px; text-align: center; color: #64748b; font-size: 0.85rem; border: 1px dashed var(--border); border-radius: var(--radius); }
.empty-state .ttl { color: #94a3b8; font-weight: 600; margin-bottom: 4px; }

div[data-testid="stMetricValue"] { color: #e2e8f0; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { background: rgba(148,163,184,0.06); border-radius: 8px 8px 0 0; color: #94a3b8; }
.stTabs [aria-selected="true"] { background: var(--electric) !important; color: white !important; }
</style>
"""

def load_custom_logo() -> str | None:
    """Looks for a user-supplied logo in assets/logo.(png|jpg|jpeg|svg) next to
    this file. Returns an <img> tag (base64 data-URI) ready to drop into the
    header banner, or None if no logo file is present - in which case the
    caller should fall back to SAMCO_LOGO_SVG."""
    import base64
    from pathlib import Path as _Path

    assets_dir = _Path(__file__).parent / "assets"
    mime_by_ext = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}
    for ext, mime in mime_by_ext.items():
        candidate = assets_dir / f"logo{ext}"
        if candidate.exists():
            try:
                data = candidate.read_bytes()
                b64 = base64.b64encode(data).decode("ascii")
                return f'<img class="custom-logo" src="data:{mime};base64,{b64}" alt="logo">'
            except OSError:
                return None
    return None


SAMCO_LOGO_SVG = """
<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="samcoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#60a5fa"/><stop offset="50%" stop-color="#a78bfa"/><stop offset="100%" stop-color="#f472b6"/>
    </linearGradient>
    <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#2563EB"/><stop offset="100%" stop-color="#06B6D4"/>
    </linearGradient>
  </defs>
  <rect x="8" y="8" width="84" height="44" rx="10" fill="rgba(37,99,235,0.08)" stroke="rgba(96,165,250,0.3)" stroke-width="1"/>
  <text x="50" y="42" font-family="Inter, sans-serif" font-size="20" font-weight="900" fill="url(#samcoGrad)" text-anchor="middle" letter-spacing="2">SAMCO</text>
  <line x1="15" y1="48" x2="85" y2="48" stroke="url(#lineGrad)" stroke-width="1.5" stroke-linecap="round"/>
</svg>
"""


def html_block(raw: str) -> str:
    """Collapse a multi-line HTML snippet into a single unbroken HTML
    block for Streamlit's Markdown renderer. Two pitfalls are neutralized:
    (1) any line starting with 4+ spaces is read as an indented *code*
    block (CommonMark), printing HTML as literal text; (2) a blank line
    (including whitespace-only, which happens when an interpolated value
    like {badge_html} is "") ends an HTML block early, fragmenting it.
    Stripping each line and dropping empties avoids both."""
    lines = [line.strip() for line in raw.strip().splitlines()]
    return "\n".join(line for line in lines if line)


def kpi_card(label: str, value: str, icon: str = "", delta: str = "", delta_type: str = "neutral",
             badge: str = "", badge_type: str = "info") -> str:
    """delta_type: 'positive' | 'negative' | 'neutral' -> sets border color + pill color,
    matching the original kpi-card / kpi-delta behavior exactly."""
    border_color = {"positive": "var(--green)", "negative": "var(--red)"}.get(delta_type, "var(--electric)")
    icon_html = f'<i class="fas {icon}"></i> ' if icon else ""
    badge_html = f'<span class="kpi-badge {badge_type}">{badge}</span>' if badge else ""
    delta_html = f'<span class="kpi-delta {delta_type}">{delta}</span>' if delta else ""
    return html_block(f"""
    <div class="kpi-card" style="border-left-color:{border_color}">
        {badge_html}
        <div class="kpi-label">{icon_html}{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """)


def sector_card(sector: str, n: int, value_m: float, avg_progress: float, avg_spi: float,
                 avg_cpi: float, total_risks: int, total_delay: int, avg_quality: float) -> str:
    """Mirrors the original renderSectorCards() status thresholds exactly:
    red if avgSPI<0.85 or avgCPI<0.85 or avgQuality<80; amber if <0.95/<0.95/<85; else green."""
    if avg_spi < 0.85 or avg_cpi < 0.85 or avg_quality < 80:
        status, status_label = "red", "Critical"
    elif avg_spi < 0.95 or avg_cpi < 0.95 or avg_quality < 85:
        status, status_label = "amber", "Warning"
    else:
        status, status_label = "green", "Healthy"
    color = sector_color(sector)
    return html_block(f"""
    <div class="sector-card" style="border-left-color:{color}">
        <span class="sector-status {status}">{status_label}</span>
        <div class="sector-name">{sector}</div>
        <div class="sector-meta">
            <span class="item"><i class="fas fa-building" style="font-size:0.55rem;"></i> <span class="val">{n}</span> projects</span>
            <span class="item"><i class="fas fa-dollar-sign" style="font-size:0.55rem;"></i> <span class="val">${value_m:.1f}M</span></span>
            <span class="item"><i class="fas fa-chart-simple" style="font-size:0.55rem;"></i> <span class="val">{avg_progress:.1f}%</span></span>
            <span class="item"><i class="fas fa-arrow-trend-down" style="font-size:0.55rem;"></i> <span class="val">{avg_spi:.2f}</span></span>
            <span class="item"><i class="fas fa-arrow-trend-up" style="font-size:0.55rem;"></i> <span class="val">{avg_cpi:.2f}</span></span>
            <span class="item"><i class="fas fa-shield" style="font-size:0.55rem;"></i> <span class="val">{total_risks}</span></span>
            <span class="item"><i class="fas fa-clock" style="font-size:0.55rem;"></i> <span class="val">{total_delay}d</span></span>
        </div>
    </div>
    """)


def kpi_grid(cards_html: list[str]) -> str:
    return f'<div class="kpi-grid">{"".join(cards_html)}</div>'


def badge(text: str, kind: str = "gray") -> str:
    return f'<span class="badge badge-{kind}">{text}</span>'


def status_badge(status: str) -> str:
    return badge(STATUS_LABELS.get(status, status), BADGE_CLASS.get(status, "badge-gray"))


def section_header(icon: str, title: str, desc: str = "") -> str:
    desc_html = f'<div class="section-desc">{desc}</div>' if desc else ""
    return f'<div class="section-title"><i class="{icon}"></i> {title}</div>{desc_html}'


def empty_state(title: str, hint: str) -> str:
    return html_block(f"""
    <div class="empty-state">
        <div class="ttl">{title}</div>
        <div>{hint}</div>
    </div>
    """)


PLOTLY_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0", size=11),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(color="#e2e8f0")),
    margin=dict(t=50, b=50, l=50, r=30),
)
GRID_COLOR = "rgba(148,163,184,0.1)"
