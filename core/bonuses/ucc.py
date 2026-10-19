"""
Universal Coverage Criteria (UCC) Module
Calculates UCC (Unique Active Shops) Incentive for SPOs and BLISS ASM UCC bonus.
"""
import pandas as pd


def calculate_ucc_incentive(employee, month, pos_code, emp_type, sales_df, bottom_line_ach=0.0, total_net_target=0.0, territory=None, active_category=None):
    """
    Calculates UCC (Unique Active Shops) Incentive based on policy.

    BLISS SPOs (active_category == 'bliss'):
    - Rs. 20 per active shop, minimum 100 active shops (shops-only gate,
      no bottom-line condition).
    - Active shop = unique shop with BLISS/MAXI product sales in the month.
    """
    emp_sales = pd.DataFrame()
    if sales_df is not None and not sales_df.empty:
        if pos_code and 'POSITION_CODE' in sales_df.columns:
            emp_filter = (
                (sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()) &
                (sales_df['REPORTING_MONTH'] == month)
            )
        elif territory and 'FF_TERRITORY' in sales_df.columns:
            emp_filter = (
                (sales_df['NAME'].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                (sales_df['FF_TERRITORY'].astype(str).str.strip().str.upper() == str(territory).strip().upper()) &
                (sales_df['REPORTING_MONTH'] == month)
            )
        else:
            emp_filter = (
                (sales_df['NAME'].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
                (sales_df['REPORTING_MONTH'] == month)
            )
        emp_sales = sales_df[emp_filter]

    ucc_mapping_cols = ['NAME', 'POSITION_CODE', 'SECTION_NAME', 'CUST_MAPPING', 'CUST_NAME', 'CUST_NUMBER']
    available_cols = [c for c in ucc_mapping_cols if c in emp_sales.columns]
    qty_col = 'NET_QTY' if 'NET_QTY' in emp_sales.columns else ('NET_SALE_QTY' if 'NET_SALE_QTY' in emp_sales.columns else 'NET_SALE_VALUE')
    val_col = 'NET_SALE_VALUE' if 'NET_SALE_VALUE' in emp_sales.columns else ('SALE_NET_VALUE' if 'SALE_NET_VALUE' in emp_sales.columns else None)

    # BLISS SPO UCC: Rs. 20 per BLISS/MAXI active shop, min 100 shops (shops-only).
    if str(active_category or '').strip().lower() == 'bliss':
        bliss_sales = emp_sales
        if not bliss_sales.empty and 'PRD_GRP' in bliss_sales.columns:
            bliss_sales = bliss_sales[bliss_sales['PRD_GRP'].astype(str).str.strip().str.upper().str.startswith(('BLISS', 'MAXI'))]
        bliss_cols = [c for c in ucc_mapping_cols if c in bliss_sales.columns]
        if not bliss_sales.empty:
            if bliss_cols and qty_col and qty_col in bliss_sales.columns:
                _sums = bliss_sales.groupby(bliss_cols, as_index=False)[qty_col].sum()
                bliss_ucc = int((_sums[qty_col] > 0).sum())
            elif qty_col and 'CUST_NUMBER' in bliss_sales.columns:
                _sums = bliss_sales.groupby('CUST_NUMBER')[qty_col].sum()
                bliss_ucc = int((_sums > 0).sum())
            elif bliss_cols:
                bliss_ucc = len(bliss_sales[bliss_cols].drop_duplicates())
            else:
                bliss_ucc = int(bliss_sales['CUST_NUMBER'].dropna().nunique()) if 'CUST_NUMBER' in bliss_sales.columns else 0
        else:
            bliss_ucc = 0
        _rate, _min = 20, 100
        _qual = bliss_ucc >= _min
        _inc = bliss_ucc * _rate if _qual else 0
        return {
            'role_name': 'BLISS SPO',
            'emp_type': emp_type or 'BLISS',
            'emp_type_label': f"BLISS SPO ({emp_type})" if emp_type else "BLISS SPO",
            'target_ucc': _min,
            'actual_ucc': bliss_ucc,
            'achievement': (bliss_ucc / _min * 100.0) if _min else 0.0,
            'min_ucc_required': _min,
            'qualified': _qual,
            'is_exempt': False,
            'status': 'QUALIFIED' if _qual else 'NOT QUALIFIED',
            'status_label': 'QUALIFIED' if _qual else 'NOT QUALIFIED',
            'slab_name': 'BLISS 100+ Slab' if _qual else 'Below 100 Active Shops',
            'slab_label': f"BLISS 100+ Slab (Rs. {_rate}/shop)" if _qual else 'Below 100 Active Shops',
            'rate_per_ucc': _rate,
            'incentive': _inc,
            'need_ucc': max(_min - bliss_ucc, 0),
            'need_text': 'Requirement Met' if _qual else f"Need: {max(_min - bliss_ucc, 0)} more active shops (min {_min})",
            'remark': f"Qualified with {bliss_ucc} BLISS active shops (Rs. {_rate}/shop | Rs. {_inc:,.0f} earned)" if _qual else f"Not Qualified: min {_min} BLISS active shops required (have {bliss_ucc})",
            'bottom_line_ach': bottom_line_ach,
            'bl_condition_text': 'Shops-only (no bottom-line gate)',
            'sd_achievement': 0.0,
            'sd_sales_value': 0.0,
            'sd_ucc': 0,
            'has_gssd': False,
        }

    if not emp_sales.empty:
        if available_cols and qty_col:
            cust_net_sums = emp_sales.groupby(available_cols, as_index=False)[qty_col].sum()
            actual_ucc = int((cust_net_sums[qty_col] > 0).sum())
        elif qty_col and 'CUST_NUMBER' in emp_sales.columns:
            cust_net_sums = emp_sales.groupby('CUST_NUMBER')[qty_col].sum()
            actual_ucc = int((cust_net_sums > 0).sum())
        elif available_cols:
            actual_ucc = len(emp_sales[available_cols].drop_duplicates())
        else:
            actual_ucc = int(emp_sales['CUST_NUMBER'].dropna().nunique())
    else:
        actual_ucc = 0

    sd_sales_value = 0.0
    sd_ucc = 0
    has_gssd = False
    if not emp_sales.empty and 'ACCOUNT_TYPE' in emp_sales.columns:
        sd_mask = emp_sales['ACCOUNT_TYPE'].astype(str).str.strip().str.upper().str.replace(' ', '', regex=False) == 'GS-SD'
        sd_sub = emp_sales[sd_mask]
        if not sd_sub.empty:
            has_gssd = False
            if val_col:
                sd_sales_value = float(sd_sub[val_col].sum())
            else:
                sd_sales_value = float(sd_sub['NET_SALE_VALUE'].sum()) if 'NET_SALE_VALUE' in sd_sub.columns else 0.0

            if available_cols and qty_col:
                sd_cust_sums = sd_sub.groupby(available_cols, as_index=False)[qty_col].sum()
                sd_ucc = int((sd_cust_sums[qty_col] > 0).sum())
            elif qty_col and 'CUST_NUMBER' in sd_sub.columns:
                sd_cust_sums = sd_sub.groupby('CUST_NUMBER')[qty_col].sum()
                sd_ucc = int((sd_cust_sums > 0).sum())
            else:
                sd_ucc = len(sd_sub[available_cols].drop_duplicates()) if available_cols else int(sd_sub['CUST_NUMBER'].dropna().nunique())

    sd_achievement = (sd_sales_value / total_net_target * 100.0) if total_net_target > 0 else 0.0
    normalized_emp_type = str(emp_type or '').strip().upper()

    # 1. SD+STREET SPOs
    if normalized_emp_type == 'SD+STREET':
        role_name = "SD+STREET SPO"
        emp_type_label = "SD+STREET"
        target_ucc = 200
        min_ucc_required = 200
        is_exempt = False
        has_gssd = False

        bl_qualified = bottom_line_ach >= 99.99
        ucc_qualified = actual_ucc >= 200
        qualified = bl_qualified and ucc_qualified

        if qualified:
            if actual_ucc >= 225:
                slab_name = "Street and 225 Slab"
                rate_per_ucc = 40
            else:
                slab_name = "Street and 200 Slab"
                rate_per_ucc = 35
            incentive = actual_ucc * rate_per_ucc
            status = "QUALIFIED"
            need_text = "Requirement Met"
            need_ucc = 0
            remark = f"Active UCC Qualify with {slab_name}"
        else:
            slab_name = "Below 200 UCC" if actual_ucc < 200 else "Bottom-Line Below 100%"
            rate_per_ucc = 0
            incentive = 0
            status = "NOT QUALIFIED"
            need_ucc = max(200 - actual_ucc, 0)
            if need_ucc > 0 and not bl_qualified:
                need_text = f"Need: {need_ucc} more UCC & Bottom-Line >= 100%"
                remark = f"Not Qualified: Mandatory 200+ UCC & 100% Bottom-Line required (Need {need_ucc} UCC)"
            elif need_ucc > 0:
                need_text = f"Need: {need_ucc} more UCC (min 200 UCC)"
                remark = f"Not Qualified: Mandatory 200+ UCC required (Need {need_ucc} UCC)"
            else:
                need_text = "Need: Bottom-Line Net Value >= 100%"
                remark = "Not Qualified: Bottom-Line Net Value must reach >= 100% for UCC payout"

    # 2. Pure STREET SPOs
    elif normalized_emp_type == 'STREET':
        role_name = "STREET SPO"
        emp_type_label = "STREET"
        target_ucc = 200
        min_ucc_required = 200
        is_exempt = False

        bl_qualified = bottom_line_ach >= 99.99
        ucc_qualified = actual_ucc >= 200
        qualified = bl_qualified and ucc_qualified

        if qualified:
            if actual_ucc >= 225:
                slab_name = "Street 225 Slab"
                rate_per_ucc = 40
            else:
                slab_name = "Street 200 Slab"
                rate_per_ucc = 35
            incentive = actual_ucc * rate_per_ucc
            status = "QUALIFIED"
            need_text = "Requirement Met"
            need_ucc = 0
            remark = f"Qualified with {slab_name} (Rs. {rate_per_ucc} per UCC | Rs. {incentive:,.0f} earned)"
        else:
            slab_name = "Below 200 UCC" if actual_ucc < 200 else "Bottom-Line Below 100%"
            rate_per_ucc = 0
            incentive = 0
            status = "NOT QUALIFIED"
            need_ucc = max(200 - actual_ucc, 0)
            if need_ucc > 0 and not bl_qualified:
                need_text = f"Need: {need_ucc} more UCC & Bottom-Line >= 100%"
                remark = f"Not Qualified: Mandatory 200+ UCC & 100% Bottom-Line required (Need {need_ucc} UCC)"
            elif need_ucc > 0:
                need_text = f"Need: {need_ucc} more UCC to Qualify"
                remark = f"Not Qualified: Mandatory 200+ UCC required (Need {need_ucc} UCC)"
            else:
                need_text = "Need: Bottom-Line Net Value >= 100%"
                remark = "Not Qualified: Bottom-Line Net Value must reach >= 100% for UCC payout"

    # 3. SD-based SPOs (SD, PHR+SD+STREET, PHR+STREET)
    elif normalized_emp_type in ('SD', 'PHR+SD+STREET', 'PHR+STREET'):
        role_name = "SD-based SPO"
        emp_type_label = "SD"
        target_ucc = 50
        min_ucc_required = 50
        is_exempt = False
        has_gssd = False

        qualified = actual_ucc >= 50
        if qualified:
            if actual_ucc >= 70:
                slab_name = "SD 70+ Slab"
                rate_per_ucc = 40
            else:
                slab_name = "SD 50 Slab"
                rate_per_ucc = 35
            incentive = actual_ucc * rate_per_ucc
            status = "QUALIFIED"
            need_text = "Requirement Met"
            need_ucc = 0
            remark = f"Qualified with {slab_name} (Rs. {rate_per_ucc}/UCC | Rs. {incentive:,.0f} earned)"
        else:
            slab_name = "Below 50 UCC"
            rate_per_ucc = 0
            incentive = 0
            status = "NOT QUALIFIED"
            need_ucc = max(50 - actual_ucc, 0)
            need_text = f"Need: {need_ucc} more UCC (min 50 UCC)"
            remark = f"Not Qualified: Mandatory min 50 UCC required (Need {need_ucc} UCC)"

    # Fallback
    else:
        role_name = "SPO"
        emp_type_label = emp_type or "N/A"
        target_ucc = 200
        min_ucc_required = 200
        is_exempt = False
        status = "NOT APPLICABLE"
        slab_name = "N/A"
        rate_per_ucc = 0
        incentive = 0
        qualified = False
        need_ucc = 0
        need_text = "N/A"
        remark = "UCC Incentive criteria applies to STREET, SD+STREET, and SD-based SPOs."

    achievement = (actual_ucc / target_ucc * 100.0) if target_ucc > 0 else 0.0

    if normalized_emp_type in ('SD', 'PHR+SD+STREET', 'PHR+STREET'):
        bl_condition_text = "Shops-only (min 50 UCC)"
    else:
        bl_condition_text = f"BL: {round(bottom_line_ach):.0f}% (Achieved >= 100%)" if bottom_line_ach >= 99.99 else f"BL: {round(bottom_line_ach):.0f}% (Below 100%)"

    return {
        'role_name': role_name,
        'emp_type': emp_type_label,
        'emp_type_label': f"{role_name} ({emp_type_label})" if emp_type_label != "N/A" else role_name,
        'target_ucc': target_ucc,
        'actual_ucc': actual_ucc,
        'achievement': achievement,
        'min_ucc_required': min_ucc_required,
        'qualified': qualified,
        'is_exempt': is_exempt,
        'status': status,
        'status_label': status,
        'slab_name': slab_name,
        'slab_label': f"{slab_name} (Rs. {rate_per_ucc}/UCC)" if rate_per_ucc > 0 else slab_name,
        'rate_per_ucc': rate_per_ucc,
        'incentive': incentive,
        'need_ucc': need_ucc,
        'need_text': need_text,
        'remark': remark,
        'bottom_line_ach': bottom_line_ach,
        'bl_condition_text': bl_condition_text,
        'sd_achievement': sd_achievement,
        'sd_sales_value': sd_sales_value,
        'sd_ucc': sd_ucc,
        'has_gssd': has_gssd,
    }


def calculate_bliss_asm_ucc_bonus(asm_employee, month, sales_df, staff_df, target_df, target_master_col, t_net_col, asm_pos_code=None):
    """
    BLISS dedicated-ASM UCC bonus: Rs. 10,000 (additive) if ALL SPOs under
    the ASM achieve their individual BLISS Bottom-Line Net targets (>= 100%).

    SPOs with no BLISS target for the month, and dummy placeholders
    (UNMAPPED / VACANT / *-00), are excluded from the check.
    """
    BONUS = 10_000
    empty = {
        'total_spo': 0, 'qualified_spo': 0, 'not_qualified_spo': 0,
        'qualified': False, 'incentive': 0, 'max_incentive': BONUS,
        'spo_breakdown': [], 'status': 'NOT QUALIFIED',
        'remark': 'No eligible BLISS SPOs found under this ASM.',
        'not_qualified_list': [],
    }
    if staff_df is None or staff_df.empty or sales_df is None or sales_df.empty:
        return empty
    if target_df is None or target_df.empty or not t_net_col or t_net_col not in target_df.columns:
        return empty

    asm_mask = pd.Series(False, index=staff_df.index)
    if asm_pos_code:
        asm_mask = asm_mask | (staff_df['Position_Code'].astype(str).str.strip().str.upper() == str(asm_pos_code).strip().upper())
        asm_mask = asm_mask | (staff_df['Dept. Territory Code'].astype(str).str.strip().str.upper() == str(asm_pos_code).strip().upper())
    if asm_employee:
        asm_mask = asm_mask | (staff_df['Employe_Name'].astype(str).str.strip().str.lower() == str(asm_employee).strip().lower())
    asm_row = staff_df[asm_mask]
    if asm_row.empty:
        return empty
    info = asm_row.iloc[0]
    asm_pos = str(info.get('Position_Code') or asm_pos_code or '').strip()
    asm_name = str(info.get('Employe_Name') or asm_employee or '').strip()
    region_name = str(info.get('Region_Name') or '').strip().upper()
    team_name = str(info.get('Team_Name') or '').strip().upper()

    spo_mask = pd.Series(False, index=staff_df.index)
    if asm_pos:
        spo_mask = spo_mask | (staff_df['Report_To_Position_Code'].astype(str).str.strip().str.upper() == asm_pos.upper())
    if asm_name:
        spo_mask = spo_mask | (staff_df['Report_To_Name'].astype(str).str.strip().str.lower() == asm_name.lower())
    if region_name:
        reg = staff_df[staff_df['Region_Name'].astype(str).str.strip().str.upper() == region_name]
        if team_name:
            reg = reg[reg['Team_Name'].astype(str).str.strip().str.upper() == team_name]
        if asm_pos:
            reg = reg[reg['Position_Code'].astype(str).str.strip().str.upper() != asm_pos.upper()]
        spo_mask = spo_mask | staff_df.index.isin(reg.index)
    reporters = staff_df[spo_mask].drop_duplicates(subset=['Position_Code'])
    if asm_pos:
        reporters = reporters[reporters['Position_Code'].astype(str).str.strip().str.upper() != asm_pos.upper()]
    if not reporters.empty:
        _nm = reporters['Employe_Name'].astype(str).str.upper()
        _pc = reporters['Position_Code'].astype(str).str.strip().str.upper()
        _dum = _nm.str.contains('UNMAPPED', na=False) | _nm.str.strip().str.startswith('VACANT', na=False)
        _dum = _dum | _pc.str.endswith('-00')
        reporters = reporters[~_dum]
    # Only BLISS-team SPOs count toward this bonus.
    if not reporters.empty and 'Team_Name' in reporters.columns:
        reporters = reporters[reporters['Team_Name'].astype(str).str.upper().str.contains('CONSUMER GOODS - 3|FMCG03|BLISS', na=False)]
    if reporters.empty:
        return empty

    bliss_groups = [
        'BLISS MAXI THICK L-9S', 'BLISS MAXI THICK XL-8S', 'BLISS ULTRA THIN L-8S',
        'BLISS ULTRA THIN XL-7S', 'BLISS MAXI VALUE PACK 16S', 'BLISS MAXI VALUE PACK 18S',
        'MAXI STRAIGHT PADS XL',
    ]
    clean_groups = [g.upper() for g in bliss_groups]
    val_col = 'NET_WO_REG_DISC_VALUE' if 'NET_WO_REG_DISC_VALUE' in sales_df.columns else (
        'NET_SALE_VALUE' if 'NET_SALE_VALUE' in sales_df.columns else None)
    tgt_pos_col = next((c for c in target_df.columns if 'position code' in str(c).lower()), None)

    breakdown, qual = [], 0
    for _, r in reporters.iterrows():
        s_name = str(r.get('Employe_Name') or '').strip()
        s_pos = str(r.get('Position_Code') or '').strip()
        # Target: this SPO's BLISS bottom-line net target.
        t_hit = pd.Series(False, index=target_df.index)
        if s_pos and tgt_pos_col:
            t_hit = t_hit | (target_df[tgt_pos_col].astype(str).str.strip().str.upper() == s_pos.upper())
        if s_name:
            t_hit = t_hit | (target_df['F.F Name'].astype(str).str.strip().str.lower() == s_name.lower())
        t_sub = target_df[t_hit]
        if not t_sub.empty and 'Product Group' in t_sub.columns:
            t_sub = t_sub[t_sub['Product Group'].astype(str).str.upper().str.startswith(('BLISS', 'MAXI'))]
        if target_master_col and target_master_col in t_sub.columns:
            t_sub = t_sub[t_sub[target_master_col].astype(str).str.strip().str.upper().isin(clean_groups)]
        tgt = float(t_sub[t_net_col].sum()) if not t_sub.empty else 0.0
        if tgt <= 0:
            continue  # no BLISS target -> not eligible for this check
        # Actual: this SPO's BLISS bottom-line net sales for the month.
        s_hit = pd.Series(False, index=sales_df.index)
        if s_pos and 'POSITION_CODE' in sales_df.columns:
            s_hit = s_hit | (sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == s_pos.upper())
        if s_hit.any():
            s_sub = sales_df[s_hit]
        elif s_name and 'NAME' in sales_df.columns:
            s_sub = sales_df[sales_df['NAME'].astype(str).str.strip().str.lower() == s_name.lower()]
        else:
            s_sub = sales_df.iloc[0:0]
        if 'REPORTING_MONTH' in s_sub.columns:
            s_sub = s_sub[s_sub['REPORTING_MONTH'].astype(str).str.strip() == str(month).strip()]
        if 'PRD_GRP' in s_sub.columns:
            s_sub = s_sub[s_sub['PRD_GRP'].astype(str).str.strip().str.upper().str.startswith(('BLISS', 'MAXI'))]
        if 'GROUP_ON' in s_sub.columns:
            s_sub = s_sub[s_sub['GROUP_ON'].astype(str).str.strip().str.upper().isin(clean_groups)]
        act = float(s_sub[val_col].sum()) if (val_col and not s_sub.empty) else 0.0
        q = act >= tgt
        if q:
            qual += 1
        breakdown.append({'name': s_name, 'pos_code': s_pos, 'actual': act, 'target': tgt,
                          'achievement': (act / tgt * 100.0) if tgt else 0.0, 'qualified': q,
                          'shortfall': max(tgt - act, 0.0)})
    total = len(breakdown)
    if total == 0:
        return empty
    ok = qual == total
    nq = [b for b in breakdown if not b['qualified']]
    nq_names = ', '.join(b['name'] for b in nq[:3]) + (f" and {len(nq) - 3} more" if len(nq) > 3 else "")
    return {
        'total_spo': total, 'qualified_spo': qual, 'not_qualified_spo': total - qual,
        'qualified': ok, 'incentive': BONUS if ok else 0, 'max_incentive': BONUS,
        'spo_breakdown': breakdown, 'status': 'QUALIFIED' if ok else 'NOT QUALIFIED',
        'remark': (f"All {qual} of {total} BLISS SPOs achieved Net targets. ASM earns Rs. {BONUS:,.0f} UCC bonus."
                   if ok else f"{qual} of {total} BLISS SPOs hit Net targets. Need all SPOs >= 100%. Not qualified: {nq_names}."),
        'not_qualified_list': nq,
    }
