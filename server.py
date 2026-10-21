"""
DKT Sales Incentive Calculation & Dashboard System - Server
------------------------------------------------------------
Unified Backend API & Web Dashboard Server.

Usage:
    python server.py
    python server.py --port 5000 --host 0.0.0.0
    python server.py --prod
"""
import argparse
import os
import sys
from pathlib import Path
from flask import Flask, render_template, request
import pandas as pd

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.db_loader import load_datasets, load_staff_df
from core.employee_service import (
    format_display_month,
    resolve_employee_selection,
    build_dynamic_header,
    get_dynamic_header_details,
    is_unmapped_or_vacant,
)
from core.engine import calculate_all_incentives


def create_app():
    flask_app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    @flask_app.after_request
    def set_utf8_charset(response):
        if response.mimetype == "text/html":
            response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response

    @flask_app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "app": "incentive_website"}

    @flask_app.route("/", methods=["GET", "POST"])
    @flask_app.route("/incentive", methods=["GET", "POST"])
    @flask_app.route("/incentive/", methods=["GET", "POST"])
    def index():
        """Render filters immediately; calculate only after employee selection."""
        target_df, sales_df, target_master_col = load_datasets()
        staff_df = load_staff_df()

        # Build employee list, metadata and team mapping (excluding unmapped and vacant positions)
        emp_list = []
        emp_team_map = {}
        emp_meta = {}
        if not staff_df.empty:
            for _, r in staff_df.iterrows():
                name = str(r.get('Employe_Name', '')).strip()
                terr = str(r.get('Dept. Territory Code', '')).strip() if pd.notna(r.get('Dept. Territory Code')) and str(r.get('Dept. Territory Code')).strip() not in ('nan', '') else ''
                desg = str(r.get('Designation_Name', '')).strip()
                reg = str(r.get('Region_Name', '')).strip()
                zone = str(r.get('Zone_Name', '')).strip()
                subzone = str(r.get('Sub_Zone', '')).strip()
                t_name = str(r.get('Team_Name', '')).strip().upper()
                p_code = str(r.get('Position_Code', '')).strip().upper()
                if is_unmapped_or_vacant(name, p_code, terr):
                    continue
                label = f"{name} - {terr}" if terr else name
                emp_list.append(label)
                if 'PHARM' in t_name or '-PHR-' in p_code:
                    emp_team_map[label] = 'PHARMA'
                elif 'CONSUMER GOODS' in t_name or 'FMCG' in t_name:
                    emp_team_map[label] = 'FMCG'
                else:
                    emp_team_map[label] = 'OTHER'
                emp_meta[label] = {
                    "name": name,
                    "designation": desg,
                    "territory": terr,
                    "region": reg,
                    "zone": zone,
                    "sub_zone": subzone,
                    "position_code": p_code,
                    "team": emp_team_map[label]
                }

        # Merge any active sales employee combos if not already present
        if not sales_df.empty and "POSITION_CODE" in sales_df.columns and "NAME" in sales_df.columns:
            valid_sales = sales_df[sales_df["POSITION_CODE"].notna() & (sales_df["POSITION_CODE"].astype(str).str.strip() != "")]
            combos_cols = ['NAME', 'POSITION_CODE', 'FF_TERRITORY']
            if 'TEAM' in valid_sales.columns:
                combos_cols.append('TEAM')
            combos = valid_sales[combos_cols].drop_duplicates()
            for _, r in combos.iterrows():
                name = str(r['NAME']).strip()
                terr = str(r['FF_TERRITORY']).strip() if pd.notna(r.get('FF_TERRITORY')) and str(r.get('FF_TERRITORY')).strip() not in ('nan', '') else ''
                p_code = str(r.get('POSITION_CODE', '')).strip().upper()
                t_name = str(r.get('TEAM', '')).strip().upper() if 'TEAM' in r else ''
                if is_unmapped_or_vacant(name, p_code, terr):
                    continue
                label = f"{name} - {terr}" if terr else name
                if label not in emp_list:
                    emp_list.append(label)
                if label not in emp_team_map:
                    if 'PHARM' in t_name or '-PHR-' in p_code:
                        emp_team_map[label] = 'PHARMA'
                    else:
                        emp_team_map[label] = 'FMCG'
                if label not in emp_meta:
                    emp_meta[label] = {
                        "name": name,
                        "designation": "",
                        "territory": terr,
                        "region": "",
                        "zone": "",
                        "sub_zone": "",
                        "position_code": p_code,
                        "team": emp_team_map[label]
                    }

        all_employees = sorted(list(set(emp_list)))
        designations = sorted(list({m["designation"] for m in emp_meta.values() if m.get("designation")}))
        territories = sorted(list({m["territory"] for m in emp_meta.values() if m.get("territory")}))
        regions = sorted(list({m["region"] for m in emp_meta.values() if m.get("region")}))
        zones = sorted(list({m["zone"] for m in emp_meta.values() if m.get("zone")}))
        sub_zones = sorted(list({m["sub_zone"] for m in emp_meta.values() if m.get("sub_zone")}))

        selected_designation = request.form.get("designation") or request.args.get("designation") or ""
        selected_territory = request.form.get("territory") or request.args.get("territory") or ""
        selected_region = request.form.get("region") or request.args.get("region") or ""
        selected_zone = request.form.get("zone") or request.args.get("zone") or ""
        selected_subzone = request.form.get("subzone") or request.args.get("subzone") or ""
        selected_team = request.form.get("team") or request.args.get("team") or ""
        team_options = [
            {"value": "", "label": "ALL TEAMS"},
            {"value": "PHARMA", "label": "PHARMACEUTICAL"},
            {"value": "FMCG", "label": "FMCG"},
        ]

        if selected_team == "PHARMA":
            employees = [e for e in all_employees if emp_team_map.get(e) == "PHARMA"]
        elif selected_team == "FMCG":
            employees = [e for e in all_employees if emp_team_map.get(e) == "FMCG"]
        else:
            employees = all_employees

        # Get available months from sales data
        months = ["July,26", "August,26"]
        if not sales_df.empty and "REPORTING_MONTH" in sales_df.columns:
            sales_months = [str(m).strip() for m in sales_df["REPORTING_MONTH"].dropna().unique()]
            for m in sales_months:
                if m not in months:
                    months.append(m)

        month_options = [{"value": m, "label": format_display_month(m)} for m in months]

        selected_employee = request.form.get("employee") or request.args.get("employee") or ""
        selected_month = request.form.get("month") or request.args.get("month") or "July,26"

        if not selected_employee and selected_territory:
            for emp_lbl, meta in emp_meta.items():
                if meta.get("territory") == selected_territory and emp_lbl in employees:
                    selected_employee = emp_lbl
                    break

        # Do not auto-select an employee. The page intentionally remains empty
        # below the filters until the user chooses a valid employee.
        if selected_employee:
            if is_unmapped_or_vacant(selected_employee) or selected_employee not in employees:
                selected_employee = ""

        result = None
        active_category = "do"
        if selected_employee and not sales_df.empty:
            emp_name, pos_code, territory = resolve_employee_selection(selected_employee, sales_df, staff_df=staff_df)
            result = calculate_all_incentives(
                employee=emp_name,
                month=selected_month,
                target_df=target_df,
                sales_df=sales_df,
                target_master_col=target_master_col,
                staff_df=staff_df,
                pos_code=pos_code,
                territory=territory
            )
            active_category = result['active_category']

        header_title = None
        header_main = None
        header_sub = None
        if result and result.get("header_title"):
            header_title = result["header_title"]
            header_main = result.get("header_main")
            header_sub = result.get("header_sub")
        else:
            header_main, header_sub, header_title = get_dynamic_header_details(
                employee="",
                month=selected_month,
                team_hint=selected_team,
                active_category=active_category
            )

        if selected_employee and selected_employee in emp_meta:
            m = emp_meta[selected_employee]
            selected_designation = m.get("designation", "") or selected_designation
            selected_territory = m.get("territory", "") or selected_territory
            selected_region = m.get("region", "") or selected_region
            selected_zone = m.get("zone", "") or selected_zone
            selected_subzone = m.get("sub_zone", "") or selected_subzone

        return render_template(
            "index.html",
            employees=employees,
            all_employees=all_employees,
            emp_meta=emp_meta,
            designations=designations,
            territories=territories,
            regions=regions,
            zones=zones,
            sub_zones=sub_zones,
            selected_designation=selected_designation,
            selected_territory=selected_territory,
            selected_region=selected_region,
            selected_zone=selected_zone,
            selected_subzone=selected_subzone,
            months=months,
            month_options=month_options,
            team_options=team_options,
            selected_team=selected_team,
            emp_team_map=emp_team_map,
            selected_employee=selected_employee,
            selected_month=selected_month,
            active_category=active_category,
            result=result,
            header_title=header_title,
            header_main=header_main,
            header_sub=header_sub
        )

    return flask_app


app = create_app()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the Sales Incentive Calculation Platform server (Unified Backend & Frontend)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Host address to bind the server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 5000)),
        help="Port to listen on (default: 5000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.environ.get("DEBUG", "true").lower() in ("true", "1", "t", "yes"),
        help="Run server in debug mode with auto-reload (default: True)",
    )
    parser.add_argument(
        "--no-debug",
        action="store_false",
        dest="debug",
        help="Disable debug mode",
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Run with production WSGI server (Waitress) to eliminate development server warning",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    banner = "=" * 70
    print(banner)
    print(" DKT Sales Incentive Calculation & Dashboard System")
    print(" Unified Web & API Server (server.py)")
    print(banner)
    print(f" -> Web Dashboard (Frontend): http://{args.host}:{args.port}/")
    print(f" -> Incentive Dashboard:      http://{args.host}:{args.port}/incentive/")
    print(f" -> Health Check:             http://{args.host}:{args.port}/health")
    if args.prod:
        print(f" -> Server Engine:            Production WSGI (Waitress)")
    else:
        print(f" -> Server Engine:            Flask Development Server")
        print(f" -> Debug Mode:               {args.debug}")
    print(banner)
    print("Press Ctrl+C to stop the server.\n")

    if args.prod:
        try:
            from waitress import serve
            serve(app, host=args.host, port=args.port)
        except ImportError:
            print("[WARNING] 'waitress' package is not installed. To use production mode, run:")
            print("          pip install waitress\n")
            print("Falling back to standard Flask server...\n")
            app.run(host=args.host, port=args.port, debug=False)
    else:
        app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
