"""Create a restorable lightweight portfolio ZIP."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
FILES = [
    "README.md", "RESULTS.md", "PORTFOLIO_CASE_STUDY.md", "UPLOAD_GUIDE.md", "Airline_Reliability_Dashboard.html", "Airline_Reliability_2025.pbix",
    "build_dashboard.py", "build_carrier_month.py", "build_route_month.py", "combine_months.py", "load_sqlite.py",
    "report.py", "queries.sql", "data/carrier_month_combined.csv", "data/route_month_combined.csv", "data/dim_carrier.csv",
    "data/carrier_month_2025_01.csv", "data/carrier_month_2025_02.csv",
]
with ZipFile(ROOT / "Airline_Reliability_Portfolio.zip", "w", ZIP_DEFLATED) as archive:
    for relative in FILES:
        archive.write(ROOT / relative, relative)
print(f"Packaged {len(FILES)} files with source paths preserved")
