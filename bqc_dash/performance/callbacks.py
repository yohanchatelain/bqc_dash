from dash import html, Input, Output
import dash_bootstrap_components as dbc

from bqc_dash.app import app
from bqc_dash.logger import logger
from bqc_dash.performance import performance


# Performance metrics display
@app.callback(
    Output("perf-metrics", "children"),
    [Input("metrics-interval", "n_intervals")],
    prevent_initial_call=True,
)
def update_performance_metrics(n):
    """Update the performance metrics display"""
    logger.debug("Start update_performance_metrics")
    metrics = performance.get_metrics()

    if not metrics:
        return "No performance data available yet."

    # Create a formatted table of metrics
    rows = []
    for name, data in metrics.items():
        rows.append(
            html.Tr(
                [
                    html.Td(name),
                    html.Td(f"{data['avg']*1000:.2f} ms"),
                    html.Td(f"{data['max']*1000:.2f} ms"),
                    html.Td(f"{data['last']*1000:.2f} ms"),
                    html.Td(f"{data['count']}"),
                ]
            )
        )

    table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Callback"),
                        html.Th("Avg Time"),
                        html.Th("Max Time"),
                        html.Th("Last Time"),
                        html.Th("Count"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        bordered=True,
        hover=True,
        striped=True,
        size="sm",
    )

    return table


# Toggle performance metrics visibility
@app.callback(
    [Output("perf-collapse", "is_open"), Output("metrics-interval", "disabled")],
    [Input("perf-toggle", "value")],
    prevent_initial_call=True,
)
def toggle_performance_panel(show_metrics):
    """Toggle the visibility of the performance metrics panel"""
    return show_metrics, not show_metrics
