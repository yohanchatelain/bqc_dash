import uuid

import dash
from dash import Input, Output, State
import dash_bootstrap_components as dbc
from flask import Flask

from bqc_dash.logger import logger

theme = dbc.themes.BOOTSTRAP

from bqc_dash.layout.layout import layout

# Initialize Flask server and Dash app
server_flask = Flask("Brain-QC Visualizer")
server_flask.secret_key = "qc_inspection_tool_secret_key"
app = dash.Dash(
    __name__,
    server=server_flask,
    external_stylesheets=[theme],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

server = app.server
app.layout = layout

from bqc_dash.toaster.callbacks import send_notification, ToastException


@app.callback(
    [
        Output("session-id-store", "data"),
        Output("toast-store", "data"),
    ],
    [
        Input("init-trigger", "children"),
    ],
    [
        State("session-id-store", "data"),
        State("toast-store", "data"),
    ],
)
def initialize_session_id(init, current_session_id, toast_data):
    """Initialize session ID"""
    logger.debug(f"Initialize session tab ID: {current_session_id}")

    session_id_key = "session-id"
    if current_session_id is None or session_id_key not in current_session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Initializing new session ID: {session_id}")
    elif session_id_key in current_session_id:
        session_id = current_session_id.get(session_id_key)
        logger.info(f"Using existing session ID: {session_id}")
    else:
        logger.critical("Session ID not found in session data")
        notification = send_notification(
            "Session ID not found in session data",
            "error",
            duration=5,
        )(toast_data)
        raise ToastException(notification)

    notification = send_notification(
        f"Session ID: {session_id}",
        "info",
        duration=5,
    )(toast_data)
    return {"session-id": session_id}, notification


@app.callback(
    [
        Output("tab-id-store", "data"),
        Output("toast-store", "data", allow_duplicate=True),
    ],
    [
        Input("session-id-store", "data"),
    ],
    [
        State("tab-id-store", "data"),
        State("toast-store", "data"),
    ],
    prevent_initial_call=True,
)
def initialize_session_tab_id(init, current_tab_id, toast_data):
    """Initialize session ID"""
    logger.debug(f"Initialize session tab ID: {current_tab_id}")

    tab_id_key = "tab-id"
    if current_tab_id is None or tab_id_key not in current_tab_id:
        tab_id = str(uuid.uuid4())
        logger.info(f"Initializing new tab session ID: {tab_id}")
    elif tab_id_key in current_tab_id:
        tab_id = current_tab_id.get(tab_id_key)
        logger.info(f"Using existing tab session ID: {tab_id}")
    else:
        logger.critical("Tab ID not found in tab data")
        notification = send_notification(
            "Tab ID not found in tab data",
            "error",
            duration=5,
        )(toast_data)
        raise ToastException(notification)

    notification = send_notification(
        f"Tab ID: {tab_id}",
        "info",
        duration=5,
    )(toast_data)

    return {"tab-id": tab_id}, notification


# # Init auto-save path
# @app.callback(
#     Output("auto-save-path", "data"),
#     [Input("auto-save-path", "modified_timestamp")],
#     [State("auto-save-path", "data")],
# )
# def initialize_auto_save_path(ts, current_path):
#     """Initialize auto-save path"""
#     if current_path is None:
#         auto_save_path = f"{session['id']}_auto_save.json"
#         logger.info(f"Initializing new auto-save path: {auto_save_path}")
#         return auto_save_path
#     logger.info(f"Using existing auto-save path: {current_path}")
#     return current_path
