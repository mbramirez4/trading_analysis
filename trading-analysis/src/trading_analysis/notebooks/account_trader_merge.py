"""Domain logic for combining accounts with their trader."""

def merge_accounts_with_traders(accounts, traders):
    """
    Left-joins accounts onto their owning trader.

    Preserves one row per account (a trader may hold several
    accounts), attaching the trader's profile columns.
    Overlapping column names are disambiguated with
    "_account" and "_trader" suffixes.

    Args:
        accounts (pd.DataFrame): Accounts table, keyed by
        trader_id.
        traders (pd.DataFrame): Traders table, keyed by id.

    Returns:
        pd.DataFrame: accounts joined with traders, one row
        per account.
    """
    return accounts.merge(
        traders,
        left_on="trader_id",
        right_on="id",
        how="left",
        suffixes=("_account", "_trader"),
    )


def count_accounts_per_trader(accounts):
    """
    Counts how many accounts each trader holds.

    Args:
        accounts (pd.DataFrame): Accounts table, keyed by
        trader_id.

    Returns:
        pd.Series: Account count indexed by trader_id, named
        "account_count".
    """
    return accounts.groupby("trader_id").size().rename("account_count")


def attach_trader_info(df, accounts, traders, account_id_column="account_id"):
    """
    Attaches each row's owning trader's profile to it.

    Joins df through accounts to traders (the two-step
    account_id -> accounts.id -> trader_id -> traders.id
    relationship), so a caller working with any table keyed by
    an account id doesn't need to know that chain itself.

    Args:
        df (pd.DataFrame): Any table with an account id
        column.
        accounts (pd.DataFrame): Accounts table, keyed by
        trader_id.
        traders (pd.DataFrame): Traders table, keyed by id.
        account_id_column (str): Name of df's account id
        column.

    Returns:
        pd.DataFrame: df left-joined with the account's and
        trader's profile columns.
    """
    accounts_with_traders = merge_accounts_with_traders(accounts, traders)
    return df.merge(
        accounts_with_traders,
        left_on=account_id_column,
        right_on="id_account",
        how="left",
    )
