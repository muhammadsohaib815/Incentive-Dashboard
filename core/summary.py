"""Employee directory and compact incentive summary fields for the category view."""

import pandas as pd

from core.employee_service import is_unmapped_or_vacant


def _text(value):
    return "" if value is None or pd.isna(value) else str(value).strip()


def _category(team, position):
    team = team.upper()
    position = position.upper()
    if "PHARM" in team or "-PHR-" in position:
        return "PHARMA"
    if "CONSUMER GOODS" in team or "FMCG" in team or "FMCG" in position:
        return "FMCG"
    return ""


def employee_directory(staff_df, month_sales):
    """Keep one current staff record per position, with sales-only records as fallback."""
    employees = {}

    if staff_df is not None and not staff_df.empty:
        for _, row in staff_df.iterrows():
            name = _text(row.get("Employe_Name"))
            position = _text(row.get("Position_Code"))
            territory = _text(row.get("Dept. Territory Code"))
            if is_unmapped_or_vacant(name, position, territory):
                continue
            team = _text(row.get("Team_Name"))
            category = _category(team, position)
            if not category:
                continue
            key = position.upper() or f"{name.upper()}|{territory.upper()}"
            employees[key] = {
                "name": name,
                "label": f"{name} - {territory}" if territory else name,
                "position": position,
                "territory": territory,
                "designation": _text(row.get("Designation_Name")),
                "region": _text(row.get("Region_Name")),
                "zone": _text(row.get("Zone_Name")),
                "subzone": _text(row.get("Sub_Zone")),
                "team": team,
                "category": category,
            }

    if month_sales is not None and not month_sales.empty:
        cols = [c for c in ("POSITION_CODE", "NAME", "FF_TERRITORY", "TEAM", "DESIGNATION",
                            "TEAM_REGION", "REGION", "ZONE", "SUB_ZONE") if c in month_sales]
        for _, row in month_sales[cols].drop_duplicates().iterrows():
            name = _text(row.get("NAME"))
            position = _text(row.get("POSITION_CODE"))
            territory = _text(row.get("FF_TERRITORY"))
            if is_unmapped_or_vacant(name, position, territory):
                continue
            key = position.upper() or f"{name.upper()}|{territory.upper()}"
            if key in employees:
                continue
            team = _text(row.get("TEAM"))
            category = _category(team, position)
            if not category:
                continue
            employees[key] = {
                "name": name,
                "label": f"{name} - {territory}" if territory else name,
                "position": position,
                "territory": territory,
                "designation": _text(row.get("DESIGNATION")),
                "region": _text(row.get("TEAM_REGION")) or _text(row.get("REGION")),
                "zone": _text(row.get("ZONE")),
                "subzone": _text(row.get("SUB_ZONE")),
                "team": team,
                "category": category,
            }

    return sorted(employees.values(), key=lambda item: (item["name"].upper(), item["position"].upper()))


def sales_for_employee(employee, month_sales, staff_df):
    """Limit evaluator scans to the employee's month and reporting area."""
    if month_sales.empty:
        return month_sales

    position = employee["position"].upper()
    designation = employee["designation"].upper()
    positions = month_sales["POSITION_CODE"].fillna("").astype(str).str.strip().str.upper()
    own = positions.eq(position) if position else pd.Series(False, index=month_sales.index)

    if designation == "RSM" or "-RSM-" in position:
        # FMCG RSM privilege checks every ASM linked by region or reporting
        # line. Some of those teams have sales outside the RSM's SUB_ZONE.
        if employee["category"] == "FMCG":
            return month_sales
        subzone = employee["subzone"].upper()
        if not subzone or "SUB_ZONE" not in month_sales:
            return month_sales
        area = month_sales["SUB_ZONE"].fillna("").astype(str).str.strip().str.upper().eq(subzone)
        return month_sales[area | own]

    if designation == "ASM" or "-ASM-" in position:
        region = employee["region"].upper()
        area = pd.Series(False, index=month_sales.index)
        if region and "TEAM_REGION" in month_sales:
            area |= month_sales["TEAM_REGION"].fillna("").astype(str).str.strip().str.upper().eq(region)
        if region and "REGION" in month_sales:
            region_token = region.split("-")[0]
            area |= month_sales["REGION"].fillna("").astype(str).str.upper().str.contains(region_token, regex=False)
        if staff_df is not None and not staff_df.empty and position:
            related = staff_df[
                staff_df["Report_To_Position_Code"].fillna("").astype(str).str.strip().str.upper().eq(position)
            ]
            related_positions = set(related["Position_Code"].dropna().astype(str).str.strip().str.upper())
            area |= positions.isin(related_positions)
        if "NAME" in month_sales:
            area |= month_sales["NAME"].fillna("").astype(str).str.strip().str.upper().eq(employee["name"].upper())
        return month_sales[area | own] if (area | own).any() else month_sales

    if own.any():
        return month_sales[own]
    if "NAME" not in month_sales:
        return month_sales.iloc[0:0]
    name = month_sales["NAME"].fillna("").astype(str).str.strip().str.upper().eq(employee["name"].upper())
    if employee["territory"] and "FF_TERRITORY" in month_sales:
        name &= month_sales["FF_TERRITORY"].fillna("").astype(str).str.strip().str.upper().eq(employee["territory"].upper())
    return month_sales[name]


def _bottom_line(result):
    category = result.get("active_category")
    if category == "pharma":
        source = result.get("pharma_rsm") if result.get("is_pharma_rsm") else result.get("pharma")
        if not source:
            return None
        if result.get("is_pharma_rsm"):
            return {"achievement": source.get("zone_val_achievement", 0),
                    "actual": source.get("zone_act_val", 0), "target": source.get("zone_tgt_val", 0)}
        return {"achievement": source.get("overall_achievement", 0),
                "actual": source.get("total_act_val", 0), "target": source.get("total_tgt_val", 0)}

    keys = {
        "do": ("criteria_dict", "do_sathi_bottom_line"),
        "touch": ("touch_criteria_dict", "touch_one_bottom_line"),
        "overlapping": ("overlapping_criteria_dict", "overlapping_overall_bottom_line"),
        "bliss": ("bliss_criteria_dict", "bliss_bottom_line"),
        "rsm": ("criteria_dict", "rsm_condom_bottom_line"),
    }
    dictionary, key = keys.get(category, ("", ""))
    criterion = (result.get(dictionary) or {}).get(key)
    if not criterion:
        return None
    return {"achievement": criterion.get("achievement", 0),
            "actual": criterion.get("actual", 0), "target": criterion.get("target", 0)}


def summarize_employee(employee, result):
    privilege = (result.get("privilege_club") or result.get("asm_privilege_club")
                 or result.get("rsm_privilege_club"))
    if privilege:
        privilege_amount = privilege.get("incentive", 0)
        privilege_status = privilege.get("status", "")
    else:
        privilege_amount = None
        privilege_status = "Not applicable"

    return {
        **employee,
        "bottom_line": _bottom_line(result),
        "team_name": result.get("active_team_name") or employee["team"],
        "team_incentive": result.get("active_incentive", 0),
        "privilege_amount": privilege_amount,
        "privilege_status": privilege_status,
        "other_bonus": (result.get("ucc_incentive") or 0)
                       + (result.get("bliss_asm_ucc_incentive") or 0),
        "final_payout": result.get("final_payout", 0),
        "status": result.get("active_tier", ""),
    }
