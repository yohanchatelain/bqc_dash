import glob
import os
import traceback
from natsort import natsorted

import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from bqc_dash.app import app
from bqc_dash.logger import logger
from bqc_dash.exceptions.callbacks import exception_callback
from bqc_dash.toaster.callbacks import send_notification, ToastException


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
    [Input("input-dir-store", "data")],
    prevent_initial_call=True,
)
def set_scan_ready(input_dir):
    """Set scan-ready flag when input-dir-store is updated"""
    logger.debug("Set scan ready")
    if not input_dir:
        logger.warning("No input directory provided")
        raise PreventUpdate

    logger.debug("Scan is ready")
    return True


@app.callback(
    [
        Output("images-path-store", "data", allow_duplicate=True),
        Output("toast-store", "data", allow_duplicate=True),
    ],
    [Input("launch-scan", "data")],
    [
        State("input-dir-store", "data"),
        State("load-checkpoint", "data"),
        State("toast-store", "data"),
    ],
    prevent_initial_call=True,
    running=[
        (Output("scan-btn", "disabled"), True, False),
        (Output("loading-scan", "display"), "show", "hide"),
    ],
    on_error=exception_callback,
)
def scan_directory_data(launch_scan, input_dir, is_loading_checkpoint, toast_data):
    logger.debug(f"Scan directory data: {input_dir}")

    if not launch_scan:
        logger.debug("No scan launched")
        raise PreventUpdate

    if not os.path.exists(input_dir):
        logger.error("Input directory does not exist")
        return dash.no_update, "Input directory does not exist", True, "danger"

    if is_loading_checkpoint:
        logger.debug("Loading checkpoint, skipping scan")
        raise PreventUpdate

    try:
        # Empty caches
        subject_gifs = {}
        images_path = []

        # Find all GIF files in the root directory
        gif_files = glob.glob(os.path.join(input_dir, "*.gif"))
        subjects = [os.path.splitext(os.path.basename(f))[0] for f in gif_files]

        # Pre-populate subject_gifs dictionary for faster lookups
        for gif_file in gif_files:
            subject = os.path.splitext(os.path.basename(gif_file))[0]
            subject_gifs[subject] = gif_file

        # For each subject, find all PNG files
        image_re = os.path.join(input_dir, "png", "**", "*.png")
        images_path = [
            path.replace(input_dir, "") for path in glob.glob(image_re, recursive=True)
        ]

        if not images_path:
            return (
                dash.no_update,
                "No images found in the input directory",
                True,
                "warning",
            )

        # Sort images by subject, then image name, then repetition
        number_images = len(images_path)
        number_subjects = len(subjects)
        status = f"Found {number_images} images across {number_subjects} subjects."
        notification = send_notification(
            status,
            "success",
            duration=5,
        )

        images_path = natsorted(images_path)

        return images_path, notification(toast_data)

    except Exception as e:
        logger.critical(f"Error scanning directory: {input_dir}")
        logger.critical(traceback.format_exc())
        raise ToastException(toast_data) from e
