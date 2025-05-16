import os
from dash import ctx, Input, Output, State
from dash.exceptions import PreventUpdate
from flask import send_from_directory, abort
import traceback
import dash

from bqc_dash.logger import logger
from bqc_dash.app import app, server

from bqc_dash.utils import get_information_from_path, get_gif_path
from bqc_dash.exceptions.callbacks import exception_callback
from bqc_dash.toaster.callbacks import send_notification, ToastException


# GIF route using session
@server.route("/gifs/<session_id>/<tab_id>/<path:input_dir>/<path:gif_path>")
def serve_gif(session_id, tab_id, input_dir, gif_path):
    """Serve GIF file from filesystem using session input_dir"""
    try:
        logger.debug(
            f"Serve GIF route /gifs/{session_id}/{tab_id}/{input_dir}/{gif_path}"
        )
        logger.debug(f"Session ID: {session_id}")
        logger.debug(f"Tab ID: {tab_id}")
        logger.debug(f"Input directory: {input_dir}")
        logger.debug(f"Image path: {gif_path}")

        abs_input_dir = os.path.abspath(input_dir)

        # Construct and serve GIF...
        server_path = os.path.normpath(os.path.join(abs_input_dir, gif_path))
        server_dir, server_name = os.path.split(server_path)

        # Construct the host path
        route_path = f"/gifs/{session_id}/{tab_id}/{input_dir}/{gif_path}"
        host_path = os.path.normpath(route_path)

        if not os.path.exists(server_path) or not os.path.isfile(server_path):
            abort(404)

        logger.debug(f"Serving GIF: {server_path}")
        logger.debug(f"Host GIF {host_path}")

        return send_from_directory(server_dir, server_name), host_path

    except Exception as e:
        logger.error(f"Error serving GIF: {str(e)}")
        logger.error("\n" + traceback.format_exc())
        abort(500)


# Get image from cache or load it
@server.route("/images/<session_id>/<tab_id>/<path:input_dir>/<path:img_path>")
def serve_image(session_id, tab_id, input_dir, img_path):
    """Serve image file from filesystem"""
    logger.debug(
        f"Serve image route /images/{session_id}/{tab_id}/{input_dir}/{img_path}"
    )
    logger.debug(f"Session ID: {session_id}")
    logger.debug(f"Tab ID: {tab_id}")
    logger.debug(f"Image path: {img_path}")
    logger.debug(f"Input directory: {input_dir}")

    try:
        base_dir = os.path.abspath(input_dir)

        # get relative if absolute path
        if os.path.isabs(img_path):
            img_path = "." + img_path

        # Construct the full path and normalize it
        full_path = os.path.normpath(os.path.join(base_dir, img_path))
        server_dir, server_name = os.path.split(full_path)

        # Security check: ensure the requested file is within the base directory
        if not os.path.commonpath([base_dir, full_path]) == base_dir:
            logger.error("Directory traversal attempt detected")
            abort(403)  # Forbidden - prevent directory traversal

        # Verify file exists
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            logger.error(f"File not found: {full_path}")
            abort(404)  # Not found

        route_path = f"/images/{session_id}/{tab_id}/{input_dir}/{img_path}"
        host_path = os.path.normpath(route_path)

        logger.debug(f"Serving image: {full_path}")
        logger.debug(f"Host image {host_path}")

        # Return the image with proper content type
        return send_from_directory(server_dir, server_name), host_path

    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        logger.error("\n" + traceback.format_exc())
        abort(500)  # Internal server error


@app.callback(
    [
        Output("image-display", "src"),
        Output("gif-display", "src"),
        Output("toast-store", "data", allow_duplicate=True),
    ],
    [Input("current-index-store", "data")],
    [
        State("images-path-store", "data"),
        State("input-dir-store", "data"),
        State("session-id-store", "data"),
        State("tab-id-store", "data"),
        State("toast-store", "data"),
    ],
    prevent_initial_call=True,
    on_error=exception_callback,
)
def load_images(current_index, images_path, input_dir, session_id, tab_id, toast_data):
    """Load image and GIF sources based on current index"""
    logger.debug("Start load_images")
    # Skip if no images are loaded
    if (
        images_path is None
        or len(images_path) == 0
        or current_index >= len(images_path)
        or current_index is None
        or not input_dir
    ):
        logger.warning("No images to load")
        raise PreventUpdate
    try:
        # Get current image info
        image_path = images_path[current_index]

        logger.debug("Loading images")
        logger.debug(f"Current index: {current_index}")
        logger.debug(f"Input directory: {input_dir}")
        logger.debug(f"Image path: {image_path}")

        # Get session ID
        session_id = session_id.get("session-id")
        tab_id = tab_id.get("tab-id")
        (subject, image_name, repetition) = get_information_from_path(
            input_dir, image_path
        )

        # Get image sources (from cache or load if needed)
        response_img, img_src = serve_image(session_id, tab_id, input_dir, image_path)
        if response_img.status_code != 200:
            logger.error(f"Error loading image: {response_img.status_code}")
            img_src = ""

        gif_path = get_gif_path(input_dir, image_path)
        response_gif, gif_src = serve_gif(session_id, tab_id, input_dir, gif_path)
        if response_gif.status_code != 200:
            logger.error(f"Error loading GIF: {response_gif.status_code}")
            gif_src = ""

        logger.debug(f"Host image: {img_src}")
        logger.debug(f"Host gif: {gif_src}")
    except Exception as e:
        toast = send_notification(
            str(e),
            "danger",
            5000,
        )(toast_data)
        raise ToastException(toast) from e

    return img_src, gif_src, dash.no_update


@app.callback(
    Output("images-path-len-store", "data"),
    [Input("images-path-store", "data")],
    prevent_initial_call=True,
)
def update_images_path_len(images_path):
    """Update the length of the images path store"""
    logger.debug("Update images path length component")
    if images_path:
        logger.debug(f"Images path length: {len(images_path)}")
        return len(images_path)

    logger.warning("No images path found")
    return None


@app.callback(
    [
        Output("subject-label", "children"),
        Output("image-name-label", "children"),
        Output("repetition-label", "children"),
        Output("progress-label", "children"),
    ],
    [Input("current-index-store", "data")],
    [State("images-path-store", "data"), State("input-dir-store", "data")],
    prevent_initial_call=True,
)
def update_image_info_ui(current_index, images_path, input_dir):
    """Update image information based on current index"""
    logger.debug("Update image information UI")
    # Skip if no images are loaded
    if (
        images_path is None
        or current_index is None
        or len(images_path) == 0
        or current_index >= len(images_path)
    ):
        return "No subject", "No image", "No repetition", "0/0"

    # Get current image info
    image_path = images_path[current_index]
    (subject, image_name, repetition) = get_information_from_path(input_dir, image_path)

    return subject, image_name, repetition, f"{current_index + 1}/{len(images_path)}"


@app.callback(
    Output("next-img-btn", "n_clicks"),
    [Input("next-btn-key", "n_keydowns")],
    [State("next-img-btn", "n_clicks")],
    prevent_initial_call=True,
)
def next_img_btn_listener(event, current_clicks):
    """Handle keydown event for next image button"""
    logger.debug("Next image event triggered")

    # Initialize clicks if None
    if current_clicks is None:
        current_clicks = 0

    if event:
        return current_clicks + 1

    # Return unchanged if no event
    return current_clicks


@app.callback(
    Output("prev-img-btn", "n_clicks"),
    [Input("prev-btn-key", "n_keydowns")],
    [State("prev-img-btn", "n_clicks")],
    prevent_initial_call=True,
)
def prev_img_btn_listener(event, current_clicks):
    """Handle keydown event for previous image button"""
    logger.debug("Prev image event triggered")

    # Initialize clicks if None
    if current_clicks is None:
        current_clicks = 0

    if event:
        return current_clicks + 1

    # Return unchanged if no event
    return current_clicks


@app.callback(
    Output("current-index-store", "data"),
    [
        Input("prev-img-btn", "n_clicks"),
        Input("next-img-btn", "n_clicks"),
        Input("images-path-len-store", "data"),
    ],
    [State("current-index-store", "data")],
    prevent_initial_call=True,
)
def update_navigation(prev_clicks, next_clicks, images_path_len, current_index):
    """Handle navigation between images"""
    logger.debug("Update navigation")
    # Skip if no images are loaded
    if images_path_len == 0:
        raise PreventUpdate

    # Determine which button was clicked
    trigger = ctx.triggered_id
    if trigger is None:
        raise PreventUpdate

    # Calculate new index
    if current_index is None and images_path_len is None:
        logger.warning("No current index found")
        raise PreventUpdate
    elif trigger == "next-img-btn":
        logger.debug("Next image button clicked")
        return (current_index + 1) % images_path_len
    elif trigger == "prev-img-btn":
        logger.debug("Previous image button clicked")
        return (current_index - 1) % images_path_len
    elif images_path_len > 0 and current_index is None:
        # Trigger to reload images at the end of the scan
        logger.debug("Trigger to reload images at the end of the scan")
        # Set current index to 0
        return 0
    else:
        # Index didn't change (at beginning or end)
        raise PreventUpdate


@app.callback(
    [Output("image-display-viewer", "width"), Output("gif-display-viewer", "width")],
    [Input("swap-view-btn", "n_clicks")],
    [State("image-display-viewer", "width"), State("gif-display-viewer", "width")],
    prevent_initial_call=True,
)
def swap_image_gif_viewer(n_clicks, image_width, gif_width):
    """Swap the order of image and GIF display"""
    logger.debug("Swap image and GIF display order")
    if n_clicks is None:
        raise PreventUpdate

    order_image = image_width.get("order")
    order_gif = gif_width.get("order")

    return {"order": order_gif, "size": image_width.get("size")}, {
        "order": order_image,
        "size": gif_width.get("size"),
    }
