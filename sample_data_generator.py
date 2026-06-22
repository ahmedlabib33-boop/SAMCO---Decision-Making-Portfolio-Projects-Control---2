"""
sample_data_generator.py
=========================
First-run onboarding only. If PROJECTS_ROOT has no project_registry.csv,
this writes a complete, realistic 5-project sample dataset to disk in the
exact schema the app expects. From that point on, the app reads it through
the normal data_loader.py file-based pipeline exactly like any real project
the user adds - there is no separate "demo mode" code path.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

SAMPLE_PROJECTS = [
    dict(project_id="PROJ_A", project_name="Project Alpha", project_folder="PROJ_A",
         sector="Building & Finishing", contractor="Contractor A", employer="SAMCO Holding",
         consultant="Consultant Partners LLC", location="New Capital, Cairo",
         project_manager="M. El-Sayed", planning_engineer="A. Labib",
         contract_value=219786025, start_date="2025-09-11", finish_date="2027-10-31",
         status="Amber", planned_progress=42.5, actual_progress=38.0, spi=0.89, cpi=0.95,
         bac=219786025, bcwp=83518689, acwp=87914410, bcws=93409060,
         open_risks=12, high_risks=5, active_claims=6, claimed_amount=18300000,
         delay_days=42, certified_amount=92100000, paid_amount=78400000,
         quality_score=82.5, safety_score=91.0, priority="High", risk_level="High",
         program="Alpha", team_size=245, equipment_units=38,
         milestones_total=12, milestones_completed=7),
    dict(project_id="PROJ_B", project_name="Project Beta", project_folder="PROJ_B",
         sector="Road Sector", contractor="Contractor C", employer="SAMCO Holding",
         consultant="Consultant Partners LLC", location="6th of October City",
         project_manager="H. Fathy", planning_engineer="N. Adel",
         contract_value=145000000, start_date="2026-01-01", finish_date="2027-03-31",
         status="Green", planned_progress=35.0, actual_progress=36.5, spi=1.04, cpi=0.98,
         bac=145000000, bcwp=52925000, acwp=54000000, bcws=50887500,
         open_risks=5, high_risks=1, active_claims=2, claimed_amount=4500000,
         delay_days=8, certified_amount=53200000, paid_amount=51000000,
         quality_score=88.0, safety_score=94.5, priority="Critical", risk_level="Medium",
         program="Beta", team_size=180, equipment_units=42,
         milestones_total=10, milestones_completed=6),
    dict(project_id="PROJ_C", project_name="Project Gamma", project_folder="PROJ_C",
         sector="Bridges Sector", contractor="Contractor D", employer="SAMCO Holding",
         consultant="Consultant Partners LLC", location="Greater Cairo Ring Road",
         project_manager="K. Mostafa", planning_engineer="R. Hany",
         contract_value=187000000, start_date="2025-08-15", finish_date="2027-12-31",
         status="Amber", planned_progress=48.0, actual_progress=42.0, spi=0.88, cpi=0.92,
         bac=187000000, bcwp=78540000, acwp=85370000, bcws=89760000,
         open_risks=9, high_risks=4, active_claims=4, claimed_amount=12800000,
         delay_days=35, certified_amount=82000000, paid_amount=71500000,
         quality_score=85.0, safety_score=88.0, priority="High", risk_level="High",
         program="Gamma", team_size=320, equipment_units=55,
         milestones_total=14, milestones_completed=8),
    dict(project_id="PROJ_D", project_name="Project Delta", project_folder="PROJ_D",
         sector="Maintenance", contractor="Contractor F", employer="SAMCO Holding",
         consultant="Consultant Partners LLC", location="Alexandria Desert Road",
         project_manager="S. Tarek", planning_engineer="D. Younis",
         contract_value=78000000, start_date="2026-02-01", finish_date="2027-01-31",
         status="Green", planned_progress=25.0, actual_progress=27.0, spi=1.08, cpi=1.02,
         bac=78000000, bcwp=21060000, acwp=20647000, bcws=19500000,
         open_risks=3, high_risks=0, active_claims=1, claimed_amount=1200000,
         delay_days=3, certified_amount=21500000, paid_amount=21000000,
         quality_score=92.0, safety_score=97.0, priority="Medium", risk_level="Low",
         program="Delta", team_size=95, equipment_units=22,
         milestones_total=8, milestones_completed=6),
    dict(project_id="PROJ_E", project_name="Project Epsilon", project_folder="PROJ_E",
         sector="Tunnels", contractor="Contractor G", employer="SAMCO Holding",
         consultant="Consultant Partners LLC", location="Ain Sokhna Corridor",
         project_manager="O. Gaber", planning_engineer="Y. Adham",
         contract_value=320000000, start_date="2025-05-01", finish_date="2028-06-30",
         status="Red", planned_progress=32.0, actual_progress=24.0, spi=0.75, cpi=0.82,
         bac=320000000, bcwp=76800000, acwp=93658537, bcws=102400000,
         open_risks=18, high_risks=8, active_claims=7, claimed_amount=32500000,
         delay_days=68, certified_amount=82000000, paid_amount=68000000,
         quality_score=76.0, safety_score=82.0, priority="Critical", risk_level="Critical",
         program="Omega", team_size=450, equipment_units=72,
         milestones_total=16, milestones_completed=5),
]

WBS_TEMPLATES = {
    "PROJ_A": [
        ("1.1", "Project Management Setup", 95, 90), ("1.2", "Site Preparation", 85, 80),
        ("2.1", "Foundation Works", 70, 65), ("2.2", "Structural Frame", 55, 50),
        ("3.1", "MEP Installation", 40, 35), ("3.2", "Finishing Works", 25, 20),
        ("4.1", "External Works", 15, 10),
    ],
    "PROJ_B": [
        ("1.1", "Mobilization & Setup", 100, 100), ("2.1", "Earthworks", 90, 92),
        ("2.2", "Sub-base Preparation", 80, 82), ("3.1", "Paving Operations", 65, 68),
        ("3.2", "Surface Course", 50, 52), ("4.1", "Finishing & Marking", 30, 32),
    ],
    "PROJ_C": [
        ("1.1", "Mobilization & Logistics", 90, 85), ("2.1", "Pile Foundations", 75, 70),
        ("2.2", "Pier Construction", 60, 55), ("3.1", "Deck Construction", 45, 40),
        ("3.2", "Bridge Systems", 30, 25), ("4.1", "Finishing & Testing", 15, 10),
    ],
    "PROJ_D": [
        ("1.1", "Mobilization & Planning", 100, 100), ("2.1", "Inspection & Assessment", 90, 92),
        ("2.2", "Repair Works", 75, 78), ("3.1", "Upgrade Works", 55, 58),
        ("3.2", "Testing & Commissioning", 35, 38), ("4.1", "Final Handover", 15, 18),
    ],
    "PROJ_E": [
        ("1.1", "Mobilization & Shaft Setup", 85, 75), ("2.1", "Shaft Excavation", 65, 55),
        ("2.2", "Tunnel Boring", 45, 35), ("3.1", "Tunnel Lining", 30, 20),
        ("3.2", "MEP & Systems", 18, 10), ("4.1", "Finishing & Testing", 8, 5),
    ],
}

ACTIVITIES_TEMPLATES = {
    "PROJ_A": [
        ("A-101", "Project Mobilization", "1.1", "2025-09-11", "2025-09-25", "2025-09-11", "2025-09-26", "2025-09-11", "2025-09-26", 100, 100, 5, 0, "No"),
        ("A-102", "Site Preparation", "1.2", "2025-09-26", "2025-10-15", "2025-09-26", "2025-10-18", "2025-09-26", "2025-10-18", 100, 95, 8, -3, "Yes"),
        ("A-103", "Foundation Excavation", "2.1", "2025-10-15", "2025-11-10", "2025-10-16", "2025-11-15", "2025-10-16", "2025-11-20", 80, 65, 12, -10, "Yes"),
        ("A-104", "Structural Frame", "2.2", "2025-11-10", "2026-01-20", "2025-11-16", "", "2025-11-16", "2026-02-05", 60, 45, 15, -16, "Yes"),
        ("A-105", "MEP Installation", "3.1", "2026-01-20", "2026-03-15", "", "", "2026-02-05", "2026-04-10", 30, 15, 10, -26, "Yes"),
        ("A-106", "Finishing Works", "3.2", "2026-03-15", "2026-05-15", "", "", "2026-04-10", "2026-06-20", 20, 8, 10, -36, "Yes"),
        ("A-107", "External Works RFT", "4.1", "2026-05-15", "2026-07-15", "", "", "2026-06-20", "2026-08-20", 10, 3, 8, -36, "No"),
    ],
    "PROJ_B": [
        ("B-101", "Mobilization & Setup", "1.1", "2026-01-01", "2026-01-15", "2026-01-01", "2026-01-14", "2026-01-01", "2026-01-14", 100, 100, 5, 1, "No"),
        ("B-102", "Earthworks", "2.1", "2026-01-15", "2026-02-20", "2026-01-14", "2026-02-18", "2026-01-14", "2026-02-18", 100, 100, 10, 2, "No"),
        ("B-103", "Sub-base Preparation", "2.2", "2026-02-20", "2026-03-20", "2026-02-18", "2026-03-18", "2026-02-18", "2026-03-18", 100, 100, 12, 2, "No"),
        ("B-104", "Paving Operations", "3.1", "2026-03-20", "2026-05-10", "2026-03-18", "", "2026-03-18", "2026-05-08", 65, 70, 18, 2, "No"),
        ("B-105", "Surface Course", "3.2", "2026-05-10", "2026-06-20", "", "", "2026-05-08", "2026-06-18", 50, 55, 15, 2, "No"),
        ("B-106", "Finishing & Marking RFT", "4.1", "2026-06-20", "2026-07-31", "", "", "2026-06-18", "2026-07-29", 30, 35, 10, 2, "No"),
    ],
    "PROJ_C": [
        ("C-101", "Mobilization & Logistics", "1.1", "2025-08-15", "2025-09-05", "2025-08-15", "2025-09-10", "2025-08-15", "2025-09-10", 100, 95, 6, -5, "Yes"),
        ("C-102", "Pile Foundations", "2.1", "2025-09-05", "2025-10-25", "2025-09-10", "2025-11-05", "2025-09-10", "2025-11-10", 75, 60, 15, -16, "Yes"),
        ("C-103", "Pier Construction", "2.2", "2025-10-25", "2026-01-10", "2025-11-05", "", "2025-11-05", "2026-01-30", 60, 45, 18, -20, "Yes"),
        ("C-104", "Deck Construction", "3.1", "2026-01-10", "2026-03-20", "", "", "2026-01-30", "2026-04-15", 45, 30, 20, -26, "Yes"),
        ("C-105", "Bridge Systems", "3.2", "2026-03-20", "2026-05-20", "", "", "2026-04-15", "2026-06-30", 30, 18, 14, -41, "Yes"),
        ("C-106", "Finishing & Testing RFT", "4.1", "2026-05-20", "2026-07-31", "", "", "2026-06-30", "2026-09-15", 15, 5, 10, -46, "No"),
    ],
    "PROJ_D": [
        ("D-101", "Mobilization & Planning", "1.1", "2026-02-01", "2026-02-14", "2026-02-01", "2026-02-13", "2026-02-01", "2026-02-13", 100, 100, 5, 1, "No"),
        ("D-102", "Inspection & Assessment", "2.1", "2026-02-14", "2026-03-05", "2026-02-13", "2026-03-03", "2026-02-13", "2026-03-03", 100, 100, 8, 2, "No"),
        ("D-103", "Repair Works", "2.2", "2026-03-05", "2026-04-15", "2026-03-03", "2026-04-12", "2026-03-03", "2026-04-12", 90, 92, 15, 3, "No"),
        ("D-104", "Upgrade Works", "3.1", "2026-04-15", "2026-06-15", "2026-04-12", "", "2026-04-12", "2026-06-10", 55, 60, 18, 5, "No"),
        ("D-105", "Testing & Commissioning RFT", "3.2", "2026-06-15", "2026-07-31", "", "", "2026-06-10", "2026-07-25", 35, 40, 12, 6, "No"),
        ("D-106", "Final Handover", "4.1", "2026-07-31", "2026-08-31", "", "", "2026-07-25", "2026-08-25", 15, 20, 8, 6, "No"),
    ],
    "PROJ_E": [
        ("E-101", "Mobilization & Shaft Setup", "1.1", "2025-05-01", "2025-06-15", "2025-05-01", "2025-06-20", "2025-05-01", "2025-06-25", 85, 70, 8, -10, "Yes"),
        ("E-102", "Shaft Excavation", "2.1", "2025-06-15", "2025-08-15", "2025-06-20", "2025-09-05", "2025-06-20", "2025-09-15", 65, 45, 16, -31, "Yes"),
        ("E-103", "Tunnel Boring", "2.2", "2025-08-15", "2025-12-15", "2025-09-05", "", "2025-09-05", "2026-01-20", 45, 25, 22, -36, "Yes"),
        ("E-104", "Tunnel Lining", "3.1", "2025-12-15", "2026-04-15", "", "", "2026-01-20", "2026-05-30", 30, 12, 18, -45, "Yes"),
        ("E-105", "MEP & Systems", "3.2", "2026-04-15", "2026-07-15", "", "", "2026-05-30", "2026-09-15", 18, 5, 14, -62, "Yes"),
        ("E-106", "Finishing & Testing RFT", "4.1", "2026-07-15", "2026-10-31", "", "", "2026-09-15", "2026-12-31", 8, 2, 10, -61, "No"),
    ],
}

S_CURVE_TEMPLATES = {
    "PROJ_A": dict(months=['2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04','2026-05','2026-06'],
                   planned=[5,8,12,10,9,11,8,7,6,4], actual=[4,6,9,8,7,9,6,5,4,3], invoiced=[3,5,7,6,6,8,5,4,3,2]),
    "PROJ_B": dict(months=['2026-01','2026-02','2026-03','2026-04','2026-05','2026-06'],
                   planned=[8,12,15,14,10,6], actual=[9,13,16,14,11,6], invoiced=[7,10,12,11,9,5]),
    "PROJ_C": dict(months=['2025-08','2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03'],
                   planned=[6,9,12,14,13,11,9,6], actual=[5,7,10,11,10,9,7,5], invoiced=[4,6,8,9,8,7,6,4]),
    "PROJ_D": dict(months=['2026-02','2026-03','2026-04','2026-05','2026-06'],
                   planned=[10,18,22,20,15], actual=[12,20,23,21,16], invoiced=[8,15,18,17,13]),
    "PROJ_E": dict(months=['2025-05','2025-06','2025-07','2025-08','2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03'],
                   planned=[5,7,9,11,10,9,8,7,6,5,4], actual=[3,5,6,7,6,5,4,3,2,2,1], invoiced=[2,4,5,6,5,4,3,2,1,1,1]),
}

CONTRACTS_TEMPLATES = {
    "PROJ_A": [
        ("CTR-001", "Main Works", "Contractor A", "Lump Sum", 219786025, 1200000, 350000, 78400000, 5, "Active"),
        ("CTR-002", "MEP Works", "Contractor B", "Unit Price", 45000000, 250000, 75000, 28000000, 5, "Active"),
    ],
    "PROJ_B": [("CTR-101", "Road Works", "Contractor C", "Lump Sum", 145000000, 800000, 200000, 51000000, 5, "Active")],
    "PROJ_C": [
        ("CTR-201", "Bridge Construction", "Contractor D", "Lump Sum", 187000000, 2500000, 500000, 71500000, 5, "Active"),
        ("CTR-202", "Geotechnical Works", "Contractor E", "Unit Price", 32000000, 150000, 0, 25000000, 5, "Active"),
    ],
    "PROJ_D": [("CTR-301", "Maintenance & Upgrades", "Contractor F", "Lump Sum", 78000000, 300000, 50000, 21000000, 5, "Active")],
    "PROJ_E": [("CTR-401", "Tunnel Works", "Contractor G", "Lump Sum", 320000000, 5000000, 1200000, 68000000, 5, "Active")],
}

PAYMENTS_TEMPLATES = {
    "PROJ_A": [
        ("PAY-001","CTR-001","INV-001","2025-10-15",15000000,14000000,"Paid"),
        ("PAY-002","CTR-001","INV-002","2025-12-20",22000000,21000000,"Paid"),
        ("PAY-003","CTR-001","INV-003","2026-03-10",18000000,16000000,"Partially Paid"),
        ("PAY-004","CTR-001","INV-004","2026-05-25",25000000,18000000,"Partially Paid"),
        ("PAY-005","CTR-002","INV-101","2025-11-05",12000000,12000000,"Paid"),
        ("PAY-006","CTR-002","INV-102","2026-02-15",16000000,14000000,"Partially Paid"),
    ],
    "PROJ_B": [
        ("PAY-101","CTR-101","INV-201","2026-02-28",18000000,18000000,"Paid"),
        ("PAY-102","CTR-101","INV-202","2026-04-15",22000000,21000000,"Partially Paid"),
        ("PAY-103","CTR-101","INV-203","2026-06-01",13200000,12000000,"Partially Paid"),
    ],
    "PROJ_C": [
        ("PAY-201","CTR-201","INV-301","2025-10-30",18000000,18000000,"Paid"),
        ("PAY-202","CTR-201","INV-302","2026-01-20",25000000,24000000,"Partially Paid"),
        ("PAY-203","CTR-201","INV-303","2026-04-10",20000000,17000000,"Partially Paid"),
        ("PAY-204","CTR-202","INV-401","2025-12-05",12000000,12000000,"Paid"),
        ("PAY-205","CTR-202","INV-402","2026-03-15",13000000,11000000,"Partially Paid"),
    ],
    "PROJ_D": [
        ("PAY-301","CTR-301","INV-501","2026-03-20",10000000,10000000,"Paid"),
        ("PAY-302","CTR-301","INV-502","2026-05-15",11500000,11000000,"Partially Paid"),
    ],
    "PROJ_E": [
        ("PAY-401","CTR-401","INV-601","2025-07-31",20000000,20000000,"Paid"),
        ("PAY-402","CTR-401","INV-602","2025-10-30",28000000,27000000,"Partially Paid"),
        ("PAY-403","CTR-401","INV-603","2026-01-31",22000000,16000000,"Partially Paid"),
        ("PAY-404","CTR-401","INV-604","2026-04-30",12000000,5000000,"Unpaid"),
    ],
}


def generate_sample_data(root: Path) -> None:
    """Write a complete sample dataset to disk under `root`."""
    root.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(SAMPLE_PROJECTS, columns=[
        "project_id", "project_name", "project_folder", "sector", "contractor",
        "employer", "consultant", "location", "project_manager", "planning_engineer",
        "contract_value", "start_date", "finish_date", "status", "planned_progress",
        "actual_progress", "spi", "cpi", "bac", "bcwp", "acwp", "bcws",
        "open_risks", "high_risks", "active_claims", "claimed_amount", "delay_days",
        "certified_amount", "paid_amount", "quality_score", "safety_score",
        "priority", "risk_level", "program", "team_size", "equipment_units",
        "milestones_total", "milestones_completed",
    ]).to_csv(root / "project_registry.csv", index=False)

    for pid, wbs_rows in WBS_TEMPLATES.items():
        folder = root / pid
        folder.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(wbs_rows, columns=["wbs_code", "wbs_name", "schedule_pct", "performance_pct"]) \
            .to_csv(folder / "wbs.csv", index=False)

    for pid, act_rows in ACTIVITIES_TEMPLATES.items():
        folder = root / pid
        pd.DataFrame(act_rows, columns=[
            "activity_id", "activity_name", "wbs_id", "planned_start", "planned_finish",
            "actual_start", "actual_finish", "forecast_start", "forecast_finish",
            "planned_progress", "actual_progress", "planned_weight", "total_float_days",
            "is_critical",
        ]).assign(responsible_party="Contractor").to_csv(folder / "activities.csv", index=False)

    for pid, sc in S_CURVE_TEMPLATES.items():
        folder = root / pid
        pd.DataFrame({
            "months": sc["months"],
            "monthly_planned": sc["planned"],
            "monthly_actual": sc["actual"],
            "monthly_invoiced": sc["invoiced"],
        }).to_csv(folder / "s_curve.csv", index=False)

    for pid, rows in CONTRACTS_TEMPLATES.items():
        folder = root / pid
        pd.DataFrame(rows, columns=[
            "contract_id", "package", "contractor", "contract_type", "original_value",
            "approved_variations", "pending_variations", "paid_to_date",
            "retention_percent", "status",
        ]).to_csv(folder / "contracts.csv", index=False)

    for pid, rows in PAYMENTS_TEMPLATES.items():
        folder = root / pid
        pd.DataFrame(rows, columns=[
            "payment_id", "contract_id", "invoice_no", "invoice_date",
            "certified_amount", "paid_amount", "payment_status",
        ]).to_csv(folder / "payments.csv", index=False)
