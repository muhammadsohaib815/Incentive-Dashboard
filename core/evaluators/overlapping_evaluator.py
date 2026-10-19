"""
Overlapping SPOs Incentive Evaluator Module
Evaluates qualifying criteria for Overlapping (DO + TOUCH) SPOs and ASMs.
"""
from core.config import OVERLAPPING_CRITERIA_CONFIG, ASM_OVERLAPPING_CRITERIA_CONFIG
from core.evaluators.base import calculate_criterion


def evaluate_asm_overlapping_incentives(employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col=None, t_tp_col=None, pos_code=None, territory=None):
    """
    Overlapping ASMs incentive evaluation (7 Qualifying Criteria from policy document).
    1. DO Category Bottom-line Net Value AND DO Silk Ultra-Thin Units (Joint: Rs. 12,000 / Rs. 14,000)
    2. Sathi Category Bottom-line Net Value (Rs. 9,000 / Rs. 10,500)
    3. Touch Delay + Touch Strawberry + Touch Multi Mix Category (Rs. 7,000 / Rs. 9,000)
    4. Touch Dotted + Touch Ribbed + Touch Classic Category (Rs. 7,000 / Rs. 8,500)
    5. ONE Category Bottom-line Net Value (Rs. 5,000 / Rs. 6,500)
    6. BLISS Bottom-Line Net Value (Rs. 15,000 / Rs. 20,000)
    7. Bottom-Line Net Value targets (Rs. 5,000 / Rs. 6,500)
    """
    criteria_dict = {}
    for cfg in ASM_OVERLAPPING_CRITERIA_CONFIG:
        res = calculate_criterion(cfg, employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col, t_tp_col, pos_code=pos_code, territory=territory)
        criteria_dict[cfg['key']] = res

    # 1. Joint DO (DO Category Net & DO Silk Ultra-Thin Units)
    do_cat_ach = criteria_dict['do_category']['achievement']
    do_ut_ach = criteria_dict['do_ultra_thin']['achievement']

    if do_cat_ach >= 120 and do_ut_ach >= 120:
        c1_slab = 120
        c1_inc = 14000
        c1_tier = '120%'
        c1_qual = True
        c1_remark = "DO Bottom-Line & DO Ultra-Thin Qualify With 120% Slab"
        c1_req_text = "DO Bottom-line & Ultra-Thin Incentive Qualified"
    elif do_cat_ach >= 100 and do_ut_ach >= 100:
        c1_slab = 100
        c1_inc = 12000
        c1_tier = '100%'
        c1_qual = True
        c1_remark = "DO Bottom-Line & DO Ultra-Thin Qualify With 100% Slab"
        c1_req_text = "DO Bottom-line & Ultra-Thin Incentive Qualified"
    else:
        c1_slab = 0
        c1_inc = 0
        c1_tier = 'Below 100%'
        c1_qual = False
        c1_remark = "DO Bottom-Line & DO Ultra-Thin Not Qualified"
        c1_req_text = "DO Bottom-line & Ultra-Thin Incentive Not Qualified"

    criteria_dict['do_category']['status'] = f'Qualified ({c1_tier})' if c1_qual else 'Not Qualified'
    criteria_dict['do_category']['qualified'] = c1_qual
    criteria_dict['do_category']['applicable_incentive'] = c1_inc
    criteria_dict['do_category']['slab'] = c1_slab
    criteria_dict['do_category']['tier'] = c1_tier
    criteria_dict['do_category']['remark'] = c1_remark

    criteria_dict['do_ultra_thin']['status'] = f'Qualified ({c1_tier})' if c1_qual else 'Not Qualified'
    criteria_dict['do_ultra_thin']['qualified'] = c1_qual
    criteria_dict['do_ultra_thin']['applicable_incentive'] = c1_inc
    criteria_dict['do_ultra_thin']['slab'] = c1_slab
    criteria_dict['do_ultra_thin']['tier'] = c1_tier
    criteria_dict['do_ultra_thin']['remark'] = c1_remark

    # 2. Other 5 criteria
    other_inc_total = 0
    payout_remarks = [
        {
            'name': 'DO Bottom-Line & DO Ultra-Thin',
            'remark': c1_remark,
            'slab': f"{c1_slab}% Slab" if c1_slab else "Below 100%",
            'qualified': c1_qual,
            'incentive': c1_inc
        }
    ]

    for cfg in ASM_OVERLAPPING_CRITERIA_CONFIG[2:]:
        res = criteria_dict[cfg['key']]
        ach = res['achievement']
        if ach >= 120:
            s = 120
            inc = cfg['slab_120']
            tier = '120%'
            qual = True
            rem = f"{cfg['remark_name']} Qualify With 120% Slab"
            req = f"{cfg['req_name']} Qualified"
        elif ach >= 100:
            s = 100
            inc = cfg['slab_100']
            tier = '100%'
            qual = True
            rem = f"{cfg['remark_name']} Qualify With 100% Slab"
            req = f"{cfg['req_name']} Qualified"
        else:
            s = 0
            inc = 0
            tier = 'Below 100%'
            qual = False
            rem = f"{cfg['remark_name']} Not Qualified"
            req = f"{cfg['req_name']} Not Qualified"

        res['status'] = f'Qualified ({tier})' if qual else 'Not Qualified'
        res['qualified'] = qual
        res['applicable_incentive'] = inc
        res['slab'] = s
        res['tier'] = tier
        res['remark'] = rem
        res['req_text'] = req
        other_inc_total += inc

        payout_remarks.append({
            'name': cfg['remark_name'],
            'remark': rem,
            'slab': f"{s}% Slab" if s else "Below 100%",
            'qualified': qual,
            'incentive': inc
        })

    total_incentive = c1_inc + other_inc_total

    # Needs calculation
    t_c1, a_c1 = criteria_dict['do_category'].get('target', 0.0), criteria_dict['do_category'].get('actual', 0.0)
    t_c2, a_c2 = criteria_dict['do_ultra_thin'].get('target', 0.0), criteria_dict['do_ultra_thin'].get('actual', 0.0)
    c1_need = 0.0 if c1_qual else (max(t_c1 - a_c1, 0.0) if t_c1 > 0 else 0.0)
    c2_need = 0.0 if c1_qual else (max(t_c2 - a_c2, 0.0) if t_c2 > 0 else 0.0)

    criteria_dict['do_category']['need'] = c1_need
    criteria_dict['do_category']['need_text'] = "Requirement Met" if c1_qual else f"Need: Rs. {c1_need:,.0f} to Qualify"
    criteria_dict['do_ultra_thin']['need'] = c2_need
    criteria_dict['do_ultra_thin']['need_text'] = "Requirement Met" if c1_qual else f"Need: {round(c2_need):,} Units to Qualify"

    all_unearned = []
    if not c1_qual:
        if c1_need > 0: all_unearned.append(c1_need)

    for cfg in ASM_OVERLAPPING_CRITERIA_CONFIG[2:]:
        item = criteria_dict[cfg['key']]
        t, a = item.get('target', 0.0), item.get('actual', 0.0)
        n = 0.0 if item['qualified'] else (max(t - a, 0.0) if t > 0 else None)
        item['need'] = n
        item['need_text'] = "Requirement Met" if item['qualified'] else (f"Need: Rs. {n:,.0f} to Qualify" if n is not None else "Need: N/A to Qualify")
        if not item['qualified'] and n is not None and n > 0:
            all_unearned.append(n)

    overall_qualifying_need = min(all_unearned) if all_unearned else None

    # Qualification requirements
    qualification_requirements = [
        {
            'category': 'DO Bottom-line & Ultra-Thin Incentive',
            'text': c1_req_text,
            'qualified': c1_qual,
            'slab': f"{c1_slab}%" if c1_slab else "None",
            'incentive': c1_inc,
            'need': max(c1_need, c2_need) if not c1_qual else 0.0
        }
    ]
    for cfg in ASM_OVERLAPPING_CRITERIA_CONFIG[2:]:
        item = criteria_dict[cfg['key']]
        qualification_requirements.append({
            'category': cfg['req_name'],
            'text': item['req_text'],
            'qualified': item['qualified'],
            'slab': f"{item['slab']}%" if item['slab'] else "None",
            'incentive': item['applicable_incentive'],
            'need': item['need']
        })

    # Breakdown (6 items)
    breakdown = [
        {
            'key': 'do_category_ultra',
            'category': 'DO Category Net Value & DO Silk Ultra-Thin Units',
            'rule': 'Both DO Net Value & Silk Ultra-Thin Units >= threshold',
            'tier': c1_tier,
            'amount': c1_inc,
            'qualified': c1_qual
        }
    ]
    for cfg in ASM_OVERLAPPING_CRITERIA_CONFIG[2:]:
        item = criteria_dict[cfg['key']]
        breakdown.append({
            'key': cfg['key'],
            'category': cfg['name'],
            'rule': f"{cfg['short_name']} Net Value >= threshold",
            'tier': item['tier'],
            'amount': item['applicable_incentive'],
            'qualified': item['qualified']
        })

    qualified_count = sum(1 for b in breakdown if b['qualified'])
    final_status = "INCENTIVE QUALIFIED" if total_incentive > 0 else "INCENTIVE NOT QUALIFIED"
    qualify_label = "Qualify Incentive" if total_incentive > 0 else "Not Qualified"
    tier = f"{qualified_count} of 7 Qualified" if total_incentive > 0 else "Not Qualified"

    return {
        'overlapping_criteria': list(criteria_dict.values()),
        'overlapping_criteria_dict': criteria_dict,
        'overlapping_breakdown': breakdown,
        'overlapping_payout_remarks': payout_remarks,
        'overlapping_qualification_requirements': qualification_requirements,
        'overlapping_total_incentive': total_incentive,
        'overlapping_joint_incentive': c1_inc,
        'overlapping_sathi_incentive': criteria_dict['sathi_category']['applicable_incentive'],
        'overlapping_touch_incentive': criteria_dict['touch_delay_mix']['applicable_incentive'] + criteria_dict['touch_classic_group']['applicable_incentive'],
        'overlapping_touch_delay_incentive': criteria_dict['touch_delay_mix']['applicable_incentive'],
        'overlapping_touch_classic_incentive': criteria_dict['touch_classic_group']['applicable_incentive'],
        'overlapping_one_incentive': criteria_dict['one_brand']['applicable_incentive'],
        'overlapping_bliss_incentive': criteria_dict['bliss_overlap_bottom_line']['applicable_incentive'],
        'overlapping_overall_incentive': criteria_dict['overlapping_bottom_line']['applicable_incentive'],
        'overlapping_joint_need': max(c1_need, c2_need) if not c1_qual else 0.0,
        'overlapping_touch_need': criteria_dict['touch_classic_group'].get('need'),
        'overlapping_overall_need': criteria_dict['overlapping_bottom_line'].get('need'),
        'overlapping_overall_qualifying_need': overall_qualifying_need,
        'overlapping_qualifying_sub': "Additional Net Value Required",
        'overlapping_qualified_count': qualified_count,
        'overlapping_qualified': total_incentive > 0,
        'overlapping_final_status': final_status,
        'overlapping_qualify_label': qualify_label,
        'overlapping_tier': tier
    }


def evaluate_overlapping_incentives(employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col=None, t_tp_col=None, pos_code=None, territory=None, is_asm=False):
    """
    Full Overlapping SPOs / ASMs incentive evaluation.
    Delegates to evaluate_asm_overlapping_incentives when is_asm is True.
    """
    if is_asm:
        return evaluate_asm_overlapping_incentives(
            employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col, t_tp_col, pos_code=pos_code, territory=territory
        )
    overlapping_criteria_dict = {}
    for cfg in OVERLAPPING_CRITERIA_CONFIG:
        res = calculate_criterion(cfg, employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col, t_tp_col, pos_code=pos_code, territory=territory)
        overlapping_criteria_dict[cfg['key']] = res

    do_sathi_perf_ach = overlapping_criteria_dict['do_sathi_perf_bottom_line']['achievement']
    ultra_ach = overlapping_criteria_dict['overlapping_silk_ultra_thin']['achievement']

    if do_sathi_perf_ach >= 120 and ultra_ach >= 120:
        ov_joint_slab = 120
        ov_joint_inc = 15000
        ov_joint_tier = '120%'
        ov_joint_qual = True
        ov_joint_remark = "DO + Sathi Perf & Ultra Qualify With 120% Slab"
        ov_joint_req_text = "DO + Sathi Perf & Ultra-Thin Incentive Qualified"
    elif do_sathi_perf_ach >= 100 and ultra_ach >= 100:
        ov_joint_slab = 100
        ov_joint_inc = 12000
        ov_joint_tier = '100%'
        ov_joint_qual = True
        ov_joint_remark = "DO + Sathi Perf & Ultra Qualify With 100% Slab"
        ov_joint_req_text = "DO + Sathi Perf & Ultra-Thin Incentive Qualified"
    else:
        ov_joint_slab = 0
        ov_joint_inc = 0
        ov_joint_tier = 'Below 100%'
        ov_joint_qual = False
        ov_joint_remark = "DO + Sathi Perf & Ultra Not Qualified"
        ov_joint_req_text = "DO + Sathi Perf & Ultra-Thin Incentive Not Qualified"

    overlapping_criteria_dict['do_sathi_perf_bottom_line']['status'] = f'Qualified ({ov_joint_tier})' if ov_joint_qual else 'Not Qualified'
    overlapping_criteria_dict['do_sathi_perf_bottom_line']['qualified'] = ov_joint_qual
    overlapping_criteria_dict['do_sathi_perf_bottom_line']['applicable_incentive'] = ov_joint_inc
    overlapping_criteria_dict['do_sathi_perf_bottom_line']['slab'] = ov_joint_slab
    overlapping_criteria_dict['do_sathi_perf_bottom_line']['tier'] = ov_joint_tier
    overlapping_criteria_dict['do_sathi_perf_bottom_line']['remark'] = ov_joint_remark

    overlapping_criteria_dict['overlapping_silk_ultra_thin']['status'] = f'Qualified ({ov_joint_tier})' if ov_joint_qual else 'Not Qualified'
    overlapping_criteria_dict['overlapping_silk_ultra_thin']['qualified'] = ov_joint_qual
    overlapping_criteria_dict['overlapping_silk_ultra_thin']['applicable_incentive'] = ov_joint_inc
    overlapping_criteria_dict['overlapping_silk_ultra_thin']['slab'] = ov_joint_slab
    overlapping_criteria_dict['overlapping_silk_ultra_thin']['tier'] = ov_joint_tier
    overlapping_criteria_dict['overlapping_silk_ultra_thin']['remark'] = ov_joint_remark

    ov_touch_cfg = next(c for c in OVERLAPPING_CRITERIA_CONFIG if c['key'] == 'touch_bottom_line')
    ov_touch_ach = overlapping_criteria_dict['touch_bottom_line']['achievement']
    if ov_touch_ach >= 120:
        ov_touch_slab = 120
        ov_touch_inc = ov_touch_cfg['slab_120']
        ov_touch_tier = '120%'
        ov_touch_qual = True
        ov_touch_remark = f"{ov_touch_cfg['remark_name']} Qualify With 120% Slab"
        ov_touch_req_text = f"{ov_touch_cfg['req_name']} Qualified"
    elif ov_touch_ach >= 100:
        ov_touch_slab = 100
        ov_touch_inc = ov_touch_cfg['slab_100']
        ov_touch_tier = '100%'
        ov_touch_qual = True
        ov_touch_remark = f"{ov_touch_cfg['remark_name']} Qualify With 100% Slab"
        ov_touch_req_text = f"{ov_touch_cfg['req_name']} Qualified"
    else:
        ov_touch_slab = 0
        ov_touch_inc = 0
        ov_touch_tier = 'Below 100%'
        ov_touch_qual = False
        ov_touch_remark = f"{ov_touch_cfg['remark_name']} Not Qualified"
        ov_touch_req_text = f"{ov_touch_cfg['req_name']} Not Qualified"

    overlapping_criteria_dict['touch_bottom_line']['status'] = f'Qualified ({ov_touch_tier})' if ov_touch_qual else 'Not Qualified'
    overlapping_criteria_dict['touch_bottom_line']['qualified'] = ov_touch_qual
    overlapping_criteria_dict['touch_bottom_line']['applicable_incentive'] = ov_touch_inc
    overlapping_criteria_dict['touch_bottom_line']['slab'] = ov_touch_slab
    overlapping_criteria_dict['touch_bottom_line']['tier'] = ov_touch_tier
    overlapping_criteria_dict['touch_bottom_line']['remark'] = ov_touch_remark

    ov_overall_cfg = next(c for c in OVERLAPPING_CRITERIA_CONFIG if c['key'] == 'overlapping_overall_bottom_line')
    ov_overall_ach = overlapping_criteria_dict['overlapping_overall_bottom_line']['achievement']
    if ov_overall_ach >= 120:
        ov_overall_slab = 120
        ov_overall_inc = ov_overall_cfg['slab_120']
        ov_overall_tier = '120%'
        ov_overall_qual = True
        ov_overall_remark = f"{ov_overall_cfg['remark_name']} Qualify With 120% Slab"
        ov_overall_req_text = f"{ov_overall_cfg['req_name']} Qualified"
    elif ov_overall_ach >= 100:
        ov_overall_slab = 100
        ov_overall_inc = ov_overall_cfg['slab_100']
        ov_overall_tier = '100%'
        ov_overall_qual = True
        ov_overall_remark = f"{ov_overall_cfg['remark_name']} Qualify With 100% Slab"
        ov_overall_req_text = f"{ov_overall_cfg['req_name']} Qualified"
    else:
        ov_overall_slab = 0
        ov_overall_inc = 0
        ov_overall_tier = 'Below 100%'
        ov_overall_qual = False
        ov_overall_remark = f"{ov_overall_cfg['remark_name']} Not Qualified"
        ov_overall_req_text = f"{ov_overall_cfg['req_name']} Not Qualified"

    overlapping_criteria_dict['overlapping_overall_bottom_line']['status'] = f'Qualified ({ov_overall_tier})' if ov_overall_qual else 'Not Qualified'
    overlapping_criteria_dict['overlapping_overall_bottom_line']['qualified'] = ov_overall_qual
    overlapping_criteria_dict['overlapping_overall_bottom_line']['applicable_incentive'] = ov_overall_inc
    overlapping_criteria_dict['overlapping_overall_bottom_line']['slab'] = ov_overall_slab
    overlapping_criteria_dict['overlapping_overall_bottom_line']['tier'] = ov_overall_tier
    overlapping_criteria_dict['overlapping_overall_bottom_line']['remark'] = ov_overall_remark

    overlapping_total_incentive = ov_joint_inc + ov_touch_inc + ov_overall_inc

    overlapping_payout_remarks = [
        {
            'name': 'DO + Sathi Performance & DO Ultra-Thin',
            'remark': ov_joint_remark,
            'slab': f"{ov_joint_slab}% Slab" if ov_joint_slab else "Below 100%",
            'qualified': ov_joint_qual,
            'incentive': ov_joint_inc
        },
        {
            'name': ov_touch_cfg['remark_name'],
            'remark': ov_touch_remark,
            'slab': f"{ov_touch_slab}% Slab" if ov_touch_slab else "Below 100%",
            'qualified': ov_touch_qual,
            'incentive': ov_touch_inc
        },
        {
            'name': ov_overall_cfg['remark_name'],
            'remark': ov_overall_remark,
            'slab': f"{ov_overall_slab}% Slab" if ov_overall_slab else "Below 100%",
            'qualified': ov_overall_qual,
            'incentive': ov_overall_inc
        }
    ]

    c_ov1 = overlapping_criteria_dict['do_sathi_perf_bottom_line']
    c_ov2 = overlapping_criteria_dict['overlapping_silk_ultra_thin']
    t_ov1, a_ov1 = c_ov1.get('target', 0.0), c_ov1.get('actual', 0.0)
    t_ov2, a_ov2 = c_ov2.get('target', 0.0), c_ov2.get('actual', 0.0)

    if ov_joint_qual:
        ov_joint_need = 0.0
    else:
        n_ov1 = max(t_ov1 - a_ov1, 0.0) if t_ov1 > 0 else (0.0 if a_ov1 > 0 else None)
        n_ov2 = max(t_ov2 - a_ov2, 0.0) if t_ov2 > 0 else (0.0 if a_ov2 > 0 else None)
        valid_ov_needs = [n for n in [n_ov1, n_ov2] if n is not None]
        ov_joint_need = max(valid_ov_needs) if valid_ov_needs else None

    c_ov3 = overlapping_criteria_dict['touch_bottom_line']
    t_ov3, a_ov3 = c_ov3.get('target', 0.0), c_ov3.get('actual', 0.0)
    ov_touch_need = 0.0 if ov_touch_qual else (max(t_ov3 - a_ov3, 0.0) if t_ov3 > 0 else None)

    c_ov4 = overlapping_criteria_dict['overlapping_overall_bottom_line']
    t_ov4, a_ov4 = c_ov4.get('target', 0.0), c_ov4.get('actual', 0.0)
    ov_overall_need = 0.0 if ov_overall_qual else (max(t_ov4 - a_ov4, 0.0) if t_ov4 > 0 else None)

    ov_unearned_needs = []
    if not ov_joint_qual and ov_joint_need is not None and ov_joint_need > 0:
        ov_unearned_needs.append(ov_joint_need)
    if not ov_touch_qual and ov_touch_need is not None and ov_touch_need > 0:
        ov_unearned_needs.append(ov_touch_need)
    if not ov_overall_qual and ov_overall_need is not None and ov_overall_need > 0:
        ov_unearned_needs.append(ov_overall_need)

    overlapping_overall_qualifying_need = min(ov_unearned_needs) if ov_unearned_needs else None

    c1_need = max(t_ov1 - a_ov1, 0.0) if t_ov1 > 0 else (0.0 if a_ov1 > 0 else 0.0)
    c2_unit_need = max(t_ov2 - a_ov2, 0.0) if t_ov2 > 0 else (0.0 if a_ov2 > 0 else 0.0)

    overlapping_criteria_dict['do_sathi_perf_bottom_line']['need'] = 0.0 if ov_joint_qual else c1_need
    overlapping_criteria_dict['do_sathi_perf_bottom_line']['need_text'] = "Requirement Met" if ov_joint_qual else f"Need: Rs. {c1_need:,.0f} to Qualify"

    overlapping_criteria_dict['overlapping_silk_ultra_thin']['need'] = 0.0 if ov_joint_qual else c2_unit_need
    overlapping_criteria_dict['overlapping_silk_ultra_thin']['need_text'] = "Requirement Met" if ov_joint_qual else f"Need: {round(c2_unit_need):,} Units to Qualify"

    overlapping_criteria_dict['touch_bottom_line']['need'] = ov_touch_need
    overlapping_criteria_dict['touch_bottom_line']['need_text'] = "Requirement Met" if ov_touch_qual else (f"Need: Rs. {ov_touch_need:,.0f} to Qualify" if ov_touch_need is not None else "Need: N/A to Qualify")

    overlapping_criteria_dict['overlapping_overall_bottom_line']['need'] = ov_overall_need
    overlapping_criteria_dict['overlapping_overall_bottom_line']['need_text'] = "Requirement Met" if ov_overall_qual else (f"Need: Rs. {ov_overall_need:,.0f} to Qualify" if ov_overall_need is not None else "Need: N/A to Qualify")

    overlapping_qualification_requirements = [
        {
            'category': 'DO + Sathi Perf & Ultra-Thin',
            'text': ov_joint_req_text,
            'qualified': ov_joint_qual,
            'slab': f"{ov_joint_slab}%" if ov_joint_slab else "None",
            'incentive': ov_joint_inc,
            'need': ov_joint_need
        },
        {
            'category': ov_touch_cfg['req_name'],
            'text': ov_touch_req_text,
            'qualified': ov_touch_qual,
            'slab': f"{ov_touch_slab}%" if ov_touch_slab else "None",
            'incentive': ov_touch_inc,
            'need': ov_touch_need
        },
        {
            'category': ov_overall_cfg['req_name'],
            'text': ov_overall_req_text,
            'qualified': ov_overall_qual,
            'slab': f"{ov_overall_slab}%" if ov_overall_slab else "None",
            'incentive': ov_overall_inc,
            'need': ov_overall_need
        }
    ]

    overlapping_breakdown = [
        {
            'key': 'do_sathi_perf_ultra',
            'category': 'DO Category + Sathi Perf & Silk Ultra-Thin',
            'rule': 'Both DO+Sathi Net & Silk Ultra-Thin Units >= threshold',
            'tier': ov_joint_tier,
            'amount': ov_joint_inc,
            'qualified': ov_joint_qual
        },
        {
            'key': 'touch_bottom_line',
            'category': 'Touch Category Bottom-Line Net Value',
            'rule': 'Touch Bottom-Line Net Value >= threshold',
            'tier': ov_touch_tier,
            'amount': ov_touch_inc,
            'qualified': ov_touch_qual
        },
        {
            'key': 'overlapping_overall_bottom_line',
            'category': 'Overall Bottom-Line Net Value',
            'rule': 'Overall Bottom-Line Net Value >= threshold',
            'tier': ov_overall_tier,
            'amount': ov_overall_inc,
            'qualified': ov_overall_qual
        }
    ]

    overlapping_qualified_count = sum(1 for b in overlapping_breakdown if b['qualified'])
    overlapping_final_status = "INCENTIVE QUALIFIED" if overlapping_total_incentive > 0 else "INCENTIVE NOT QUALIFIED"
    overlapping_qualify_label = "Qualify Incentive" if overlapping_total_incentive > 0 else "Not Qualified"
    overlapping_tier = f"{overlapping_qualified_count} of 3 Qualified" if overlapping_total_incentive > 0 else "Not Qualified"

    return {
        'overlapping_criteria': list(overlapping_criteria_dict.values()),
        'overlapping_criteria_dict': overlapping_criteria_dict,
        'overlapping_breakdown': overlapping_breakdown,
        'overlapping_payout_remarks': overlapping_payout_remarks,
        'overlapping_qualification_requirements': overlapping_qualification_requirements,
        'overlapping_total_incentive': overlapping_total_incentive,
        'overlapping_joint_incentive': ov_joint_inc,
        'overlapping_touch_incentive': ov_touch_inc,
        'overlapping_overall_incentive': ov_overall_inc,
        'overlapping_joint_need': ov_joint_need,
        'overlapping_touch_need': ov_touch_need,
        'overlapping_overall_need': ov_overall_need,
        'overlapping_overall_qualifying_need': overlapping_overall_qualifying_need,
        'overlapping_qualifying_sub': "Additional Net Value Required",
        'overlapping_qualified_count': overlapping_qualified_count,
        'overlapping_qualified': overlapping_total_incentive > 0,
        'overlapping_final_status': overlapping_final_status,
        'overlapping_qualify_label': overlapping_qualify_label,
        'overlapping_tier': overlapping_tier
    }
