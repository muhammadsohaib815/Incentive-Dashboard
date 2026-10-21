"""
Incentive Calculation Platform - Flask Application
Run the local web dashboard:
    python app.py
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
from core.employee_service import format_display_month, resolve_employee_selection, build_dynamic_header, get_dynamic_header_details
from core.engine import calculate_all_incentives


def create_app():
    flask_app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static")
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

        # Build employee list and team mapping
        emp_list = []
        emp_team_map = {}
        if not staff_df.empty:
            for _, r in staff_df.iterrows():
                name = str(r.get('Employe_Name', '')).strip()
                terr = str(r.get('Dept. Territory Code', '')).strip() if pd.notna(r.get('Dept. Territory Code')) and str(r.get('Dept. Territory Code')).strip() not in ('nan', '') else ''
                t_name = str(r.get('Team_Name', '')).strip().upper()
                p_code = str(r.get('Position_Code', '')).strip().upper()
                if not name or name.upper() in ("NAN", "NONE", "NULL"):
                    continue
                label = f"{name} - {terr}" if terr else name
                emp_list.append(label)
                if 'PHARM' in t_name or '-PHR-' in p_code:
                    emp_team_map[label] = 'PHARMA'
                elif 'CONSUMER GOODS' in t_name or 'FMCG' in t_name:
                    emp_team_map[label] = 'FMCG'
                else:
                    emp_team_map[label] = 'OTHER'

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
                if not name or name.upper() in ("NAN", "NONE", "NULL"):
                    continue
                label = f"{name} - {terr}" if terr else name
                if label not in emp_list:
                    emp_list.append(label)
                if label not in emp_team_map:
                    if 'PHARM' in t_name or '-PHR-' in p_code:
                        emp_team_map[label] = 'PHARMA'
                    else:
                        emp_team_map[label] = 'FMCG'

        all_employees = sorted(list(set(emp_list)))

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

        # Do not auto-select an employee. The page intentionally remains empty
        # below the filters until the user chooses a valid employee.
        if selected_employee and selected_employee not in employees:
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

        return render_template(
            "index.html",
            employees=employees,
            all_employees=all_employees,
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
        description="Run the Sales Incentive Calculation Platform server (Unified Web & API)"
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
    print(" Unified Web & API Server (app.py)")
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
