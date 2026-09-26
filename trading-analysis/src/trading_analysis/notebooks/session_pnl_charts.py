"""Chart: session P&L against how much an account bought.

Scatter, not a bar/line aggregate: each point is one
account's activity in one session, so the relationship
between size (contracts bought) and outcome (P&L) is visible
directly, rather than compressed into a single ratio.
"""

import numpy as np
import matplotlib.pyplot as plt

ACCENT_COLOR = "#2a78d6"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID_COLOR = "#e3e2dc"
SURFACE_COLOR = "#fcfcfb"


def aggregate_pnl_by_account_session(session_account_instrument_pnl):
    """
    Rolls per-instrument session P&L up to one row per account
    per session.

    Sums total_buys and total_profit_and_loss_usd across every
    instrument an account traded within that session.

    Args:
        session_account_instrument_pnl (pd.DataFrame): Output
        of compute_session_account_instrument_pnl.

    Returns:
        pd.DataFrame: One row per (account_id, session_date),
        with total_buys and total_profit_and_loss_usd.
    """
    return session_account_instrument_pnl.groupby(
        ["account_id", "session_date"], as_index=False
    ).agg(
        total_buys=("total_buys", "sum"),
        total_profit_and_loss_usd=("total_profit_and_loss_usd", "sum"),
    )


def plot_pnl_against_buys(account_session_pnl):
    """
    Scatters each account-session's P&L against its buy count.

    One point per (account_id, session_date): total_buys on
    the x axis, total_profit_and_loss_usd on the y axis, with
    a dashed zero-line marking the profit/loss boundary.

    Args:
        account_session_pnl (pd.DataFrame): Output of
        aggregate_pnl_by_account_session.

    Returns:
        matplotlib.figure.Figure: The rendered chart.
    """
    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.patch.set_facecolor(SURFACE_COLOR)
    ax.set_facecolor(SURFACE_COLOR)

    ax.scatter(
        account_session_pnl["total_buys"],
        account_session_pnl["total_profit_and_loss_usd"],
        s=40,
        color=ACCENT_COLOR,
        alpha=0.55,
        edgecolors="none",
    )
    ax.axhline(0, color=TEXT_SECONDARY, linewidth=1, linestyle="--")

    ax.set_xlabel(
        "Total contracts bought (account, session)", color=TEXT_SECONDARY
    )
    ax.set_ylabel("Total profit/loss (USD)", color=TEXT_SECONDARY)
    ax.set_title(
        "Session P&L vs. contracts bought, per account per session",
        color=TEXT_PRIMARY,
        fontsize=13,
        loc="left",
    )

    ax.grid(True, color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine_name in ("top", "right"):
        ax.spines[spine_name].set_visible(False)
    for spine_name in ("left", "bottom"):
        ax.spines[spine_name].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_SECONDARY)

    fig.tight_layout()
    return fig


def plot_pnl_trend_over_sessions(account_session_pnl):
    """
    Lines the average session P&L over time, with individual
    account-session points behind it for context.

    One faint point per (account_id, session_date), jittered
    slightly on the x axis to separate overlapping accounts in
    the same session; a bold line connects each session's mean
    total_profit_and_loss_usd across accounts, in session
    order, to surface whether losses cluster around particular
    sessions rather than being spread evenly over time.

    Args:
        account_session_pnl (pd.DataFrame): Output of
        aggregate_pnl_by_account_session.

    Returns:
        matplotlib.figure.Figure: The rendered chart.
    """
    ordered_sessions = sorted(account_session_pnl["session_date"].unique())
    session_index = {date: i for i, date in enumerate(ordered_sessions)}
    session_means = (
        account_session_pnl.groupby("session_date")["total_profit_and_loss_usd"]
        .mean()
        .reindex(ordered_sessions)
    )

    rng = np.random.default_rng(0)
    x_positions = account_session_pnl["session_date"].map(session_index)
    jitter = rng.uniform(-0.15, 0.15, size=len(x_positions))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor(SURFACE_COLOR)
    ax.set_facecolor(SURFACE_COLOR)

    ax.scatter(
        x_positions.to_numpy(dtype=float) + jitter,
        account_session_pnl["total_profit_and_loss_usd"],
        s=18,
        color=TEXT_SECONDARY,
        alpha=0.25,
        edgecolors="none",
        zorder=2,
    )
    ax.plot(
        range(len(ordered_sessions)),
        session_means.to_numpy(),
        color=ACCENT_COLOR,
        linewidth=2,
        marker="o",
        markersize=5,
        zorder=3,
    )
    ax.axhline(0, color=TEXT_SECONDARY, linewidth=1, linestyle="--", zorder=1)

    ax.set_xticks(range(len(ordered_sessions)))
    ax.set_xticklabels(
        [date.strftime("%b %d") for date in ordered_sessions],
        rotation=45,
        ha="right",
        color=TEXT_SECONDARY,
    )
    ax.set_ylabel("Total profit/loss (USD)", color=TEXT_SECONDARY)
    ax.set_title(
        "Average session P&L over time, with per-account spread",
        color=TEXT_PRIMARY,
        fontsize=13,
        loc="left",
    )

    ax.grid(True, axis="y", color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine_name in ("top", "right"):
        ax.spines[spine_name].set_visible(False)
    for spine_name in ("left", "bottom"):
        ax.spines[spine_name].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_SECONDARY)

    fig.tight_layout()
    return fig
