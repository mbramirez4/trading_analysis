"""Splits each account's fills into closed and open P&L.

For every account/instrument pair, walks the fills in time
order to track a running position and its dollar cost basis
per contract (commission blended in). Price-difference P&L
is realized into closed_pnl_usd as the position is reduced or
closed. Whatever remains open at the end is valued against
the current market_prices mark for that instrument, as a
single "right now" open_pnl_usd -- there is no historical
mark to value it against at any earlier point.
"""

import pandas as pd


def _apply_fill_to_position(
    position, side, quantity, price, commission_usd, point_value_usd
):
    """
    Folds one fill into a running position, in place.

    Everything here is kept in dollars per contract (price is
    converted via point_value_usd before any arithmetic), so
    it can be combined with commission_usd -- itself already a
    dollar amount -- without a unit mismatch.

    Commission always drags against whoever pays it: a BUY
    fill's dollar value is price plus commission (it cost
    more), a SELL fill's is price minus commission (it netted
    less) -- true whether that fill is opening, closing or
    flipping a position, so it is computed once and reused.

    Extends the position when the fill matches its current
    direction (or opens one from flat), blending the fill's
    dollar value into the average cost basis. Otherwise closes
    it -- fully, partially, or flipping direction -- realizing
    price-difference P&L into position["closed_pnl_usd"].

    Args:
        position (dict): Running state with "quantity",
        "avg_cost_usd_per_contract" and "closed_pnl_usd",
        mutated here.
        side (str): "BUY" or "SELL".
        quantity (int): Contracts filled.
        price (float): Execution price per contract.
        commission_usd (float): Commission charged for this
        fill.
        point_value_usd (float): Dollar value of one point of
        price movement, for one contract of this instrument.
    """
    signed_quantity = quantity if side == "BUY" else -quantity
    commission_per_contract_usd = commission_usd / quantity
    fill_sign = 1 if side == "BUY" else -1
    fill_value_usd_per_contract = (
        price * point_value_usd + fill_sign * commission_per_contract_usd
    )

    opens_or_extends = position["quantity"] == 0 or (
        position["quantity"] > 0
    ) == (signed_quantity > 0)

    if opens_or_extends:
        combined_quantity = abs(position["quantity"]) + quantity
        prior_cost_usd = (
            abs(position["quantity"]) * position["avg_cost_usd_per_contract"]
        )
        position["avg_cost_usd_per_contract"] = (
            prior_cost_usd + quantity * fill_value_usd_per_contract
        ) / combined_quantity
        position["quantity"] += signed_quantity
        return

    closing_direction = 1 if position["quantity"] > 0 else -1
    closing_quantity = min(abs(position["quantity"]), quantity)
    leftover_quantity = quantity - closing_quantity

    price_diff_usd = (
        fill_value_usd_per_contract - position["avg_cost_usd_per_contract"]
    ) * closing_direction
    position["closed_pnl_usd"] += price_diff_usd * closing_quantity
    position["quantity"] -= closing_direction * closing_quantity

    if leftover_quantity > 0:
        position["avg_cost_usd_per_contract"] = fill_value_usd_per_contract
        position["quantity"] = fill_sign * leftover_quantity


def compute_account_instrument_positions(fills, instruments, market_prices):
    """
    Splits every account/instrument's fills into closed and
    open P&L.

    Walks each account's fills for each instrument in time
    order, tracking a running dollar cost basis per contract.
    Realized price-difference P&L (net of commission)
    accumulates into closed_pnl_usd as the position is reduced
    or closed. Whatever remains open at the end is valued
    against the current market_prices mark for that
    instrument, as a single "right now" open_pnl_usd.

    Args:
        fills (pd.DataFrame): Fills table.
        instruments (pd.DataFrame): Instruments table, for
        point_value_usd per symbol.
        market_prices (pd.DataFrame): Current mark price per
        symbol.

    Returns:
        pd.DataFrame: One row per (account_id,
        instrument_symbol) that has at least one fill, with
        closed_pnl_usd, open_quantity,
        open_avg_cost_usd_per_contract, open_pnl_usd and
        total_pnl_usd.
    """
    point_value_by_symbol = instruments.set_index("symbol")["point_value_usd"]
    mark_price_by_symbol = market_prices.set_index("symbol")["mark_price"]

    records = []
    ordered = fills.sort_values("filled_at")
    for (account_id, symbol), group in ordered.groupby(
        ["account_id", "instrument_symbol"]
    ):
        point_value_usd = point_value_by_symbol[symbol]
        position = {
            "quantity": 0,
            "avg_cost_usd_per_contract": 0.0,
            "closed_pnl_usd": 0.0,
        }

        for fill in group.itertuples():
            _apply_fill_to_position(
                position,
                side=fill.side,
                quantity=fill.quantity,
                price=fill.price,
                commission_usd=fill.commission_usd,
                point_value_usd=point_value_usd,
            )

        is_open = position["quantity"] != 0
        open_pnl_usd = (
            (
                mark_price_by_symbol[symbol] * point_value_usd
                - position["avg_cost_usd_per_contract"]
            )
            * position["quantity"]
            if is_open
            else 0.0
        )
        records.append(
            {
                "account_id": account_id,
                "instrument_symbol": symbol,
                "closed_pnl_usd": position["closed_pnl_usd"],
                "open_quantity": position["quantity"],
                "open_avg_cost_usd_per_contract": (
                    position["avg_cost_usd_per_contract"] if is_open else None
                ),
                "open_pnl_usd": open_pnl_usd,
            }
        )

    result = pd.DataFrame.from_records(records)
    result["total_pnl_usd"] = result["closed_pnl_usd"] + result["open_pnl_usd"]
    return result


def aggregate_positions_by_account(account_instrument_pnl):
    """
    Rolls per-instrument P&L up to one row per account.

    Sums closed_pnl_usd, open_pnl_usd and total_pnl_usd
    across every instrument an account has traded. Also
    counts how many instruments the account still holds an
    open position in -- open_quantity itself isn't summed,
    since contracts on different instruments aren't the same
    unit and adding them together would be meaningless.

    Args:
        account_instrument_pnl (pd.DataFrame): Output of
        compute_account_instrument_positions.

    Returns:
        pd.DataFrame: One row per account_id, with
        n_instruments_traded, n_open_positions,
        closed_pnl_usd, open_pnl_usd and total_pnl_usd.
    """
    return account_instrument_pnl.groupby("account_id").agg(
        n_instruments_traded=("instrument_symbol", "nunique"),
        n_open_positions=("open_quantity", lambda q: (q != 0).sum()),
        closed_pnl_usd=("closed_pnl_usd", "sum"),
        open_pnl_usd=("open_pnl_usd", "sum"),
        total_pnl_usd=("total_pnl_usd", "sum"),
    ).reset_index()
