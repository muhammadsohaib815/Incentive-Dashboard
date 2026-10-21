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
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlencode, quote

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.db_loader import load_datasets, load_reporting_months, load_staff_df
from core.employee_service import (
    format_display_month,
    resolve_employee_selection,
    build_dynamic_header,
    get_dynamic_header_details,
    is_unmapped_or_vacant,
)
from core.engine import calculate_all_incentives
from core.summary import employee_directory, sales_for_employee, summarize_employee


def create_app():
    fastapi_app = FastAPI(title="DKT Sales Incentive Dashboard")
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    logger = logging.getLogger("uvicorn.error")
    fastapi_app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    def route_url(endpoint, **values):
        routes = {"index": "/", "summary_page": "/summary"}
        if endpoint == "static":
            return "/static/" + quote(str(values.pop("filename", "")), safe="/")
        path = routes.get(endpoint, "/")
        return path + ("?" + urlencode(values, doseq=True) if values else "")

    templates.env.globals["route_url"] = route_url

    @fastapi_app.get("/health")
    def health():
        return {"status": "ok", "app": "incentive_website"}

    @fastapi_app.get("/summary", name="summary_page")
    def summary_page(request: Request):
        category = request.query_params.get("category", "PHARMA").strip().upper()
        if category not in ("PHARMA", "FMCG"):
            raise HTTPException(status_code=404)

        months = load_reporting_months() or ["July,26", "August,26"]
        month = request.query_params.get("month", "July,26")
        if month not in months:
            month = months[0]

        target_df, sales_df, target_master_col = load_datasets(month)
        staff_df = load_staff_df()
        if not sales_df.empty and "REPORTING_MONTH" in sales_df:
            month_sales = sales_df[sales_df["REPORTING_MONTH"].astype(str).str.strip().eq(month)]
        else:
            month_sales = sales_df
        employees = [item for item in employee_directory(staff_df, month_sales)
                     if item["category"] == category]
        designations = sorted({item["designation"] for item in employees if item["designation"]})
        designation = request.query_params.get("designation", "").strip()
        if designation not in designations:
            designation = ""
        if designation:
            employees = [item for item in employees if item["designation"] == designation]
        payout_sort = request.query_params.get("sort", "").strip().lower()
        if payout_sort not in ("highest", "lowest"):
            payout_sort = ""
        search = request.query_params.get("q", "").strip()[:80]
        if search:
            term = search.casefold()
            employees = [item for item in employees if term in " ".join(
                str(item[field]) for field in ("name", "position", "territory", "designation", "region", "zone")
            ).casefold()]

        page_size = 20
        try:
            requested_page = int(request.query_params.get("page", "1"))
        except ValueError:
            requested_page = 1
        page_count = max(1, (len(employees) + page_size - 1) // page_size)
        page = min(max(requested_page, 1), page_count)
        current = employees[(page - 1) * page_size:page * page_size]

        rows = []
        for employee in current:
            try:
                scoped_sales = sales_for_employee(employee, month_sales, staff_df)
                result = calculate_all_incentives(
                    employee=employee["name"], month=month, target_df=target_df,
                    sales_df=scoped_sales, target_master_col=target_master_col,
                    staff_df=staff_df, pos_code=employee["position"],
                    territory=employee["territory"],
                )
                rows.append(summarize_employee(employee, result))
            except Exception:
                logger.exception("Unable to calculate summary for %s", employee["position"])
                rows.append({**employee, "error": "Unable to calculate"})

        if payout_sort:
            rows.sort(
                key=lambda row: float(row.get("final_payout", 0) or 0),
                reverse=payout_sort == "highest",
            )

        return templates.TemplateResponse(
            request=request,
            name="summary.html",
            context={
                "category": category, "rows": rows, "month": month,
                "month_options": [{"value": value, "label": format_display_month(value)} for value in months],
                "search": search, "total": len(employees), "page": page, "page_count": page_count,
                "designations": designations, "designation": designation, "payout_sort": payout_sort,
            },
        )

    def build_index_context(values):
        """Render filters immediately; calculate only after employee selection."""
        months = load_reporting_months() or ["July,26", "August,26"]
        selected_month = values.get("month") or "July,26"
        if selected_month not in months:
            selected_month = months[0]
        target_df, sales_df, target_master_col = load_datasets(selected_month)
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

        selected_designation = values.get("designation") or ""
        selected_territory = values.get("territory") or ""
        selected_region = values.get("region") or ""
        selected_zone = values.get("zone") or ""
        selected_subzone = values.get("subzone") or ""
        selected_team = values.get("team") or ""
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

        month_options = [{"value": m, "label": format_display_month(m)} for m in months]

        selected_employee = values.get("employee") or ""

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

        return {
            "employees": employees,
            "all_employees": all_employees,
            "emp_meta": emp_meta,
            "designations": designations,
            "territories": territories,
            "regions": regions,
            "zones": zones,
            "sub_zones": sub_zones,
            "selected_designation": selected_designation,
            "selected_territory": selected_territory,
            "selected_region": selected_region,
            "selected_zone": selected_zone,
            "selected_subzone": selected_subzone,
            "months": months,
            "month_options": month_options,
            "team_options": team_options,
            "selected_team": selected_team,
            "emp_team_map": emp_team_map,
            "selected_employee": selected_employee,
            "selected_month": selected_month,
            "active_category": active_category,
            "result": result,
            "header_title": header_title,
            "header_main": header_main,
            "header_sub": header_sub,
        }

    @fastapi_app.api_route("/", methods=["GET", "POST"], name="index")
    @fastapi_app.api_route("/incentive", methods=["GET", "POST"])
    @fastapi_app.api_route("/incentive/", methods=["GET", "POST"])
    async def index(request: Request):
        values = dict(request.query_params)
        if request.method == "POST":
            form_values = await request.form()
            values.update(dict(form_values))
        context = await run_in_threadpool(build_index_context, values)
        return templates.TemplateResponse(request=request, name="index.html", context=context)

    return fastapi_app


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
        help="Disable development auto-reload",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    banner = "=" * 70
    print(banner)
    print(" DKT Sales Incentive Calculation & Dashboard System")
    print(" FastAPI Web & API Server (Uvicorn)")
    print(banner)
    print(f" -> Web Dashboard (Frontend): http://{args.host}:{args.port}/")
    print(f" -> Incentive Dashboard:      http://{args.host}:{args.port}/incentive/")
    print(f" -> Health Check:             http://{args.host}:{args.port}/health")
    print(" -> Server Engine:            FastAPI (Uvicorn)")
    print(f" -> Auto Reload:              {args.debug and not args.prod}")
    print(banner)
    print("Press Ctrl+C to stop the server.\n")

    import uvicorn
    uvicorn.run(
        "server:app" if args.debug and not args.prod else app,
        host=args.host,
        port=args.port,
        reload=args.debug and not args.prod,
    )


if __name__ == "__main__":
    main()
