"""Loaders for the ArrowFin trading assessment CSV dataset."""

from pathlib import Path

import pandas as pd

DATETIME_COLUMNS_BY_TABLE = {
    "accounts": ["created_at"],
    "traders": ["created_at"],
    "instruments": [],
    "market_prices": ["as_of"],
    "fills": ["filled_at"],
    "brokers": ["created_at"],
}


def resolve_dataset_dir(marker_filename="accounts.csv"):
    """
    Finds the dataset directory by walking up from this file.

    Searches this file's directory and its parents for a
    "dataset" folder containing marker_filename, so callers
    do not need to know the repo layout or working directory.

    Args:
        marker_filename (str): A file expected inside the
        dataset directory, used to confirm a match.

    Returns:
        Path: The resolved dataset directory.

    Raises:
        FileNotFoundError: If no matching "dataset" directory
        is found among this file's parents.
    """
    here = Path(__file__).resolve()
    for directory in [here.parent, *here.parents]:
        candidate = directory / "dataset"
        if (candidate / marker_filename).is_file():
            return candidate
    raise FileNotFoundError(
        f"Could not locate a 'dataset' directory containing "
        f"{marker_filename} above {here}"
    )


def load_table(dataset_dir, table_name):
    """
    Loads a single CSV table as a DataFrame.

    Applies the datetime parsing registered for table_name in
    DATETIME_COLUMNS_BY_TABLE, if any.

    Args:
        dataset_dir (Path): Directory containing the CSV
        files.
        table_name (str): Table name, matching a CSV file's
        stem (e.g. "accounts" for "accounts.csv").

    Returns:
        pd.DataFrame: The loaded table.
    """
    csv_path = Path(dataset_dir) / f"{table_name}.csv"
    parse_dates = DATETIME_COLUMNS_BY_TABLE.get(table_name) or None
    return pd.read_csv(csv_path, parse_dates=parse_dates)


def load_trading_tables(dataset_dir=None):
    """
    Loads every known table into a name-to-DataFrame mapping.

    Args:
        dataset_dir (Path | None): Directory containing the
        CSV files. Defaults to the result of
        resolve_dataset_dir().

    Returns:
        dict[str, pd.DataFrame]: One entry per table name in
        DATETIME_COLUMNS_BY_TABLE.
    """
    dataset_dir = Path(dataset_dir) if dataset_dir else resolve_dataset_dir()
    return {
        table_name: load_table(dataset_dir, table_name)
        for table_name in DATETIME_COLUMNS_BY_TABLE
    }
