"""Data Loader Compatibility Module.

All data is loaded directly from the PostgreSQL database tables:
  1. staff_master
  2. target_data
  3. sales_data

No CSV or Excel files are read. This module provides backward-compatible
aliases pointing to core.db_loader.
"""
from core.db_loader import (
    load_staff_df,
    load_datasets,
    get_val_logic_mapping,
    get_target_columns,
)

__all__ = [
    "load_staff_df",
    "load_datasets",
    "get_val_logic_mapping",
    "get_target_columns",
]
