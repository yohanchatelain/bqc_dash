# Installation requirements:
# pip install dash dash-bootstrap-components

from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
import time
import uuid

from bqc_dash.app import app


class ToastException(Exception):
    """Custom exception class for handling toast notifications"""

    def __init__(self, toast):
        super().__init__("")
        self.toast = toast


# Function to create a new toast
def create_toast(message, toast_type="info", duration=5):
    """
    Helper function to create a new toast object
    """
    return {
        "id": str(uuid.uuid4()),
        "message": message,
        "type": toast_type,
        "created_at": time.time(),
        "duration": duration,
    }


# Callback to render toast notifications and handle auto-dismissal
@app.callback(
    Output("toast-container", "children"),
    Output("toast-store", "data", allow_duplicate=True),
    Input("toast-store", "data"),
    prevent_initial_call=True,
)
def update_toasts(data):
    """
    Update the toast display based on the current state of the toast store.
    Removes expired toasts and renders active ones with progress bars.
    """
    # Get the current time
    current_time = time.time()

    # Filter out toasts that should be removed (expired)
    active_toasts = []
    for toast in data["toasts"]:
        if current_time - toast["created_at"] < toast["duration"]:
            active_toasts.append(toast)

    # Update the toast store if any toasts were removed
    if len(active_toasts) < len(data["toasts"]):
        data["toasts"] = active_toasts

    # Render the active toasts (newest at the top)
    toast_components = []
    for toast in reversed(active_toasts):
        # Map toast type to Bootstrap color
        color_map = {
            "info": "info",
            "success": "success",
            "warning": "warning",
            "danger": "danger",
        }
        color = color_map.get(toast["type"], "info")

        # Create toast component
        toast_components.append(
            dbc.Toast(
                [
                    html.P(toast["message"], className="mb-0"),
                ],
                id=f"toast-{toast['id']}",
                header=f"{toast['type'].capitalize()}",
                icon=toast["type"],
                dismissable=True,
                is_open=True,
                className="mb-3",
                style={"opacity": "0.95"},
            )
        )

    return toast_components, data


# Utility function to show how to send a notification from any callback
def send_notification(message, toast_type="info", duration=5):
    """
    Utility function to demonstrate how to send notifications from other callbacks.

    Example usage in another part of your app:

    @app.callback(
        Output("some-output", "children"),
        Output("toast-store", "data", allow_duplicate=True),  # Need to include this
        Input("some-input", "value"),
        State("toast-store", "data"),
        prevent_initial_call=True
    )
    def some_callback(value, toast_data):
        # Process data
        result = process_data(value)

        # Send notification
        updated_toast_data = send_notification(
            "Processing complete!", "success", 5
        )(toast_data)

        return result, updated_toast_data
    """

    def update_toast_store(data):
        new_toast = create_toast(message, toast_type, duration)
        data["toasts"].append(new_toast)
        return data

    return update_toast_store
