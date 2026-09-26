"""Generic DataFrame profiling helpers for exploratory analysis.

Domain-free: every function here works on any DataFrame and
carries no trading-specific concepts.
"""

import pandas as pd


def summarize_frame(df):
    """
    Builds a per-column profile: dtype, nulls and cardinality.

    Args:
        df (pd.DataFrame): The frame to profile.

    Returns:
        pd.DataFrame: One row per column of df, indexed by
        column name, with dtype, non_null_count, null_count,
        null_pct and n_unique.
    """
    return pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "non_null_count": df.notna().sum(),
            "null_count": df.isna().sum(),
            "null_pct": (df.isna().mean() * 100).round(2),
            "n_unique": df.nunique(),
        }
    )


def low_cardinality_value_counts(df, max_uniques=15):
    """
    Collects value counts for every low-cardinality column.

    Args:
        df (pd.DataFrame): The frame to inspect.
        max_uniques (int): Upper bound on distinct values for
        a column to be considered low-cardinality.

    Returns:
        dict[str, pd.Series]: One value_counts() Series per
        column whose number of unique values is at most
        max_uniques.
    """
    return {
        column: df[column].value_counts()
        for column in df.columns
        if df[column].nunique() <= max_uniques
    }


def foreign_key_coverage(child_df, child_key, parent_df, parent_key):
    """
    Checks a foreign key's coverage in both directions.

    Args:
        child_df (pd.DataFrame): Frame holding the foreign
        key.
        child_key (str): Column in child_df referencing
        parent_key.
        parent_df (pd.DataFrame): Frame holding the referenced
        key.
        parent_key (str): Column in parent_df being
        referenced.

    Returns:
        dict: "orphaned_child_values" (values present in
        child_df[child_key] but missing from
        parent_df[parent_key]) and
        "unreferenced_parent_values" (the reverse), both sets.
    """
    child_values = set(child_df[child_key])
    parent_values = set(parent_df[parent_key])
    return {
        "orphaned_child_values": child_values - parent_values,
        "unreferenced_parent_values": parent_values - child_values,
    }
