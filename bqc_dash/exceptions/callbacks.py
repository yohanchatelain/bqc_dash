import traceback

from dash import set_props

from bqc_dash.app import app
from bqc_dash.logger import logger
from bqc_dash.toaster.callbacks import send_notification


def exception_callback(exception):
    """Handle exceptions and display them in a toast"""
    logger.debug("Start exception_callback")
    toast_data = exception.toast
    # if exception is Warning, log it as a warning
    if isinstance(exception, Warning):
        logger.warning(f"Warning: {exception}")
        warning_toast = send_notification(
            f"Warning: {exception}",
            "warning",
            duration=5,
        )(toast_data)
        set_props("toast-store", {"data": warning_toast})
    elif exception:
        logger.error(f"Exception: {exception}")
        logger.error(traceback.format_exc())
        error_toast = send_notification(
            f"Error: {exception}",
            "danger",
            duration=30,
        )(toast_data)
        set_props("toast-store", {"data": error_toast})
