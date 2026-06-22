"""
charts.py
==========
All Plotly figure builders. Every function takes a DataFrame and returns a
go.Figure - there is no embedded sample/demo data in this module.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from style import PLOTLY_LAYOUT_BASE, GRID_COLOR, sector_color, status_color


def _layout(**overrides) -> dict:
    layout = dict(PLOTLY_LAYOUT_BASE)
    layout.update(overrides)
    return layout


def sector_distribution_donut(projects: pd.DataFrame) -> go.Figure:
    counts = projects["sector"].value_counts()
    colors = [sector_color(s) for s in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.65,
        marker=dict(colors=colors, line=dict(color="rgba(15,23,42,0.8)", width=3)),
        textinfo="label+percent", textfont=dict(size=11, color="#e2e8f0"),
    ))
    fig.update_layout(**_layout(
        height=330, showlegend=False,
        annotations=[dict(text=f"<b>{len(projects)}</b><br>Projects", x=0.5, y=0.5,
                           font=dict(size=16, color="#e2e8f0"), showarrow=False)],
    ))
    return fig


def budget_by_sector_horizontal(projects: pd.DataFrame) -> go.Figure:
    s = projects.groupby("sector")["contract_value"].sum().sort_values(ascending=True) / 1e6
    colors = [sector_color(sec) for sec in s.index]
    fig = go.Figure(go.Bar(
        y=s.index, x=s.values, orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.1)", width=1)),
        text=[f"${v:.1f}M" for v in s.values], textposition="outside",
        textfont=dict(color="#e2e8f0", size=10),
    ))
    fig.update_layout(**_layout(height=330, showlegend=False,
                                 xaxis=dict(title="Budget ($M)", gridcolor=GRID_COLOR, zeroline=False),
                                 yaxis=dict(showgrid=False)))
    return fig


def spi_cpi_project_bubble(projects: pd.DataFrame) -> go.Figure:
    sizes = (projects["contract_value"] / 5_000_000).clip(10, 50)
    colors = [sector_color(s) for s in projects["sector"]]
    fig = go.Figure(go.Scatter(
        x=projects["spi"], y=projects["cpi"], mode="markers", text=projects["project_name"],
        hovertemplate="<b>%{text}</b><br>SPI: %{x:.2f}<br>CPI: %{y:.2f}<extra></extra>",
        marker=dict(size=sizes, color=colors, opacity=0.8, line=dict(color="rgba(255,255,255,0.2)", width=1)),
    ))
    fig.update_layout(**_layout(
        height=330, showlegend=False,
        xaxis=dict(title="SPI", range=[0.6, 1.2], gridcolor=GRID_COLOR),
        yaxis=dict(title="CPI", range=[0.6, 1.2], gridcolor=GRID_COLOR),
        shapes=[
            dict(type="line", x0=0.6, x1=1.2, y0=1, y1=1, line=dict(color="rgba(148,163,184,0.3)", dash="dash")),
            dict(type="line", x0=1, x1=1, y0=0.6, y1=1.2, line=dict(color="rgba(148,163,184,0.3)", dash="dash")),
        ],
    ))
    return fig


def status_breakdown_donut(projects: pd.DataFrame) -> go.Figure:
    counts = projects["status"].value_counts()
    colors = [status_color(s) for s in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.6, sort=False,
        marker=dict(colors=colors, line=dict(color="rgba(15,23,42,0.8)", width=2)),
        textinfo="label+percent", textfont=dict(size=11, color="#e2e8f0"),
    ))
    fig.update_layout(**_layout(height=330, showlegend=True,
                                 legend=dict(orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5,
                                             font=dict(color="#94a3b8"))))
    return fig


def spi_cpi_sector_quadrant(projects: pd.DataFrame) -> go.Figure:
    g = projects.groupby("sector").agg(spi=("spi", "mean"), cpi=("cpi", "mean"),
                                        value=("contract_value", "sum")).reset_index()
    fig = go.Figure()
    for _, row in g.iterrows():
        size = max(20, min(50, row["value"] / 5_000_000))
        fig.add_trace(go.Scatter(
            x=[row["spi"]], y=[row["cpi"]], mode="markers+text", name=row["sector"],
            text=[row["sector"]], textposition="top center", textfont=dict(color="#e2e8f0", size=9),
            marker=dict(size=size, color=sector_color(row["sector"]),
                        line=dict(color="rgba(255,255,255,0.3)", width=2), opacity=0.8),
        ))
    fig.update_layout(**_layout(
        height=330,
        xaxis=dict(title="SPI", range=[0.6, 1.2], gridcolor=GRID_COLOR),
        yaxis=dict(title="CPI", range=[0.6, 1.2], gridcolor=GRID_COLOR),
        shapes=[
            dict(type="line", x0=0.6, x1=1.2, y0=1, y1=1, line=dict(color="rgba(148,163,184,0.3)", dash="dash")),
            dict(type="line", x0=1, x1=1, y0=0.6, y1=1.2, line=dict(color="rgba(148,163,184,0.3)", dash="dash")),
        ],
        annotations=[
            dict(x=1.15, y=1.15, text="On Track", showarrow=False, font=dict(color="#4ade80", size=10)),
            dict(x=0.85, y=1.15, text="Over Budget", showarrow=False, font=dict(color="#f87171", size=10)),
            dict(x=1.15, y=0.85, text="Behind Schedule", showarrow=False, font=dict(color="#fbbf24", size=10)),
            dict(x=0.85, y=0.85, text="Critical", showarrow=False, font=dict(color="#ef4444", size=10)),
        ],
    ))
    return fig


def quality_safety_radar(projects: pd.DataFrame) -> go.Figure:
    g = projects.groupby("sector").agg(quality=("quality_score", "mean"), safety=("safety_score", "mean"))
    sectors = g.index.tolist()
    quality = g["quality"].tolist() + [g["quality"].iloc[0]] if sectors else []
    safety = g["safety"].tolist() + [g["safety"].iloc[0]] if sectors else []
    theta = sectors + [sectors[0]] if sectors else []
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=quality, theta=theta, fill="toself", name="Quality Score",
                                   fillcolor="rgba(59,130,246,0.2)", line=dict(color="#3b82f6", width=2)))
    fig.add_trace(go.Scatterpolar(r=safety, theta=theta, fill="toself", name="Safety Score",
                                   fillcolor="rgba(16,185,129,0.2)", line=dict(color="#10b981", width=2)))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[60, 100], tickfont=dict(color="#94a3b8"),
                                    gridcolor=GRID_COLOR),
                   angularaxis=dict(tickfont=dict(color="#e2e8f0")), bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)", height=330,
        font=dict(family="Inter, sans-serif", color="#e2e8f0", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5,
                    font=dict(color="#e2e8f0")),
        margin=dict(t=40, b=40, l=60, r=60),
    )
    return fig


def ev_metrics_by_sector(projects: pd.DataFrame) -> go.Figure:
    g = projects.groupby("sector").agg(bac=("bac", "sum"), pv=("bcws", "sum"),
                                        ev=("bcwp", "sum"), ac=("acwp", "sum")) / 1e6
    fig = go.Figure()
    fig.add_bar(x=g.index, y=g["bac"], name="BAC", marker_color="rgba(148,163,184,0.4)")
    fig.add_bar(x=g.index, y=g["pv"], name="PV", marker_color="rgba(59,130,246,0.6)")
    fig.add_bar(x=g.index, y=g["ev"], name="EV", marker_color="rgba(16,185,129,0.7)")
    fig.add_bar(x=g.index, y=g["ac"], name="AC", marker_color="rgba(239,68,68,0.6)")
    fig.update_layout(**_layout(barmode="group", height=330,
                                 xaxis=dict(showgrid=False),
                                 yaxis=dict(title="Value ($M)", gridcolor=GRID_COLOR)))
    return fig


def risk_heatmap(projects: pd.DataFrame) -> go.Figure:
    levels = ["Low", "Medium", "High", "Critical"]
    sectors = sorted(projects["sector"].dropna().unique().tolist())
    z = [[int(((projects["sector"] == s) & (projects["risk_level"] == lvl)).sum()) for lvl in levels] for s in sectors]
    fig = go.Figure(go.Heatmap(
        z=z, x=levels, y=sectors,
        colorscale=[[0, "rgba(34,197,94,0.3)"], [0.33, "rgba(251,191,36,0.5)"],
                    [0.66, "rgba(239,68,68,0.7)"], [1, "rgba(153,27,27,0.9)"]],
        text=z, texttemplate="%{text}", textfont=dict(color="#e2e8f0", size=13),
        showscale=False,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=330,
        font=dict(family="Inter, sans-serif", color="#e2e8f0", size=11),
        xaxis=dict(showgrid=False, tickfont=dict(color="#e2e8f0")),
        yaxis=dict(showgrid=False, tickfont=dict(color="#e2e8f0")),
        margin=dict(t=20, b=40, l=110, r=20),
    )
    return fig


def sector_distribution_pie(projects: pd.DataFrame) -> go.Figure:
    counts = projects["sector"].value_counts()
    colors = [sector_color(s) for s in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="#0a0e1a", width=2)),
        textfont=dict(color="#e2e8f0", size=11),
    ))
    fig.update_layout(**_layout(height=320, showlegend=True))
    return fig


def status_breakdown_pie(projects: pd.DataFrame) -> go.Figure:
    counts = projects["status"].value_counts()
    colors = [status_color(s) for s in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="#0a0e1a", width=2)),
        textfont=dict(color="#e2e8f0", size=11),
    ))
    fig.update_layout(**_layout(height=320, showlegend=True))
    return fig


def budget_vs_spent_bar(projects: pd.DataFrame) -> go.Figure:
    names = projects["project_name"]
    fig = go.Figure()
    fig.add_bar(x=names, y=projects["contract_value"] / 1e6, name="Budget ($M)",
                marker_color="rgba(59,130,246,0.65)")
    fig.add_bar(x=names, y=projects["acwp"] / 1e6, name="Spent ($M)",
                marker_color="rgba(239,68,68,0.65)")
    fig.update_layout(**_layout(barmode="group", height=340,
                                 xaxis=dict(tickangle=-25, gridcolor=GRID_COLOR),
                                 yaxis=dict(title="$M", gridcolor=GRID_COLOR)))
    return fig


def spi_cpi_bar(projects: pd.DataFrame) -> go.Figure:
    names = projects["project_name"]
    fig = go.Figure()
    fig.add_bar(x=names, y=projects["spi"], name="SPI", marker_color="rgba(59,130,246,0.65)")
    fig.add_bar(x=names, y=projects["cpi"], name="CPI", marker_color="rgba(16,185,129,0.65)")
    fig.add_hline(y=1.0, line_dash="dash", line_color="rgba(148,163,184,0.5)")
    fig.update_layout(**_layout(barmode="group", height=340,
                                 xaxis=dict(tickangle=-25, gridcolor=GRID_COLOR),
                                 yaxis=dict(range=[0, max(1.5, float(pd.concat([projects['spi'], projects['cpi']]).max() or 1.5) + 0.1)],
                                            gridcolor=GRID_COLOR)))
    return fig


def progress_bubble(projects: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=projects["planned_progress"], y=projects["actual_progress"],
        mode="markers+text", text=projects["project_name"], textposition="top center",
        textfont=dict(size=9, color="#94a3b8"),
        marker=dict(
            size=(projects["contract_value"] / projects["contract_value"].max() * 40 + 12)
            if projects["contract_value"].max() else 20,
            color=[status_color(s) for s in projects["status"]],
            line=dict(width=1, color="#0a0e1a"), opacity=0.85,
        ),
    ))
    max_v = float(max(projects["planned_progress"].max(), projects["actual_progress"].max(), 10)) + 10
    fig.add_shape(type="line", x0=0, y0=0, x1=max_v, y1=max_v,
                  line=dict(color="rgba(148,163,184,0.4)", dash="dash"))
    fig.update_layout(**_layout(height=360,
                                 xaxis=dict(title="Planned Progress (%)", gridcolor=GRID_COLOR),
                                 yaxis=dict(title="Actual Progress (%)", gridcolor=GRID_COLOR),
                                 showlegend=False))
    return fig


def risk_claims_scatter(projects: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=projects["open_risks"], y=projects["active_claims"],
        mode="markers+text", text=projects["project_name"], textposition="top center",
        textfont=dict(size=9, color="#94a3b8"),
        marker=dict(size=14, color=[status_color(s) for s in projects["status"]],
                    line=dict(width=1, color="#0a0e1a")),
    ))
    fig.update_layout(**_layout(height=340,
                                 xaxis=dict(title="Open Risks", gridcolor=GRID_COLOR),
                                 yaxis=dict(title="Active Claims", gridcolor=GRID_COLOR),
                                 showlegend=False))
    return fig


def sector_gauges(projects: pd.DataFrame) -> go.Figure:
    traces = []
    n = len(projects)
    for i, (_, p) in enumerate(projects.iterrows()):
        color = sector_color(p.get("sector", ""))
        traces.append(go.Indicator(
            mode="gauge+number", value=float(p.get("actual_progress", 0) or 0),
            title=dict(text=str(p.get("project_name", ""))[:14], font=dict(size=9, color="#94a3b8")),
            number=dict(suffix="%", font=dict(size=16, color="#e2e8f0")),
            gauge=dict(axis=dict(range=[0, 100], tickfont=dict(color="#94a3b8")),
                       bar=dict(color=color), bgcolor="rgba(0,0,0,0)", borderwidth=0,
                       steps=[dict(range=[0, 33], color="rgba(239,68,68,0.1)"),
                              dict(range=[33, 66], color="rgba(251,191,36,0.1)"),
                              dict(range=[66, 100], color="rgba(34,197,94,0.1)")]),
            domain=dict(row=i // 3, column=i % 3),
        ))
    fig = go.Figure(traces)
    fig.update_layout(**_layout(
        grid=dict(rows=max(1, -(-n // 3)), columns=3, pattern="independent"),
        height=160 * max(1, -(-n // 3)) + 40))
    return fig


def wbs_chart(wbs: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=wbs["wbs_name"], y=wbs["schedule_pct"], name="Schedule %",
                marker_color="rgba(59,130,246,0.65)")
    fig.add_bar(x=wbs["wbs_name"], y=wbs["performance_pct"], name="Performance %",
                marker_color="rgba(16,185,129,0.65)")
    fig.update_layout(**_layout(barmode="group", height=360,
                                 xaxis=dict(tickangle=-20, gridcolor=GRID_COLOR),
                                 yaxis=dict(range=[0, 105], gridcolor=GRID_COLOR)))
    return fig


def activities_float_chart(activities: pd.DataFrame) -> go.Figure:
    colors = ["#ef4444" if c == "Yes" else "#3b82f6" for c in activities.get("is_critical", [])]
    fig = go.Figure(go.Bar(
        x=activities["activity_name"], y=activities["total_float_days"],
        marker_color=colors,
    ))
    fig.add_hline(y=0, line_color="rgba(148,163,184,0.4)")
    fig.update_layout(**_layout(height=340,
                                 xaxis=dict(tickangle=-25, gridcolor=GRID_COLOR),
                                 yaxis=dict(title="Total Float (days)", gridcolor=GRID_COLOR),
                                 showlegend=False))
    return fig


def activities_progress_chart(activities: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=activities["activity_name"], y=activities["planned_progress"], name="Planned %",
                marker_color="rgba(148,163,184,0.5)")
    fig.add_bar(x=activities["activity_name"], y=activities["actual_progress"], name="Actual %",
                marker_color="rgba(59,130,246,0.7)")
    fig.update_layout(**_layout(barmode="group", height=340,
                                 xaxis=dict(tickangle=-25, gridcolor=GRID_COLOR),
                                 yaxis=dict(range=[0, 105], gridcolor=GRID_COLOR)))
    return fig


def s_curve_chart(cashflow: pd.DataFrame, cumulative: bool = True) -> go.Figure:
    df = cashflow.copy()
    if cumulative:
        planned = df["cash_out"].cumsum() / 1e6
        actual = df["cash_in"].cumsum() / 1e6
        invoiced = df["cash_invoiced"].cumsum() / 1e6
    else:
        planned = df["cash_out"] / 1e6
        actual = df["cash_in"] / 1e6
        invoiced = df["cash_invoiced"] / 1e6

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["period"], y=planned, name="Planned", mode="lines+markers",
                              line=dict(color="#94a3b8", width=2)))
    fig.add_trace(go.Scatter(x=df["period"], y=actual, name="Actual", mode="lines+markers",
                              line=dict(color="#2563EB", width=2.5)))
    fig.add_trace(go.Scatter(x=df["period"], y=invoiced, name="Invoiced", mode="lines+markers",
                              line=dict(color="#14B8A6", width=2, dash="dot")))
    fig.update_layout(**_layout(height=360,
                                 xaxis=dict(title="Period", gridcolor=GRID_COLOR),
                                 yaxis=dict(title="$ Millions", gridcolor=GRID_COLOR)))
    return fig


def contracts_value_bar(contracts: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=contracts["package"], y=contracts["original_value"] / 1e6, name="Original Value",
                marker_color="rgba(59,130,246,0.65)")
    fig.add_bar(x=contracts["package"], y=contracts["paid_to_date"] / 1e6, name="Paid to Date",
                marker_color="rgba(16,185,129,0.65)")
    fig.update_layout(**_layout(barmode="group", height=340,
                                 xaxis=dict(tickangle=-15, gridcolor=GRID_COLOR),
                                 yaxis=dict(title="$M", gridcolor=GRID_COLOR)))
    return fig


def payments_certified_vs_paid(payments: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=payments["invoice_no"], y=payments["certified_amount"] / 1e6, name="Certified",
                marker_color="rgba(59,130,246,0.65)")
    fig.add_bar(x=payments["invoice_no"], y=payments["paid_amount"] / 1e6, name="Paid",
                marker_color="rgba(16,185,129,0.65)")
    fig.update_layout(**_layout(barmode="group", height=340,
                                 xaxis=dict(tickangle=-25, gridcolor=GRID_COLOR),
                                 yaxis=dict(title="$M", gridcolor=GRID_COLOR)))
    return fig


def evm_bar(evm: dict) -> go.Figure:
    labels = ["BAC", "PV (BCWS)", "EV (BCWP)", "AC (ACWP)", "EAC"]
    values = [evm["bac"], evm["pv"], evm["ev"], evm["ac"], evm["eac"]]
    colors = ["#94a3b8", "#3b82f6", "#22c55e", "#ef4444", "#a78bfa"]
    fig = go.Figure(go.Bar(x=labels, y=[v / 1e6 for v in values], marker_color=colors))
    fig.update_layout(**_layout(height=320, showlegend=False,
                                 yaxis=dict(title="$M", gridcolor=GRID_COLOR)))
    return fig
