"""Flags a session as a "very bad day" for an account.

Judges each session against that same account's OWN prior
history, rather than a fixed dollar threshold or a comparison
across accounts of very different size.
"""

import pandas as pd


def flag_bad_sessions(
    account_session_pnl, z_threshold=-1.5, min_history_sessions=3
):
    """
    Flags sessions that are unusually bad for that account.

    For each account, walks its sessions in order and builds a
    running baseline (mean, std of total_profit_and_loss_usd)
    from every STRICTLY EARLIER session -- the session being
    judged is never part of its own baseline. A session is
    flagged when it falls more than abs(z_threshold) standard
    deviations below that baseline's mean.

    An account with fewer than min_history_sessions of prior
    sessions is left unjudged (is_very_bad_day is None) rather
    than scored off too small a sample to be meaningful.

    Args:
        account_session_pnl (pd.DataFrame): One row per
        (account_id, session_date), with
        total_profit_and_loss_usd. Output of
        aggregate_pnl_by_account_session, or anything with the
        same shape.
        z_threshold (float): Bad-day cutoff, in standard
        deviations below the account's historical mean.
        Negative; more negative is a stricter (rarer) flag.
        min_history_sessions (int): Minimum number of prior
        sessions required before a session can be judged.

    Returns:
        pd.DataFrame: account_session_pnl with three added
        columns: n_prior_sessions, historical_mean_pnl_usd,
        historical_std_pnl_usd and is_very_bad_day (True/False,
        or None where history is insufficient).
    """
    ordered = account_session_pnl.sort_values(["account_id", "session_date"])

    records = []
    for _, group in ordered.groupby("account_id"):
        prior_pnls = []
        for row in group.to_dict("records"):
            n_prior_sessions = len(prior_pnls)
            is_very_bad_day = None
            mean_pnl_usd = None
            std_pnl_usd = None

            if n_prior_sessions >= min_history_sessions:
                mean_pnl_usd = sum(prior_pnls) / n_prior_sessions
                variance = sum(
                    (pnl - mean_pnl_usd) ** 2 for pnl in prior_pnls
                ) / n_prior_sessions
                std_pnl_usd = variance**0.5
                pnl_usd = row["total_profit_and_loss_usd"]
                if std_pnl_usd > 0:
                    z_score = (pnl_usd - mean_pnl_usd) / std_pnl_usd
                    is_very_bad_day = z_score < z_threshold
                else:
                    is_very_bad_day = pnl_usd < mean_pnl_usd

            records.append(
                {
                    **row,
                    "n_prior_sessions": n_prior_sessions,
                    "historical_mean_pnl_usd": mean_pnl_usd,
                    "historical_std_pnl_usd": std_pnl_usd,
                    "is_very_bad_day": is_very_bad_day,
                }
            )
            prior_pnls.append(row["total_profit_and_loss_usd"])

    return pd.DataFrame.from_records(records)
