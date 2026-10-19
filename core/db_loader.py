"""PostgreSQL-backed data provider for the incentive engine.

The incentive evaluators still use the column names they were written for, but
all rows now come directly from the shared PostgreSQL database. No CSV, Excel,
pickle, or local cache is read by this module.
"""
from functools import lru_cache
from pathlib import Path
import sys
import threading

import pandas as pd
from psycopg2.pool import ThreadedConnectionPool


BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from performance_monitor import PoolMetrics, query_identifier, run_query


def _load_env(path: Path) -> dict:
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


ENV = {**_load_env(ROOT_DIR / ".env"), **_load_env(BASE_DIR / ".env")}
POOL = None
POOL_SLOTS = None
POOL_METRICS = None
POOL_ACQUIRE_TIMEOUT_SECONDS = 5
_POOL_LOCK = threading.Lock()


def _int_setting(name, default, minimum, maximum):
    try:
        value = int(ENV.get(name, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def configure_database_pool(pool, slots, metrics, acquire_timeout_seconds):
    """Use the parent FastAPI pool when this Flask app is mounted there."""
    global POOL, POOL_SLOTS, POOL_METRICS, POOL_ACQUIRE_TIMEOUT_SECONDS
    with _POOL_LOCK:
        previous = POOL
        POOL = pool
        POOL_SLOTS = slots
        POOL_METRICS = metrics
        POOL_ACQUIRE_TIMEOUT_SECONDS = acquire_timeout_seconds
        if previous is not None and previous is not pool:
            previous.closeall()


def _pool_bundle():
    """Lazily create a thread-safe pool only for standalone Flask execution."""
    global POOL, POOL_SLOTS, POOL_METRICS, POOL_ACQUIRE_TIMEOUT_SECONDS
    if POOL is None:
        with _POOL_LOCK:
            if POOL is None:
                minimum = _int_setting("DB_POOL_MIN", 1, 1, 20)
                maximum = _int_setting("DB_POOL_MAX", 5, minimum, 30)
                POOL_ACQUIRE_TIMEOUT_SECONDS = _int_setting(
                    "DB_POOL_ACQUIRE_TIMEOUT_SECONDS", 5, 1, 60,
                )
                statement_ms = _int_setting("DB_STATEMENT_TIMEOUT_MS", 15000, 1000, 300000)
                idle_ms = _int_setting("DB_IDLE_TRANSACTION_TIMEOUT_MS", 30000, 1000, 300000)
                POOL = ThreadedConnectionPool(
                    minimum, maximum,
                    host=ENV["DB_HOST"], port=int(ENV["DB_PORT"]), dbname=ENV["DB_NAME"],
                    user=ENV["DB_USER"], password=ENV["DB_PASSWORD"],
                    connect_timeout=_int_setting("DB_CONNECT_TIMEOUT_SECONDS", 5, 1, 60),
                    application_name="incentive-dashboard",
                    keepalives=1,
                    keepalives_idle=_int_setting("DB_KEEPALIVES_IDLE_SECONDS", 30, 10, 300),
                    keepalives_interval=_int_setting("DB_KEEPALIVES_INTERVAL_SECONDS", 10, 5, 120),
                    keepalives_count=_int_setting("DB_KEEPALIVES_COUNT", 5, 1, 10),
                    options=(f"-c statement_timeout={statement_ms} "
                             f"-c idle_in_transaction_session_timeout={idle_ms}"),
                )
                POOL_SLOTS = threading.BoundedSemaphore(maximum)
                POOL_METRICS = PoolMetrics(maximum)
    return POOL, POOL_SLOTS, POOL_METRICS, POOL_ACQUIRE_TIMEOUT_SECONDS


def _read_sql(sql: str, params=None) -> pd.DataFrame:
    query_id = query_identifier(sql)
    database_pool, slots, metrics, timeout = _pool_bundle()
    rows, columns = run_query(
        database_pool, sql, params or [], query_id, slots, timeout, metrics,
    )
    return pd.DataFrame.from_records(rows, columns=columns)


def _clean_text(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].where(df[col].notna(), "")
    return df


@lru_cache(maxsize=1)
def load_staff_df() -> pd.DataFrame:
    raw = _read_sql("SELECT * FROM staff_master")
    if raw.empty:
        return raw

    # Keep the legacy names expected by the incentive calculation modules.
    mapping = {
        "position_code": "Position_Code",
        "team_id": "Team_ID",
        "team_name": "Team_Name",
        "zone_id": "Zone_ID",
        "zone_name": "Zone_Name",
        "sub_zone": "Sub_Zone",
        "alias_zone": "ALIAS_Zone",
        "team_region_id": "Team_Region_ID",
        "region_name": "Region_Name",
        "alias_region": "ALIAS_Region",
        "province": "Province",
        "hawk_emp_id": "HAWK Emp_ID",
        "check_status": "Check",
        "sas_id": "SAS_ID",
        "sas_upload": "SAS Upload",
        "dept_territory_code": "Dept. Territory Code",
        "employee_position_code": "Position_Code.1",
        "employee_name": "Employe_Name",
        "base_town": "Base Town",
        "nature_type": "Nature Type",
        "payroll_type": "Payroll Type",
        "e_code": "E-CODE",
        "doj": "D.O.J",
        "desg_id": "Desg._ID",
        "designation_name": "Designation_Name",
        "level": "Level",
        "dept_id": "Dept._ID",
        "department_name": "Depatment_Name",
        "report_to_position_code": "Report_To_Position_Code",
        "report_to_name": "Report_To_Name",
        "base_name": "Base_Name",
        "actual_field_force": "Actual_Field_Force",
        "remarks": "Remarks",
    }
    staff = raw.rename(columns=mapping)
    return _clean_text(staff)


def _target_column_map() -> dict:
    return {
        "team": "Team",
        "team_channel_26_27": "Team Channel-26-27",
        "sub_teams": "Sub Teams",
        "zone": "Zone",
        "sub_zone": "Sub-Zone",
        "region": "Region",
        "dept_territory_code_2026_27": "Dept. Territory Code 2026-27",
        "position_code_2026_27": "Position Code 2026-27",
        "ff_name": "F.F Name",
        "base": "Base",
        "emp_no": "Emp. #",
        "desg": "Desg.",
        "sgp_grp": "SGP GRP",
        "type": "Type",
        "category": "Category",
        "group": "Group",
        "product_group": "Product Group",
        "product_group_on_master": "Product Group On Master",
        "mapping": "Mapping",
        "sas_code": "SAS Code",
        "product_no": "Product #",
        "prd_bu_sas": "PRD_BU_SAS",
    }


def _month_label(suffix: str) -> str:
    month, year = suffix.split("_")
    return f"{month.title()}-{year}"


def _rename_target_columns(target: pd.DataFrame) -> pd.DataFrame:
    target = target.rename(columns=_target_column_map())
    months = ("jul_26", "aug_26", "sep_26", "oct_26", "nov_26", "dec_26",
              "jan_27", "feb_27", "mar_27", "apr_27", "may_27", "jun_27")
    families = {
        "tgt_unit": "TGT Unit",
        "tgt_tp_value": "TGT TP Value",
        "tgt_add_disc_value": "TGT Add. Disc Value",
        "tgt_reg_disc_value": "TGT Reg. Disc Value",
        "tgt_net_w_reg": "TGT Net W/Reg.",
        "tgt_net_wo_reg": "TGT Net WO/Reg.",
        "tgt_cogs": "TGT COGS",
        "tgt_cyps": "TGT CYPs",
    }
    rename = {}
    for family, label in families.items():
        for suffix in months:
            source = f"{family}_{suffix}"
            if source in target.columns:
                rename[source] = f"{label} {_month_label(suffix)}"
    target = target.rename(columns=rename)
    return _clean_text(target)


@lru_cache(maxsize=1)
def load_datasets():
    """Return target, sales and staff-compatible frames from PostgreSQL."""
    staff = load_staff_df()
    target = _rename_target_columns(_read_sql("SELECT * FROM target_data"))

    # Filter at SQL level by fiscal year; product-group filtering below mirrors
    # the previous loader and keeps the incentive rules focused and fast.
    sales = _read_sql(
        "SELECT * FROM sales_data WHERE fiscal_year = %s",
        ["2026-27"],
    )
    if not sales.empty:
        sales = sales.rename(columns={c: c.upper() for c in sales.columns})
        if "EMPLOYEE_NAME" in sales.columns:
            sales["NAME"] = sales["EMPLOYEE_NAME"]
        if "FF_TERRITORY" not in sales.columns:
            sales["FF_TERRITORY"] = sales.get("TERRITORY", "")
        if "EMP. TYPE" not in sales.columns and "NATURE_TYPE" in sales.columns:
            sales["Emp. Type"] = sales["NATURE_TYPE"]
        if "D.O.J" not in sales.columns and "DOJ" in sales.columns:
            sales["D.O.J"] = sales["DOJ"]
        numeric_sales_columns = (
            "NET_QTY", "E_QTY", "NET_VALUE", "BONUS_VALUE", "DISCOUNTS",
            "FOC_DISCOUNT", "CYP", "TP_SALE_VALUE", "BONUS_DISCOUNT",
            "MNP_COMMISSION", "NET_WO_REG_DISC_VALUE", "NET_SALE_VALUE",
            "PRICE", "ORIGINAL_NET_VALUE_SALE_MONTHLY",
        )
        for column in numeric_sales_columns:
            if column in sales.columns:
                sales[column] = pd.to_numeric(
                    sales[column].astype(str).str.replace(",", "", regex=False),
                    errors="coerce",
                ).fillna(0.0)
        sales = _clean_text(sales)

    valid_prefixes = (
        "DO", "SATHI", "TOUCH", "ONE", "BLISS", "MAXI", "DEPO", "ECP",
        "IRON", "MULTI", "FEMI", "MISOTAL", "GREKIE", "NOVADOL", "ZINC",
        "OBSTETRIC", "CALCIUM", "ORS", "PROTECT", "ANTIFUNGAL",
    )
    if not sales.empty and "PRD_GRP" in sales.columns:
        sales_pharma = sales.get("TEAM", pd.Series("", index=sales.index)).astype(str).str.upper().str.contains("PHARM", na=False)
        mask = sales["PRD_GRP"].astype(str).str.upper().map(
            lambda value: any(value.startswith(prefix) for prefix in valid_prefixes)
        ) | sales_pharma
        sales = sales[mask].copy()

    if not target.empty and "Product Group" in target.columns:
        target_pharma = target.get("Team", pd.Series("", index=target.index)).astype(str).str.upper().str.contains("PHARM", na=False)
        mask = target["Product Group"].astype(str).str.upper().map(
            lambda value: any(value.startswith(prefix) for prefix in valid_prefixes)
        ) | target_pharma
        target = target[mask].copy()

    target_master_col = "Product Group On Master" if "Product Group On Master" in target.columns else None
    return target, sales, target_master_col


@lru_cache(maxsize=1)
def get_val_logic_mapping():
    staff = load_staff_df()
    mapping = {}
    if not staff.empty and "Position_Code" in staff.columns and "Nature Type" in staff.columns:
        for _, row in staff.iterrows():
            position = str(row.get("Position_Code", "")).strip().upper()
            value = str(row.get("Nature Type", "")).strip()
            if position and value and position not in mapping:
                mapping[position] = value
    return mapping


def get_target_columns(month, target_df):
    """Resolve monthly target columns using the existing incentive API."""
    month = str(month).strip()
    try:
        label = pd.to_datetime(month, format="%B,%y").strftime("%b-%y")
    except Exception:
        label = ""
    unit_col = f"TGT Unit {label}" if label and f"TGT Unit {label}" in target_df.columns else None
    net_col = f"TGT Net WO/Reg. {label}" if label and f"TGT Net WO/Reg. {label}" in target_df.columns else None
    tp_col = f"TGT TP Value {label}" if label and f"TGT TP Value {label}" in target_df.columns else None
    return net_col, unit_col, tp_col
