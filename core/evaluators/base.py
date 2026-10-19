"""
Base Evaluator Functions
Universal calculation helpers for SPO, ASM, TE, and RSM criteria.
"""
import pandas as pd


def calculate_criterion(cfg, employee, month, target_df, sales_df, target_master_col, t_net_col, t_unit_col=None, t_tp_col=None, pos_code=None, territory=None):
    """
    Generic calculation function for any DO, TOUCH, OVERLAPPING, or TE criterion.
    Supports filtering by pos_code and territory to differentiate duplicate employee names.
    """
    if cfg.get('target_type') == 'unit' and t_unit_col:
        target_col = t_unit_col
    elif cfg.get('target_type') == 'tp' and t_tp_col:
        target_col = t_tp_col
    else:
        target_col = t_net_col
    clean_groups = [g.strip().upper() for g in cfg['groups']]

    # Determine metric column from sales_df
    metric_col = cfg.get('metric', 'NET_SALE_VALUE')
    if cfg.get('target_type') == 'unit':
        metric_col = 'E_QTY' if 'E_QTY' in sales_df.columns else ('NET_QTY' if 'NET_QTY' in sales_df.columns else metric_col)
    elif cfg.get('target_type') == 'net' and 'NET_WO_REG_DISC_VALUE' in sales_df.columns:
        metric_col = 'NET_WO_REG_DISC_VALUE'

    # 1. Actual from sales_df
    sales_prd_mask = sales_df['PRD_GRP'].apply(lambda x: any(str(x).upper().startswith(p) for p in cfg['prd_prefix']))
    
    if pos_code and 'POSITION_CODE' in sales_df.columns:
        emp_sales_mask = (sales_df['POSITION_CODE'].astype(str).str.strip().str.upper() == str(pos_code).strip().upper())
    elif territory and 'FF_TERRITORY' in sales_df.columns:
        emp_sales_mask = (
            (sales_df['NAME'].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
            (sales_df['FF_TERRITORY'].astype(str).str.strip().str.upper() == str(territory).strip().upper())
        )
    else:
        emp_sales_mask = (sales_df['NAME'].astype(str).str.strip().str.lower() == str(employee).strip().lower())

    sales_mask = (
        sales_prd_mask &
        emp_sales_mask &
        (sales_df['GROUP_ON'].str.upper().isin(clean_groups)) &
        (sales_df['REPORTING_MONTH'] == month)
    )
    actual = float(sales_df.loc[sales_mask, metric_col].sum()) if not sales_df.empty and metric_col in sales_df.columns else 0.0

    # 2. Target from target_df
    target_prd_mask = target_df['Product Group'].apply(lambda x: any(str(x).upper().startswith(p) for p in cfg['prd_prefix']))
    
    tgt_pos_col = None
    tgt_terr_col = None
    if not target_df.empty:
        for c in target_df.columns:
            c_str = str(c).lower().strip()
            if 'position code' in c_str or 'position_code' in c_str:
                tgt_pos_col = c
            if 'dept. territory code' in c_str or 'territory code' in c_str:
                tgt_terr_col = c

    if pos_code and tgt_pos_col and tgt_pos_col in target_df.columns:
        emp_tgt_mask = (target_df[tgt_pos_col].astype(str).str.strip().str.upper() == str(pos_code).strip().upper())
    elif territory and tgt_terr_col and tgt_terr_col in target_df.columns:
        emp_tgt_mask = (
            (target_df['F.F Name'].astype(str).str.strip().str.lower() == str(employee).strip().lower()) &
            (target_df[tgt_terr_col].astype(str).str.strip().str.upper() == str(territory).strip().upper())
        )
    else:
        emp_tgt_mask = (target_df['F.F Name'].astype(str).str.strip().str.lower() == str(employee).strip().lower())

    target_mask = (
        target_prd_mask &
        emp_tgt_mask &
        (target_df[target_master_col].str.upper().isin(clean_groups))
    )
    target = float(target_df.loc[target_mask, target_col].sum()) if not target_df.empty and target_col and target_col in target_df.columns else 0.0

    achievement = (actual / target * 100.0) if target > 0 else 0.0

    return {
        'id': cfg['id'],
        'key': cfg['key'],
        'name': cfg['name'],
        'short_name': cfg['short_name'],
        'groups': clean_groups,
        'metric': cfg['metric'],
        'actual': actual,
        'target': target,
        'achievement': achievement,
        'is_currency': cfg['is_currency']
    }
