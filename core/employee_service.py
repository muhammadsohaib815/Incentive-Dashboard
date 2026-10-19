"""
Employee Service Module
Handles employee resolution, designation & team categorization, and dataset aggregation for ASMs and RSMs.
"""
import re
import pandas as pd
from core.db_loader import load_staff_df


def get_initials(name):
    """Generate 2-letter uppercase initials for employee avatar."""
    if not name:
        return "FF"
    cleaned = str(name).replace(".", " ").replace("-", " ").strip()
    parts = [p for p in cleaned.split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "FF"


def format_display_month(month_str):
    """Format 'July,26' to 'July 2026'."""
    if not month_str:
        return ""
    m = str(month_str).strip()
    if "," in m:
        parts = m.split(",")
        name = parts[0].strip()
        yr = parts[1].strip()
        if len(yr) == 2:
            return f"{name} 20{yr}"
        return f"{name} {yr}"
    return m


def get_dynamic_header_details(employee, month, staff_df=None, sales_df=None, pos_code=None, territory=None, team_hint=None, active_category=None):
    """
    Returns (line1, line2, full_title) where:
    - line1: Primary title (e.g., 'ABDUL KHALIL Dashboard - PHARMA')
    - line2: Subtitle metadata (e.g., 'PHR | GUJ01-PHR-MIO-05 | GUJRANWALA | September 2026')
    - full_title: Combined string for page title
    """
    month_display = format_display_month(month)

    if not employee:
        if team_hint == "PHARMA" or active_category == "pharma":
            team_label = "Pharmaceutical"
        elif team_hint == "FMCG":
            team_label = "FMCG"
        else:
            team_label = ""
        line1 = f"{team_label} Field Force Incentives Dashboard".strip() if team_label else "Field Force Incentives Dashboard"
        line2 = month_display
        full_title = f"{line1} - {line2}" if line2 else line1
        return line1, line2, full_title

    if staff_df is None:
        staff_df = load_staff_df()

    matches = pd.DataFrame()
    if staff_df is not None and not staff_df.empty:
        if pos_code and "Position_Code" in staff_df.columns:
            matches = staff_df[staff_df["Position_Code"].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()]
        elif territory and "Dept. Territory Code" in staff_df.columns and employee:
            matches = staff_df[
                (staff_df["Employe_Name"].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                (staff_df["Dept. Territory Code"].astype(str).str.strip().str.upper() == str(territory).strip().upper())
            ]
        if matches.empty and "Employe_Name" in staff_df.columns and employee:
            matches = staff_df[staff_df["Employe_Name"].astype(str).str.strip().str.lower() == str(employee).strip().lower()]

    r = matches.iloc[0] if not matches.empty else {}

    # Fallback lookup in sales_df if staff_df had no match
    if (not hasattr(r, '__len__') or len(r) == 0) and sales_df is not None and not sales_df.empty:
        s_matches = pd.DataFrame()
        if pos_code and "POSITION_CODE" in sales_df.columns:
            s_matches = sales_df[sales_df["POSITION_CODE"].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()]
        elif territory and "FF_TERRITORY" in sales_df.columns:
            s_matches = sales_df[
                (sales_df["NAME"].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                (sales_df["FF_TERRITORY"].astype(str).str.strip().str.upper() == str(territory).strip().upper())
            ]
        elif "NAME" in sales_df.columns:
            s_matches = sales_df[sales_df["NAME"].astype(str).str.strip().str.lower() == str(employee).strip().lower()]
        if not s_matches.empty:
            r = s_matches.iloc[0]

    # 1. Employee Name
    name = str(r.get("Employe_Name") or r.get("NAME") or employee).strip()

    # 2. Team: PHARMACEUTICAL -> PHARMA, FMCG -> FMCG
    raw_team = str(r.get("Team_Name") or r.get("TEAM") or team_hint or "").strip().upper()
    resolved_pos = str(r.get("Position_Code") or r.get("POSITION_CODE") or pos_code or "").strip().upper()

    if "PHARM" in raw_team or "-PHR-" in resolved_pos or active_category == "pharma":
        team_display = "PHARMA"
    elif "CONSUMER" in raw_team or "FMCG" in raw_team or "-FMCG" in resolved_pos:
        team_display = "FMCG"
    elif raw_team:
        team_display = raw_team
    else:
        team_display = "FMCG"

    # 3. Department Code
    dept_code = ""
    parts = resolved_pos.split("-")
    if "PHR" in parts or team_display == "PHARMA":
        dept_code = "PHR"
    else:
        for p in parts:
            if p.startswith("FMCG"):
                dept_code = "FMCG"
                break
            elif p in ("MKT", "KFW", "GSM", "SF"):
                dept_code = p
                break
        if not dept_code:
            dept_name = str(r.get("Depatment_Name") or "").strip().upper()
            if "KFW" in dept_name:
                dept_code = "KFW"
            elif "MARKET" in dept_name:
                dept_code = "MKT" if team_display != "FMCG" else "FMCG"
            else:
                dept_code = team_display

    # 4. Territory Code
    desg = str(r.get("Designation_Name") or r.get("DESIGNATION") or "").strip().upper()
    dept_terr = str(r.get("Dept. Territory Code") or r.get("FF_TERRITORY") or territory or "").strip()
    terr_code = resolved_pos or dept_terr or "ALL"

    # 5. Region / Organizational Scope
    region_raw = str(r.get("Region_Name") or r.get("REGION") or "").strip()
    base_name = str(r.get("Base_Name") or "").strip()
    zone_name = str(r.get("Zone_Name") or r.get("ZONE") or "").strip()

    if desg in ("HOD", "EXEC"):
        region_display = zone_name if zone_name and zone_name != "HEAD OFFICE" else "NATIONAL"
    elif desg == "DGM":
        region_display = zone_name if zone_name else (region_raw or "NATIONAL")
    elif desg == "RSM":
        region_display = region_raw or zone_name or "REGIONAL"
    else:
        # Standard field force (MIO, SPO, PS, ASM, TE, CM, etc.)
        if base_name and base_name not in ("HEAD OFFICE", "Others"):
            clean_base = re.sub(r'\s+\d+$', '', base_name).strip()
            region_display = clean_base
        elif region_raw:
            clean_reg = re.sub(r'-\d+$', '', region_raw).strip()
            region_display = clean_reg
        elif zone_name:
            region_display = zone_name
        else:
            region_display = "GENERAL"

    line1 = f"{name} Dashboard - {team_display}"
    sub_parts = [p for p in (dept_code, terr_code, region_display, month_display) if p]
    line2 = " | ".join(sub_parts)
    full_title = f"{line1} | {line2}"

    return line1, line2, full_title


def build_dynamic_header(employee, month, staff_df=None, sales_df=None, pos_code=None, territory=None, team_hint=None, active_category=None):
    """
    Constructs dynamic header in the format:
    [Employee Name] Dashboard - [Team] | [Department] | [Territory Code] | [Region] | [Month Year]

    Example:
    ABDUL KHALIL Dashboard - PHARMA | PHR | GUJ01-PHR-MIO-05 | GUJRANWALA | September 2026
    """
    _, _, full_title = get_dynamic_header_details(
        employee=employee,
        month=month,
        staff_df=staff_df,
        sales_df=sales_df,
        pos_code=pos_code,
        territory=territory,
        team_hint=team_hint,
        active_category=active_category
    )
    return full_title


def resolve_employee_selection(selected_employee, sales_df, staff_df=None):
    """
    Resolves selected_employee string (e.g. 'NAME - TERRITORY' or 'NAME' or 'POS_CODE')
    into (emp_name, pos_code, territory) using Master Staff List first, then sales_df.
    """
    if not selected_employee:
        return "", "", ""

    if staff_df is None:
        staff_df = load_staff_df()

    selected_clean = str(selected_employee).strip()

    # 1. Exact match with Position_Code in Master Staff List
    if staff_df is not None and not staff_df.empty and "Position_Code" in staff_df.columns:
        pos_match = staff_df[staff_df["Position_Code"].astype(str).str.strip().str.upper() == selected_clean.upper()]
        if not pos_match.empty:
            r = pos_match.iloc[0]
            return str(r.get("Employe_Name", "")).strip(), str(r.get("Position_Code", "")).strip(), str(r.get("Dept. Territory Code", "")).strip()

    # 2. Check 'NAME - TERRITORY' format in Master Staff List
    if " - " in selected_clean:
        parts = selected_clean.rsplit(" - ", 1)
        name_part = parts[0].strip()
        terr_part = parts[1].strip()
        if staff_df is not None and not staff_df.empty and "Employe_Name" in staff_df.columns:
            # Exact match on name and dept territory code
            if "Dept. Territory Code" in staff_df.columns:
                match = staff_df[
                    (staff_df["Employe_Name"].astype(str).str.strip().str.lower() == name_part.lower()) &
                    (staff_df["Dept. Territory Code"].astype(str).str.strip().str.upper() == terr_part.upper())
                ]
                if not match.empty:
                    r = match.iloc[0]
                    return str(r.get("Employe_Name", "")).strip(), str(r.get("Position_Code", "")).strip(), str(r.get("Dept. Territory Code", "")).strip()

            # Partial match on territory code
            if "Dept. Territory Code" in staff_df.columns:
                match = staff_df[
                    (staff_df["Employe_Name"].astype(str).str.strip().str.lower() == name_part.lower()) &
                    (staff_df["Dept. Territory Code"].astype(str).str.strip().str.upper().str.contains(terr_part.upper()))
                ]
                if not match.empty:
                    r = match.iloc[0]
                    return str(r.get("Employe_Name", "")).strip(), str(r.get("Position_Code", "")).strip(), str(r.get("Dept. Territory Code", "")).strip()

            # Fallback to name_part alone
            name_only = staff_df[staff_df["Employe_Name"].astype(str).str.strip().str.lower() == name_part.lower()]
            if not name_only.empty:
                r = name_only.iloc[0]
                return str(r.get("Employe_Name", "")).strip(), str(r.get("Position_Code", "")).strip(), str(r.get("Dept. Territory Code", "")).strip()

    # 3. Match Employe_Name in Master Staff List
    if staff_df is not None and not staff_df.empty and "Employe_Name" in staff_df.columns:
        name_match = staff_df[staff_df["Employe_Name"].astype(str).str.strip().str.lower() == selected_clean.lower()]
        if not name_match.empty:
            r = name_match.iloc[0]
            return str(r.get("Employe_Name", "")).strip(), str(r.get("Position_Code", "")).strip(), str(r.get("Dept. Territory Code", "")).strip()

    # 4. Fallback to sales_df
    if sales_df is not None and not sales_df.empty:
        if "POSITION_CODE" in sales_df.columns:
            pos_match = sales_df[sales_df["POSITION_CODE"].astype(str).str.strip().str.upper() == selected_clean.upper()]
            if not pos_match.empty:
                r = pos_match.iloc[0]
                return str(r.get("NAME", "")).strip(), str(r.get("POSITION_CODE", "")).strip(), str(r.get("FF_TERRITORY", "")).strip()

        if " - " in selected_clean:
            parts = selected_clean.rsplit(" - ", 1)
            name_part = parts[0].strip()
            terr_part = parts[1].strip()
            if "FF_TERRITORY" in sales_df.columns and "NAME" in sales_df.columns:
                match = sales_df[
                    (sales_df["NAME"].astype(str).str.strip().str.lower() == name_part.lower()) &
                    (sales_df["FF_TERRITORY"].astype(str).str.strip().str.upper() == terr_part.upper())
                ]
                if not match.empty:
                    r = match.iloc[0]
                    return str(r.get("NAME", "")).strip(), str(r.get("POSITION_CODE", "")).strip(), str(r.get("FF_TERRITORY", "")).strip()

        if "NAME" in sales_df.columns:
            name_match = sales_df[sales_df["NAME"].astype(str).str.strip().str.lower() == selected_clean.lower()]
            if not name_match.empty:
                r = name_match.iloc[0]
                return str(r.get("NAME", "")).strip(), str(r.get("POSITION_CODE", "")).strip(), str(r.get("FF_TERRITORY", "")).strip()

    return selected_clean, "", ""


def get_employee_info(employee, target_df, sales_df, staff_df=None, pos_code=None, territory=None):
    """
    Extract employee details in order:
    [Designation, Team, Nature Type, Payroll Type, D.O.J, Region_Name, Dept. Territory Code, Position Code]
    """
    if staff_df is None:
        staff_df = load_staff_df()

    desg, team, nature_type, payroll_type, doj, region, dept_territory, resolved_pos = "", "", "", "", "", "", "", ""

    # 1. Primary extraction from GSM Field Force Master Staff List 2026-27.xlsx
    if staff_df is not None and not staff_df.empty:
        matches = pd.DataFrame()
        if pos_code and "Position_Code" in staff_df.columns:
            matches = staff_df[staff_df["Position_Code"].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()]
        elif territory and "Dept. Territory Code" in staff_df.columns and employee:
            matches = staff_df[
                (staff_df["Employe_Name"].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                (staff_df["Dept. Territory Code"].astype(str).str.strip().str.upper() == str(territory).strip().upper())
            ]
        elif employee and "Employe_Name" in staff_df.columns:
            matches = staff_df[staff_df["Employe_Name"].astype(str).str.strip().str.lower() == str(employee).strip().lower()]
            if matches.empty and "Position_Code" in staff_df.columns:
                matches = staff_df[staff_df["Position_Code"].astype(str).str.strip().str.upper() == str(employee).strip().upper()]

        if not matches.empty:
            r = matches.iloc[0]
            desg = str(r.get("Designation_Name") or "").strip()
            team = str(r.get("Team_Name") or "").strip()
            nature_type = str(r.get("Nature Type") or "").strip()
            payroll_type = str(r.get("Payroll Type") or "").strip()
            raw_doj = r.get("D.O.J")
            if pd.notna(raw_doj) and str(raw_doj).strip() not in ('', 'NaT', 'nan', 'None'):
                try:
                    doj = pd.to_datetime(raw_doj).strftime('%d-%b-%Y')
                except Exception:
                    doj = str(raw_doj).strip()
            region = str(r.get("Region_Name") or "").strip()
            dept_territory = str(r.get("Dept. Territory Code") or "").strip()
            resolved_pos = str(r.get("Position_Code") or "").strip()

    # 2. Fallback to sales_df for any missing attributes
    if sales_df is not None and not sales_df.empty:
        s_matches = pd.DataFrame()
        if (pos_code or resolved_pos) and "POSITION_CODE" in sales_df.columns:
            p_to_check = str(pos_code or resolved_pos).strip().upper()
            s_matches = sales_df[sales_df["POSITION_CODE"].astype(str).str.strip().str.upper() == p_to_check]
        elif (territory or dept_territory) and "FF_TERRITORY" in sales_df.columns:
            t_to_check = str(territory or dept_territory).strip().upper()
            s_matches = sales_df[
                (sales_df["NAME"].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                (sales_df["FF_TERRITORY"].astype(str).str.strip().str.upper() == t_to_check)
            ]
        else:
            s_matches = sales_df[sales_df["NAME"].astype(str).str.strip().str.lower() == str(employee).strip().lower()]
            if s_matches.empty and "POSITION_CODE" in sales_df.columns:
                s_matches = sales_df[sales_df["POSITION_CODE"].astype(str).str.strip().str.upper() == str(employee).strip().upper()]

        if not s_matches.empty:
            r = s_matches.iloc[0]
            if not desg:
                desg = str(r.get("DESIGNATION") or r.get("Designation") or "").strip()
            if not team:
                team = str(r.get("TEAM") or "").strip()
            if not nature_type:
                nature_type = str(r.get("Emp. Type") or r.get("Emp Type") or r.get("NATURE") or "").strip()
            if not payroll_type:
                payroll_type = str(r.get("Payroll Status") or r.get("Payroll") or "").strip()
            if not doj:
                raw_doj = r.get("D.O.J") if "D.O.J" in r else r.get("DOJ")
                if pd.notna(raw_doj) and str(raw_doj).strip() not in ('', 'NaT', 'nan', 'None'):
                    try:
                        doj = pd.to_datetime(raw_doj).strftime('%d-%b-%Y')
                    except Exception:
                        doj = str(raw_doj).strip()
            if not region:
                region = str(r.get("TEAM_REGION") or r.get("REGION") or "").strip()
            if not dept_territory:
                dept_territory = str(r.get("FF_TERRITORY") or r.get("TERRITORY") or "").strip()
            if not resolved_pos:
                resolved_pos = str(r.get("POSITION_CODE") or "").strip()

    # 3. Fallback to target_df
    if target_df is not None and not target_df.empty:
        tgt_pos_col = None
        tgt_terr_col = None
        for c in target_df.columns:
            c_str = str(c).lower().strip()
            if 'position code' in c_str or 'position_code' in c_str:
                tgt_pos_col = c
            if 'dept. territory code' in c_str or 'territory code' in c_str:
                tgt_terr_col = c

        if (pos_code or resolved_pos) and tgt_pos_col and tgt_pos_col in target_df.columns:
            p_to_check = str(pos_code or resolved_pos).strip().upper()
            t_matches = target_df[target_df[tgt_pos_col].astype(str).str.strip().str.upper() == p_to_check]
        elif (territory or dept_territory) and tgt_terr_col and tgt_terr_col in target_df.columns:
            t_to_check = str(territory or dept_territory).strip().upper()
            t_matches = target_df[
                (target_df["F.F Name"].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                (target_df[tgt_terr_col].astype(str).str.strip().str.upper() == t_to_check)
            ]
        else:
            t_matches = target_df[target_df["F.F Name"].astype(str).str.strip().str.lower() == str(employee).strip().lower()]

        if not t_matches.empty:
            r = t_matches.iloc[0]
            if not desg:
                desg = str(r.get("Desg.") or r.get("Designation") or "").strip()
            if not team:
                team = str(r.get("Team") or "").strip()
            if not region:
                region = str(r.get("Region") or "").strip()
            if not dept_territory:
                dept_territory = str(r.get("Dept. Territory Code 2026-27") or r.get("Dept. Territory Code") or "").strip()
            if not resolved_pos:
                if tgt_pos_col:
                    resolved_pos = str(r.get(tgt_pos_col) or "").strip()

    if not desg:
        desg = "SPO"

    # 4. Extract ACCOUNT_TYPE directly from sales_df
    acc_types = []
    if sales_df is not None and not sales_df.empty:
        acc_col = None
        for c in sales_df.columns:
            if c.strip().lower() in ('account_type', 'account type', 'account'):
                acc_col = c
                break
        if acc_col:
            if resolved_pos and "POSITION_CODE" in sales_df.columns:
                emp_sales = sales_df[sales_df["POSITION_CODE"].astype(str).str.strip().str.upper() == str(resolved_pos).strip().upper()]
            elif (territory or dept_territory) and "FF_TERRITORY" in sales_df.columns:
                emp_sales = sales_df[
                    (sales_df["NAME"].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                    (sales_df["FF_TERRITORY"].astype(str).str.strip().str.upper() == str(territory or dept_territory).strip().upper())
                ]
            else:
                emp_sales = sales_df[sales_df["NAME"].astype(str).str.strip().str.lower() == str(employee).strip().lower()]
            if not emp_sales.empty:
                for a in emp_sales[acc_col].dropna().unique():
                    a_clean = str(a).strip()
                    if a_clean and a_clean.lower() not in ("nan", "none", "-", "null", "nat") and a_clean not in acc_types:
                        acc_types.append(a_clean)

    if 'PHARM' in str(team).upper() or 'PHR' in str(resolved_pos or pos_code).upper():
        phr_vals = [desg or "MIO", team or "PHARMACEUTICAL", resolved_pos or pos_code, region, dept_territory, doj]
        return [v for v in phr_vals if v and str(v).lower() not in ("nan", "none", "-", "null", "nat")]

    raw_vals = [desg, team, nature_type, payroll_type, doj, region, dept_territory, resolved_pos]
    for a in acc_types:
        if a not in raw_vals:
            raw_vals.append(a)

    return [v for v in raw_vals if v and v.lower() not in ("nan", "none", "-", "null", "nat")]


def determine_employee_category(emp, target_df, sales_df, staff_df=None, pos_code=None, territory=None):
    """
    Automatically determine the single relevant incentive category for an employee:
    - 'do': DO Team SPO (FMCG - 1)
    - 'touch': TOUCH Team SPO (FMCG - 2)
    - 'bliss': BLISS Team SPO (FMCG - 3)
    - 'overlapping': Overlapping SPO (FMCG Overlapping / Both)
    - 'rsm': Regional Sales Manager
    """
    if staff_df is None:
        staff_df = load_staff_df()

    # 1. Primary check in Master Staff List
    if staff_df is not None and not staff_df.empty:
        st_rows = pd.DataFrame()
        if pos_code and "Position_Code" in staff_df.columns:
            st_rows = staff_df[staff_df['Position_Code'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()]
        elif territory and "Dept. Territory Code" in staff_df.columns and emp:
            st_rows = staff_df[
                (staff_df['Employe_Name'].astype(str).str.strip().str.lower() == str(emp).strip().lower()) &
                (staff_df['Dept. Territory Code'].astype(str).str.strip().str.upper() == str(territory).strip().upper())
            ]
        elif emp and "Employe_Name" in staff_df.columns:
            st_rows = staff_df[staff_df['Employe_Name'].astype(str).str.strip().str.lower() == str(emp).strip().lower()]
            if st_rows.empty and "Position_Code" in staff_df.columns:
                st_rows = staff_df[staff_df['Position_Code'].astype(str).str.strip().str.upper() == str(emp).strip().upper()]

        if not st_rows.empty:
            desigs = set(st_rows['Designation_Name'].dropna().astype(str).str.strip().str.upper()) if 'Designation_Name' in st_rows.columns else set()
            team_names = set(st_rows['Team_Name'].dropna().astype(str).str.strip().str.upper())
            pos_codes = set(st_rows['Position_Code'].dropna().astype(str).str.strip().str.upper())

            if any('PHARMACEUTICAL' in t for t in team_names) or any('-PHR-' in p for p in pos_codes):
                return 'pharma'
            if 'RSM' in desigs:
                return 'rsm'
            if any('FAST MOVING CONSUMER GOODS - 3' in t for t in team_names) or any('FMCG03' in p for p in pos_codes):
                return 'bliss'
            if any('FAST MOVING CONSUMER GOODS - 1' in t for t in team_names) or any('FMCG01' in p for p in pos_codes):
                return 'do'
            if any('FAST MOVING CONSUMER GOODS - 2' in t for t in team_names) or any('FMCG02' in p for p in pos_codes):
                return 'touch'
            if any(t == 'FAST MOVING CONSUMER GOODS' for t in team_names) or any('FMCG-SPO' in p for p in pos_codes):
                return 'overlapping'

    # 2. Check Sales profile
    if sales_df is not None and not sales_df.empty:
        if pos_code and "POSITION_CODE" in sales_df.columns:
            sl_rows = sales_df[sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()]
        elif territory and "FF_TERRITORY" in sales_df.columns:
            sl_rows = sales_df[
                (sales_df['NAME'].astype(str).str.strip().str.lower() == str(emp).strip().lower()) &
                (sales_df['FF_TERRITORY'].astype(str).str.strip().str.upper() == str(territory).strip().upper())
            ]
        else:
            sl_rows = sales_df[sales_df['NAME'].astype(str).str.strip().str.lower() == str(emp).strip().lower()]
            if sl_rows.empty and "POSITION_CODE" in sales_df.columns:
                sl_rows = sales_df[sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == str(emp).strip().upper()]

        if not sl_rows.empty:
            desigs = set(sl_rows['DESIGNATION'].dropna().astype(str).str.strip().str.upper()) if 'DESIGNATION' in sl_rows.columns else set()
            subteams = set(sl_rows['SUB_TEAM'].dropna().astype(str).str.strip().str.upper())
            team_names = set(sl_rows['TEAM'].dropna().astype(str).str.strip().str.upper())
            team_channels = set(sl_rows['TEAM_CHANNEL'].dropna().astype(str).str.strip().str.upper()) if 'TEAM_CHANNEL' in sl_rows.columns else set()
            pos_codes = set(sl_rows['POSITION_CODE'].dropna().astype(str).str.strip().str.upper())

            if any('PHARMACEUTICAL' in t for t in team_names) or any('-PHR-' in p for p in pos_codes):
                return 'pharma'
            if 'RSM' in desigs:
                return 'rsm'
            if any('FAST MOVING CONSUMER GOODS - 3' in t for t in team_names) or any('FMCG03' in p for p in pos_codes) or ('FMCG-3' in subteams) or any('BLISS' in tc for tc in team_channels):
                return 'bliss'
            if ('FMCG-1' in subteams and 'FMCG-2' in subteams) or any(t == 'FAST MOVING CONSUMER GOODS' for t in team_names) or any('FMCG-SPO' in p for p in pos_codes):
                return 'overlapping'
            if any('FAST MOVING CONSUMER GOODS - 1' in t for t in team_names) or any('FMCG01' in p for p in pos_codes) or ('FMCG-1' in subteams and 'FMCG-2' not in subteams):
                return 'do'
            if any('FAST MOVING CONSUMER GOODS - 2' in t for t in team_names) or any('FMCG02' in p for p in pos_codes) or ('FMCG-2' in subteams and 'FMCG-1' not in subteams):
                return 'touch'

    # 3. Fallback to Target Sub Teams profile
    if target_df is not None and not target_df.empty:
        tgt_pos_col = None
        for c in target_df.columns:
            if 'position code' in str(c).lower():
                tgt_pos_col = c
                break
        if pos_code and tgt_pos_col and tgt_pos_col in target_df.columns:
            t_rows = target_df[target_df[tgt_pos_col].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()]
        else:
            t_rows = target_df[target_df['F.F Name'].astype(str).str.strip().str.lower() == str(emp).strip().lower()]
        if not t_rows.empty:
            tgt_subs = set(t_rows['Sub Teams'].dropna().astype(str).str.strip().str.upper())
            tgt_channels = set(t_rows['Team Channel-26-27'].dropna().astype(str).str.strip().str.upper()) if 'Team Channel-26-27' in t_rows.columns else set()
            tgt_pos_list = set(t_rows[tgt_pos_col].dropna().astype(str).str.strip().str.upper()) if tgt_pos_col and tgt_pos_col in t_rows.columns else set()

            if any('PHARM' in str(t).upper() for t in tgt_subs) or any('PHARM' in tc for tc in tgt_channels) or any('-PHR-' in p for p in tgt_pos_list):
                return 'pharma'
            if 'FMCG-3' in tgt_subs or any('BLISS' in tc for tc in tgt_channels) or any('FMCG03' in p for p in tgt_pos_list):
                return 'bliss'
            if 'FMCG-1' in tgt_subs and 'FMCG-2' not in tgt_subs:
                return 'do'
            if 'FMCG-2' in tgt_subs and 'FMCG-1' not in tgt_subs:
                return 'touch'
            if 'FMCG-1' in tgt_subs and 'FMCG-2' in tgt_subs:
                return 'overlapping'

    return 'do'


def aggregate_asm_datasets(employee, pos_code, month, target_df, sales_df, staff_df, territory=None):
    """
    For an ASM (Area Sales Manager), targets and actual net sales are aggregated from
    the ASM's entire Team Region (e.g. LAHORE-1), including all reporting Field Force SPOs
    as well as any direct sales/targets under the ASM's own position/territory.
    """
    if staff_df is None or staff_df.empty:
        return target_df, sales_df

    # 1. Match ASM in staff_df
    asm_row = staff_df[
        (staff_df['Position_Code'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()) |
        (staff_df['Dept. Territory Code'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()) |
        (staff_df['Employe_Name'].astype(str).str.strip().str.lower() == str(employee).strip().lower())
    ]
    if territory and asm_row.empty:
        asm_row = staff_df[staff_df['Dept. Territory Code'].astype(str).str.strip().str.upper() == str(territory).strip().upper()]

    region_name = ""
    team_name = ""
    asm_pos = str(pos_code or "").strip()
    asm_terr = str(territory or "").strip()
    asm_emp_name = str(employee or "").strip()

    if not asm_row.empty:
        r0 = asm_row.iloc[0]
        region_name = str(r0.get('Region_Name') or "").strip().upper()
        team_name = str(r0.get('Team_Name') or "").strip().upper()
        asm_pos = str(r0.get('Position_Code') or asm_pos).strip()
        asm_terr = str(r0.get('Dept. Territory Code') or asm_terr).strip()
        asm_emp_name = str(r0.get('Employe_Name') or asm_emp_name).strip()

    is_fmcg = any(x in team_name for x in ['CONSUMER GOODS', 'FMCG']) or any(x in asm_pos for x in ['FMCG'])
    is_fmcg_1 = 'CONSUMER GOODS - 1' in team_name or 'FMCG01' in asm_pos
    is_fmcg_2 = 'CONSUMER GOODS - 2' in team_name or 'FMCG02' in asm_pos
    is_fmcg_3 = 'CONSUMER GOODS - 3' in team_name or 'FMCG03' in asm_pos

    # 2. Collect reporting SPOs
    reporters = staff_df[
        (staff_df['Report_To_Position_Code'].astype(str).str.strip().str.upper() == asm_pos.upper()) |
        (staff_df['Report_To_Name'].astype(str).str.strip().str.lower() == asm_emp_name.lower())
    ]

    # 3. Collect region staff belonging to this ASM's team channel
    if region_name:
        reg_staff = staff_df[staff_df['Region_Name'].astype(str).str.strip().str.upper() == region_name]
        if is_fmcg_1:
            reg_staff = reg_staff[reg_staff['Team_Name'].astype(str).str.strip().str.upper().str.contains('CONSUMER GOODS - 1|FMCG01', na=False)]
        elif is_fmcg_2:
            reg_staff = reg_staff[reg_staff['Team_Name'].astype(str).str.strip().str.upper().str.contains('CONSUMER GOODS - 2|FMCG02', na=False)]
        elif is_fmcg_3:
            reg_staff = reg_staff[reg_staff['Team_Name'].astype(str).str.strip().str.upper().str.contains('CONSUMER GOODS - 3|FMCG03', na=False)]
        elif is_fmcg:
            reg_staff = reg_staff[reg_staff['Team_Name'].astype(str).str.strip().str.upper().str.contains('CONSUMER GOODS|FMCG', na=False)]
        reporters = pd.concat([reporters, reg_staff]).drop_duplicates(subset=['Position_Code'])

    all_team = pd.concat([reporters, asm_row]).drop_duplicates(subset=['Position_Code']) if not asm_row.empty else reporters

    team_positions = set(all_team['Position_Code'].dropna().astype(str).str.strip())
    if asm_pos:
        team_positions.add(asm_pos)
    team_terrs = set(all_team['Dept. Territory Code'].dropna().astype(str).str.strip())
    if asm_terr:
        team_terrs.add(asm_terr)

    # 4. Target Mask
    tgt_pos_col = next((c for c in target_df.columns if 'position code' in str(c).lower()), 'Position Code 2026-27')
    tgt_mask = target_df[tgt_pos_col].astype(str).str.strip().isin(team_positions)
    if is_fmcg_3 and 'Sub Teams' in target_df.columns:
        tgt_mask = tgt_mask & (target_df['Sub Teams'].astype(str).str.upper() == 'FMCG-3')
    elif is_fmcg and 'Sub Teams' in target_df.columns:
        tgt_mask = tgt_mask & target_df['Sub Teams'].astype(str).str.upper().str.contains('FMCG')

    asm_tgt = target_df[tgt_mask].copy()

    # 5. Sales Mask
    sal_mask = pd.Series(False, index=sales_df.index)
    if 'POSITION_CODE' in sales_df.columns:
        sal_mask = sal_mask | sales_df['POSITION_CODE'].astype(str).str.strip().isin(team_positions)
    if 'FF_TERRITORY' in sales_df.columns:
        sal_mask = sal_mask | sales_df['FF_TERRITORY'].astype(str).str.strip().isin(team_terrs)
    if region_name and 'TEAM_REGION' in sales_df.columns:
        reg_mask = sales_df['TEAM_REGION'].astype(str).str.strip().str.upper() == region_name
        if is_fmcg_1 and 'SUB_TEAM' in sales_df.columns:
            reg_mask = reg_mask & (sales_df['SUB_TEAM'].astype(str).str.upper() == 'FMCG-1')
        elif is_fmcg_2 and 'SUB_TEAM' in sales_df.columns:
            reg_mask = reg_mask & (sales_df['SUB_TEAM'].astype(str).str.upper() == 'FMCG-2')
        elif is_fmcg_3 and 'SUB_TEAM' in sales_df.columns:
            reg_mask = reg_mask & (sales_df['SUB_TEAM'].astype(str).str.upper() == 'FMCG-3')
        elif is_fmcg and 'SUB_TEAM' in sales_df.columns:
            reg_mask = reg_mask & sales_df['SUB_TEAM'].astype(str).str.upper().str.contains('FMCG')
        sal_mask = sal_mask | reg_mask

    if asm_emp_name and 'NAME' in sales_df.columns:
        asm_direct = sales_df['NAME'].astype(str).str.strip().str.lower() == asm_emp_name.lower()
        if region_name and 'REGION' in sales_df.columns:
            reg_token = region_name.split('-')[0].strip()
            asm_direct = asm_direct & sales_df['REGION'].astype(str).str.strip().str.upper().str.contains(reg_token)
        if is_fmcg and 'SUB_TEAM' in sales_df.columns:
            asm_direct = asm_direct & sales_df['SUB_TEAM'].astype(str).str.upper().str.contains('FMCG')
        sal_mask = sal_mask | asm_direct

    if is_fmcg_3 and 'TEAM' in sales_df.columns:
        sal_mask = sal_mask & (sales_df['TEAM'].astype(str).str.strip().str.upper() == 'FAST MOVING CONSUMER GOODS - 3')

    if 'REPORTING_MONTH' in sales_df.columns:
        sal_mask = sal_mask & (sales_df['REPORTING_MONTH'].astype(str).str.strip() == str(month).strip())

    asm_sal = sales_df[sal_mask].copy()

    asm_tgt['F.F Name'] = str(employee).strip()
    if tgt_pos_col and tgt_pos_col in asm_tgt.columns:
        asm_tgt[tgt_pos_col] = str(pos_code or asm_pos).strip()
    asm_sal['NAME'] = str(employee).strip()
    if 'POSITION_CODE' in asm_sal.columns:
        asm_sal['POSITION_CODE'] = str(pos_code or asm_pos).strip()

    return asm_tgt, asm_sal


def aggregate_rsm_datasets(employee, pos_code, month, target_df, sales_df, staff_df, territory=None):
    """
    For an RSM (Regional Sales Manager), aggregates datasets:
    - street_tgt, street_sal: targets and actual sales aggregated across all ASMs working under this RSM.
    - reg_tgt, reg_sal: regional targets and sales for Trade, Wholesale, and BLISS channels in the RSM's Sub-Zone.
    """
    if staff_df is None or staff_df.empty:
        return target_df, sales_df, target_df, sales_df

    rsm_row = staff_df[
        (staff_df['Position_Code'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()) |
        (staff_df['Dept. Territory Code'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()) |
        (staff_df['Employe_Name'].astype(str).str.strip().str.lower() == str(employee).strip().lower())
    ]
    if territory and rsm_row.empty:
        rsm_row = staff_df[staff_df['Dept. Territory Code'].astype(str).str.strip().str.upper() == str(territory).strip().upper()]

    rsm_pos = str(pos_code or "").strip()
    rsm_name = str(employee or "").strip()
    sub_zone = ""
    if not rsm_row.empty:
        r0 = rsm_row.iloc[0]
        rsm_pos = str(r0.get('Position_Code') or rsm_pos).strip()
        rsm_name = str(r0.get('Employe_Name') or rsm_name).strip()
        sub_zone = str(r0.get('Sub_Zone') or "").strip().upper()

    asm_mask = (staff_df['Designation_Name'].astype(str).str.strip().str.upper() == 'ASM') & (
        (staff_df['Sub_Zone'].astype(str).str.strip().str.upper() == sub_zone) |
        (staff_df['Report_To_Position_Code'].astype(str).str.strip().str.upper() == rsm_pos.upper()) |
        (staff_df['Report_To_Name'].astype(str).str.strip().str.lower() == rsm_name.lower())
    ) & staff_df['Team_Name'].astype(str).str.upper().str.contains('CONSUMER GOODS|FMCG', na=False)

    asms = staff_df[asm_mask].drop_duplicates(subset=['Position_Code'])

    street_tgts = []
    street_sals = []
    for _, a in asms.iterrows():
        a_name = str(a.get('Employe_Name') or '').strip()
        a_pos = str(a.get('Position_Code') or '').strip()
        a_terr = str(a.get('Dept. Territory Code') or '').strip()
        a_tgt, a_sal = aggregate_asm_datasets(a_name, a_pos, month, target_df, sales_df, staff_df, territory=a_terr)
        street_tgts.append(a_tgt)
        street_sals.append(a_sal)

    street_tgt = pd.concat(street_tgts, ignore_index=True) if street_tgts else pd.DataFrame(columns=target_df.columns)
    street_sal = pd.concat(street_sals, ignore_index=True) if street_sals else pd.DataFrame(columns=sales_df.columns)

    t_mask = (target_df['Sub-Zone'].astype(str).str.strip().str.upper() == sub_zone) if 'Sub-Zone' in target_df.columns else pd.Series(True, index=target_df.index)
    s_mask = (sales_df['SUB_ZONE'].astype(str).str.strip().str.upper() == sub_zone) if 'SUB_ZONE' in sales_df.columns else pd.Series(True, index=sales_df.index)
    if 'REPORTING_MONTH' in sales_df.columns:
        s_mask = s_mask & (sales_df['REPORTING_MONTH'].astype(str).str.strip() == str(month).strip())

    reg_tgt = target_df[t_mask].copy()
    reg_sal = sales_df[s_mask].copy()

    return street_tgt, street_sal, reg_tgt, reg_sal
