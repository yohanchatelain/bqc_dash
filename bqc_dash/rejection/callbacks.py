from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from bqc_dash.logger import logger

from bqc_dash.app import app


@app.callback(
    Output("toggle-reject-btn", "n_clicks"),
    [Input("toggle-reject-btn-key", "n_keydowns")],
    [State("toggle-reject-btn", "n_clicks")],
    prevent_initial_call=True,
)
def toggle_rejection_btn_listener(event, current_clicks):
    """Handle keydown event for toggle rejection button"""
    logger.debug("Toggle rejection button triggered")

    # Initialize clicks if None
    if current_clicks is None:
        current_clicks = 0

    if event:
        return current_clicks + 1

    # Return unchanged if no event
    return current_clicks


@app.callback(
    [
        Output("rejected-images-store", "data", allow_duplicate=True),
        Output("current-rejected-status-store", "data", allow_duplicate=True),
    ],
    [Input("toggle-reject-btn", "n_clicks")],
    [State("rejected-images-store", "data"), State("current-index-store", "data")],
    prevent_initial_call=True,
)
def toggle_rejection_status(toggle_clicks, rejected_images, current_index):
    """Toggle the rejection status of the current image"""
    logger.debug("Toggle rejection status")
    # Handle invalid inputs
    if current_index is None:
        # raise an alert
        logger.warning("No current index found")
        raise PreventUpdate

    current_index = str(current_index)

    logger.debug(f"Rejected current index: {current_index} type")

    if rejected_images is None or rejected_images == {}:
        rejected_images = {}

    if current_index not in rejected_images:
        rejected_images[current_index] = False

    rejected_images[current_index] = not rejected_images.get(current_index, False)

    logger.debug(
        f"Rejection status for index {current_index}: {rejected_images[current_index]}"
    )

    return rejected_images, rejected_images[current_index]


@app.callback(
    Output("current-rejected-status-store", "data", allow_duplicate=True),
    [Input("current-index-store", "data")],
    [State("rejected-images-store", "data")],
    prevent_initial_call=True,
)
def get_rejection_status(current_index, rejected_images):
    """Get the rejection status of the current image"""
    logger.debug("Get rejection status")
    # Handle invalid inputs
    if rejected_images is None or current_index is None:
        raise PreventUpdate

    # Get the rejection status for the current index
    return rejected_images.get(str(current_index), False)


@app.callback(
    [
        Output("status-label", "children"),
        Output("status-label", "color"),
        Output("toggle-reject-btn", "children"),
    ],
    [Input("current-rejected-status-store", "data")],
    [State("current-index-store", "data")],
    prevent_initial_call=True,
)
def update_rejection_status_ui(rejected_status, current_index):
    """Update the rejection status UI based on the current index"""
    logger.debug("Update rejection status UI")
    logger.debug(f"Rejected status: {rejected_status}")
    if rejected_status is None or current_index is None:
        raise PreventUpdate

    # Update status based on rejection status
    if rejected_status:
        status_color = "danger"
        status_text = "REJECTED"
        toggle_text = "Mark as Accepted"
    else:
        status_color = "success"
        status_text = "ACCEPTED"
        toggle_text = "Mark as Rejected"

    return status_text, status_color, toggle_text
