"""
RSM Evaluator Module
Contains evaluation logic for GSM Regional Sales Managers (RSMs)
based on the policy guidelines:
- C1: DO Team (Street) - 100% -> Rs. 20,000
- C2: TOUCH Team (Street) - 100% -> Rs. 20,000
- C3: Trade Bottom-Line - 100% -> Rs. 20,000
- C4: Wholesale Sathi 4s - 100% -> Rs. 20,000
- C5: Wholesale TOUCH - 100% -> Rs. 20,000
- C6: Condom Bottom-Line (Street + Trade + WS) - 100% -> Rs. 50,000
- C7: BLISS Bottom-Line - 100% -> Rs. 40,000 | 120% -> Rs. 50,000
"""
import pandas as pd
from core.config import RSM_CRITERIA_CONFIG, RSM_BLISS_CRITERIA_CONFIG


def evaluate_rsm_incentives(
    employee,
    month,
    rsm_street_tgt,
    rsm_street_sal,
    rsm_reg_tgt,
    rsm_reg_sal,
    t_net_col,
    val_col='NET_WO_REG_DISC_VALUE'
):
    """
    Evaluates all 7 qualifying criteria for an RSM.
    - rsm_street_tgt, rsm_street_sal: targets and sales aggregated across the RSM's underlying ASMs.
    - rsm_reg_tgt, rsm_reg_sal: regional targets and sales for Trade, Wholesale, and BLISS.
    """
    criteria = []
    criteria_dict = {}
    payout_remarks = []
    qualification_requirements = []
    breakdown = []

    # 1. C1: DO Team (Street)
    # Target and Sales of DO + SATHI in Street channel (FMCG CONDOM STREET)
    do_t_mask = (
        (rsm_street_tgt['Team Channel-26-27'].astype(str).str.strip().str.upper() == 'FMCG CONDOM STREET') &
        rsm_street_tgt['Product Group'].apply(lambda x: any(str(x).upper().startswith(p) for p in ['DO', 'SATHI']))
    ) if not rsm_street_tgt.empty and 'Product Group' in rsm_street_tgt.columns and 'Team Channel-26-27' in rsm_street_tgt.columns else pd.Series(False, index=rsm_street_tgt.index)

    do_s_mask = (
        (rsm_street_sal['TEAM_CHANNEL'].astype(str).str.strip().str.upper() == 'FMCG CONDOM STREET') &
        rsm_street_sal['PRD_GRP'].apply(lambda x: any(str(x).upper().startswith(p) for p in ['DO', 'SATHI']))
    ) if not rsm_street_sal.empty and 'PRD_GRP' in rsm_street_sal.columns and 'TEAM_CHANNEL' in rsm_street_sal.columns else pd.Series(False, index=rsm_street_sal.index)

    t_c1 = float(pd.to_numeric(rsm_street_tgt.loc[do_t_mask, t_net_col], errors='coerce').sum()) if t_net_col and t_net_col in rsm_street_tgt.columns else 0.0
    s_c1 = float(pd.to_numeric(rsm_street_sal.loc[do_s_mask, val_col], errors='coerce').sum()) if val_col and val_col in rsm_street_sal.columns else 0.0
    ach_c1 = (s_c1 / t_c1 * 100.0) if t_c1 > 0 else 0.0
    qual_c1 = (t_c1 > 0 and s_c1 >= t_c1)
    inc_c1 = 20000 if qual_c1 else 0
    shortfall_c1 = max(t_c1 - s_c1, 0.0) if not qual_c1 else 0.0

    c1_dict = {
        'id': 1,
        'key': 'rsm_do_street',
        'name': '100% Target vs Achievement of Do Team bottom-line Net Value (Street)',
        'short_name': 'DO Team (Street)',
        'target': t_c1,
        'actual': s_c1,
        'achievement': ach_c1,
        'qualified': qual_c1,
        'incentive': inc_c1,
        'applicable_incentive': inc_c1,
        'slab_name': '100% Slab' if qual_c1 else 'Not Qualified',
        'status': 'QUALIFIED' if qual_c1 else 'NOT QUALIFIED',
        'remark': 'DO Team Bottom-line Incentive Qualified' if qual_c1 else f"(Min.) NET Value = {round(shortfall_c1):,}/= fell short to Qualify DO Team Bottom-line",
        'need': shortfall_c1,
        'need_text': 'Requirement Met' if qual_c1 else f"Need: Rs. {shortfall_c1:,.0f} to Qualify",
        'policy_rule': '100% Target vs Achievement of Do Team bottom-line Net Value (Street) -> Rs. 20,000',
        'is_currency': True,
    }
    criteria.append(c1_dict)
    criteria_dict['rsm_do_street'] = c1_dict

    # 2. C2: TOUCH Team (Street)
    # Target and Sales of TOUCH + ONE in Street channel (FMCG CONDOM STREET)
    touch_t_mask = (
        (rsm_street_tgt['Team Channel-26-27'].astype(str).str.strip().str.upper() == 'FMCG CONDOM STREET') &
        rsm_street_tgt['Product Group'].apply(lambda x: any(str(x).upper().startswith(p) for p in ['TOUCH', 'ONE']))
    ) if not rsm_street_tgt.empty and 'Product Group' in rsm_street_tgt.columns and 'Team Channel-26-27' in rsm_street_tgt.columns else pd.Series(False, index=rsm_street_tgt.index)

    touch_s_mask = (
        (rsm_street_sal['TEAM_CHANNEL'].astype(str).str.strip().str.upper() == 'FMCG CONDOM STREET') &
        rsm_street_sal['PRD_GRP'].apply(lambda x: any(str(x).upper().startswith(p) for p in ['TOUCH', 'ONE']))
    ) if not rsm_street_sal.empty and 'PRD_GRP' in rsm_street_sal.columns and 'TEAM_CHANNEL' in rsm_street_sal.columns else pd.Series(False, index=rsm_street_sal.index)

    t_c2 = float(pd.to_numeric(rsm_street_tgt.loc[touch_t_mask, t_net_col], errors='coerce').sum()) if t_net_col and t_net_col in rsm_street_tgt.columns else 0.0
    s_c2 = float(pd.to_numeric(rsm_street_sal.loc[touch_s_mask, val_col], errors='coerce').sum()) if val_col and val_col in rsm_street_sal.columns else 0.0
    ach_c2 = (s_c2 / t_c2 * 100.0) if t_c2 > 0 else 0.0
    qual_c2 = (t_c2 > 0 and s_c2 >= t_c2)
    inc_c2 = 20000 if qual_c2 else 0
    shortfall_c2 = max(t_c2 - s_c2, 0.0) if not qual_c2 else 0.0

    c2_dict = {
        'id': 2,
        'key': 'rsm_touch_street',
        'name': '100% Target vs Achievement of Touch Team bottom-line Net Value (Street)',
        'short_name': 'TOUCH Team (Street)',
        'target': t_c2,
        'actual': s_c2,
        'achievement': ach_c2,
        'qualified': qual_c2,
        'incentive': inc_c2,
        'applicable_incentive': inc_c2,
        'slab_name': '100% Slab' if qual_c2 else 'Not Qualified',
        'status': 'QUALIFIED' if qual_c2 else 'NOT QUALIFIED',
        'remark': 'TOUCH Team Bottom-line Incentive Qualified' if qual_c2 else f"(Min.) NET Value = {round(shortfall_c2):,}/= fell short to Qualify TOUCH Team Bottom-line",
        'need': shortfall_c2,
        'need_text': 'Requirement Met' if qual_c2 else f"Need: Rs. {shortfall_c2:,.0f} to Qualify",
        'policy_rule': '100% Target vs Achievement of Touch Team bottom-line Net Value (Street) -> Rs. 20,000',
        'is_currency': True,
    }
    criteria.append(c2_dict)
    criteria_dict['rsm_touch_street'] = c2_dict

    # 3. C3: Trade Bottom-Line
    t_c3 = float(pd.to_numeric(rsm_reg_tgt[rsm_reg_tgt['Team Channel-26-27'].astype(str).str.strip().str.upper() == 'FMCG TRADE'][t_net_col], errors='coerce').sum()) if not rsm_reg_tgt.empty and 'Team Channel-26-27' in rsm_reg_tgt.columns and t_net_col in rsm_reg_tgt.columns else 0.0
    s_c3 = float(pd.to_numeric(rsm_reg_sal[rsm_reg_sal['TEAM_CHANNEL'].astype(str).str.strip().str.upper() == 'FMCG TRADE'][val_col], errors='coerce').sum()) if not rsm_reg_sal.empty and 'TEAM_CHANNEL' in rsm_reg_sal.columns and val_col in rsm_reg_sal.columns else 0.0
    ach_c3 = (s_c3 / t_c3 * 100.0) if t_c3 > 0 else 0.0
    qual_c3 = (t_c3 > 0 and s_c3 >= t_c3)
    inc_c3 = 20000 if qual_c3 else 0
    shortfall_c3 = max(t_c3 - s_c3, 0.0) if not qual_c3 else 0.0

    c3_dict = {
        'id': 3,
        'key': 'rsm_trade',
        'name': '100% Target vs Achievement of Trade Bottom-line Value',
        'short_name': 'Trade Bottom-Line',
        'target': t_c3,
        'actual': s_c3,
        'achievement': ach_c3,
        'qualified': qual_c3,
        'incentive': inc_c3,
        'applicable_incentive': inc_c3,
        'slab_name': '100% Slab' if qual_c3 else 'Not Qualified',
        'status': 'QUALIFIED' if qual_c3 else 'NOT QUALIFIED',
        'remark': 'TRADE Bottom-line Incentive Qualified' if qual_c3 else f"(Min.) NET Value = {round(shortfall_c3):,}/= fell short to Qualify TRADE Bottom-line",
        'need': shortfall_c3,
        'need_text': 'Requirement Met' if qual_c3 else f"Need: Rs. {shortfall_c3:,.0f} to Qualify",
        'policy_rule': '100% Target vs Achievement of Trade Bottom-line Value -> Rs. 20,000',
        'is_currency': True,
    }
    criteria.append(c3_dict)
    criteria_dict['rsm_trade'] = c3_dict

    # 4. C4: Wholesale Sathi 4s
    ws_sathi_t = rsm_reg_tgt[(rsm_reg_tgt['Team Channel-26-27'].astype(str).str.strip().str.upper() == 'FMCG WHOLESALE') & (rsm_reg_tgt['Product Group'].astype(str).str.upper().str.startswith('SATHI'))] if not rsm_reg_tgt.empty and 'Team Channel-26-27' in rsm_reg_tgt.columns and 'Product Group' in rsm_reg_tgt.columns else pd.DataFrame()
    ws_sathi_s = rsm_reg_sal[(rsm_reg_sal['TEAM_CHANNEL'].astype(str).str.strip().str.upper() == 'FMCG WHOLESALE') & (rsm_reg_sal['PRD_GRP'].astype(str).str.upper().str.startswith('SATHI'))] if not rsm_reg_sal.empty and 'TEAM_CHANNEL' in rsm_reg_sal.columns and 'PRD_GRP' in rsm_reg_sal.columns else pd.DataFrame()
    t_c4 = float(pd.to_numeric(ws_sathi_t[t_net_col], errors='coerce').sum()) if not ws_sathi_t.empty and t_net_col in ws_sathi_t.columns else 0.0
    s_c4 = float(pd.to_numeric(ws_sathi_s[val_col], errors='coerce').sum()) if not ws_sathi_s.empty and val_col in ws_sathi_s.columns else 0.0
    ach_c4 = (s_c4 / t_c4 * 100.0) if t_c4 > 0 else 0.0
    qual_c4 = (t_c4 > 0 and s_c4 >= t_c4)
    inc_c4 = 20000 if qual_c4 else 0
    shortfall_c4 = max(t_c4 - s_c4, 0.0) if not qual_c4 else 0.0

    c4_dict = {
        'id': 4,
        'key': 'rsm_ws_sathi',
        'name': 'Target vs Achievement of Wholesale - Sathi 4s Bottom-line Value',
        'short_name': 'WS Sathi 4s Bottom-Line',
        'target': t_c4,
        'actual': s_c4,
        'achievement': ach_c4,
        'qualified': qual_c4,
        'incentive': inc_c4,
        'applicable_incentive': inc_c4,
        'slab_name': '100% Slab' if qual_c4 else 'Not Qualified',
        'status': 'QUALIFIED' if qual_c4 else 'NOT QUALIFIED',
        'remark': 'WS SATHI 4s Bottom-line Incentive Qualified' if qual_c4 else f"(Min.) NET Value = {round(shortfall_c4):,}/= fell short to Qualify WS SATHI 4s Bottom-line",
        'need': shortfall_c4,
        'need_text': 'Requirement Met' if qual_c4 else f"Need: Rs. {shortfall_c4:,.0f} to Qualify",
        'policy_rule': 'Target vs Achievement of Wholesale - Sathi 4s Bottom-line Value -> Rs. 20,000',
        'is_currency': True,
    }
    criteria.append(c4_dict)
    criteria_dict['rsm_ws_sathi'] = c4_dict

    # 5. C5: Wholesale TOUCH
    ws_touch_t = rsm_reg_tgt[(rsm_reg_tgt['Team Channel-26-27'].astype(str).str.strip().str.upper() == 'FMCG WHOLESALE') & (rsm_reg_tgt['Product Group'].astype(str).str.upper().str.startswith('TOUCH'))] if not rsm_reg_tgt.empty and 'Team Channel-26-27' in rsm_reg_tgt.columns and 'Product Group' in rsm_reg_tgt.columns else pd.DataFrame()
    ws_touch_s = rsm_reg_sal[(rsm_reg_sal['TEAM_CHANNEL'].astype(str).str.strip().str.upper() == 'FMCG WHOLESALE') & (rsm_reg_sal['PRD_GRP'].astype(str).str.upper().str.startswith('TOUCH'))] if not rsm_reg_sal.empty and 'TEAM_CHANNEL' in rsm_reg_sal.columns and 'PRD_GRP' in rsm_reg_sal.columns else pd.DataFrame()
    t_c5 = float(pd.to_numeric(ws_touch_t[t_net_col], errors='coerce').sum()) if not ws_touch_t.empty and t_net_col in ws_touch_t.columns else 0.0
    s_c5 = float(pd.to_numeric(ws_touch_s[val_col], errors='coerce').sum()) if not ws_touch_s.empty and val_col in ws_touch_s.columns else 0.0
    ach_c5 = (s_c5 / t_c5 * 100.0) if t_c5 > 0 else 0.0
    qual_c5 = (t_c5 > 0 and s_c5 >= t_c5)
    inc_c5 = 20000 if qual_c5 else 0
    shortfall_c5 = max(t_c5 - s_c5, 0.0) if not qual_c5 else 0.0

    c5_dict = {
        'id': 5,
        'key': 'rsm_ws_touch',
        'name': 'Target vs Achievement of Wholesale - TOUCH Bottom-line Value',
        'short_name': 'WS TOUCH Bottom-Line',
        'target': t_c5,
        'actual': s_c5,
        'achievement': ach_c5,
        'qualified': qual_c5,
        'incentive': inc_c5,
        'applicable_incentive': inc_c5,
        'slab_name': '100% Slab' if qual_c5 else 'Not Qualified',
        'status': 'QUALIFIED' if qual_c5 else 'NOT QUALIFIED',
        'remark': 'WS TOUCH Bottom-line Incentive Qualified' if qual_c5 else f"(Min.) NET Value = {round(shortfall_c5):,}/= fell short to Qualify WS TOUCH Bottom-line",
        'need': shortfall_c5,
        'need_text': 'Requirement Met' if qual_c5 else f"Need: Rs. {shortfall_c5:,.0f} to Qualify",
        'policy_rule': 'Target vs Achievement of Wholesale - TOUCH Bottom-line Value -> Rs. 20,000',
        'is_currency': True,
    }
    criteria.append(c5_dict)
    criteria_dict['rsm_ws_touch'] = c5_dict

    # 6. C6: Condom Bottom-Line (Street + Trade + Wholesale)
    t_c6 = t_c1 + t_c2 + t_c3 + t_c4 + t_c5
    s_c6 = s_c1 + s_c2 + s_c3 + s_c4 + s_c5
    ach_c6 = (s_c6 / t_c6 * 100.0) if t_c6 > 0 else 0.0
    qual_c6 = (t_c6 > 0 and s_c6 >= t_c6)
    inc_c6 = 50000 if qual_c6 else 0
    shortfall_c6 = max(t_c6 - s_c6, 0.0) if not qual_c6 else 0.0

    c6_dict = {
        'id': 6,
        'key': 'rsm_condom_bottom_line',
        'name': '100% of Target vs Achievement of Bottom-line Value (Street + Trade + Wholesale)',
        'short_name': 'Condom Bottom-Line',
        'target': t_c6,
        'actual': s_c6,
        'achievement': ach_c6,
        'qualified': qual_c6,
        'incentive': inc_c6,
        'applicable_incentive': inc_c6,
        'slab_name': '100% Slab' if qual_c6 else 'Not Qualified',
        'status': 'QUALIFIED' if qual_c6 else 'NOT QUALIFIED',
        'remark': 'RSM CONDOM Bottom-line Incentive Qualified' if qual_c6 else f"(Min.) NET Value = {round(shortfall_c6):,}/= fell short to Qualify RSM Condom Bottom-line",
        'need': shortfall_c6,
        'need_text': 'Requirement Met' if qual_c6 else f"Need: Rs. {shortfall_c6:,.0f} to Qualify",
        'policy_rule': '100% of Target vs Achievement of Bottom-line Value (Street + Trade + Wholesale) -> Rs. 50,000',
        'is_currency': True,
    }
    criteria.append(c6_dict)
    criteria_dict['rsm_condom_bottom_line'] = c6_dict

    # 7. C7: BLISS Bottom-Line
    t_c7 = float(pd.to_numeric(rsm_reg_tgt[rsm_reg_tgt['Team Channel-26-27'].astype(str).str.strip().str.upper() == 'FMCG BLISS'][t_net_col], errors='coerce').sum()) if not rsm_reg_tgt.empty and 'Team Channel-26-27' in rsm_reg_tgt.columns and t_net_col in rsm_reg_tgt.columns else 0.0
    s_c7 = float(pd.to_numeric(rsm_reg_sal[rsm_reg_sal['TEAM_CHANNEL'].astype(str).str.strip().str.upper() == 'FMCG BLISS'][val_col], errors='coerce').sum()) if not rsm_reg_sal.empty and 'TEAM_CHANNEL' in rsm_reg_sal.columns and val_col in rsm_reg_sal.columns else 0.0
    ach_c7 = (s_c7 / t_c7 * 100.0) if t_c7 > 0 else 0.0
    qual_c7 = (t_c7 > 0 and s_c7 >= t_c7)
    if ach_c7 >= 120.0:
        inc_c7 = 50000
        slab_c7 = "120% Slab"
    elif ach_c7 >= 100.0:
        inc_c7 = 40000
        slab_c7 = "100% Slab"
    else:
        inc_c7 = 0
        slab_c7 = "Not Qualified"
    shortfall_c7 = max(t_c7 - s_c7, 0.0) if not qual_c7 else 0.0

    c7_dict = {
        'id': 7,
        'key': 'rsm_bliss_bottom_line',
        'name': 'Target vs Achievement of Bottom-Line Net Value',
        'short_name': 'BLISS Bottom-Line',
        'target': t_c7,
        'actual': s_c7,
        'achievement': ach_c7,
        'qualified': qual_c7,
        'incentive': inc_c7,
        'applicable_incentive': inc_c7,
        'slab_name': slab_c7,
        'status': 'QUALIFIED' if qual_c7 else 'NOT QUALIFIED',
        'remark': f"RSM BLISS Bottom-line Incentive Qualified ({slab_c7})" if qual_c7 else f"(Min.) NET Value = {round(shortfall_c7):,}/= fell short to Qualify RSM BLISS Bottom-line",
        'need': shortfall_c7,
        'need_text': 'Requirement Met' if qual_c7 else f"Need: Rs. {shortfall_c7:,.0f} to Qualify",
        'policy_rule': 'Target vs Achievement of Bottom-Line Net Value: 100% -> Rs. 40,000 | 120% -> Rs. 50,000',
        'is_currency': True,
    }
    criteria.append(c7_dict)
    criteria_dict['rsm_bliss_bottom_line'] = c7_dict

    # Build remarks and requirements
    for c in criteria:
        payout_remarks.append(c['remark'])
        qualification_requirements.append(c['need_text'])
        breakdown.append({
            'name': c['name'],
            'target': c['target'],
            'actual': c['actual'],
            'achievement': c['achievement'],
            'qualified': c['qualified'],
            'incentive': c['incentive'],
            'status': c['status'],
            'is_currency': c['is_currency'],
        })

    qualified_count = sum(1 for c in criteria if c['qualified'])
    total_core_incentive = sum(c['incentive'] for c in criteria)
    is_qualified = (total_core_incentive > 0)

    return {
        'rsm_criteria': criteria,
        'rsm_criteria_dict': criteria_dict,
        'rsm_breakdown': breakdown,
        'rsm_payout_remarks': payout_remarks,
        'rsm_qualification_requirements': qualification_requirements,
        'rsm_core_incentive': total_core_incentive,
        'rsm_qualified_count': qualified_count,
        'rsm_total_rules': 7,
        'rsm_qualified': is_qualified,
    }
