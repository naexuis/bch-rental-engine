from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_frontier_probability_chart(
    chart_df: pd.DataFrame,
) -> go.Figure:
    """
    Build the budget-frontier probability chart.
    """
    fig = px.line(
        chart_df,
        x="budget_usd",
        y="prob_1plus_pct",
        markers=True,
        labels={
            "budget_usd": "Budget USD",
            "prob_1plus_pct": "P(1+ Block) %",
        },
    )

    fig.update_traces(
        hovertemplate=(
            "Budget: $%{x:,.0f}<br>"
            "P(1+): %{y:.2f}%"
            "<extra></extra>"
        )
    )

    return fig
