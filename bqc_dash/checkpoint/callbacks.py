from dash import Input, Output, State, no_update, ctx
from dash.exceptions import PreventUpdate
from flask import session
import traceback
import json

from bqc_dash.logger import logger
from bqc_dash.app import app
from bqc_dash.checkpoint.server import (
    save_checkpoint,
    checkpoint_load,
    save_results,
)
from bqc_dash.exceptions.callbacks import exception_callback
from bqc_dash.toaster.callbacks import send_notification, ToastException


@app.callback(
    Output("toast-store", "data", allow_duplicate=True),
    [
        Input("save-checkpoint-btn", "n_clicks"),
        # Input("auto-save-interval", "n_intervals"),
    ],
    [
        State("images-path-store", "data"),
        State("rejected-images-store", "data"),
        State("current-index-store", "data"),
        State("input-dir-store", "data"),
        State("checkpoint-file-input", "value"),
        State("toast-store", "data"),
        # State("auto-save-path", "data"),
    ],
    prevent_initial_call=True,
    on_error=exception_callback,
)
def handle_checkpoint_save_operations(
    save_clicks,
    images_path,
    rejected_indices,
    current_index,
    input_dir,
    checkpoint_file,
    toast_data,
    # auto_save_path,
):
    """Handle save checkpoint and save results operations"""
    logger.debug("Checkpoint save operation triggered")

    # if ctx.triggered_id == "auto-save-interval":
    #     logger.debug("Auto-save triggered")
    #     checkpoint_file = auto_save_path

    if not save_clicks:
        logger.debug("No save clicks detected")
        raise PreventUpdate

    if not checkpoint_file:
        logger.warning("No checkpoint file provided")
        notification = send_notification(
            "No checkpoint file provided",
            "warning",
            duration=5,
        )(toast_data)
        return notification

    # Handle invalid inputs
    if not images_path or len(images_path) == 0:
        logger.warning("No images to save")
        notification = send_notification(
            "No images to save",
            "warning",
            duration=5,
        )(toast_data)
        return notification

    try:
        save_checkpoint(
            checkpoint_file,
            images_path,
            rejected_indices,
            current_index,
            input_dir,
        )
    except Exception as e:
        logger.critical("Error saving checkpoint")
        notification = send_notification(
            "Error saving checkpoint",
            "error",
            duration=5,
        )(toast_data)
        raise ToastException(notification) from e

    logger.info("Checkpoint saved successfully")
    notification = send_notification(
        "Checkpoint saved successfully",
        "success",
        duration=5,
    )(toast_data)
    return notification


@app.callback(
    [
        Output("input-dir-store", "data", allow_duplicate=True),
        Output("images-path-store", "data", allow_duplicate=True),
        Output("current-index-store", "data", allow_duplicate=True),
        Output("rejected-images-store", "data", allow_duplicate=True),
        Output("toast-store", "data", allow_duplicate=True),
    ],
    [
        Input("load-checkpoint-btn", "n_clicks"),
    ],
    [
        State("images-path-store", "data"),
        State("rejected-images-store", "data"),
        State("current-index-store", "data"),
        State("input-dir-store", "data"),
        State("checkpoint-file-input", "value"),
        State("tab-id-store", "data"),
        State("toast-store", "data"),
    ],
    prevent_initial_call=True,
    on_error=exception_callback,
    running=[
        (Output("scan-btn", "disabled"), True, False),
        (Output("save-checkpoint-btn", "disabled"), True, False),
        (Output("save-results-btn", "disabled"), True, False),
        (Output("load-checkpoint-btn", "disabled"), True, False),
        (Output("load-checkpoint", "data"), True, False),
    ],
)
def handle_checkpoint_load_operations(
    save_clicks,
    images_path,
    rejected_indices,
    current_index,
    input_dir,
    checkpoint_file,
    tab_id,
    toast_data,
):
    """Handle save checkpoint and save results operations"""
    logger.debug("Checkpoint load operation triggered")

    if not save_clicks:
        logger.debug("No save clicks detected")
        raise PreventUpdate

    if not checkpoint_file:
        logger.warning("No checkpoint file provided")
        notification = send_notification(
            "No checkpoint file provided",
            "warning",
            duration=5,
        )(toast_data)
        raise ToastException(notification)

    try:
        content = checkpoint_load(checkpoint_file)
    except Exception as e:
        logger.critical("Error processing checkpoint load")
        logger.critical(traceback.format_exc())
        notification = send_notification(
            "Error processing checkpoint load",
            "error",
            duration=5,
        )(toast_data)
        raise ToastException(notification) from e

    notification = send_notification(
        f"Checkpoint [{content.timestamp}] loaded successfully",
        "success",
        duration=5,
    )(toast_data)

    # Update the session with the loaded content
    content = (
        content.input_dir,
        content.images_path,
        content.current_index,
        content.rejected_images,
    )

    return content + (notification,)


@app.callback(
    Output("toast-store", "data", allow_duplicate=True),
    [
        Input("save-results-btn", "n_clicks"),
    ],
    [
        State("images-path-store", "data"),
        State("rejected-images-store", "data"),
        State("current-index-store", "data"),
        State("input-dir-store", "data"),
        State("checkpoint-file-input", "value"),
        State("toast-store", "data"),
    ],
    prevent_initial_call=True,
    running=[
        (Output("scan-btn", "disabled"), True, False),
        (Output("save-checkpoint-btn", "disabled"), True, False),
        (Output("save-results-btn", "disabled"), True, False),
        (Output("load-checkpoint-btn", "disabled"), True, False),
    ],
)
def handle_save_results_operations(
    save_clicks,
    images_path,
    rejected_indices,
    current_index,
    input_dir,
    checkpoint_file,
    toast_data,
):
    """Handle save checkpoint and save results operations"""
    logger.debug("Start handle_save_results_operations")
    # Get which button was clicked

    if not save_clicks:
        logger.debug("No save clicks detected")
        raise PreventUpdate

    if not images_path or len(images_path) == 0:
        logger.warning("No images to save")
        return "No images to save", True, "warning"

    results = {
        "input_dir": input_dir,
        "images_path": images_path,
        "rejected_images": rejected_indices,
    }

    try:
        save_results(checkpoint_file, results)
    except Exception as e:
        logger.critical("Error processing save results")
        logger.critical(traceback.format_exc())
        notification = send_notification(
            "Error processing save results",
            "error",
            duration=5,
        )
        raise ToastException(notification) from e

    # Check if the save was successful
    notification = send_notification(
        f"Results saved successfully to {checkpoint_file}",
        "success",
        duration=5,
    )(toast_data)
    logger.info("Results saved successfully")
    return notification


# Toogle checkpoint panel visibility
@app.callback(
    Output("checkpoint-collapse", "is_open"),
    [Input("checkpoint-toggle", "value")],
    prevent_initial_call=True,
)
def toggle_checkpoint_panel(show_checkpoint):
    """Toggle the visibility of the checkpoint panel"""
    status = "on" if show_checkpoint else "off"
    logger.debug(f"Toggle {status} checkpoint panel")
    return show_checkpoint
