"""Approximates each session's closing price per instrument.

market_prices only carries one snapshot mark, taken at the
dataset cut. There is no separately recorded closing price
for the 11 earlier sessions, so this approximates one from
each session's last fill -- the last traded price is a
standard stand-in for a mark when no official one exists.
"""


def build_session_closing_prices(tagged_fills):
    """
    Builds one closing price per session per instrument.

    Uses the price of the last fill (by filled_at) within
    each session_date/instrument_symbol group as that
    session's closing price.

    Args:
        tagged_fills (pd.DataFrame): Fills tagged with
        tag_fills_with_session (must carry a "session_date"
        column).

    Returns:
        pd.DataFrame: One row per (session_date,
        instrument_symbol), with closing_price and
        closing_filled_at.
    """
    ordered = tagged_fills.sort_values("filled_at")
    return ordered.groupby(
        ["session_date", "instrument_symbol"], as_index=False
    ).agg(
        closing_price=("price", "last"),
        closing_filled_at=("filled_at", "last"),
    )
