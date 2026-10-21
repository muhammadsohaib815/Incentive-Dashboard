"""
Pharma Regional Sales Manager (RSM) Evaluator Module
Policy: Pharma Incentive Policy 2026-27 (July 2026 – June 2027)
Rule: Regional Sales Manager (RSM) receives 10% of the Total Incentive Payout of his Zone
      in case: (MIO/PS + ASM).
"""
import pandas as pd
from core.db_loader import get_target_columns
from core.employee_service import aggregate_asm_datasets, is_unmapped_or_vacant
from core.evaluators.pharma_evaluator import evaluate_pharma_incentives

# Module-level memory cache for quick re-renders: (zone_name, month) -> result
_PHARMA_RSM_CACHE = {}


def clear_pharma_rsm_cache():
    """Clear memory cache if datasets reload."""
    _PHARMA_RSM_CACHE.clear()


def evaluate_pharma_rsm_incentives(
    employee, month, target_df, sales_df, target_master_col, staff_df,
    pos_code=None, territory=None
):
    """
    Evaluates incentives for a Pharmaceutical Regional Sales Manager (RSM).
    Criteria: 10% of the Total Incentive Payout of his Zone in case: (MIO/PS + ASM).
    """
    # 1. Determine RSM's Zone
    zone_name = ""
    rsm_pos = str(pos_code or "").strip().upper()
    rsm_name = str(employee or "").strip()

    if staff_df is not None and not staff_df.empty:
        rsm_match = pd.DataFrame()
        if rsm_pos and "Position_Code" in staff_df.columns:
            rsm_match = staff_df[staff_df["Position_Code"].astype(str).str.strip().str.upper() == rsm_pos]
        if rsm_match.empty and rsm_name and "Employe_Name" in staff_df.columns:
            rsm_match = staff_df[staff_df["Employe_Name"].astype(str).str.strip().str.lower() == rsm_name.lower()]

        if not rsm_match.empty:
            zone_name = str(rsm_match.iloc[0].get("Zone_Name") or "").strip().upper()
            if not rsm_pos:
                rsm_pos = str(rsm_match.iloc[0].get("Position_Code") or "").strip().upper()
            if not rsm_name:
                rsm_name = str(rsm_match.iloc[0].get("Employe_Name") or "").strip()

    # Fallback zone from position code prefix if not in staff_df
    if not zone_name or zone_name in ("NAN", "NONE", ""):
        if "STH" in rsm_pos or "SOUTH" in str(territory or "").upper():
            zone_name = "SOUTH"
        elif "CNT" in rsm_pos or "CENTRAL" in str(territory or "").upper():
            zone_name = "CENTRAL"
        elif "NTH" in rsm_pos or "NORTH" in str(territory or "").upper():
            zone_name = "NORTH"
        else:
            zone_name = "SOUTH"

    cache_key = (zone_name, str(month).strip())
    if cache_key in _PHARMA_RSM_CACHE:
        cached = _PHARMA_RSM_CACHE[cache_key].copy()
        cached["rsm_name"] = rsm_name
        cached["rsm_pos_code"] = rsm_pos
        return cached

    t_net_col, t_unit_col, _ = get_target_columns(month, target_df)

    # 2. Identify all Pharma Field Staff in this Zone (MIO, PS, ASM)
    z_staff = pd.DataFrame()
    if staff_df is not None and not staff_df.empty:
        z_filter = (
            (staff_df["Zone_Name"].astype(str).str.strip().str.upper() == zone_name) &
            (
                staff_df["Team_Name"].astype(str).str.contains("PHARM", case=False, na=False) |
                staff_df["Position_Code"].astype(str).str.contains("-PHR-", case=False, na=False)
            ) &
            (staff_df["Designation_Name"].astype(str).str.strip().str.upper().isin(["MIO", "PS", "ASM"]))
        )
        z_staff = staff_df[z_filter].copy()
        if not z_staff.empty:
            z_dummy = z_staff.apply(
                lambda row: is_unmapped_or_vacant(
                    row.get("Employe_Name"),
                    row.get("Position_Code"),
                    row.get("Dept. Territory Code"),
                ),
                axis=1,
            )
            z_staff = z_staff[~z_dummy].copy()

    # 3. Pre-filter month sales and zone subsets for high performance
    s_m = sales_df
    if sales_df is not None and not sales_df.empty and "REPORTING_MONTH" in sales_df.columns:
        s_m = sales_df[sales_df["REPORTING_MONTH"].astype(str).str.strip() == str(month).strip()]

    z_pos_set = set(z_staff["Position_Code"].dropna().astype(str).str.strip().str.upper()) if not z_staff.empty else set()
    z_terr_set = set(z_staff["Dept. Territory Code"].dropna().astype(str).str.strip().str.upper()) if not z_staff.empty else set()

    # Pre-slice target and sales data to zone elements
    if target_df is not None and not target_df.empty:
        tgt_pos_col = next((c for c in target_df.columns if "position code" in str(c).lower()), "Position Code 2026-27")
        t_zone = target_df[target_df[tgt_pos_col].astype(str).str.strip().str.upper().isin(z_pos_set)].copy() if tgt_pos_col in target_df.columns else target_df
    else:
        t_zone = pd.DataFrame()

    if s_m is not None and not s_m.empty:
        pos_match = s_m["POSITION_CODE"].astype(str).str.strip().str.upper().isin(z_pos_set) if "POSITION_CODE" in s_m.columns else pd.Series(False, index=s_m.index)
        terr_match = s_m["FF_TERRITORY"].astype(str).str.strip().str.upper().isin(z_terr_set) if "FF_TERRITORY" in s_m.columns else pd.Series(False, index=s_m.index)
        s_zone = s_m[pos_match | terr_match].copy()
    else:
        s_zone = pd.DataFrame()

    # 4. Evaluate each subordinate (MIO, PS, ASM)
    team_breakdown = []
    mio_ps_total_payout = 0.0
    asm_total_payout = 0.0

    total_zone_act_val = 0.0
    total_zone_tgt_val = 0.0
    total_zone_act_units = 0.0
    total_zone_tgt_units = 0.0

    if not z_staff.empty:
        for _, r in z_staff.iterrows():
            sub_name = str(r.get("Employe_Name") or "").strip()
            sub_pos = str(r.get("Position_Code") or "").strip()
            sub_desg = str(r.get("Designation_Name") or "").strip().upper()
            sub_terr = str(r.get("Dept. Territory Code") or "").strip()
            sub_region = str(r.get("Region_Name") or "").strip()
            is_sub_asm = (sub_desg == "ASM")

            if is_sub_asm:
                eval_tgt, eval_sal = aggregate_asm_datasets(
                    sub_name, sub_pos, month, t_zone, s_zone, staff_df, territory=sub_terr
                )
            else:
                eval_tgt, eval_sal = t_zone, s_zone

            eval_res = evaluate_pharma_incentives(
                employee=sub_name,
                month=month,
                target_df=eval_tgt,
                sales_df=eval_sal,
                target_master_col=target_master_col,
                t_net_col=t_net_col,
                t_unit_col=t_unit_col,
                pos_code=sub_pos,
                territory=sub_terr,
                is_asm=is_sub_asm,
                designation=sub_desg
            )

            earned = eval_res["total_incentive"]
            rsm_share = round(0.10 * earned, 2)

            if is_sub_asm:
                asm_total_payout += earned
            else:
                mio_ps_total_payout += earned
                # Track zone-level totals using MIO/PS actuals to avoid double-counting ASM aggregated totals
                total_zone_act_val += eval_res["total_act_val"]
                total_zone_tgt_val += eval_res["total_tgt_val"]
                total_zone_act_units += eval_res["total_act_units"]
                total_zone_tgt_units += eval_res["total_tgt_units"]

            team_breakdown.append({
                "name": sub_name,
                "pos_code": sub_pos,
                "designation": sub_desg,
                "territory": sub_terr,
                "region": sub_region,
                "total_act_val": eval_res["total_act_val"],
                "total_tgt_val": eval_res["total_tgt_val"],
                "val_achievement": eval_res["overall_achievement"],
                "total_act_units": eval_res["total_act_units"],
                "total_tgt_units": eval_res["total_tgt_units"],
                "unit_achievement": eval_res["overall_unit_achievement"],
                "bottom_line_qualified": eval_res["bottom_line_qualified"],
                "qualified_count": eval_res["qualified_count"],
                "rate_bearing_products": eval_res["rate_bearing_products"],
                "status": eval_res["status"],
                "earned_incentive": earned,
                "rsm_share": rsm_share,
                "remark": eval_res["remark"],
            })

    # Sort team breakdown: qualified staff with highest payout first, then others
    team_breakdown.sort(key=lambda x: (x["earned_incentive"], x["val_achievement"]), reverse=True)

    zone_total_pool = mio_ps_total_payout + asm_total_payout
    rsm_incentive = round(0.10 * zone_total_pool, 2)

    mio_ps_members = [b for b in team_breakdown if b["designation"] in ["MIO", "PS"]]
    asm_members = [b for b in team_breakdown if b["designation"] == "ASM"]

    mio_ps_count = len(mio_ps_members)
    asm_count = len(asm_members)
    total_staff_count = len(team_breakdown)

    qualified_mio_ps_count = len([b for b in mio_ps_members if b["earned_incentive"] > 0])
    qualified_asm_count = len([b for b in asm_members if b["earned_incentive"] > 0])
    qualified_staff_count = qualified_mio_ps_count + qualified_asm_count

    zone_val_ach = (total_zone_act_val / total_zone_tgt_val * 100.0) if total_zone_tgt_val > 0 else 0.0
    zone_unit_ach = (total_zone_act_units / total_zone_tgt_units * 100.0) if total_zone_tgt_units > 0 else 0.0

    remark = (
        f"Earned Rs. {rsm_incentive:,.0f} (10% of Zone {zone_name} Total Incentive Pool of "
        f"Rs. {zone_total_pool:,.0f} across {qualified_staff_count} qualifying Field Force staff: "
        f"{qualified_mio_ps_count}/{mio_ps_count} MIO/PS and {qualified_asm_count}/{asm_count} ASMs)."
    )

    result = {
        "rsm_name": rsm_name,
        "rsm_pos_code": rsm_pos,
        "rsm_zone": zone_name,
        "month": month,
        "total_incentive": rsm_incentive,
        "rsm_rate_pct": 10.0,
        "zone_total_pool": zone_total_pool,
        "mio_ps_total_payout": mio_ps_total_payout,
        "asm_total_payout": asm_total_payout,
        "total_staff_count": total_staff_count,
        "mio_ps_count": mio_ps_count,
        "asm_count": asm_count,
        "qualified_staff_count": qualified_staff_count,
        "qualified_mio_ps_count": qualified_mio_ps_count,
        "qualified_asm_count": qualified_asm_count,
        "team_breakdown": team_breakdown,
        "zone_act_val": total_zone_act_val,
        "zone_tgt_val": total_zone_tgt_val,
        "zone_val_achievement": zone_val_ach,
        "zone_act_units": total_zone_act_units,
        "zone_tgt_units": total_zone_tgt_units,
        "zone_unit_achievement": zone_unit_ach,
        "zone_units_qualified": bool(zone_unit_ach >= 85.0),
        "status": "QUALIFIED" if rsm_incentive > 0 else "NOT QUALIFIED",
        "active_qualified": bool(rsm_incentive > 0),
        "remark": remark,
        "is_pharma_rsm": True
    }

    _PHARMA_RSM_CACHE[cache_key] = result
    return result
