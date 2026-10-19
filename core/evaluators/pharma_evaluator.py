"""
Pharma Team Incentive Evaluator Module
Evaluates the qualifying criteria for Pharmaceutical MIO & PS (OMR).
Policy: Pharma Incentive Policy 2026-27 (July 2026 – June 2027)
Criteria: Regular Incentive (Monthly) on Net Value
Slabs:
- 85-99%: Rate per unit sold (E_QTY)
- 100-109%: Rate per unit sold (E_QTY)
- 110 & Above%: Rate per unit sold (E_QTY)
"""
import pandas as pd


# MIO & PS (OMR) Rates Matrix
PHARMA_MIO_RATES = {
    'depoqueen': {'85-99': 4, '100-109': 7, '110_above': 10},
    'ecp': {'85-99': 1.0, '100-109': 1.5, '110_above': 2.0},
    'grekie': {'85-99': 6, '100-109': 8, '110_above': 10},
    'femijict': {'85-99': 2, '100-109': 4, '110_above': 5},
    'novodol': {'85-99': 2, '100-109': 3, '110_above': 5},
    'vical_plus': {'85-99': 20, '100-109': 30, '110_above': 35},
    'vitaferol': {'85-99': 13, '100-109': 17, '110_above': 20},
    'enofer': {'85-99': 40, '100-109': 80, '110_above': 95},
    'enoject': {'85-99': 75, '100-109': 150, '110_above': 170},
    'envit_inj': {'85-99': 0, '100-109': 0, '110_above': 0},
    'sarset_tab': {'85-99': 15, '100-109': 25, '110_above': 30},
    'sarset_inj': {'85-99': 25, '100-109': 35, '110_above': 40},
    'unimmap': {'85-99': 20, '100-109': 25, '110_above': 30},
}

# Area Sales Manager (ASM) Rates Matrix
PHARMA_ASM_RATES = {
    'depoqueen': {'85-99': 2, '100-109': 4, '110_above': 6},
    'ecp': {'85-99': 0.5, '100-109': 1.0, '110_above': 1.5},
    'grekie': {'85-99': 2, '100-109': 4, '110_above': 6},
    'femijict': {'85-99': 1, '100-109': 2, '110_above': 3},
    'novodol': {'85-99': 1, '100-109': 2, '110_above': 3},
    'vical_plus': {'85-99': 7, '100-109': 12, '110_above': 25},
    'vitaferol': {'85-99': 7, '100-109': 12, '110_above': 25},
    'enofer': {'85-99': 15, '100-109': 25, '110_above': 34},
    'enoject': {'85-99': 30, '100-109': 65, '110_above': 90},
    'envit_inj': {'85-99': 0, '100-109': 0, '110_above': 0},
    'sarset_tab': {'85-99': 10, '100-109': 15, '110_above': 25},
    'sarset_inj': {'85-99': 10, '100-109': 15, '110_above': 25},
    'unimmap': {'85-99': 10, '100-109': 15, '110_above': 25},
}

PHARMA_PRODUCTS_CONFIG = [
    {
        'id': 1,
        'key': 'depoqueen',
        'name': 'DEPOQUEEN',
        'full_name': 'DEPO QUEEN INJECTION',
        'tgt_match': ['DEPO QUEEN INJECTION'],
        'sales_match': ['DEPO QUEEN INJECTION'],
        'sales_prd_grp': ['DEPO INJ'],
        'rates': PHARMA_MIO_RATES['depoqueen'],
        'mio_rates': PHARMA_MIO_RATES['depoqueen'],
        'asm_rates': PHARMA_ASM_RATES['depoqueen'],
        'has_rates': True,
    },
    {
        'id': 2,
        'key': 'ecp',
        'name': 'ECP',
        'full_name': 'ECP PILLS',
        'tgt_match': ['ECP PILLS'],
        'sales_match': ['ECP PILLS', 'EMERGENCY PILLS (EP)'],
        'sales_prd_grp': ['ECP/EP'],
        'rates': PHARMA_MIO_RATES['ecp'],
        'mio_rates': PHARMA_MIO_RATES['ecp'],
        'asm_rates': PHARMA_ASM_RATES['ecp'],
        'has_rates': True,
    },
    {
        'id': 3,
        'key': 'grekie',
        'name': 'GREKIE',
        'full_name': 'GREKIE TAB 200mcg',
        'tgt_match': ['GREKIE TAB 200mcg'],
        'sales_match': ['GREKIE TAB 200mcg', 'MISOPROSTOL'],
        'sales_prd_grp': ['MISOTAL/GREKIE'],
        'rates': PHARMA_MIO_RATES['grekie'],
        'mio_rates': PHARMA_MIO_RATES['grekie'],
        'asm_rates': PHARMA_ASM_RATES['grekie'],
        'has_rates': True,
    },
    {
        'id': 4,
        'key': 'femijict',
        'name': 'FEMIJECT',
        'full_name': 'FEMIJECT INJECTION',
        'tgt_match': ['FEMIJECT INJECTION'],
        'sales_match': ['FEMIJECT INJECTION'],
        'sales_prd_grp': ['FEMIJ./NORESEL INJ'],
        'rates': PHARMA_MIO_RATES['femijict'],
        'mio_rates': PHARMA_MIO_RATES['femijict'],
        'asm_rates': PHARMA_ASM_RATES['femijict'],
        'has_rates': True,
    },
    {
        'id': 5,
        'key': 'novodol',
        'name': 'NOVODOL',
        'full_name': 'NOVADOL 3 PACK',
        'tgt_match': ['NOVADOL 3 PACK'],
        'sales_match': ['NOVADOL 3 PACK'],
        'sales_prd_grp': ['NOVADOL'],
        'rates': PHARMA_MIO_RATES['novodol'],
        'mio_rates': PHARMA_MIO_RATES['novodol'],
        'asm_rates': PHARMA_ASM_RATES['novodol'],
        'has_rates': True,
    },
    {
        'id': 6,
        'key': 'vical_plus',
        'name': 'VICAL+',
        'full_name': 'VICAL PLUS',
        'tgt_match': ['VICAL PLUS'],
        'sales_match': ['VICAL PLUS'],
        'sales_prd_grp': ['CALCIUM SUPP'],
        'rates': PHARMA_MIO_RATES['vical_plus'],
        'mio_rates': PHARMA_MIO_RATES['vical_plus'],
        'asm_rates': PHARMA_ASM_RATES['vical_plus'],
        'has_rates': True,
    },
    {
        'id': 7,
        'key': 'vitaferol',
        'name': 'VITAFEROL',
        'full_name': 'VITAFEROL 1s',
        'tgt_match': ['VITAFEROL 1s'],
        'sales_match': ['VITAFEROL 1s', 'VITAFEROL 5s'],
        'sales_prd_grp': ['MULTIVITAMINS'],
        'rates': PHARMA_MIO_RATES['vitaferol'],
        'mio_rates': PHARMA_MIO_RATES['vitaferol'],
        'asm_rates': PHARMA_ASM_RATES['vitaferol'],
        'has_rates': True,
    },
    {
        'id': 8,
        'key': 'enofer',
        'name': 'ENOFER',
        'full_name': 'ENOFER 5ML',
        'tgt_match': ['ENOFER 5ML'],
        'sales_match': ['ENOFER 5ML'],
        'sales_prd_grp': ['IRON SUPP'],
        'rates': PHARMA_MIO_RATES['enofer'],
        'mio_rates': PHARMA_MIO_RATES['enofer'],
        'asm_rates': PHARMA_ASM_RATES['enofer'],
        'has_rates': True,
    },
    {
        'id': 9,
        'key': 'enoject',
        'name': 'ENOJECT',
        'full_name': 'ENOJECT INJECTION',
        'tgt_match': ['ENOJECT INJECTION'],
        'sales_match': ['ENOJECT INJECTION'],
        'sales_prd_grp': ['IRON SUPP'],
        'rates': PHARMA_MIO_RATES['enoject'],
        'mio_rates': PHARMA_MIO_RATES['enoject'],
        'asm_rates': PHARMA_ASM_RATES['enoject'],
        'has_rates': True,
    },
    {
        'id': 10,
        'key': 'envit_inj',
        'name': 'ENVIT INJ',
        'full_name': 'ENVIT INJ',
        'tgt_match': ['ENVIT INJ'],
        'sales_match': ['ENVIT INJ'],
        'sales_prd_grp': ['MULTIVITAMINS'],
        'rates': PHARMA_MIO_RATES['envit_inj'],
        'mio_rates': PHARMA_MIO_RATES['envit_inj'],
        'asm_rates': PHARMA_ASM_RATES['envit_inj'],
        'has_rates': False,
    },
    {
        'id': 11,
        'key': 'sarset_tab',
        'name': 'SARSET Tab',
        'full_name': 'SARSET TABLET 8MG',
        'tgt_match': ['SARSET TABLET 8MG'],
        'sales_match': ['SARSET TABLET 8MG'],
        'sales_prd_grp': ['OBSTETRIC'],
        'rates': PHARMA_MIO_RATES['sarset_tab'],
        'mio_rates': PHARMA_MIO_RATES['sarset_tab'],
        'asm_rates': PHARMA_ASM_RATES['sarset_tab'],
        'has_rates': True,
    },
    {
        'id': 12,
        'key': 'sarset_inj',
        'name': 'SARSET INJ',
        'full_name': 'SARSET INJECTION 1S',
        'tgt_match': ['SARSET INJECTION 1S'],
        'sales_match': ['SARSET INJECTION 1S'],
        'sales_prd_grp': ['OBSTETRIC'],
        'rates': PHARMA_MIO_RATES['sarset_inj'],
        'mio_rates': PHARMA_MIO_RATES['sarset_inj'],
        'asm_rates': PHARMA_ASM_RATES['sarset_inj'],
        'has_rates': True,
    },
    {
        'id': 13,
        'key': 'unimmap',
        'name': 'UNIMMAP',
        'full_name': 'UNIMMAP',
        'tgt_match': ['UNIMMAP'],
        'sales_match': ['UNIMMAP'],
        'sales_prd_grp': ['MULTIVITAMINS'],
        'rates': PHARMA_MIO_RATES['unimmap'],
        'mio_rates': PHARMA_MIO_RATES['unimmap'],
        'asm_rates': PHARMA_ASM_RATES['unimmap'],
        'has_rates': True,
    },
]


def evaluate_pharma_incentives(
    employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col,
    pos_code=None, territory=None, is_asm=False, designation="MIO"
):
    """
    Evaluates monthly incentives for Pharma Field Force (MIO, PS, and ASM).
    Computes achievement per product against target, determines slab,
    and applies per-unit rate to actual E_QTY using the designation's rates matrix.
    """
    # 1. Filter target records for this employee
    t_sub = pd.DataFrame()
    if target_df is not None and not target_df.empty:
        tgt_pos_col = None
        for c in target_df.columns:
            if 'position code' in str(c).lower():
                tgt_pos_col = c
                break

        if pos_code and tgt_pos_col and tgt_pos_col in target_df.columns:
            t_sub = target_df[target_df[tgt_pos_col].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()]
        elif employee and 'F.F Name' in target_df.columns:
            t_sub = target_df[target_df['F.F Name'].astype(str).str.strip().str.lower() == str(employee).strip().lower()]
            if t_sub.empty and tgt_pos_col and tgt_pos_col in target_df.columns:
                t_sub = target_df[target_df[tgt_pos_col].astype(str).str.strip().str.upper() == str(employee).strip().upper()]

    # 2. Filter sales records for this employee and reporting month
    s_sub = pd.DataFrame()
    if sales_df is not None and not sales_df.empty:
        s_filter = pd.Series(True, index=sales_df.index)
        if 'REPORTING_MONTH' in sales_df.columns:
            s_filter = s_filter & (sales_df['REPORTING_MONTH'].astype(str).str.strip() == str(month).strip())

        if pos_code and 'POSITION_CODE' in sales_df.columns:
            emp_s = sales_df[s_filter & (sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper())]
        elif employee and 'NAME' in sales_df.columns:
            emp_s = sales_df[s_filter & (sales_df['NAME'].astype(str).str.strip().str.lower() == str(employee).strip().lower())]
            if emp_s.empty and 'POSITION_CODE' in sales_df.columns:
                emp_s = sales_df[s_filter & (sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == str(employee).strip().upper())]
        else:
            emp_s = pd.DataFrame()

        s_sub = emp_s

    is_pharma_asm = bool(is_asm or ('ASM' in str(designation).upper()) or ('-ASM-' in str(pos_code).upper()))
    role_title = "Area Sales Manager (ASM)" if is_pharma_asm else "OMR (MIO & PS)"
    designation_name = "ASM" if is_pharma_asm else "MIO"

    # 3. First pass: aggregate all product targets and actuals for bottom-line calculation
    raw_products = []
    total_act_units = 0.0
    total_tgt_units = 0.0
    total_act_val = 0.0
    total_tgt_val = 0.0

    for cfg in PHARMA_PRODUCTS_CONFIG:
        rates = cfg['asm_rates'] if is_pharma_asm else cfg['mio_rates']

        # Match target
        p_tgt = pd.DataFrame()
        if not t_sub.empty and target_master_col and target_master_col in t_sub.columns:
            p_tgt = t_sub[t_sub[target_master_col].astype(str).str.strip().str.upper().isin([x.upper() for x in cfg['tgt_match']])]

        tgt_units = float(p_tgt[t_unit_col].sum()) if (t_unit_col and not p_tgt.empty and t_unit_col in p_tgt.columns) else 0.0
        tgt_val = float(p_tgt[t_net_col].sum()) if (t_net_col and not p_tgt.empty and t_net_col in p_tgt.columns) else 0.0

        # Match sales
        p_sales = pd.DataFrame()
        if not s_sub.empty:
            if 'GROUP_ON' in s_sub.columns:
                p_sales = s_sub[s_sub['GROUP_ON'].astype(str).str.strip().str.upper().isin([x.upper() for x in cfg['sales_match']])]
            if p_sales.empty and 'PRD_GRP' in s_sub.columns and cfg.get('sales_prd_grp'):
                p_sales = s_sub[s_sub['PRD_GRP'].astype(str).str.strip().str.upper().isin([x.upper() for x in cfg['sales_prd_grp']])]

        act_units = float(p_sales['E_QTY'].sum()) if (not p_sales.empty and 'E_QTY' in p_sales.columns) else 0.0
        act_val = float(p_sales['NET_WO_REG_DISC_VALUE'].sum()) if (not p_sales.empty and 'NET_WO_REG_DISC_VALUE' in p_sales.columns) else 0.0

        total_act_units += act_units
        total_tgt_units += tgt_units
        total_act_val += act_val
        total_tgt_val += tgt_val

        raw_products.append({
            'cfg': cfg,
            'rates': rates,
            'tgt_units': tgt_units,
            'act_units': act_units,
            'tgt_val': tgt_val,
            'act_val': act_val,
        })

    # Overall Bottom-Line Net Sales Value Achievement (must be >= 85% to unlock any incentives)
    overall_ach = (total_act_val / total_tgt_val * 100.0) if total_tgt_val > 0 else 0.0
    overall_unit_ach = (total_act_units / total_tgt_units * 100.0) if total_tgt_units > 0 else 0.0
    bottom_line_qualified = bool(overall_ach >= 85.0)
    units_qualified = bool(overall_unit_ach >= 85.0)
    shortfall_bottom_line = max(0.0, total_tgt_val * 0.85 - total_act_val)

    # 4. Evaluate each product with dual qualification criteria & bottom-line gate
    products = []
    total_incentive = 0.0
    qualified_count = 0

    for item in raw_products:
        cfg = item['cfg']
        rates = item['rates']
        tgt_units = item['tgt_units']
        act_units = item['act_units']
        tgt_val = item['tgt_val']
        act_val = item['act_val']

        unit_ach = (act_units / tgt_units * 100.0) if tgt_units > 0 else 0.0
        val_ach = (act_val / tgt_val * 100.0) if tgt_val > 0 else 0.0
        ach_pct = val_ach

        val_meets = bool(val_ach >= 85.0)
        unit_meets = bool(unit_ach >= 85.0)
        product_meets_criteria = bool(val_meets and unit_meets and cfg['has_rates'])

        # Determine Slab & Rate based on Net Sales Value achievement % (when criteria met)
        if not cfg['has_rates']:
            slab = "Exempt"
            slab_tier = "Exempt"
            rate = 0
            qual = False
            earned_inc = 0.0
            need_text = "Exempt from incentive policy"
            applicable_slab = "Exempt / No Incentive"
            formula_text = "Exempt from incentive policy"
        else:
            # Determine slab from val_ach
            if val_ach >= 110.0:
                slab = "110% & Above"
                slab_tier = "110%+"
                rate = rates['110_above']
            elif val_ach >= 100.0:
                slab = "100-109%"
                slab_tier = "100%"
                rate = rates['100-109']
            elif val_ach >= 85.0:
                slab = "85-99%"
                slab_tier = "85%"
                rate = rates['85-99']
            else:
                slab = "Below 85%"
                slab_tier = "<85%"
                rate = 0

            applicable_slab = f"{slab} (Rs. {rate:g}/unit)" if rate > 0 else "Below 85% (No Incentive)"

            if not bottom_line_qualified:
                # Bottom-Line gate failed!
                qual = False
                earned_inc = 0.0
                if product_meets_criteria:
                    need_text = f"Product met criteria ({val_ach:.1f}% Value & {unit_ach:.1f}% Units), but locked: Bottom-Line Net Value ({overall_ach:.1f}%) is below 85% threshold (Need Rs. {shortfall_bottom_line:,.0f} overall)"
                    formula_text = f"Locked by Bottom-Line ({overall_ach:.1f}% < 85%)"
                else:
                    if not val_meets and not unit_meets:
                        need_text = f"Value ({val_ach:.1f}%) & Units ({unit_ach:.1f}%) below 85% & Bottom-Line below 85% ({overall_ach:.1f}%)"
                    elif not val_meets:
                        need_text = f"Value shortfall ({val_ach:.1f}% < 85%) & Bottom-Line below 85% ({overall_ach:.1f}%)"
                    else:
                        need_text = f"Units shortfall ({unit_ach:.1f}% < 85%) & Bottom-Line below 85% ({overall_ach:.1f}%)"
                    formula_text = f"Below 85% threshold & Bottom-Line not met"
            else:
                # Bottom-Line passed!
                if product_meets_criteria:
                    qual = True
                    earned_inc = round(rate * act_units, 2)
                    if val_ach >= 110.0:
                        need_text = f"Top slab achieved! (Earned Rs. {rate:g}/unit on {act_units:,.0f} units)"
                        formula_text = f"Rs. {rate:g} × {act_units:,.0f} units = Rs. {rate * act_units:,.0f}"
                    elif val_ach >= 100.0:
                        s_val_110 = max(0.0, tgt_val * 1.10 - act_val)
                        need_text = f"Qualified (100–109%). Need Rs. {s_val_110:,.0f} for 110%+ slab (Rs. {rates['110_above']:g}/unit)"
                        formula_text = f"Rs. {rate:g} × {act_units:,.0f} units = Rs. {rate * act_units:,.0f}"
                    else:
                        s_val_100 = max(0.0, tgt_val * 1.00 - act_val)
                        need_text = f"Qualified (85–99%). Need Rs. {s_val_100:,.0f} for 100% slab (Rs. {rates['100-109']:g}/unit)"
                        formula_text = f"Rs. {rate:g} × {act_units:,.0f} units = Rs. {rate * act_units:,.0f}"
                else:
                    # Product did not meet both 85% criteria
                    qual = False
                    earned_inc = 0.0
                    rate = 0
                    applicable_slab = "Below 85% (No Incentive)"
                    if not val_meets and not unit_meets:
                        s_val = max(0.0, tgt_val * 0.85 - act_val)
                        s_units = max(0.0, tgt_units * 0.85 - act_units)
                        need_text = f"Not qualified: Need Rs. {s_val:,.0f} Net Value ({val_ach:.1f}%) & {s_units:,.0f} units ({unit_ach:.1f}%) to qualify"
                        formula_text = f"Both Value ({val_ach:.1f}%) and Units ({unit_ach:.1f}%) below 85%"
                    elif not val_meets:
                        s_val = max(0.0, tgt_val * 0.85 - act_val)
                        need_text = f"Not qualified: Units met ({unit_ach:.1f}%), but Value shortfall of Rs. {s_val:,.0f} (achieved {val_ach:.1f}% < 85%)"
                        formula_text = f"Net Value ({val_ach:.1f}%) below 85% threshold"
                    else:
                        s_units = max(0.0, tgt_units * 0.85 - act_units)
                        need_text = f"Not qualified: Value met ({val_ach:.1f}%), but Units shortfall of {s_units:,.0f} units (achieved {unit_ach:.1f}% < 85%)"
                        formula_text = f"Units ({unit_ach:.1f}%) below 85% threshold"

        if qual and earned_inc > 0:
            qualified_count += 1

        total_incentive += earned_inc
        progress_pct = min(max(val_ach, 0.0), 100.0)

        products.append({
            'id': cfg['id'],
            'key': cfg['key'],
            'name': cfg['name'],
            'full_name': cfg['full_name'],
            'tgt_units': tgt_units,
            'act_units': act_units,
            'unit_achievement': unit_ach,
            'tgt_val': tgt_val,
            'act_val': act_val,
            'val_achievement': val_ach,
            'achievement': ach_pct,
            'progress_pct': progress_pct,
            'rate': rate,
            'slab': slab,
            'slab_tier': slab_tier,
            'applicable_slab': applicable_slab,
            'earned_incentive': earned_inc,
            'qualified': qual,
            'product_meets_criteria': product_meets_criteria,
            'val_meets': val_meets,
            'unit_meets': unit_meets,
            'has_rates': cfg['has_rates'],
            'rates_table': rates,
            'need_text': need_text,
            'formula_text': formula_text,
        })

    if not bottom_line_qualified:
        remark = f"Overall Bottom-Line Net Value achievement is {overall_ach:.1f}% (Below 85% minimum threshold). Need Rs. {shortfall_bottom_line:,.0f} to unlock incentives."
    elif total_incentive > 0:
        remark = f"Earned Rs. {total_incentive:,.0f} across {qualified_count} qualifying products (Bottom-Line Net Value: {overall_ach:.1f}%)."
    else:
        remark = f"Bottom-Line Net Value met ({overall_ach:.1f}%), but no products met both the 85% Net Value and 85% Units criteria."

    return {
        'products': products,
        'total_incentive': total_incentive,
        'qualified_count': qualified_count,
        'total_products': len(products),
        'rate_bearing_products': sum(1 for p in products if p['has_rates']),
        'total_act_units': total_act_units,
        'total_tgt_units': total_tgt_units,
        'total_act_val': total_act_val,
        'total_tgt_val': total_tgt_val,
        'overall_achievement': overall_ach,
        'overall_unit_achievement': overall_unit_ach,
        'bottom_line_qualified': bottom_line_qualified,
        'units_qualified': units_qualified,
        'bottom_line_threshold': 85.0,
        'bottom_line_shortfall': shortfall_bottom_line,
        'status': 'QUALIFIED' if total_incentive > 0 else 'NOT QUALIFIED',
        'active_qualified': total_incentive > 0,
        'is_asm': is_pharma_asm,
        'role_title': role_title,
        'designation': designation_name,
        'remark': remark
    }
