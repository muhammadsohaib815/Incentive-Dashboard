"""
TOUCH Team Incentive Evaluator Module
Evaluates the 4 qualifying criteria for TOUCH Team SPOs and ASMs.
"""
from core.config import TOUCH_CRITERIA_CONFIG, ASM_TOUCH_CRITERIA_CONFIG
from core.evaluators.base import calculate_criterion


def evaluate_touch_incentives(employee, month, target_df, sales_df, target_master_col, t_net_col, pos_code=None, territory=None, is_asm=False):
    """
    Full TOUCH Team incentive evaluation (4 Criteria, 4 Incentive Slabs).
    Supports both TOUCH Team SPOs and TOUCH Team ASMs (GSM ASMs).
    Returns all criteria dicts, breakdowns, payout remarks, shortfalls, etc.
    """
    active_cfg = ASM_TOUCH_CRITERIA_CONFIG if is_asm else TOUCH_CRITERIA_CONFIG
    touch_criteria_dict = {}
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
        touch_criteria_dict[cfg['key']] = res

    touch_delay_inc = touch_criteria_dict['touch_delay_mix']['applicable_incentive']
    touch_classic_inc = touch_criteria_dict['touch_classic_group']['applicable_incentive']
    touch_one_inc = touch_criteria_dict['one_brand']['applicable_incentive']
    touch_comb_inc = touch_criteria_dict['touch_one_bottom_line']['applicable_incentive']

    touch_total_incentive = touch_delay_inc + touch_classic_inc + touch_one_inc + touch_comb_inc

    touch_payout_remarks = [
        {
            'name': cfg['remark_name'],
            'remark': touch_criteria_dict[cfg['key']]['remark'],
            'slab': f"{touch_criteria_dict[cfg['key']]['slab']}% Slab" if touch_criteria_dict[cfg['key']]['slab'] else "Below 100%",
            'qualified': touch_criteria_dict[cfg['key']]['qualified'],
            'incentive': touch_criteria_dict[cfg['key']]['applicable_incentive']
        }
        for cfg in active_cfg
    ]

    c_td = touch_criteria_dict['touch_delay_mix']
    t_td, a_td = c_td.get('target', 0.0), c_td.get('actual', 0.0)
    touch_delay_need = 0.0 if c_td.get('qualified') else (max(t_td - a_td, 0.0) if t_td > 0 else None)

    c_tc = touch_criteria_dict['touch_classic_group']
    t_tc, a_tc = c_tc.get('target', 0.0), c_tc.get('actual', 0.0)
    touch_classic_need = 0.0 if c_tc.get('qualified') else (max(t_tc - a_tc, 0.0) if t_tc > 0 else None)

    c_to = touch_criteria_dict['one_brand']
    t_to, a_to = c_to.get('target', 0.0), c_to.get('actual', 0.0)
    touch_one_need = 0.0 if c_to.get('qualified') else (max(t_to - a_to, 0.0) if t_to > 0 else None)

    c_tcomb = touch_criteria_dict['touch_one_bottom_line']
    t_tcomb, a_tcomb = c_tcomb.get('target', 0.0), c_tcomb.get('actual', 0.0)
    touch_comb_need = 0.0 if c_tcomb.get('qualified') else (max(t_tcomb - a_tcomb, 0.0) if t_tcomb > 0 else None)

    touch_needs_map = {
        'touch_delay_mix': touch_delay_need,
        'touch_classic_group': touch_classic_need,
        'one_brand': touch_one_need,
        'touch_one_bottom_line': touch_comb_need
    }

    touch_unearned_needs = [n for n in touch_needs_map.values() if n is not None and n > 0]
    touch_overall_qualifying_need = min(touch_unearned_needs) if touch_unearned_needs else None

    for cfg in active_cfg:
        c_item = touch_criteria_dict[cfg['key']]
        c_need = touch_needs_map.get(cfg['key'])
        c_item['need'] = c_need
        if c_item['qualified']:
            c_item['need_text'] = "Requirement Met"
        else:
            c_item['need_text'] = f"Need: Rs. {c_need:,.0f} to Qualify" if c_need is not None else "Need: N/A to Qualify"

    touch_qualification_requirements = [
        {
            'category': cfg['req_name'],
            'text': touch_criteria_dict[cfg['key']]['req_text'],
            'qualified': touch_criteria_dict[cfg['key']]['qualified'],
            'slab': f"{touch_criteria_dict[cfg['key']]['slab']}%" if touch_criteria_dict[cfg['key']]['slab'] else "None",
            'incentive': touch_criteria_dict[cfg['key']]['applicable_incentive'],
            'need': touch_needs_map.get(cfg['key'])
        }
        for cfg in active_cfg
    ]

    touch_breakdown = [
        {
            'key': cfg['key'],
            'category': cfg['name'],
            'rule': f"{cfg['short_name']} Net Value >= threshold",
            'tier': touch_criteria_dict[cfg['key']]['tier'],
            'amount': touch_criteria_dict[cfg['key']]['applicable_incentive'],
            'qualified': touch_criteria_dict[cfg['key']]['qualified']
        }
        for cfg in active_cfg
    ]

    touch_qualified_count = sum(1 for b in touch_breakdown if b['qualified'])
    touch_final_status = "INCENTIVE QUALIFIED" if touch_total_incentive > 0 else "INCENTIVE NOT QUALIFIED"
    touch_qualify_label = "Qualify Incentive" if touch_total_incentive > 0 else "Not Qualified"

    return {
        'touch_criteria': list(touch_criteria_dict.values()),
        'touch_criteria_dict': touch_criteria_dict,
        'touch_breakdown': touch_breakdown,
        'touch_payout_remarks': touch_payout_remarks,
        'touch_qualification_requirements': touch_qualification_requirements,
        'touch_total_incentive': touch_total_incentive,
        'touch_delay_incentive': touch_delay_inc,
        'touch_classic_incentive': touch_classic_inc,
        'touch_one_incentive': touch_one_inc,
        'touch_combined_incentive': touch_comb_inc,
        'touch_delay_need': touch_delay_need,
        'touch_classic_need': touch_classic_need,
        'touch_one_need': touch_one_need,
        'touch_comb_need': touch_comb_need,
        'touch_overall_qualifying_need': touch_overall_qualifying_need,
        'touch_qualifying_sub': "Additional Net Value Required",
        'touch_qualified_count': touch_qualified_count,
        'touch_qualified': touch_total_incentive > 0,
        'touch_final_status': touch_final_status,
        'touch_qualify_label': touch_qualify_label,
        'touch_tier': f"{touch_qualified_count} of 4 Qualified" if touch_total_incentive > 0 else "Not Qualified",
    }
