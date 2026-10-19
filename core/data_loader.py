"""
Data Loader Module
Manages caching and loading of Targets, Sales, and Staff Master Excel/CSV datasets.
"""
from pathlib import Path
import functools
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent


def find_file(filename):
    """
    Search for data files across common project paths.
    """
    for base in [
        BASE_DIR / "data",
        BASE_DIR,
        Path(r"C:\Users\InternMIS\Desktop\Sohaib\AI Sales Intelligence Platform\data_csv"),
        Path(r"C:\Users\InternMIS\Desktop\Sohaib\data"),
        BASE_DIR / "scripts",
        Path.cwd()
    ]:
        try:
            p1 = base / filename
            if p1.exists() and (p1.stat().st_size > 1000000 or not str(filename).endswith('.csv')):
                return p1
            p2 = base / "data" / filename
            if p2.exists() and (p2.stat().st_size > 1000000 or not str(filename).endswith('.csv')):
                return p2
            if p1.exists():
                return p1
            if p2.exists():
                return p2
        except Exception:
            continue
    return BASE_DIR / "data" / filename


STAFF_FILE = find_file("GSM Field Force Master Staff List 2026-27.xlsx")
TARGET_FILE = find_file("F.F & Team wise National Targets 2026-27.xlsx")
SALES_FILE = find_file("GSM Sales Data YTD 2026-27 till Aug-26.xlsx")
TARGET_SHEET = "National Targets 2026-27"
STAFF_SHEET = "GSM F.F Master 2026-27"
SALES_SHEET = "GSM YTD Sales 2026-27"
SALES_CACHE_FILE = BASE_DIR / "data" / ".cache_sales_ytd.pkl"
TARGET_CACHE_FILE = BASE_DIR / "data" / ".cache_target.pkl"
STAFF_CACHE_FILE = BASE_DIR / "data" / ".cache_staff.pkl"


@functools.lru_cache(maxsize=1)
def load_staff_df():
    """Load Master Staff List from GSM Field Force Master Staff List 2026-27.xlsx."""
    if STAFF_CACHE_FILE.exists() and STAFF_FILE.exists() and STAFF_CACHE_FILE.stat().st_mtime >= STAFF_FILE.stat().st_mtime:
        try:
            return pd.read_pickle(STAFF_CACHE_FILE)
        except Exception:
            pass

    if STAFF_FILE.exists():
        try:
            df = pd.read_excel(STAFF_FILE, sheet_name=STAFF_SHEET)
            df = df[df["Position_Code"].notna() & df["Employe_Name"].notna()].copy()
            df.columns = [str(c).strip() for c in df.columns]
            try:
                df.to_pickle(STAFF_CACHE_FILE)
            except Exception:
                pass
            return df
        except Exception as e:
            print(f"Error loading staff master excel: {e}")
    return pd.DataFrame()


@functools.lru_cache(maxsize=1)
def get_val_logic_mapping():
    """Map Position_Code -> Nature Type / Emp. Type using Master Staff List."""
    mapping = {}
    staff_df = load_staff_df()
    if not staff_df.empty and 'Position_Code' in staff_df.columns and 'Nature Type' in staff_df.columns:
        for _, row in staff_df.iterrows():
            pos = str(row['Position_Code']).strip().upper()
            etype = str(row['Nature Type']).strip()
            if pos and pos != 'NAN' and etype and etype != 'NAN' and pos not in mapping:
                mapping[pos] = etype
    return mapping


@functools.lru_cache(maxsize=1)
def load_datasets():
    """
    Loads target and sales datasets, filtered for relevant product groups:
    DO, SATHI, TOUCH, ONE, BLISS, MAXI, and PHARMACEUTICAL.
    """
    target_df = pd.DataFrame()
    sales_df = pd.DataFrame()

    if TARGET_CACHE_FILE.exists() and TARGET_FILE.exists() and TARGET_CACHE_FILE.stat().st_mtime >= TARGET_FILE.stat().st_mtime:
        try:
            target_df = pd.read_pickle(TARGET_CACHE_FILE)
        except Exception:
            target_df = pd.DataFrame()

    if target_df.empty and TARGET_FILE.exists():
        try:
            target_df = pd.read_excel(
                TARGET_FILE,
                header=2,
                sheet_name=TARGET_SHEET
            )
            target_df.columns = [str(c).strip() for c in target_df.columns]
            try:
                target_df.to_pickle(TARGET_CACHE_FILE)
            except Exception:
                pass
        except Exception as e:
            print(f"Error loading target excel: {e}")

    # 1. Attempt ultra-fast load from pre-built pickle cache
    if SALES_CACHE_FILE.exists() and SALES_FILE.exists() and SALES_CACHE_FILE.stat().st_mtime >= SALES_FILE.stat().st_mtime:
        try:
            sales_df = pd.read_pickle(SALES_CACHE_FILE)
        except Exception as e:
            print(f"Error reading sales cache: {e}")
            sales_df = pd.DataFrame()

    # 2. If not cached, load from Excel / CSV and enrich with Staff metadata
    if sales_df.empty and SALES_FILE.exists():
        try:
            if str(SALES_FILE).lower().endswith(('.xlsx', '.xls')):
                sales_df = pd.read_excel(SALES_FILE, sheet_name=SALES_SHEET)
            else:
                sales_df = pd.read_csv(SALES_FILE, encoding="latin1", low_memory=False)
            sales_df.columns = [str(c).strip() for c in sales_df.columns]

            # Enrich sales_df with staff metadata (NAME, Emp. Type, D.O.J) from Master Staff List
            staff_df = load_staff_df()
            if not staff_df.empty and "Position_Code" in staff_df.columns:
                p_code = staff_df["Position_Code"].astype(str).str.strip().str.upper()
                if "NAME" not in sales_df.columns and "Employe_Name" in staff_df.columns:
                    name_map = dict(zip(p_code, staff_df["Employe_Name"].astype(str).str.strip()))
                    sales_df["NAME"] = sales_df["POSITION_CODE"].astype(str).str.strip().str.upper().map(name_map).fillna("")
                if "Emp. Type" not in sales_df.columns and "Nature Type" in staff_df.columns:
                    etype_map = dict(zip(p_code, staff_df["Nature Type"].astype(str).str.strip()))
                    sales_df["Emp. Type"] = sales_df["POSITION_CODE"].astype(str).str.strip().str.upper().map(etype_map).fillna("")
                if "D.O.J" not in sales_df.columns and "D.O.J" in staff_df.columns:
                    doj_map = dict(zip(p_code, staff_df["D.O.J"].astype(str).str.strip()))
                    sales_df["D.O.J"] = sales_df["POSITION_CODE"].astype(str).str.strip().str.upper().map(doj_map).fillna("")

            # Persist cache for fast subsequent application boots
            try:
                sales_df.to_pickle(SALES_CACHE_FILE)
            except Exception as ce:
                print(f"Notice: Could not write sales cache: {ce}")
        except Exception as e:
            print(f"Error loading sales data: {e}")

    # Find master group column in target_df
    target_master_col = None
    if not target_df.empty:
        for col in target_df.columns:
            if "Product Group On" in col:
                target_master_col = col
                break

    # Filter to DO, SATHI, TOUCH, ONE, BLISS, MAXI, and PHARMACEUTICAL records
    filtered_sales = pd.DataFrame()
    filtered_target = pd.DataFrame()

    valid_prefixes = (
        "DO", "SATHI", "TOUCH", "ONE", "BLISS", "MAXI",
        "DEPO", "ECP", "IRON", "MULTI", "FEMI", "MISOTAL", "GREKIE",
        "NOVADOL", "ZINC", "OBSTETRIC", "CALCIUM", "ORS", "PROTECT", "ANTIFUNGAL"
    )
    if not sales_df.empty and "PRD_GRP" in sales_df.columns:
        sales_phr = sales_df["TEAM"].astype(str).str.upper().str.contains("PHARM", na=False) if "TEAM" in sales_df.columns else False
        sales_mask = sales_df["PRD_GRP"].apply(lambda x: any(str(x).upper().startswith(p) for p in valid_prefixes)) | sales_phr
        filtered_sales = sales_df[sales_mask].copy()
        if "NAME" in filtered_sales.columns:
            filtered_sales["NAME"] = filtered_sales["NAME"].astype(str).str.strip()
        filtered_sales["GROUP_ON"] = filtered_sales["GROUP_ON"].astype(str).str.strip().str.upper()
        filtered_sales["PRD_GRP"] = filtered_sales["PRD_GRP"].astype(str).str.strip()
        filtered_sales["REPORTING_MONTH"] = filtered_sales["REPORTING_MONTH"].astype(str).str.strip()

    if not target_df.empty and "Product Group" in target_df.columns and target_master_col:
        tgt_phr = target_df["Team"].astype(str).str.upper().str.contains("PHARM", na=False) if "Team" in target_df.columns else False
        target_mask = target_df["Product Group"].apply(lambda x: any(str(x).upper().startswith(p) for p in valid_prefixes)) | tgt_phr
        filtered_target = target_df[target_mask].copy()
        filtered_target["F.F Name"] = filtered_target["F.F Name"].astype(str).str.strip()
        filtered_target["Product Group"] = filtered_target["Product Group"].astype(str).str.strip()
        filtered_target[target_master_col] = filtered_target[target_master_col].astype(str).str.strip().str.upper()

    return filtered_target, filtered_sales, target_master_col


def get_target_columns(month, target_df):
    """
    Dynamically determine the Net Target, Unit Target, and TP Target column names
    based on the reporting month (e.g. July,26 -> TGT Net WO/Reg. Jul-26, TGT Unit Jul-26).
    """
    m_clean = str(month).lower()
    net_col = None
    unit_col = None
    tp_col = None

    try:
        m_short = pd.to_datetime(str(month).strip(), format="%B,%y").strftime("%b-%y")
    except Exception:
        m_short = None

    if m_short and not target_df.empty:
        exact_unit_col = f"TGT Unit {m_short}"
        exact_net_col = f"TGT Net WO/Reg. {m_short}"
        avail = {str(c).strip(): c for c in target_df.columns}
        if exact_unit_col in avail:
            unit_col = avail[exact_unit_col]
        if exact_net_col in avail:
            net_col = avail[exact_net_col]

    month_tokens = ["jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun"]
    matched_token = None
    for token in month_tokens:
        if token in m_clean:
            matched_token = token
            break

    if matched_token and not target_df.empty:
        for c in target_df.columns:
            c_low = str(c).lower()
            if net_col is None and "net wo/reg" in c_low and matched_token in c_low:
                net_col = c
            elif "tp value" in c_low and matched_token in c_low and "ytd" not in c_low:
                tp_col = c
            elif unit_col is None and "unit" in c_low and matched_token in c_low and "ytd" not in c_low and "mnt" not in c_low:
                unit_col = c

    return net_col, unit_col, tp_col
