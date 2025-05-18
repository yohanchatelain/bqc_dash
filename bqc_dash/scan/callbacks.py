import os
import traceback

import dash
from dash import Input, Output, State, callback_context, html, dcc
from dash.exceptions import PreventUpdate
from flask import session

from bqc_dash.app import app
from bqc_dash.logger import logger
from bqc_dash.exceptions.callbacks import exception_callback
from bqc_dash.toaster.callbacks import send_notification, ToastException
from bqc_dash.scan.fast_scanner import FastDirectoryScanner

# Create a global scanner object for reuse
scanner = FastDirectoryScanner()

@app.callback(
    Output("input-dir-store", "data", allow_duplicate=True),
    [Input("scan-btn", "n_clicks")],
    [State("input-dir", "value"), State("tab-id-store", "data")],
    prevent_initial_call=True,
)
def update_input_dir(n_clicks, input_dir, tab_id):
    """Update the input directory in the store"""
    logger.debug("Start update_input_dir")
    if not n_clicks or not input_dir:
        logger.debug("No input directory provided.")
        raise PreventUpdate

    logger.debug(f"Input directory: {input_dir}")
    return input_dir


@app.callback(
    Output("launch-scan", "data"),
    [
        Input("input-dir-store", "data"),
        Input("subject-filter-input", "value"),
        Input("apply-filter-btn", "n_clicks")
    ],
    prevent_initial_call=True,
)
def set_scan_ready(input_dir, subject_filter, filter_clicks):
    """Set scan-ready flag when input-dir-store is updated or filter is applied"""
    logger.debug("Set scan ready")
    
    # Determine which input triggered the callback
    trigger = callback_context.triggered[0]['prop_id'] if callback_context.triggered else None
    
    if not input_dir:
        logger.warning("No input directory provided")
        raise PreventUpdate
    
    # Only trigger a scan if directory changed or filter applied
    if trigger in ["input-dir-store.data", "apply-filter-btn.n_clicks"]:
        logger.debug(f"Scan is ready with filter: {subject_filter}")
        return True
    
    raise PreventUpdate


@app.callback(
    [
        Output("images-path-store", "data", allow_duplicate=True),
        Output("toast-store", "data", allow_duplicate=True),
        Output("subject-list-store", "data"),
        Output("current-filter-store", "data"),
    ],
    [Input("launch-scan", "data")],
    [
        State("input-dir-store", "data"),
        State("load-checkpoint", "data"),
        State("toast-store", "data"),
        State("subject-filter-input", "value"),
    ],
    prevent_initial_call=True,
    running=[
        (Output("scan-btn", "disabled"), True, False),
        (Output("loading-scan", "display"), "show", "hide"),
        (Output("apply-filter-btn", "disabled"), True, False),
    ],
    on_error=exception_callback,
)
def scan_directory_data(launch_scan, input_dir, is_loading_checkpoint, toast_data, subject_filter):
    logger.debug(f"Scan directory data: {input_dir}, filter: {subject_filter}")

    if not launch_scan:
        logger.debug("No scan launched")
        raise PreventUpdate

    if not os.path.exists(input_dir):
        logger.error("Input directory does not exist")
        notification = send_notification(
            "Input directory does not exist",
            "danger", 
            5
        )(toast_data)
        return dash.no_update, notification, [], None

    if is_loading_checkpoint:
        logger.debug("Loading checkpoint, skipping scan")
        raise PreventUpdate

    try:
        # Use the fast scanner to scan the directory
        images_path = scanner.scan_directory(input_dir, subject_filter)
        
        if not images_path:
            notification = send_notification(
                "No images found in the input directory",
                "warning",
                5
            )(toast_data)
            return dash.no_update, notification, [], subject_filter

        # Get statistics
        number_images = len(images_path)
        number_subjects = len(scanner.subject_list)
        filtered_msg = " after filtering" if subject_filter else ""
        
        status = f"Found {number_images} images across {number_subjects} subjects{filtered_msg}."
        notification = send_notification(
            status,
            "success",
            duration=5,
        )(toast_data)

        # Return the image paths and notification
        return images_path, notification, scanner.subject_list, subject_filter

    except Exception as e:
        logger.critical(f"Error scanning directory: {input_dir}")
        logger.critical(traceback.format_exc())
        notification = send_notification(
            f"Error scanning directory: {str(e)}",
            "danger",
            30
        )(toast_data)
        raise ToastException(notification) from e


@app.callback(
    Output("subject-filter-input", "value"),
    [Input("clear-filter-btn", "n_clicks")],
    prevent_initial_call=True
)
def clear_subject_filter(n_clicks):
    """Clear the subject filter input"""
    if n_clicks:
        return ""
    raise PreventUpdate


@app.callback(
    [
        Output("next-subject-btn", "disabled"),
        Output("prev-subject-btn", "disabled"),
    ],
    [Input("current-index-store", "data")],
    [State("images-path-store", "data")],
    prevent_initial_call=True,
)
def update_subject_navigation_buttons(current_index, images_path):
    """Enable/disable subject navigation buttons based on current position"""
    if current_index is None or not images_path:
        return True, True
    
    # Check if we can move to next/prev subject
    next_subject_idx = scanner.get_next_subject_index(current_index)
    prev_subject_idx = scanner.get_prev_subject_index(current_index)
    
    return next_subject_idx is None, prev_subject_idx is None


@app.callback(
    Output("current-subject-label", "children"),
    [Input("current-index-store", "data")],
    prevent_initial_call=True,
)
def update_current_subject(current_index):
    """Update the current subject label"""
    if current_index is None:
        return "No subject"
    
    current_subject = scanner.get_subject_at_index(current_index)
    return current_subject or "No subject"


@app.callback(
    Output("current-index-store", "data", allow_duplicate=True),
    [
        Input("next-subject-btn", "n_clicks"),
        Input("prev-subject-btn", "n_clicks"),
        Input("next-subject-key", "n_keydowns"),
        Input("prev-subject-key", "n_keydowns"),
    ],
    [State("current-index-store", "data")],
    prevent_initial_call=True,
)
def handle_subject_navigation(next_clicks, prev_clicks, next_keys, prev_keys, current_index):
    """Handle navigation between subjects"""
    logger.debug("Handle subject navigation")
    
    # Get the ID of the component that triggered the callback
    trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if current_index is None:
        raise PreventUpdate
    
    # Navigate to next or previous subject
    if trigger_id in ["next-subject-btn", "next-subject-key"]:
        logger.debug("Moving to next subject")
        next_idx = scanner.get_next_subject_index(current_index)
        if next_idx is not None:
            return next_idx
    elif trigger_id in ["prev-subject-btn", "prev-subject-key"]:
        logger.debug("Moving to previous subject")
        prev_idx = scanner.get_prev_subject_index(current_index)
        if prev_idx is not None:
            return prev_idx
    
    # If we couldn't navigate, prevent update
    raise PreventUpdate