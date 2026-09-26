"""Tags fills with the trading session they belong to.

A CME Globex session opens at 17:00 US Central and runs
until 16:00 US Central the next day, so it does not align
with UTC calendar dates -- one session can span two of them.
"""

import pandas as pd

SESSION_OPEN_HOUR_CENTRAL = 17
SESSION_TIMEZONE = "America/Chicago"


def tag_fills_with_session(fills, filled_at_column="filled_at"):
    """
    Labels each fill with the trading session it belongs to.

    Converts filled_at to US Central time (pandas resolves
    the daylight-saving offset) and rolls the calendar date
    back by SESSION_OPEN_HOUR_CENTRAL hours, so every fill in
    one session shares the same label even when the session
    itself crosses a UTC (or Central) date boundary.

    Args:
        fills (pd.DataFrame): Fills table with a UTC
        timestamp column.
        filled_at_column (str): Name of that timestamp
        column.

    Returns:
        pd.DataFrame: A copy of fills with an added
        "session_date" column.
    """
    central_time = fills[filled_at_column].dt.tz_convert(SESSION_TIMEZONE)
    session_date = (
        central_time - pd.Timedelta(hours=SESSION_OPEN_HOUR_CENTRAL)
    ).dt.date
    return fills.assign(session_date=session_date)
