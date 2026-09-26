"""Human-readable column glossaries for the raw CSV tables.

Captures what each column means and how it is used
downstream, for the tables whose columns are not
self-explanatory (instruments, market_prices, fills).
"""

import pandas as pd

INSTRUMENTS_GLOSSARY = {
    "symbol": "Futures contract ticker, e.g. ES, MES, NQ.",
    "description": "Human-readable name of the contract.",
    "exchange": "Exchange the contract trades on.",
    "point_value_usd": (
        "USD value of one full point of price movement, for "
        "one contract. Scales notional value and P&L: e.g. "
        "NQ (20) is 10x MNQ (2) despite tracking the same "
        "index."
    ),
    "tick_size": "Smallest price increment the contract can move.",
    "tick_value_usd": (
        "USD value of one tick move (tick_size * "
        "point_value_usd)."
    ),
    "initial_margin_usd": (
        "Margin required to open one contract's position."
    ),
    "maintenance_margin_usd": (
        "Minimum margin to keep one contract's position open "
        "before a margin call."
    ),
}

MARKET_PRICES_GLOSSARY = {
    "symbol": "Instrument ticker; joins to instruments.symbol.",
    "mark_price": (
        "Latest price used to value open positions for "
        "unrealized P&L as of the dataset cut."
    ),
    "as_of": (
        "Timestamp of the mark. Constant across rows: the "
        "dataset cut, 2026-08-25T14:30:00Z."
    ),
}

FILLS_GLOSSARY = {
    "id": "Unique identifier of this execution (fill).",
    "account_id": "Foreign key to accounts.id.",
    "instrument_symbol": "Foreign key to instruments.symbol.",
    "side": "Trade direction: BUY or SELL.",
    "quantity": "Number of contracts executed in this fill.",
    "price": "Execution price per contract for this fill.",
    "filled_at": "UTC ISO 8601 timestamp of the execution.",
    "order_id": (
        "Groups fills belonging to one order. An order can "
        "fill in several pieces, sharing this id; those "
        "pieces are not separate trades."
    ),
    "liquidity": (
        "'maker' (this fill added resting liquidity to the "
        "book) or 'taker' (it crossed the spread against "
        "resting liquidity). Commissions can differ by this."
    ),
    "commission_usd": (
        "Commission charged for this fill, per contract per "
        "side. Real cost, not a rounding artifact."
    ),
}

GLOSSARIES_BY_TABLE = {
    "instruments": INSTRUMENTS_GLOSSARY,
    "market_prices": MARKET_PRICES_GLOSSARY,
    "fills": FILLS_GLOSSARY,
}


def glossary_table(table_name):
    """
    Renders a table's column glossary as a DataFrame.

    Args:
        table_name (str): One of GLOSSARIES_BY_TABLE's keys.

    Returns:
        pd.DataFrame: Two columns, "column" and "meaning".
    """
    glossary = GLOSSARIES_BY_TABLE[table_name]
    return pd.DataFrame(
        {"column": glossary.keys(), "meaning": glossary.values()}
    )
