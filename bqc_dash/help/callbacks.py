from dash import Input, Output, State
from bqc_dash.app import app
from bqc_dash.logger import logger


@app.callback(
    Output("keyboard-shortcuts-offcanvas", "is_open"),
    [Input("keyboard-shortcuts-btn", "n_clicks")],
    [State("keyboard-shortcuts-offcanvas", "is_open")],
    prevent_initial_call=True,
)
def toggle_keyboard_shortcuts(n_clicks, is_open):
    """Toggle the keyboard shortcuts offcanvas"""
    logger.debug("Toggle keyboard shortcuts")
    if is_open:
        return False
    return True
