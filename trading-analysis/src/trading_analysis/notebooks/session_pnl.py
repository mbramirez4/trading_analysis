"""Per-session, per-account, per-instrument P&L breakdown.

Combines fills with session_closing_prices to attribute each
session's cash movement and mark-to-market P&L, carrying an
account's running position forward from one of its active
sessions to the next.
"""

import pandas as pd


def compute_session_account_instrument_pnl(
    tagged_fills, session_closing_prices, instruments
):
    """
    Builds one row per account, instrument and session.

    For every session an account/instrument pair has at least
    one fill in, reports gross cash spent buying (spent) and
    received selling (income), contract counts (total_buys,
    total_sells), net contracts traded that session, signed
    positive for net buying (total_open), commissions
    (total_commissions_usd) and that session's total P&L
    (total_profit_and_loss_usd).

    total_profit_and_loss_usd combines whatever was realized
    this session with the mark-to-market change in value of
    anything still held, using the position carried over from
    the account's previous *active* session and each session's
    closing price (from session_closing_prices) as the
    before/after marks:

        pnl = (qty_after * price_after - qty_before * price_before)
              * point_value_usd + income - spent - commissions

    A session with no fills for a held position is skipped
    entirely (no row is produced), so that position's price
    drift over such a gap is folded into the next session that
    does have a fill -- it isn't lost, just not attributed to
    the quiet session itself.

    Args:
        tagged_fills (pd.DataFrame): Fills tagged with
        tag_fills_with_session.
        session_closing_prices (pd.DataFrame): Output of
        build_session_closing_prices, built from the same
        tagged_fills.
        instruments (pd.DataFrame): Instruments table, for
        point_value_usd per symbol.

    Returns:
        pd.DataFrame: One row per (account_id,
        instrument_symbol, session_date), with spent, income,
        total_buys, total_sells, total_open,
        total_commissions_usd and total_profit_and_loss_usd.
    """
    point_value_by_symbol = instruments.set_index("symbol")["point_value_usd"]
    closing_price_by_session_symbol = session_closing_prices.set_index(
        ["session_date", "instrument_symbol"]
    )["closing_price"]

    records = []
    for (account_id, symbol), group in tagged_fills.groupby(
        ["account_id", "instrument_symbol"]
    ):
        point_value_usd = point_value_by_symbol[symbol]
        quantity_before_session = 0
        price_before_session = 0.0

        for session_date, session_fills in group.groupby("session_date"):
            buys = session_fills[session_fills["side"] == "BUY"]
            sells = session_fills[session_fills["side"] == "SELL"]

            spent = (buys["quantity"] * buys["price"] * point_value_usd).sum()
            income = (
                sells["quantity"] * sells["price"] * point_value_usd
            ).sum()
            total_buys = buys["quantity"].sum()
            total_sells = sells["quantity"].sum()
            total_open = total_buys - total_sells
            total_commissions_usd = session_fills["commission_usd"].sum()

            price_after_session = closing_price_by_session_symbol[
                (session_date, symbol)
            ]
            quantity_after_session = quantity_before_session + total_open

            mark_to_market_change_usd = (
                quantity_after_session * price_after_session
                - quantity_before_session * price_before_session
            ) * point_value_usd
            total_profit_and_loss_usd = (
                mark_to_market_change_usd + income - spent - total_commissions_usd
            )

            records.append(
                {
                    "account_id": account_id,
                    "instrument_symbol": symbol,
                    "session_date": session_date,
                    "spent": spent,
                    "income": income,
                    "total_buys": total_buys,
                    "total_sells": total_sells,
                    "total_open": total_open,
                    "total_commissions_usd": total_commissions_usd,
                    "total_profit_and_loss_usd": total_profit_and_loss_usd,
                }
            )

            quantity_before_session = quantity_after_session
            price_before_session = price_after_session

    return pd.DataFrame.from_records(records)
