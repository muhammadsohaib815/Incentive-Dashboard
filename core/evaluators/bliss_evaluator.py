"""
BLISS Team Incentive Evaluator Module
Evaluates the qualifying criteria for BLISS Team SPOs, Dedicated BLISS ASMs, and Overlap ASMs.
Criteria: Target vs Achievement of Bottom-Line Net Value

Slabs:
- SPOs:
  - 100%: Rs. 30,000
  - 120%: Rs. 35,000
- Dedicated ASMs:
  - 100%: Rs. 40,000
  - 120%: Rs. 50,000
- Overlap ASMs:
  - 100%: Rs. 15,000
  - 120%: Rs. 20,000
"""
from core.config import BLISS_CRITERIA_CONFIG, ASM_BLISS_CRITERIA_CONFIG, ASM_OVERLAP_BLISS_CRITERIA_CONFIG
from core.evaluators.base import calculate_criterion


def evaluate_bliss_incentives(employee, month, target_df, sales_df, target_master_col, t_net_col, pos_code=None, territory=None, is_asm=False, is_overlap=False):
    """
    Full BLISS Team incentive evaluation (Bottom-Line Net Value).
    Supports:
    - SPOs (Rs. 30k / 35k)
    - Dedicated ASMs (Rs. 40k / 50k)
    - Overlap ASMs (Rs. 15k / 20k)
    Returns all criteria dicts, breakdowns, payout remarks, shortfalls, etc.
    """
    if is_asm and is_overlap:
        active_cfg = ASM_OVERLAP_BLISS_CRITERIA_CONFIG
        slab_100_amount = 15000
        slab_120_amount = 20000
    elif is_asm:
        active_cfg = ASM_BLISS_CRITERIA_CONFIG
        slab_100_amount = 40000
        slab_120_amount = 50000
    else:
        active_cfg = BLISS_CRITERIA_CONFIG
        slab_100_amount = 30000
        slab_120_amount = 35000

    bliss_criteria_dict = {}
    for cfg in active_cfg:
        res = calculate_criterion(cfg, employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col=None, pos_code=pos_code, territory=territory)
        ach = res['achievement']
        if ach >= 120:
            slab = 120
            inc = cfg['slab_120']
            tier = '120%'
            qual = True
            remark = f"{cfg['remark_name']} Qualify With 120% Slab"
            req_text = f"{cfg['req_name']} Qualified"
        elif ach >= 100:
            slab = 100
            inc = cfg['slab_100']
            tier = '100%'
            qual = True
            remark = f"{cfg['remark_name']} Qualify With 100% Slab"
            req_text = f"{cfg['req_name']} Qualified"
        else:
            slab = 0
            inc = 0
            tier = 'Below 100%'
            qual = False
            remark = f"{cfg['remark_name']} Not Qualified"
            req_text = f"{cfg['req_name']} Not Qualified"

        res['status'] = f'Qualified ({tier})' if qual else 'Not Qualified'
        res['qualified'] = qual
        res['applicable_incentive'] = inc
        res['slab'] = slab
        res['tier'] = tier
        res['remark'] = remark
        res['req_text'] = req_text
        bliss_criteria_dict[cfg['key']] = res

    c_bl = bliss_criteria_dict['bliss_bottom_line']
    bliss_total_incentive = c_bl['applicable_incentive']

    bliss_payout_remarks = [
        {
            'name': cfg['remark_name'],
            'remark': bliss_criteria_dict[cfg['key']]['remark'],
            'slab': f"{bliss_criteria_dict[cfg['key']]['slab']}% Slab" if bliss_criteria_dict[cfg['key']]['slab'] else "Below 100%",
            'qualified': bliss_criteria_dict[cfg['key']]['qualified'],
            'incentive': bliss_criteria_dict[cfg['key']]['applicable_incentive']
        }
        for cfg in active_cfg
    ]

    t_bl, a_bl = c_bl.get('target', 0.0), c_bl.get('actual', 0.0)
    bliss_bottom_line_need = 0.0 if c_bl.get('qualified') else (max(t_bl - a_bl, 0.0) if t_bl > 0 else None)

    bliss_needs_map = {
        'bliss_bottom_line': bliss_bottom_line_need
    }

    bliss_unearned_needs = [n for n in bliss_needs_map.values() if n is not None and n > 0]
    bliss_overall_qualifying_need = min(bliss_unearned_needs) if bliss_unearned_needs else None

    for cfg in active_cfg:
        c_item = bliss_criteria_dict[cfg['key']]
        c_need = bliss_needs_map.get(cfg['key'])
        c_item['need'] = c_need
        if c_item['qualified']:
            c_item['need_text'] = "Requirement Met"
        else:
            c_item['need_text'] = f"Need: Rs. {c_need:,.0f} to Qualify" if c_need is not None else "Need: N/A to Qualify"

    bliss_qualification_requirements = [
        {
            'category': cfg['req_name'],
            'text': bliss_criteria_dict[cfg['key']]['req_text'],
            'qualified': bliss_criteria_dict[cfg['key']]['qualified'],
            'slab': f"{bliss_criteria_dict[cfg['key']]['slab']}%" if bliss_criteria_dict[cfg['key']]['slab'] else "None",
            'incentive': bliss_criteria_dict[cfg['key']]['applicable_incentive'],
            'need': bliss_needs_map.get(cfg['key'])
        }
        for cfg in active_cfg
    ]

    bliss_breakdown = [
        {
            'key': cfg['key'],
            'category': cfg['name'],
            'rule': f"{cfg['short_name']} Net Value >= threshold",
            'tier': bliss_criteria_dict[cfg['key']]['tier'],
            'amount': bliss_criteria_dict[cfg['key']]['applicable_incentive'],
            'qualified': bliss_criteria_dict[cfg['key']]['qualified']
        }
        for cfg in active_cfg
    ]

    bliss_qualified_count = sum(1 for b in bliss_breakdown if b['qualified'])
    bliss_final_status = "INCENTIVE QUALIFIED" if bliss_total_incentive > 0 else "INCENTIVE NOT QUALIFIED"
    bliss_qualify_label = "Qualify Incentive" if bliss_total_incentive > 0 else "Not Qualified"

    return {
        'bliss_criteria': list(bliss_criteria_dict.values()),
        'bliss_criteria_dict': bliss_criteria_dict,
        'bliss_breakdown': bliss_breakdown,
        'bliss_payout_remarks': bliss_payout_remarks,
        'bliss_qualification_requirements': bliss_qualification_requirements,
        'bliss_total_incentive': bliss_total_incentive,
        'bliss_bottom_line_incentive': bliss_total_incentive,
        'bliss_bottom_line_need': bliss_bottom_line_need,
        'bliss_overall_qualifying_need': bliss_overall_qualifying_need,
        'bliss_qualifying_sub': "Additional Net Value Required",
        'bliss_qualified_count': bliss_qualified_count,
        'bliss_qualified': bliss_total_incentive > 0,
        'bliss_final_status': bliss_final_status,
        'bliss_qualify_label': bliss_qualify_label,
        'bliss_tier': f"100% ({bliss_qualified_count}/1 Qualified)" if bliss_total_incentive == slab_100_amount else (f"120% ({bliss_qualified_count}/1 Qualified)" if bliss_total_incentive == slab_120_amount else "Not Qualified"),
        'is_asm': is_asm,
        'slab_100_amount': slab_100_amount,
        'slab_120_amount': slab_120_amount,
    }
