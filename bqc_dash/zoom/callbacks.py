from dash import Input, Output, State, ctx, clientside_callback
from dash.exceptions import PreventUpdate

from bqc_dash.app import app
from bqc_dash.logger import logger


# Zoom level callback from slider
@app.callback(
    Output("zoom-level-store", "data", allow_duplicate=True),
    [Input("zoom-slider", "value")],
    prevent_initial_call=True,
)
def update_zoom_from_slider(slider_value):
    """Update zoom from slider changes"""
    logger.debug("Update zoom from slider")
    return slider_value


# Update slider when zoom level changes (from buttons only)
@app.callback(
    Output("zoom-slider", "value"),
    [Input("zoom-level-store", "data")],
    prevent_initial_call=True,
)
def update_slider(zoom_level):
    """Update slider to match zoom level"""
    logger.debug("Start update_slider")
    return zoom_level


# Toggle zoom panel visibility
@app.callback(
    Output("zoom-collapse", "is_open"),
    [Input("zoom-toggle", "value")],
    prevent_initial_call=True,
)
def toggle_zoom_panel(show_zoom):
    """Toggle the visibility of the zoom panel"""
    status = "on" if show_zoom else "off"
    logger.debug(f"Toggle {status} zoom panel")
    return show_zoom


@app.callback(
    Output("zoom-out-btn", "n_clicks"),
    [Input("zoom-out-btn-key", "n_keydowns")],
    [State("zoom-out-btn", "n_clicks")],
    prevent_initial_call=True,
)
def zoom_out_btn_listener(event, current_clicks):
    """Handle keydown event for zoom out button"""
    logger.debug("Zoom out button triggered")
    # Initialize clicks if None
    if current_clicks is None:
        current_clicks = 0

    if event:
        return current_clicks + 1

    # Return unchanged if no event
    return current_clicks


@app.callback(
    Output("zoom-in-btn", "n_clicks"),
    [Input("zoom-in-btn-key", "n_keydowns")],
    [State("zoom-in-btn", "n_clicks")],
    prevent_initial_call=True,
)
def zoom_in_btn_listener(event, current_clicks):
    """Handle keydown event for zoom out button"""
    logger.debug("Zoom in button triggered")

    # Initialize clicks if None
    if current_clicks is None:
        current_clicks = 0

    if event:
        return current_clicks + 1

    # Return unchanged if no event
    return current_clicks


@app.callback(
    Output("zoom-reset-btn", "n_clicks"),
    [Input("zoom-reset-btn-key", "n_keydowns")],
    [State("zoom-reset-btn", "n_clicks")],
    prevent_initial_call=True,
)
def zoom_reset_btn_listener(event, current_clicks):
    """Handle keydown event for zoom reset button"""
    logger.debug("Zoom reset button triggered")

    # Initialize clicks if None
    if current_clicks is None:
        current_clicks = 0

    if event:
        return current_clicks + 1

    # Return unchanged if no event
    return current_clicks


# Zoom level callback from buttons
@app.callback(
    Output("zoom-level-store", "data", allow_duplicate=True),
    [
        Input("zoom-in-btn", "n_clicks"),
        Input("zoom-out-btn", "n_clicks"),
        Input("zoom-reset-btn", "n_clicks"),
    ],
    [State("zoom-level-store", "data")],
    prevent_initial_call=True,
)
def update_zoom_from_buttons(zoom_in, zoom_out, zoom_reset, current_zoom):
    """Update zoom from button clicks"""

    trigger = ctx.triggered_id
    if not trigger:
        raise PreventUpdate

    logger.debug("Update zoom's buttons")

    if trigger == "zoom-in-btn":
        logger.debug("Zoom in button clicked")
        return min(200, current_zoom + 10)
    elif trigger == "zoom-out-btn":
        logger.debug("Zoom out button clicked")
        return max(50, current_zoom - 10)
    elif trigger == "zoom-reset-btn":
        logger.debug("Zoom reset button clicked")
        return 100

    raise PreventUpdate


@app.callback(
    [
        Output("image-display-viewer", "style"),
        Output("gif-display-viewer", "style"),
    ],
    Input("zoom-level-store", "data"),
    [State("image-display-viewer", "style"), State("gif-display-viewer", "style")],
    prevent_initial_call=True,
)
def update_image_zoom(zoom_level, image_style, gif_style):
    """Update the zoom level of the image and gif viewers"""
    if zoom_level is None:
        raise PreventUpdate

    logger.debug(f"Update image zoom to {zoom_level}%")

    # Initialize styles if they're None
    image_style = image_style or {}
    gif_style = gif_style or {}

    # Calculate the width ratio based on zoom level
    # At 100% zoom, maintain the original 8:4 ratio
    if zoom_level == 100:
        image_width = 66.67  # 8/12 * 100%
        gif_width = 33.33  # 4/12 * 100%
    else:
        # Adjust the ratio based on zoom level
        # Increase image width and decrease gif width when zooming in
        # Base ratio is 2:1 (8:4) at 100% zoom
        ratio_factor = zoom_level / 100
        total_width = 100  # Total percentage width

        # Calculate proportional widths
        base_image_ratio = 2 / 3  # 8/12

        # Adjust ratio based on zoom (increase image portion when zooming in)
        adjusted_image_ratio = min(0.85, base_image_ratio * ratio_factor)  # Cap at 85%

        image_width = adjusted_image_ratio * total_width
        gif_width = total_width - image_width

    # Update the styles with the new widths
    image_style.update({"width": f"{image_width}%", "transition": "width 0.3s ease"})
    gif_style.update({"width": f"{gif_width}%", "transition": "width 0.3s ease"})

    return image_style, gif_style
