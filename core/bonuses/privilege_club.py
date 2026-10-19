"""
Privilege Club Incentive Module
Calculates Privilege Club (1 Million Net Sales) incentive for:
- SPOs (Rs. 25,000 for individual 1M net sales)
- ASMs (Rs. 60,000 if ALL SPOs achieve 1M net sales)
- RSMs (Rs. 100,000 if ALL ASMs achieve 100% Net Sales target)
"""
import pandas as pd


def calculate_privilege_club_incentive(employee, month, sales_df, pos_code=None, territory=None):
    """
    Calculates Privilege Club (1 Million Club) Incentive for SPOs across all teams:
    DO, TOUCH, OVERLAPPING, and BLISS.
    Qualifying Criteria: On Achievement of PKR 1 Million Net Sales in a month.
    Incentive Amount: Rs. 25,000.
    """
    if sales_df is None or sales_df.empty:
        actual = 0.0
    else:
        if pos_code and 'POSITION_CODE' in sales_df.columns:
            emp_mask = (sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper())
        elif territory and 'FF_TERRITORY' in sales_df.columns:
            emp_mask = (
                (sales_df['NAME'].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                (sales_df['FF_TERRITORY'].astype(str).str.strip().str.upper() == str(territory).strip().upper())
            )
        else:
            emp_mask = (sales_df['NAME'].astype(str).str.strip().str.lower() == str(employee).strip().lower())

        month_mask = (sales_df['REPORTING_MONTH'].astype(str).str.strip() == str(month).strip())
        emp_sales = sales_df[emp_mask & month_mask]

        val_col = 'NET_WO_REG_DISC_VALUE' if 'NET_WO_REG_DISC_VALUE' in emp_sales.columns else ('NET_SALE_VALUE' if 'NET_SALE_VALUE' in emp_sales.columns else None)
        actual = float(emp_sales[val_col].sum()) if (val_col and not emp_sales.empty) else 0.0

    target = 1000000.0
    qualified = (actual >= target)
    achievement = (actual / target * 100.0) if target > 0 else 0.0
    incentive = 25000 if qualified else 0
    shortfall = max(target - actual, 0.0) if not qualified else 0.0

    if qualified:
        status = "Qualified (1 Million Club)"
        slab_name = "1 Million Club"
        remark = "1 Million Club Incentive Criteria Qualified"
        req_text = "Requirement Met"
    else:
        status = "Not Qualified"
        slab_name = "Below 1 Million"
        remark = f"(Min.) NET Value = {round(shortfall):,}/= fell short to Qualify 1 Million Club Criteria"
        req_text = f"Need: Rs. {shortfall:,.0f} to Qualify"

    return {
        'id': 'privilege_club',
        'key': 'privilege_club',
        'name': 'Privilege Club',
        'short_name': 'Privilege Club',
        'target': target,
        'actual': actual,
        'achievement': achievement,
        'qualified': qualified,
        'incentive': incentive,
        'applicable_incentive': incentive,
        'status': status,
        'slab_name': slab_name,
        'remark': remark,
        'need': shortfall,
        'need_text': req_text,
        'policy_rule': 'On Achievement of PKR 1 Million Net Sales in a month',
    }


def calculate_asm_privilege_club(asm_employee, month, sales_df, staff_df, asm_pos_code=None):
    """
    Calculates the ASM Privilege Club incentive.

    Business Rule:
    - Identify ALL SPOs working under the selected ASM's region.
    - For each SPO, calculate their monthly Net Sales.
    - SPO qualifies if Net Sales >= Rs. 1,000,000.
    - ASM qualifies ONLY when EVERY SPO individually qualifies (all-or-nothing).
    - ASM Incentive: Rs. 60,000 if all qualify, else Rs. 0.
    """
    SPO_TARGET = 1_000_000.0
    ASM_INCENTIVE = 60_000
    SPO_INCENTIVE = 25_000

    spo_breakdown = []
    total_spo = 0
    qualified_spo = 0

    if sales_df is None or sales_df.empty or staff_df is None or staff_df.empty:
        return _asm_privilege_result(0, 0, 0, spo_breakdown, SPO_TARGET, ASM_INCENTIVE)

    # 1. Find the ASM in staff_df
    asm_mask = pd.Series(False, index=staff_df.index)
    if asm_pos_code:
        asm_mask = asm_mask | (staff_df['Position_Code'].astype(str).str.strip().str.upper() == str(asm_pos_code).strip().upper())
        asm_mask = asm_mask | (staff_df['Dept. Territory Code'].astype(str).str.strip().str.upper() == str(asm_pos_code).strip().upper())
    if asm_employee:
        asm_mask = asm_mask | (staff_df['Employe_Name'].astype(str).str.strip().str.lower() == str(asm_employee).strip().lower())

    asm_row = staff_df[asm_mask]
    if asm_row.empty:
        return _asm_privilege_result(0, 0, 0, spo_breakdown, SPO_TARGET, ASM_INCENTIVE)

    asm_info = asm_row.iloc[0]
    asm_pos = str(asm_info.get('Position_Code') or asm_pos_code or '').strip()
    asm_name = str(asm_info.get('Employe_Name') or asm_employee or '').strip()
    region_name = str(asm_info.get('Region_Name') or '').strip().upper()
    team_name = str(asm_info.get('Team_Name') or '').strip().upper()

    # 2. Find all SPOs reporting to this ASM
    spo_mask = pd.Series(False, index=staff_df.index)
    if asm_pos:
        spo_mask = spo_mask | (staff_df['Report_To_Position_Code'].astype(str).str.strip().str.upper() == asm_pos.upper())
    if asm_name:
        spo_mask = spo_mask | (staff_df['Report_To_Name'].astype(str).str.strip().str.lower() == asm_name.lower())

    # Also include all staff in same region/team (excluding ASM themselves)
    if region_name:
        reg_staff = staff_df[staff_df['Region_Name'].astype(str).str.strip().str.upper() == region_name]
        if team_name:
            reg_staff = reg_staff[reg_staff['Team_Name'].astype(str).str.strip().str.upper() == team_name]
        if asm_pos:
            reg_staff = reg_staff[reg_staff['Position_Code'].astype(str).str.strip().str.upper() != asm_pos.upper()]
        spo_mask = spo_mask | staff_df.index.isin(reg_staff.index)

    reporters = staff_df[spo_mask].drop_duplicates(subset=['Position_Code'])
    if asm_pos:
        reporters = reporters[reporters['Position_Code'].astype(str).str.strip().str.upper() != asm_pos.upper()]
    if not reporters.empty:
        _nm = reporters['Employe_Name'].astype(str).str.upper()
        _pc = reporters['Position_Code'].astype(str).str.strip().str.upper()
        _is_dummy = _nm.str.contains('UNMAPPED', na=False) | _nm.str.strip().str.startswith('VACANT', na=False)
        _is_dummy = _is_dummy | _pc.str.endswith('-00')
        reporters = reporters[~_is_dummy]

    total_spo = len(reporters)

    # 3. For each SPO, calculate Net Sales
    val_col = 'NET_WO_REG_DISC_VALUE' if 'NET_WO_REG_DISC_VALUE' in sales_df.columns else (
        'NET_SALE_VALUE' if 'NET_SALE_VALUE' in sales_df.columns else None
    )
    month_mask = (sales_df['REPORTING_MONTH'].astype(str).str.strip() == str(month).strip()) if 'REPORTING_MONTH' in sales_df.columns else pd.Series(True, index=sales_df.index)

    for _, spo_row in reporters.iterrows():
        spo_name = str(spo_row.get('Employe_Name') or '').strip()
        spo_pos = str(spo_row.get('Position_Code') or '').strip()

        spo_sales = sales_df[month_mask] if 'REPORTING_MONTH' in sales_df.columns else sales_df
        if spo_pos and 'POSITION_CODE' in sales_df.columns:
            _pos_hit = (spo_sales['POSITION_CODE'].astype(str).str.strip().str.upper() == spo_pos.upper())
            if _pos_hit.any():
                spo_sales = spo_sales[_pos_hit]
            elif spo_name and 'NAME' in sales_df.columns:
                spo_sales = spo_sales[spo_sales['NAME'].astype(str).str.strip().str.lower() == spo_name.lower()]
            else:
                spo_sales = spo_sales.iloc[0:0]
        elif spo_name and 'NAME' in sales_df.columns:
            spo_sales = spo_sales[spo_sales['NAME'].astype(str).str.strip().str.lower() == spo_name.lower()]
        else:
            spo_sales = spo_sales.iloc[0:0]
        actual = float(spo_sales[val_col].sum()) if (val_col and not spo_sales.empty) else 0.0
        is_qualified = actual >= SPO_TARGET
        shortfall = max(SPO_TARGET - actual, 0.0)
        if is_qualified:
            qualified_spo += 1

        spo_breakdown.append({
            'name': spo_name,
            'pos_code': spo_pos,
            'actual': actual,
            'target': SPO_TARGET,
            'qualified': is_qualified,
            'incentive': SPO_INCENTIVE if is_qualified else 0,
            'shortfall': shortfall,
        })

    return _asm_privilege_result(total_spo, qualified_spo, ASM_INCENTIVE, spo_breakdown, SPO_TARGET, ASM_INCENTIVE)


def _asm_privilege_result(total_spo, qualified_spo, asm_incentive_max, spo_breakdown, spo_target, asm_incentive_max_val):
    """Helper to build the ASM Privilege Club result dict."""
    asm_qualified = (total_spo > 0) and (qualified_spo == total_spo)
    earned = asm_incentive_max_val if asm_qualified else 0
    not_qualified_list = [s for s in spo_breakdown if not s['qualified']]

    if asm_qualified:
        status = 'QUALIFIED'
        remark = (
            f"All {qualified_spo} of {total_spo} SPOs achieved the PKR 1 Million monthly Net Sales "
            f"requirement. ASM qualified for Rs. {asm_incentive_max_val:,.0f} Privilege Club incentive."
        )
    else:
        status = 'NOT QUALIFIED'
        if total_spo == 0:
            remark = "No SPOs found under this ASM for the selected month."
        else:
            nq_names = ', '.join(s['name'] for s in not_qualified_list[:3])
            if len(not_qualified_list) > 3:
                nq_names += f" and {len(not_qualified_list) - 3} more"
            remark = (
                f"{qualified_spo} of {total_spo} SPOs qualified. All SPOs must individually achieve "
                f"PKR 1 Million Net Sales. ASM Privilege Club incentive is Rs. 0. "
                f"Not qualified: {nq_names}."
            )

    return {
        'total_spo': total_spo,
        'qualified_spo': qualified_spo,
        'not_qualified_spo': total_spo - qualified_spo,
        'asm_qualified': asm_qualified,
        'incentive': earned,
        'max_incentive': asm_incentive_max_val,
        'spo_target': spo_target,
        'spo_breakdown': spo_breakdown,
        'status': status,
        'remark': remark,
        'not_qualified_list': not_qualified_list,
    }


def calculate_rsm_privilege_club(rsm_employee, month, sales_df, staff_df, target_df, rsm_pos_code=None, aggregate_asm_fn=None):
    """
    Calculates the RSM Privilege Club incentive (Rs. 100,000).

    Policy (per Incentive Criteria sheet):
    - RSMs: "If all ASMs of His/her respective region achieve Net Sales
      Target in a month." -> Rs. 100,000.
    - 100% Target vs Achievement is necessary; Net Sales value considered.
    - All-or-nothing: RSM qualifies ONLY when EVERY ASM hits 100%.
    """
    RSM_INCENTIVE = 100_000
    asm_breakdown = []
    total_asm = 0
    qualified_asm = 0

    if staff_df is None or staff_df.empty or target_df is None or target_df.empty or sales_df is None or sales_df.empty:
        return _rsm_privilege_result(0, 0, RSM_INCENTIVE, asm_breakdown)

    # 1. Find the RSM in staff_df
    rsm_mask = pd.Series(False, index=staff_df.index)
    if rsm_pos_code:
        rsm_mask = rsm_mask | (staff_df['Position_Code'].astype(str).str.strip().str.upper() == str(rsm_pos_code).strip().upper())
        rsm_mask = rsm_mask | (staff_df['Dept. Territory Code'].astype(str).str.strip().str.upper() == str(rsm_pos_code).strip().upper())
    if rsm_employee:
        rsm_mask = rsm_mask | (staff_df['Employe_Name'].astype(str).str.strip().str.lower() == str(rsm_employee).strip().lower())

    rsm_row = staff_df[rsm_mask]
    if rsm_row.empty:
        return _rsm_privilege_result(0, 0, RSM_INCENTIVE, asm_breakdown)

    r0 = rsm_row.iloc[0]
    rsm_pos = str(r0.get('Position_Code') or rsm_pos_code or '').strip()
    rsm_name = str(r0.get('Employe_Name') or rsm_employee or '').strip()
    sub_zone = str(r0.get('Sub_Zone') or '').strip().upper()

    # 2. Find all ASMs under this RSM
    asm_mask = (staff_df['Designation_Name'].astype(str).str.strip().str.upper() == 'ASM') & (
        (staff_df['Sub_Zone'].astype(str).str.strip().str.upper() == sub_zone) |
        (staff_df['Report_To_Position_Code'].astype(str).str.strip().str.upper() == rsm_pos.upper()) |
        (staff_df['Report_To_Name'].astype(str).str.strip().str.lower() == rsm_name.lower())
    ) & staff_df['Team_Name'].astype(str).str.upper().str.contains('CONSUMER GOODS|FMCG', na=False)

    asms = staff_df[asm_mask].drop_duplicates(subset=['Position_Code'])
    total_asm = len(asms)

    # Resolve the month's Net Target column robustly
    t_net_col = None
    try:
        m_short = pd.to_datetime(str(month).strip(), format="%B,%y").strftime("%b-%y")
    except Exception:
        m_short = None
    if m_short:
        for c in target_df.columns:
            if str(c).strip() == f"TGT Net WO/Reg. {m_short}":
                t_net_col = c
                break
    if not t_net_col:
        m_clean = str(month).lower()
        for c in target_df.columns:
            c_str = str(c).lower().strip()
            if 'tgt net' in c_str and ('jul' in m_clean if 'jul' in c_str else ('aug' in m_clean if 'aug' in c_str else True)):
                t_net_col = c
                break
    if not t_net_col:
        for c in target_df.columns:
            if 'net' in str(c).lower():
                t_net_col = c
                break

    val_col = 'NET_WO_REG_DISC_VALUE' if 'NET_WO_REG_DISC_VALUE' in sales_df.columns else (
        'NET_SALE_VALUE' if 'NET_SALE_VALUE' in sales_df.columns else None
    )

    for _, a_row in asms.iterrows():
        a_name = str(a_row.get('Employe_Name') or '').strip()
        a_pos = str(a_row.get('Position_Code') or '').strip()
        a_terr = str(a_row.get('Dept. Territory Code') or '').strip()

        if aggregate_asm_fn:
            a_tgt, a_sal = aggregate_asm_fn(a_name, a_pos, month, target_df, sales_df, staff_df, territory=a_terr)
        else:
            t_mask = target_df['Position Code 2026-27'].astype(str).str.strip().str.upper() == a_pos.upper() if 'Position Code 2026-27' in target_df.columns else pd.Series(False, index=target_df.index)
            s_mask = sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == a_pos.upper() if 'POSITION_CODE' in sales_df.columns else pd.Series(False, index=sales_df.index)
            a_tgt, a_sal = target_df[t_mask], sales_df[s_mask]

        tot_tgt = float(a_tgt[t_net_col].sum()) if (t_net_col and t_net_col in a_tgt.columns) else 0.0
        tot_sal = float(a_sal[val_col].sum()) if (val_col and val_col in a_sal.columns) else 0.0
        is_qual = (tot_sal >= tot_tgt) if tot_tgt > 0 else False
        ach = (tot_sal / tot_tgt * 100.0) if tot_tgt > 0 else 0.0
        shortfall = max(tot_tgt - tot_sal, 0.0)

        if is_qual:
            qualified_asm += 1

        asm_breakdown.append({
            'name': a_name,
            'pos_code': a_pos,
            'actual': tot_sal,
            'target': tot_tgt,
            'achievement': ach,
            'qualified': is_qual,
            'shortfall': shortfall,
        })

    return _rsm_privilege_result(total_asm, qualified_asm, RSM_INCENTIVE, asm_breakdown)


def _rsm_privilege_result(total_asm, qualified_asm, rsm_incentive_max, asm_breakdown):
    """Helper to build the RSM Privilege Club result dict."""
    rsm_qualified = (total_asm > 0) and (qualified_asm == total_asm)
    earned = rsm_incentive_max if rsm_qualified else 0
    not_qualified_list = [a for a in asm_breakdown if not a['qualified']]
    total_target = float(sum(float(a.get('target', 0.0) or 0.0) for a in asm_breakdown))
    total_actual = float(sum(float(a.get('actual', 0.0) or 0.0) for a in asm_breakdown))

    if rsm_qualified:
        status = 'QUALIFIED'
        remark = (
            f"All {qualified_asm} ASMs of the region achieved 100% Net Sales Target "
            f"(Rs. {total_actual:,.0f} / Rs. {total_target:,.0f}). "
            f"RSM qualified for Rs. {rsm_incentive_max:,.0f} Privilege Club incentive."
        )
    else:
        status = 'NOT QUALIFIED'
        if total_asm == 0:
            remark = "No ASMs found under this RSM for the selected month."
        else:
            nq_names = ', '.join(a['name'] for a in not_qualified_list[:3])
            if len(not_qualified_list) > 3:
                nq_names += f" and {len(not_qualified_list) - 3} more"
            remark = (
                f"{len(not_qualified_list)} of {total_asm} ASM fell short to Achieve 100% Net Criteria "
                f"(Rs. {total_actual:,.0f} / Rs. {total_target:,.0f}). Not qualified: {nq_names}."
            )

    return {
        'total_asm': total_asm,
        'qualified_asm': qualified_asm,
        'not_qualified_asm': total_asm - qualified_asm,
        'rsm_qualified': rsm_qualified,
        'incentive': earned,
        'max_incentive': rsm_incentive_max,
        'asm_breakdown': asm_breakdown,
        'status': status,
        'remark': remark,
        'not_qualified_list': not_qualified_list,
        'total_target': total_target,
        'total_actual': total_actual,
    }
