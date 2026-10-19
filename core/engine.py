"""
Master Calculation Engine
Coordinates dataset resolution, role dispatching, evaluators, and secondary bonus schemes.
"""
import pandas as pd
from core.db_loader import (
    load_staff_df,
    load_datasets,
    get_val_logic_mapping,
    get_target_columns,
)
from core.employee_service import (
    get_initials,
    format_display_month,
    resolve_employee_selection,
    get_employee_info,
    determine_employee_category,
    aggregate_asm_datasets,
    aggregate_rsm_datasets,
    build_dynamic_header,
    get_dynamic_header_details,
)
from core.evaluators import (
    evaluate_do_incentives,
    evaluate_touch_incentives,
    evaluate_overlapping_incentives,
    evaluate_bliss_incentives,
    evaluate_rsm_incentives,
    evaluate_pharma_incentives,
    evaluate_pharma_rsm_incentives,
)
from core.bonuses import (
    calculate_ucc_incentive,
    calculate_bliss_asm_ucc_bonus,
    calculate_privilege_club_incentive,
    calculate_asm_privilege_club,
    calculate_rsm_privilege_club,
)


def calculate_all_incentives(employee, month, target_df, sales_df, target_master_col, staff_df=None, pos_code=None, territory=None):
    """
    Calculates incentives for DO Team SPOs/ASMs, TOUCH Team SPOs/ASMs, Overlapping SPOs/ASMs, and GSM RSMs.
    Returns a unified dictionary with all scorecard components.
    """
    if staff_df is None:
        staff_df = load_staff_df()

    t_net_col, t_unit_col, t_tp_col = get_target_columns(month, target_df)

    # 1. Resolve employee details and designation FIRST
    employee_details = get_employee_info(employee, target_df, sales_df, staff_df=staff_df, pos_code=pos_code, territory=territory)
    designation = employee_details[0] if employee_details else "SPO"
    if employee_details:
        for itm in employee_details:
            if str(itm).strip().upper() in ("ASM", "RSM", "MIO", "PS", "OMR", "SPO"):
                designation = str(itm).strip().upper()
                break
    is_asm = (str(designation).strip().upper() == "ASM") or ('-ASM-' in str(pos_code or '').upper())
    is_rsm = (str(designation).strip().upper() == "RSM") or ('-RSM-' in str(pos_code or '').upper())
    if is_asm:
        designation = "ASM"
    elif is_rsm:
        designation = "RSM"

    # Fallback to sales_df for designation if needed
    if not is_asm and not is_rsm:
        if sales_df is not None and not sales_df.empty:
            if pos_code and "POSITION_CODE" in sales_df.columns:
                s_match = sales_df[sales_df["POSITION_CODE"].astype(str).str.strip().str.upper() == str(pos_code).strip().upper()]
            else:
                s_match = sales_df[sales_df["NAME"].astype(str).str.strip().str.lower() == str(employee).strip().lower()]
            if not s_match.empty:
                s_desg = str(s_match.iloc[0].get("DESIGNATION") or "").strip().upper()
                if s_desg == "ASM":
                    is_asm = True
                    designation = "ASM"
                elif s_desg == "RSM":
                    is_rsm = True
                    designation = "RSM"

    resolved_pos = pos_code or ""
    if employee_details:
        for itm in employee_details:
            if ('-PHR-' in str(itm).upper()) or ('-FMCG' in str(itm).upper()) or ('-RSM-' in str(itm).upper()):
                resolved_pos = str(itm).strip()
                break
        if not resolved_pos and len(employee_details) > 7:
            resolved_pos = employee_details[7] or (pos_code or "")

    # Automatically determine the single active incentive category
    active_category = determine_employee_category(employee, target_df, sales_df, staff_df=staff_df, pos_code=pos_code, territory=territory)
    is_pharma_rsm = bool(is_rsm and (active_category == 'pharma' or '-PHR-' in str(resolved_pos or pos_code).upper()))
    if is_pharma_rsm:
        active_category = 'pharma'

    # For ASM, aggregate targets and sales from reporting SPOs, team region, and ASM direct sales
    if is_asm:
        eval_target_df, eval_sales_df = aggregate_asm_datasets(
            employee, resolved_pos or pos_code, month, target_df, sales_df, staff_df, territory=territory
        )
    elif is_rsm:
        eval_target_df, eval_sales_df = target_df, sales_df
    else:
        eval_target_df, eval_sales_df = target_df, sales_df

    pharma_rsm_result = None

    if active_category == 'pharma':
        do_result = {'criteria': [], 'criteria_dict': {}, 'breakdown': [], 'payout_remarks': [], 'qualification_requirements': [], 'total_incentive': 0, 'qualified_count': 0}
        do_total_incentive = 0
        do_qualified_count = 0
        touch_result = {'touch_criteria': [], 'touch_criteria_dict': {}, 'touch_breakdown': [], 'touch_payout_remarks': [], 'touch_qualification_requirements': [], 'touch_total_incentive': 0, 'touch_qualified_count': 0}
        touch_total_incentive = 0
        touch_qualified_count = 0
        overlapping_result = {'overlapping_criteria': [], 'overlapping_criteria_dict': {}, 'overlapping_breakdown': [], 'overlapping_payout_remarks': [], 'overlapping_qualification_requirements': [], 'overlapping_total_incentive': 0, 'overlapping_qualified_count': 0}
        overlapping_total_incentive = 0
        overlapping_qualified_count = 0
        bliss_result = {'bliss_criteria': [], 'bliss_criteria_dict': {}, 'bliss_breakdown': [], 'bliss_payout_remarks': [], 'bliss_qualification_requirements': [], 'bliss_total_incentive': 0, 'bliss_qualified_count': 0}
        bliss_total_incentive = 0
        bliss_qualified_count = 0

        if is_pharma_rsm:
            pharma_rsm_result = evaluate_pharma_rsm_incentives(
                employee=employee,
                month=month,
                target_df=target_df,
                sales_df=sales_df,
                target_master_col=target_master_col,
                staff_df=staff_df,
                pos_code=resolved_pos or pos_code,
                territory=territory
            )
            pharma_result = None
        else:
            pharma_result = evaluate_pharma_incentives(
                employee, month, eval_target_df, eval_sales_df, target_master_col, t_net_col, t_unit_col,
                pos_code=resolved_pos or pos_code, territory=territory, is_asm=is_asm, designation=designation
            )
    else:
        # Team Incentive Evaluations (DO, TOUCH, OVERLAPPING, BLISS)
        do_result = evaluate_do_incentives(
            employee, month, eval_target_df, eval_sales_df, target_master_col, t_net_col, t_unit_col, pos_code=pos_code, territory=territory, is_asm=is_asm
        )
        do_total_incentive = do_result['total_incentive']
        do_qualified_count = do_result['qualified_count']

        touch_result = evaluate_touch_incentives(
            employee, month, eval_target_df, eval_sales_df, target_master_col, t_net_col, pos_code=pos_code, territory=territory, is_asm=is_asm
        )
        touch_total_incentive = touch_result['touch_total_incentive']
        touch_qualified_count = touch_result['touch_qualified_count']

        overlapping_result = evaluate_overlapping_incentives(
            employee, month, eval_target_df, eval_sales_df, target_master_col, t_net_col, t_unit_col, t_tp_col, pos_code=pos_code, territory=territory, is_asm=is_asm
        )
        overlapping_total_incentive = overlapping_result['overlapping_total_incentive']
        overlapping_qualified_count = overlapping_result['overlapping_qualified_count']

        is_overlap_asm = is_asm and (active_category == 'overlapping')
        bliss_result = evaluate_bliss_incentives(
            employee, month, eval_target_df, eval_sales_df, target_master_col, t_net_col, pos_code=pos_code, territory=territory, is_asm=is_asm, is_overlap=is_overlap_asm
        )
        bliss_total_incentive = bliss_result['bliss_total_incentive']
        bliss_qualified_count = bliss_result['bliss_qualified_count']
        pharma_result = None

    # Default ASM privilege values
    asm_privilege_result = {'total_spo': 0, 'qualified_spo': 0, 'not_qualified_spo': 0, 'asm_qualified': False, 'incentive': 0, 'max_incentive': 60000, 'spo_target': 1000000.0, 'spo_breakdown': [], 'status': 'NOT QUALIFIED', 'remark': '', 'not_qualified_list': []}
    asm_privilege_inc = 0

    # Default RSM privilege values
    rsm_privilege_result = {'total_asm': 0, 'qualified_asm': 0, 'not_qualified_asm': 0, 'rsm_qualified': False, 'incentive': 0, 'max_incentive': 100000, 'asm_breakdown': [], 'status': 'NOT QUALIFIED', 'remark': '', 'not_qualified_list': []}
    rsm_privilege_inc = 0

    # Default BLISS ASM UCC bonus values
    bliss_asm_ucc_result = None
    bliss_asm_ucc_inc = 0

    if is_asm:
        # Dedicated Area Sales Manager (ASM) incentive evaluation
        if active_category == 'pharma':
            active_team_name = "PHARMACEUTICAL ASMs"
            active_team_title = "Pharma Incentive Policy (Area Sales Manager)"
            active_incentive = pharma_result['total_incentive']
            active_qualified = pharma_result['active_qualified']
            if not pharma_result.get('bottom_line_qualified', True):
                active_tier = f"Bottom-Line ({pharma_result['overall_achievement']:.1f}% < 85%) Not Qualified"
            else:
                active_tier = f"Pharma ASM ({pharma_result['qualified_count']}/{pharma_result['rate_bearing_products']}) Qualified" if active_qualified else "Not Qualified"
            active_qualified_count = pharma_result['qualified_count']
            active_total_rules = pharma_result['rate_bearing_products']
            ucc_result = None
            ucc_inc = 0
            privilege_club_result = None
            privilege_inc = 0
            asm_privilege_result = None
            asm_privilege_inc = 0
            bliss_asm_ucc_result = None
            bliss_asm_ucc_inc = 0
            final_payout = pharma_result['total_incentive']
            touch_final_payout = final_payout
            overlapping_final_payout = final_payout
            bliss_final_payout = final_payout
            grand_total_incentive = final_payout
            is_qualified = active_qualified
            val_logic_map = get_val_logic_mapping()
            emp_type = val_logic_map.get(str(resolved_pos).strip().upper()) or designation or "ASM"
        else:
            if active_category == 'do':
                active_team_name = "DO Team ASMs"
                active_team_title = "Incentive criteria for DO Team ASMs:"
                active_incentive = do_total_incentive
                active_qualified = do_total_incentive > 0
                active_tier = f"DO ASM ({do_qualified_count}/4) Qualified" if active_qualified else "Not Qualified"
                active_qualified_count = do_qualified_count
                active_total_rules = 4
            elif active_category == 'touch':
                active_team_name = "TOUCH Team ASMs"
                active_team_title = "Incentive criteria for TOUCH team ASMs:"
                active_incentive = touch_total_incentive
                active_qualified = touch_total_incentive > 0
                active_tier = f"TOUCH ASM ({touch_qualified_count}/4) Qualified" if active_qualified else "Not Qualified"
                active_qualified_count = touch_qualified_count
                active_total_rules = 4
            elif active_category == 'bliss':
                active_team_name = "BLISS Team ASMs"
                active_team_title = "Incentive criteria for BLISS Team ASMs:"
                active_incentive = bliss_total_incentive
                active_qualified = bliss_total_incentive > 0
                active_tier = f"BLISS ASM ({bliss_qualified_count}/1) Qualified" if active_qualified else "Not Qualified"
                active_qualified_count = bliss_qualified_count
                active_total_rules = 1
            else:  # overlapping
                active_team_name = "Overlapping ASMs"
                active_team_title = "Incentive criteria for Overlapping ASMs:"
                active_incentive = overlapping_total_incentive
                active_qualified = overlapping_total_incentive > 0
                active_tier = f"Overlapping ASM ({overlapping_qualified_count}/7) Qualified" if active_qualified else "Not Qualified"
                active_qualified_count = overlapping_qualified_count
                active_total_rules = 7

            ucc_result = None
            ucc_inc = 0
            privilege_club_result = None
            privilege_inc = 0

            # ASM Privilege Club: all-or-nothing based on ALL SPOs individually qualifying
            asm_privilege_result = calculate_asm_privilege_club(
                asm_employee=employee,
                month=month,
                sales_df=sales_df,
                staff_df=staff_df,
                asm_pos_code=resolved_pos or pos_code
            )
            asm_privilege_inc = asm_privilege_result['incentive']

            # BLISS dedicated-ASM UCC bonus: Rs. 10,000 additive if ALL BLISS SPOs
            # under this ASM achieve their individual Net targets.
            bliss_asm_ucc_result = None
            bliss_asm_ucc_inc = 0
            if active_category == 'bliss':
                bliss_asm_ucc_result = calculate_bliss_asm_ucc_bonus(
                    asm_employee=employee,
                    month=month,
                    sales_df=sales_df,
                    staff_df=staff_df,
                    target_df=target_df,
                    target_master_col=target_master_col,
                    t_net_col=t_net_col,
                    asm_pos_code=resolved_pos or pos_code
                )
                bliss_asm_ucc_inc = bliss_asm_ucc_result['incentive']

            final_payout = active_incentive + asm_privilege_inc + bliss_asm_ucc_inc
            touch_final_payout = active_incentive + asm_privilege_inc + bliss_asm_ucc_inc
            overlapping_final_payout = active_incentive + asm_privilege_inc + bliss_asm_ucc_inc
            bliss_final_payout = active_incentive + asm_privilege_inc + bliss_asm_ucc_inc
            grand_total_incentive = active_incentive + asm_privilege_inc + bliss_asm_ucc_inc
            is_qualified = active_qualified

            val_logic_map = get_val_logic_mapping()
            emp_type = val_logic_map.get(str(resolved_pos).strip().upper())
            if not emp_type:
                nature = employee_details[2] if len(employee_details) > 2 else ""
                emp_type = nature or "ASM"
    elif is_rsm:
        if is_pharma_rsm:
            # Dedicated Pharma Regional Sales Manager (RSM) incentive evaluation
            active_category = 'pharma'
            active_team_name = "PHARMACEUTICAL RSMs"
            active_team_title = "Pharma Incentive Policy (Regional Sales Manager)"
            active_incentive = pharma_rsm_result['total_incentive']
            active_qualified = pharma_rsm_result['active_qualified']
            active_tier = f"Pharma RSM ({pharma_rsm_result['qualified_staff_count']}/{pharma_rsm_result['total_staff_count']} Staff) Qualified" if active_qualified else "Not Qualified"
            active_qualified_count = pharma_rsm_result['qualified_staff_count']
            active_total_rules = pharma_rsm_result['total_staff_count']

            ucc_result = None
            ucc_inc = 0
            privilege_club_result = None
            privilege_inc = 0
            asm_privilege_result = None
            asm_privilege_inc = 0
            rsm_privilege_result = None
            rsm_privilege_inc = 0

            final_payout = active_incentive
            touch_final_payout = final_payout
            overlapping_final_payout = final_payout
            bliss_final_payout = final_payout
            grand_total_incentive = final_payout
            is_qualified = active_qualified

            val_logic_map = get_val_logic_mapping()
            emp_type = val_logic_map.get(str(resolved_pos).strip().upper()) or designation or "RSM"
        else:
            # Dedicated Regional Sales Manager (RSM) incentive evaluation (FMCG)
            street_tgt, street_sal, reg_tgt, reg_sal = aggregate_rsm_datasets(
                employee, resolved_pos or pos_code, month, target_df, sales_df, staff_df, territory=territory
            )
            val_col = 'NET_WO_REG_DISC_VALUE' if 'NET_WO_REG_DISC_VALUE' in sales_df.columns else ('NET_SALE_VALUE' if 'NET_SALE_VALUE' in sales_df.columns else None)
            rsm_result = evaluate_rsm_incentives(
                employee, month, street_tgt, street_sal, reg_tgt, reg_sal, t_net_col, val_col=val_col or 'NET_WO_REG_DISC_VALUE'
            )
            rsm_privilege_result = calculate_rsm_privilege_club(
                rsm_employee=employee,
                month=month,
                sales_df=sales_df,
                staff_df=staff_df,
                target_df=target_df,
                rsm_pos_code=resolved_pos or pos_code,
                aggregate_asm_fn=aggregate_asm_datasets
            )
            active_category = 'rsm'
            active_team_name = "GSM RSMs"
            active_team_title = "Incentive Criteria for RSMs:"
            active_incentive = rsm_result['rsm_core_incentive']
            active_qualified = (rsm_result['rsm_core_incentive'] > 0)
            active_tier = f"GSM RSM ({rsm_result['rsm_qualified_count']}/7) Qualified" if active_qualified else "Not Qualified"
            active_qualified_count = rsm_result['rsm_qualified_count']
            active_total_rules = 7

            ucc_result = None
            ucc_inc = 0
            privilege_club_result = None
            privilege_inc = 0
            asm_privilege_result = None
            asm_privilege_inc = 0
            rsm_privilege_inc = rsm_privilege_result['incentive']

            final_payout = active_incentive + rsm_privilege_inc
            touch_final_payout = final_payout
            overlapping_final_payout = final_payout
            bliss_final_payout = final_payout
            grand_total_incentive = final_payout
            is_qualified = active_qualified or (rsm_privilege_inc > 0)

            val_logic_map = get_val_logic_mapping()
            emp_type = val_logic_map.get(str(resolved_pos).strip().upper())
            if not emp_type:
                nature = employee_details[2] if len(employee_details) > 2 else ""
                emp_type = nature or "RSM"
    else:
        if active_category == 'pharma':
            active_team_name = "PHARMACEUTICAL"
            active_team_title = "Pharma Incentive Policy (MIO & PS)"
            active_incentive = pharma_result['total_incentive']
            active_qualified = pharma_result['active_qualified']
            if not pharma_result.get('bottom_line_qualified', True):
                active_tier = f"Bottom-Line ({pharma_result['overall_achievement']:.1f}% < 85%) Not Qualified"
            else:
                active_tier = f"Pharma ({pharma_result['qualified_count']}/{pharma_result['rate_bearing_products']}) Qualified" if active_qualified else "Not Qualified"
            active_qualified_count = pharma_result['qualified_count']
            active_total_rules = pharma_result['rate_bearing_products']
            ucc_result = None
            privilege_club_result = None
            ucc_inc = 0
            privilege_inc = 0
            do_final_payout = 0
            touch_final_payout = 0
            overlapping_final_payout = 0
            bliss_final_payout = 0
            final_payout = pharma_result['total_incentive']
            grand_total_incentive = final_payout
            is_qualified = active_qualified
            val_logic_map = get_val_logic_mapping()
            emp_type = val_logic_map.get(str(resolved_pos).strip().upper()) or designation or "MIO"
        elif active_category == 'do':
            active_team_name = "DO Team"
            active_team_title = "DO Team SPOs Incentive Performance"
            active_incentive = do_total_incentive
            active_qualified = do_total_incentive > 0
            active_tier = f"DO ({do_qualified_count}/4) Qualified" if active_qualified else "Not Qualified"
            active_qualified_count = do_qualified_count
            active_total_rules = 4
        elif active_category == 'touch':
            active_team_name = "TOUCH Team"
            active_team_title = "TOUCH Team SPOs Incentive Performance"
            active_incentive = touch_total_incentive
            active_qualified = touch_total_incentive > 0
            active_tier = f"TOUCH ({touch_qualified_count}/4) Qualified" if active_qualified else "Not Qualified"
            active_qualified_count = touch_qualified_count
            active_total_rules = 4
        elif active_category == 'bliss':
            active_team_name = "BLISS Team"
            active_team_title = "Incentive criteria for BLISS Team:"
            active_incentive = bliss_total_incentive
            active_qualified = bliss_total_incentive > 0
            active_tier = f"BLISS ({bliss_qualified_count}/1) Qualified" if active_qualified else "Not Qualified"
            active_qualified_count = bliss_qualified_count
            active_total_rules = 1
        else:  # overlapping
            active_team_name = "Overlapping SPOs"
            active_team_title = "Overlapping SPOs Incentive Performance"
            active_incentive = overlapping_total_incentive
            active_qualified = overlapping_total_incentive > 0
            active_tier = f"Overlapping ({overlapping_qualified_count}/3) Qualified" if active_qualified else "Not Qualified"
            active_qualified_count = overlapping_qualified_count
            active_total_rules = 3

        if active_category != 'pharma':
            # UCC INCENTIVE EVALUATION (STREET, SD+STREET, SD-based SPOs)
            val_logic_map = get_val_logic_mapping()
            emp_type = val_logic_map.get(str(resolved_pos).strip().upper())
            if not emp_type:
                nature = employee_details[2] if len(employee_details) > 2 else ""
                emp_type = nature or "SD+STREET"

            if active_category == 'touch':
                bl_crit = touch_result.get('touch_criteria_dict', {}).get('touch_one_bottom_line', {})
            elif active_category == 'overlapping':
                bl_crit = overlapping_result.get('overlapping_criteria_dict', {}).get('overlapping_overall_bottom_line', {})
            elif active_category == 'bliss':
                bl_crit = bliss_result.get('bliss_criteria_dict', {}).get('bliss_bottom_line', {})
            else:
                bl_crit = do_result.get('criteria_dict', {}).get('do_sathi_bottom_line', {}) or do_result.get('do_criteria_dict', {}).get('do_sathi_bottom_line', {})

            bl_ach = bl_crit.get('achievement', 0.0)
            total_net_target = bl_crit.get('target', 0.0)

            ucc_result = calculate_ucc_incentive(
                employee=employee,
                month=month,
                pos_code=resolved_pos or pos_code,
                emp_type=emp_type,
                sales_df=sales_df,
                bottom_line_ach=bl_ach,
                total_net_target=total_net_target,
                territory=territory,
                active_category=active_category
            )

            # PRIVILEGE CLUB INCENTIVE EVALUATION (PKR 1 Million Net Sales)
            privilege_club_result = calculate_privilege_club_incentive(
                employee=employee,
                month=month,
                sales_df=sales_df,
                pos_code=resolved_pos or pos_code,
                territory=territory
            )

            ucc_inc = ucc_result['incentive'] if ucc_result else 0
            privilege_inc = privilege_club_result['incentive'] if privilege_club_result else 0
            do_final_payout = do_total_incentive + ucc_inc + privilege_inc
            touch_final_payout = touch_total_incentive + ucc_inc + privilege_inc
            overlapping_final_payout = overlapping_total_incentive + ucc_inc + privilege_inc
            bliss_final_payout = bliss_total_incentive + ucc_inc + privilege_inc
            grand_total_incentive = do_total_incentive + touch_total_incentive + overlapping_total_incentive + bliss_total_incentive + ucc_inc + privilege_inc

            if active_category == 'overlapping':
                final_payout = overlapping_final_payout
            elif active_category == 'touch':
                final_payout = touch_final_payout
            elif active_category == 'bliss':
                final_payout = bliss_final_payout
            else:
                final_payout = do_final_payout

            active_qualified = (final_payout > 0)
            if not active_qualified:
                active_tier = "Not Qualified"

            is_qualified = active_qualified

    # =============================================================
    # Assemble final result dict (merging DO, TOUCH, OVERLAPPING, BLISS results)
    # =============================================================
    header_main, header_sub, header_title = get_dynamic_header_details(
        employee=employee,
        month=month,
        staff_df=staff_df,
        sales_df=sales_df,
        pos_code=resolved_pos or pos_code,
        territory=territory,
        team_hint=active_team_name,
        active_category=active_category
    )

    result = {
        'employee': employee,
        'initials': get_initials(employee),
        'designation': designation,
        'month': month,
        'display_month': format_display_month(month),
        'header_title': header_title,
        'header_main': header_main,
        'header_sub': header_sub,
        'employee_details': employee_details,
        'pos_code': resolved_pos or pos_code,
        'emp_type': emp_type,
        'is_asm': is_asm,
        'is_rsm': is_rsm,

        # Automatically Selected Active Category
        'active_category': active_category,
        'active_team_name': active_team_name,
        'active_team_title': active_team_title,
        'active_incentive': active_incentive,
        'active_qualified': active_qualified,
        'active_tier': active_tier,
        'active_qualified_count': active_qualified_count,
        'active_total_rules': active_total_rules,

        # UCC Incentive Evaluation
        'ucc': ucc_result,
        'ucc_incentive': 0 if (is_asm or is_rsm) else (ucc_result['incentive'] if ucc_result else 0),

        # Privilege Club Evaluation
        'privilege_club': None if (is_asm or is_rsm) else privilege_club_result,
        'privilege_incentive': 0 if (is_asm or is_rsm) else privilege_inc,

        # ASM Privilege Club Evaluation (only applies to ASMs)
        'asm_privilege_club': asm_privilege_result if is_asm else None,
        'asm_privilege_incentive': asm_privilege_inc if is_asm else 0,

        # BLISS dedicated-ASM UCC bonus (only applies to BLISS ASMs)
        'bliss_asm_ucc': bliss_asm_ucc_result if (is_asm and active_category == 'bliss') else None,
        'bliss_asm_ucc_incentive': bliss_asm_ucc_inc if (is_asm and active_category == 'bliss') else 0,

        # RSM Privilege Club Evaluation (only applies to RSMs)
        'rsm_privilege_club': rsm_privilege_result if is_rsm else None,
        'rsm_privilege_incentive': rsm_privilege_inc if is_rsm else 0,

        'total_incentive_with_ucc': final_payout,
        'final_payout': final_payout,
        'touch_final_payout': touch_final_payout,
        'overlapping_final_payout': overlapping_final_payout,
        'bliss_final_payout': bliss_final_payout,

        # Combined Evaluation
        'grand_total_incentive': grand_total_incentive,
        'is_qualified': is_qualified,
        'overall_tier': active_tier,
        'overall_qualified_count': active_qualified_count,

        # Pharma Evaluation
        'pharma': pharma_result,
        'pharma_rsm': pharma_rsm_result,
        'is_pharma_rsm': is_pharma_rsm,
    }

    # Merge DO, TOUCH, OVERLAPPING, and BLISS result dicts
    result.update(do_result)
    result.update(touch_result)
    result.update(overlapping_result)
    result.update(bliss_result)

    if is_asm:
        result.update({
            'is_asm': True,
            'is_rsm': False,
            'ucc': None,
            'ucc_incentive': 0,
            'privilege_club': None,
            'privilege_incentive': 0,
            'asm_privilege_club': asm_privilege_result,
            'asm_privilege_incentive': asm_privilege_inc,
            'bliss_asm_ucc': bliss_asm_ucc_result,
            'bliss_asm_ucc_incentive': bliss_asm_ucc_inc,
            'rsm_privilege_club': None,
            'rsm_privilege_incentive': 0,
        })
        if active_category == 'pharma':
            result.update({
                'criteria': [],
                'criteria_dict': {},
                'breakdown': [],
                'payout_remarks': [
                    {
                        'name': p['name'],
                        'remark': p['need_text'],
                        'slab': p['applicable_slab'],
                        'qualified': p['qualified'],
                        'incentive': p['earned_incentive'],
                    }
                    for p in pharma_result['products']
                ],
                'qualification_requirements': [],
                'total_incentive': pharma_result['total_incentive'],
                'final_payout': pharma_result['total_incentive'],
                'total_incentive_with_ucc': pharma_result['total_incentive'],
                'grand_total_incentive': pharma_result['total_incentive'],
                'is_qualified': pharma_result['total_incentive'] > 0,
            })
        elif active_category == 'overlapping':
            result.update({
                'criteria': overlapping_result['overlapping_criteria'],
                'criteria_dict': overlapping_result['overlapping_criteria_dict'],
                'breakdown': overlapping_result['overlapping_breakdown'],
                'payout_remarks': overlapping_result['overlapping_payout_remarks'],
                'qualification_requirements': overlapping_result['overlapping_qualification_requirements'],
            })
        elif active_category == 'bliss':
            result.update({
                'criteria': bliss_result['bliss_criteria'],
                'criteria_dict': bliss_result['bliss_criteria_dict'],
                'breakdown': bliss_result['bliss_breakdown'],
                'payout_remarks': bliss_result['bliss_payout_remarks'],
                'qualification_requirements': bliss_result['bliss_qualification_requirements'],
            })
        elif active_category == 'touch':
            result.update({
                'criteria': touch_result['touch_criteria'],
                'criteria_dict': touch_result['touch_criteria_dict'],
                'breakdown': touch_result['touch_breakdown'],
                'payout_remarks': touch_result['touch_payout_remarks'],
                'qualification_requirements': touch_result['touch_qualification_requirements'],
            })
        elif active_category == 'do':
            result.update({
                'criteria': do_result['criteria'],
                'criteria_dict': do_result['criteria_dict'],
                'breakdown': do_result['breakdown'],
                'payout_remarks': do_result['payout_remarks'],
                'qualification_requirements': do_result['qualification_requirements'],
            })
    elif is_rsm:
        if is_pharma_rsm and pharma_rsm_result:
            result.update({
                'is_rsm': True,
                'is_pharma_rsm': True,
                'is_asm': False,
                'ucc': None,
                'ucc_incentive': 0,
                'privilege_club': None,
                'privilege_incentive': 0,
                'asm_privilege_club': None,
                'asm_privilege_incentive': 0,
                'bliss_asm_ucc': None,
                'bliss_asm_ucc_incentive': 0,
                'rsm_privilege_club': None,
                'rsm_privilege_incentive': 0,
                'pharma_rsm': pharma_rsm_result,
                'criteria': [],
                'criteria_dict': {},
                'breakdown': [],
                'payout_remarks': [
                    {
                        'name': f"{b['designation']} - {b['name']} ({b['territory']})",
                        'remark': f"Net Val: {b['val_achievement']:.1f}%, Units: {b['unit_achievement']:.1f}% -> Payout Rs. {b['earned_incentive']:,.0f} (RSM 10%: Rs. {b['rsm_share']:,.0f})",
                        'slab': f"10% Share (Rs. {b['rsm_share']:,.0f})",
                        'qualified': b['earned_incentive'] > 0,
                        'incentive': b['rsm_share'],
                    }
                    for b in pharma_rsm_result['team_breakdown']
                ],
                'qualification_requirements': [],
                'total_incentive': active_incentive,
                'final_payout': final_payout,
                'total_incentive_with_ucc': final_payout,
                'grand_total_incentive': grand_total_incentive,
                'touch_final_payout': final_payout,
                'overlapping_final_payout': final_payout,
                'bliss_final_payout': final_payout,
                'is_qualified': is_qualified,
            })
        else:
            result.update({
                'is_rsm': True,
                'is_pharma_rsm': False,
                'is_asm': False,
                'ucc': None,
                'ucc_incentive': 0,
                'privilege_club': None,
                'privilege_incentive': 0,
                'asm_privilege_club': None,
                'asm_privilege_incentive': 0,
                'bliss_asm_ucc': None,
                'bliss_asm_ucc_incentive': 0,
                'rsm_privilege_club': rsm_privilege_result,
                'rsm_privilege_incentive': rsm_privilege_inc,
                'criteria': rsm_result['rsm_criteria'],
                'criteria_dict': rsm_result['rsm_criteria_dict'],
                'breakdown': rsm_result['rsm_breakdown'],
                'payout_remarks': rsm_result['rsm_payout_remarks'],
                'qualification_requirements': rsm_result['rsm_qualification_requirements'],
                'rsm_result': rsm_result,
                'total_incentive': active_incentive,
                'final_payout': final_payout,
                'total_incentive_with_ucc': final_payout,
                'grand_total_incentive': grand_total_incentive,
                'touch_final_payout': final_payout,
                'overlapping_final_payout': final_payout,
                'bliss_final_payout': final_payout,
            })
    else:
        result['is_asm'] = False
        result['is_rsm'] = False
        if active_category == 'pharma':
            result.update({
                'criteria': [],
                'criteria_dict': {},
                'breakdown': [],
                'payout_remarks': [
                    {
                        'name': p['name'],
                        'remark': p['need_text'],
                        'slab': p['applicable_slab'],
                        'qualified': p['qualified'],
                        'incentive': p['earned_incentive'],
                    }
                    for p in pharma_result['products']
                ],
                'qualification_requirements': [],
                'total_incentive': pharma_result['total_incentive'],
                'final_payout': pharma_result['total_incentive'],
                'total_incentive_with_ucc': pharma_result['total_incentive'],
                'grand_total_incentive': pharma_result['total_incentive'],
                'is_qualified': pharma_result['total_incentive'] > 0,
            })

    return result
