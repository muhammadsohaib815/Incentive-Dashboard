"""
DO Team Incentive Evaluator Module
Evaluates the 5 qualifying criteria for DO Team SPOs and ASMs.
"""
from core.config import CRITERIA_CONFIG, ASM_DO_CRITERIA_CONFIG
from core.evaluators.base import calculate_criterion


def evaluate_do_incentives(employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col=None, pos_code=None, territory=None, is_asm=False):
    """
    Full DO Team incentive evaluation (5 Criteria, 4 Incentive Slabs).
    Supports both DO Team SPOs and DO Team ASMs (GSM ASMs).
    Returns all criteria dicts, breakdowns, payout remarks, shortfalls, etc.
    """
    active_cfg = ASM_DO_CRITERIA_CONFIG if is_asm else CRITERIA_CONFIG
    do_criteria_dict = {}
    for cfg in active_cfg:
        res = calculate_criterion(cfg, employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col, pos_code=pos_code, territory=territory)
        do_criteria_dict[cfg['key']] = res

    # DO Category 1 (Joint DO Net + DO Silk Ultra-Thin Units)
    do_cat_ach = do_criteria_dict['do_category']['achievement']
    do_ut_ach = do_criteria_dict['do_ultra_thin']['achievement']

    joint_120_payout = 18000 if is_asm else 12500
    joint_100_payout = 16000 if is_asm else 10000

    if do_cat_ach >= 120 and do_ut_ach >= 120:
        do_slab = 120
        do_incentive = joint_120_payout
        do_tier = '120%'
        do_qualified = True
        do_remark = "DO Bottom-Line & DO Ultra-Thin Qualify With 120% Slab"
        do_req_text = "DO Bottom-line Incentive Qualified"
    elif do_cat_ach >= 100 and do_ut_ach >= 100:
        do_slab = 100
        do_incentive = joint_100_payout
        do_tier = '100%'
        do_qualified = True
        do_remark = "DO Bottom-Line & DO Ultra-Thin Qualify With 100% Slab"
        do_req_text = "DO Bottom-line Incentive Qualified"
    else:
        do_slab = 0
        do_incentive = 0
        do_tier = 'Below 100%'
        do_qualified = False
        do_remark = "DO Bottom-Line & DO Ultra-Thin Not Qualified"
        do_req_text = "DO Bottom-line Incentive Not Qualified"

    do_status = f'Qualified ({do_tier})' if do_qualified else 'Not Qualified'
    do_criteria_dict['do_category']['status'] = do_status
    do_criteria_dict['do_category']['qualified'] = do_qualified
    do_criteria_dict['do_category']['applicable_incentive'] = do_incentive
    do_criteria_dict['do_category']['remark'] = do_remark
    do_criteria_dict['do_category']['slab'] = do_slab
    do_criteria_dict['do_category']['tier'] = do_tier

    do_criteria_dict['do_ultra_thin']['status'] = do_status
    do_criteria_dict['do_ultra_thin']['qualified'] = do_qualified
    do_criteria_dict['do_ultra_thin']['applicable_incentive'] = do_incentive
    do_criteria_dict['do_ultra_thin']['remark'] = do_remark
    do_criteria_dict['do_ultra_thin']['slab'] = do_slab
    do_criteria_dict['do_ultra_thin']['tier'] = do_tier

    # DO Category 2: Sathi 6S / Sathi Plain
    sathi_plain_title = "SATHI Plain Bottom-Line" if is_asm else "SATHI 6s Bottom-Line"
    s6_120_payout = 8000 if is_asm else 5500
    s6_100_payout = 6500 if is_asm else 4500

    sathi_6s_ach = do_criteria_dict['sathi_6s']['achievement']
    if sathi_6s_ach >= 120:
        sathi_6s_slab = 120
        sathi_6s_inc = s6_120_payout
        sathi_6s_tier = '120%'
        sathi_6s_qual = True
        sathi_6s_remark = f"{sathi_plain_title} Qualify With 120% Slab"
        sathi_6s_req_text = f"{sathi_plain_title} Incentive Qualified"
    elif sathi_6s_ach >= 100:
        sathi_6s_slab = 100
        sathi_6s_inc = s6_100_payout
        sathi_6s_tier = '100%'
        sathi_6s_qual = True
        sathi_6s_remark = f"{sathi_plain_title} Qualify With 100% Slab"
        sathi_6s_req_text = f"{sathi_plain_title} Incentive Qualified"
    else:
        sathi_6s_slab = 0
        sathi_6s_inc = 0
        sathi_6s_tier = 'Below 100%'
        sathi_6s_qual = False
        sathi_6s_remark = f"{sathi_plain_title} Not Qualified"
        sathi_6s_req_text = f"{sathi_plain_title} Incentive Not Qualified"

    do_criteria_dict['sathi_6s']['status'] = f'Qualified ({sathi_6s_tier})' if sathi_6s_qual else 'Not Qualified'
    do_criteria_dict['sathi_6s']['qualified'] = sathi_6s_qual
    do_criteria_dict['sathi_6s']['applicable_incentive'] = sathi_6s_inc
    do_criteria_dict['sathi_6s']['remark'] = sathi_6s_remark
    do_criteria_dict['sathi_6s']['slab'] = sathi_6s_slab
    do_criteria_dict['sathi_6s']['tier'] = sathi_6s_tier

    # DO Category 3: Sathi Performance
    sp_120_payout = 14000 if is_asm else 9500
    sp_100_payout = 12500 if is_asm else 7500

    sathi_p_ach = do_criteria_dict['sathi_performance']['achievement']
    if sathi_p_ach >= 120:
        sathi_p_slab = 120
        sathi_p_inc = sp_120_payout
        sathi_p_tier = '120%'
        sathi_p_qual = True
        sathi_p_remark = "SATHI Perf. Category Qualify With 120% Slab"
        sathi_p_req_text = "SATHI Perf. Category Incentive Qualified"
    elif sathi_p_ach >= 100:
        sathi_p_slab = 100
        sathi_p_inc = sp_100_payout
        sathi_p_tier = '100%'
        sathi_p_qual = True
        sathi_p_remark = "SATHI Perf. Category Qualify With 100% Slab"
        sathi_p_req_text = "SATHI Perf. Category Incentive Qualified"
    else:
        sathi_p_slab = 0
        sathi_p_inc = 0
        sathi_p_tier = 'Below 100%'
        sathi_p_qual = False
        sathi_p_remark = "SATHI Perf. Category Not Qualified"
        sathi_p_req_text = "SATHI Perf. Category Incentive Not Qualified"

    do_criteria_dict['sathi_performance']['status'] = f'Qualified ({sathi_p_tier})' if sathi_p_qual else 'Not Qualified'
    do_criteria_dict['sathi_performance']['qualified'] = sathi_p_qual
    do_criteria_dict['sathi_performance']['applicable_incentive'] = sathi_p_inc
    do_criteria_dict['sathi_performance']['remark'] = sathi_p_remark
    do_criteria_dict['sathi_performance']['slab'] = sathi_p_slab
    do_criteria_dict['sathi_performance']['tier'] = sathi_p_tier

    # DO Category 4: Combined Bottom-Line
    bl_title = "ASM Bottom-Line" if is_asm else "SPO Bottom-Line"
    bl_120_payout = 15000 if is_asm else 6500
    bl_100_payout = 10000 if is_asm else 5000

    comb_ach = do_criteria_dict['do_sathi_bottom_line']['achievement']
    if comb_ach >= 120:
        spo_slab = 120
        comb_inc = bl_120_payout
        comb_tier = '120%'
        comb_qual = True
        spo_remark = f"{bl_title} Qualify With 120% Slab"
        spo_req_text = f"{bl_title} Incentive Qualified"
    elif comb_ach >= 100:
        spo_slab = 100
        comb_inc = bl_100_payout
        comb_tier = '100%'
        comb_qual = True
        spo_remark = f"{bl_title} Qualify With 100% Slab"
        spo_req_text = f"{bl_title} Incentive Qualified"
    else:
        spo_slab = 0
        comb_inc = 0
        comb_tier = 'Below 100%'
        comb_qual = False
        spo_remark = f"{bl_title} Not Qualified"
        spo_req_text = f"{bl_title} Incentive Not Qualified"

    do_criteria_dict['do_sathi_bottom_line']['status'] = f'Qualified ({comb_tier})' if comb_qual else 'Not Qualified'
    do_criteria_dict['do_sathi_bottom_line']['qualified'] = comb_qual
    do_criteria_dict['do_sathi_bottom_line']['applicable_incentive'] = comb_inc
    do_criteria_dict['do_sathi_bottom_line']['remark'] = spo_remark
    do_criteria_dict['do_sathi_bottom_line']['slab'] = spo_slab
    do_criteria_dict['do_sathi_bottom_line']['tier'] = comb_tier

    do_total_incentive = do_incentive + sathi_6s_inc + sathi_p_inc + comb_inc

    do_payout_remarks = [
        {
            'name': 'DO Bottom-Line & DO Ultra-Thin',
            'remark': do_remark,
            'slab': f"{do_slab}% Slab" if do_slab else "Below 100%",
            'qualified': do_qualified,
            'incentive': do_incentive
        },
        {
            'name': sathi_plain_title,
            'remark': sathi_6s_remark,
            'slab': f"{sathi_6s_slab}% Slab" if sathi_6s_slab else "Below 100%",
            'qualified': sathi_6s_qual,
            'incentive': sathi_6s_inc
        },
        {
            'name': 'SATHI Perf. Category',
            'remark': sathi_p_remark,
            'slab': f"{sathi_p_slab}% Slab" if sathi_p_slab else "Below 100%",
            'qualified': sathi_p_qual,
            'incentive': sathi_p_inc
        },
        {
            'name': bl_title,
            'remark': spo_remark,
            'slab': f"{spo_slab}% Slab" if spo_slab else "Below 100%",
            'qualified': comb_qual,
            'incentive': comb_inc
        }
    ]

    # DO shortfall calculations
    c_do_cat = do_criteria_dict['do_category']
    c_do_ult = do_criteria_dict['do_ultra_thin']
    t_do_cat, a_do_cat = c_do_cat.get('target', 0.0), c_do_cat.get('actual', 0.0)
    t_do_ult, a_do_ult = c_do_ult.get('target', 0.0), c_do_ult.get('actual', 0.0)

    if do_qualified:
        do_joint_need = 0.0
    else:
        n_c1 = max(t_do_cat - a_do_cat, 0.0) if t_do_cat > 0 else (0.0 if a_do_cat > 0 else None)
        n_c2 = max(t_do_ult - a_do_ult, 0.0) if t_do_ult > 0 else (0.0 if a_do_ult > 0 else None)
        valid_do_needs = [n for n in [n_c1, n_c2] if n is not None]
        do_joint_need = max(valid_do_needs) if valid_do_needs else None

    c_s6 = do_criteria_dict['sathi_6s']
    t_s6, a_s6 = c_s6.get('target', 0.0), c_s6.get('actual', 0.0)
    sathi_6s_need = 0.0 if sathi_6s_qual else (max(t_s6 - a_s6, 0.0) if t_s6 > 0 else None)

    c_sp = do_criteria_dict['sathi_performance']
    t_sp, a_sp = c_sp.get('target', 0.0), c_sp.get('actual', 0.0)
    sathi_performance_need = 0.0 if sathi_p_qual else (max(t_sp - a_sp, 0.0) if t_sp > 0 else None)

    c_comb = do_criteria_dict['do_sathi_bottom_line']
    t_comb, a_comb = c_comb.get('target', 0.0), c_comb.get('actual', 0.0)
    do_sathi_need = 0.0 if comb_qual else (max(t_comb - a_comb, 0.0) if t_comb > 0 else None)

    do_unearned_needs = []
    if not do_qualified and do_joint_need is not None and do_joint_need > 0:
        do_unearned_needs.append(do_joint_need)
    if not sathi_6s_qual and sathi_6s_need is not None and sathi_6s_need > 0:
        do_unearned_needs.append(sathi_6s_need)
    if not sathi_p_qual and sathi_performance_need is not None and sathi_performance_need > 0:
        do_unearned_needs.append(sathi_performance_need)
    if not comb_qual and do_sathi_need is not None and do_sathi_need > 0:
        do_unearned_needs.append(do_sathi_need)

    do_overall_qualifying_need = min(do_unearned_needs) if do_unearned_needs else None

    # Attach need & need_text directly to criteria
    do_c1_need = max(t_do_cat - a_do_cat, 0.0) if t_do_cat > 0 else (0.0 if a_do_cat > 0 else 0.0)
    do_c2_unit_need = max(t_do_ult - a_do_ult, 0.0) if t_do_ult > 0 else (0.0 if a_do_ult > 0 else 0.0)

    do_criteria_dict['do_category']['need'] = 0.0 if do_qualified else do_c1_need
    do_criteria_dict['do_category']['need_text'] = "Requirement Met" if do_qualified else f"Need: Rs. {do_c1_need:,.0f} to Qualify"

    do_criteria_dict['do_ultra_thin']['need'] = 0.0 if do_qualified else do_c2_unit_need
    do_criteria_dict['do_ultra_thin']['need_text'] = "Requirement Met" if do_qualified else f"Need: {round(do_c2_unit_need):,} Units to Qualify"

    do_criteria_dict['sathi_6s']['need'] = sathi_6s_need
    do_criteria_dict['sathi_6s']['need_text'] = "Requirement Met" if sathi_6s_qual else (f"Need: Rs. {sathi_6s_need:,.0f} to Qualify" if sathi_6s_need is not None else "Need: N/A to Qualify")

    do_criteria_dict['sathi_performance']['need'] = sathi_performance_need
    do_criteria_dict['sathi_performance']['need_text'] = "Requirement Met" if sathi_p_qual else (f"Need: Rs. {sathi_performance_need:,.0f} to Qualify" if sathi_performance_need is not None else "Need: N/A to Qualify")

    do_criteria_dict['do_sathi_bottom_line']['need'] = do_sathi_need
    do_criteria_dict['do_sathi_bottom_line']['need_text'] = "Requirement Met" if comb_qual else (f"Need: Rs. {do_sathi_need:,.0f} to Qualify" if do_sathi_need is not None else "Need: N/A to Qualify")

    do_qualification_requirements = [
        {
            'category': 'DO Bottom-line Incentive',
            'text': do_req_text,
            'qualified': do_qualified,
            'slab': f"{do_slab}%" if do_slab else "None",
            'incentive': do_incentive,
            'need': do_joint_need
        },
        {
            'category': f'{sathi_plain_title} Incentive',
            'text': sathi_6s_req_text,
            'qualified': sathi_6s_qual,
            'slab': f"{sathi_6s_slab}%" if sathi_6s_slab else "None",
            'incentive': sathi_6s_inc,
            'need': sathi_6s_need
        },
        {
            'category': 'SATHI Perf. Category Incentive',
            'text': sathi_p_req_text,
            'qualified': sathi_p_qual,
            'slab': f"{sathi_p_slab}%" if sathi_p_slab else "None",
            'incentive': sathi_p_inc,
            'need': sathi_performance_need
        },
        {
            'category': f'{bl_title} Incentive',
            'text': spo_req_text,
            'qualified': comb_qual,
            'slab': f"{spo_slab}%" if spo_slab else "None",
            'incentive': comb_inc,
            'need': do_sathi_need
        }
    ]

    do_breakdown = [
        {
            'key': 'do_incentive',
            'category': 'DO Category & Silk Ultra-Thin Units',
            'rule': 'Both DO Net & Silk Ultra-Thin Units >= threshold',
            'tier': do_tier,
            'amount': do_incentive,
            'qualified': do_qualified
        },
        {
            'key': 'sathi_6s',
            'category': f'{sathi_plain_title} Net Value',
            'rule': f'{sathi_plain_title} Net Value >= threshold',
            'tier': sathi_6s_tier,
            'amount': sathi_6s_inc,
            'qualified': sathi_6s_qual
        },
        {
            'key': 'sathi_performance',
            'category': 'Sathi Performance Category Bottom-Line',
            'rule': 'Performance Category Net Value >= threshold',
            'tier': sathi_p_tier,
            'amount': sathi_p_inc,
            'qualified': sathi_p_qual
        },
        {
            'key': 'do_sathi_bottom_line',
            'category': f'{bl_title} Net Value',
            'rule': f'{bl_title} Net Value >= threshold',
            'tier': comb_tier,
            'amount': comb_inc,
            'qualified': comb_qual
        },
    ]

    do_qualified_count = sum(1 for b in do_breakdown if b['qualified'])
    do_final_status = "INCENTIVE QUALIFIED" if do_total_incentive > 0 else "INCENTIVE NOT QUALIFIED"
    do_qualify_label = "Qualify Incentive" if do_total_incentive > 0 else "Not Qualified"

    return {
        'criteria': list(do_criteria_dict.values()),
        'criteria_dict': do_criteria_dict,
        'breakdown': do_breakdown,
        'payout_remarks': do_payout_remarks,
        'qualification_requirements': do_qualification_requirements,
        'do_incentive': do_incentive,
        'sathi_6s_incentive': sathi_6s_inc,
        'sathi_performance_incentive': sathi_p_inc,
        'do_sathi_incentive': comb_inc,
        'do_joint_need': do_joint_need,
        'sathi_6s_need': sathi_6s_need,
        'sathi_performance_need': sathi_performance_need,
        'do_sathi_need': do_sathi_need,
        'do_overall_qualifying_need': do_overall_qualifying_need,
        'do_qualifying_sub': "Additional Net Value Required",
        'total_incentive': do_total_incentive,
        'qualified_count': do_qualified_count,
        'qualified': do_total_incentive > 0,
        'final_status': do_final_status,
        'qualify_label': do_qualify_label,
        'tier': f"{do_qualified_count} of 4 Qualified" if do_total_incentive > 0 else "Not Qualified",
    }
