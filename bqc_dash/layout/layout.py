import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_extensions import Keyboard
import dash_mantine_components as dmc

from bqc_dash.layout.kbd import Kbd


class AbstractPanel:
    """
    Abstract class for creating panels.
    """

    panel = None

    @classmethod
    def get(cls):
        """
        Returns the panel.
        """
        if cls.panel is None:
            raise NotImplementedError(
                f"Panel not implemented. Please create a panel for class {cls.__name__}."
            )
        return cls.panel


# Information panel
def get_info_item(label, value):
    return dbc.ListGroupItem(
        [
            html.Strong(label),
            html.Span(id=value),
        ],
        style={"white-space": "nowrap"},
    )


def get_keyboard_shortcut_item(labels, description, active=False):
    if isinstance(labels, str):
        labels_kbd = [Kbd(labels)]
    elif isinstance(labels, list):
        labels_kbd = sum([[Kbd(label), " / "] for label in labels], start=[])[:-1]
    msg = labels_kbd + [" : ", description]
    return dbc.ListGroupItem(html.P(msg), active=active)


# Zoom panel for image controls
class ZoomPanel:
    """
    Empty class to hold zoom panel components.
    """

    zoom_out_btn = html.Div(
        [
            Keyboard(
                id="zoom-out-btn-key",
                eventProps=["n_keydowns"],
                captureKeys=["-"],
            ),
            dbc.Button(
                "Zoom Out",
                id="zoom-out-btn",
                color="secondary",
                className="me-2",
            ),
        ]
    )

    zoom_in_btn = html.Div(
        [
            Keyboard(
                id="zoom-in-btn-key",
                eventProps=["n_keydowns"],
                captureKeys=["+"],
            ),
            dbc.Button(
                "Zoom In",
                id="zoom-in-btn",
                color="secondary",
                className="me-2",
            ),
        ]
    )

    zoom_reset_btn = html.Div(
        [
            Keyboard(
                id="zoom-reset-btn-key",
                eventProps=["n_keydowns"],
                captureKeys=["0"],
            ),
            dbc.Button(
                "Zoom Reset",
                id="zoom-reset-btn",
                color="secondary",
                className="me-2",
            ),
        ]
    )

    zoom_slider = dcc.Slider(
        id="zoom-slider",
        min=50,
        max=200,
        step=10,
        value=100,
        marks={i: f"{i}%" for i in range(50, 201, 50)},
        className="mt-1",
    )

    zoom_btns = dbc.ButtonGroup(
        [
            zoom_out_btn,
            zoom_in_btn,
            zoom_reset_btn,
        ]
    )

    header = dbc.CardHeader(
        [
            "Image Zoom Controls",
            dbc.Switch(
                id="zoom-toggle",
                value=False,
                className="float-end",
            ),
        ]
    )

    body = dbc.CardBody(
        [
            dbc.Collapse(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(zoom_btns),
                                dbc.Col(zoom_slider),
                            ]
                        ),
                    ]
                ),
                id="zoom-collapse",
                is_open=False,
            ),
        ]
    )

    panel = dbc.Card(
        [header, body],
        className="mb-2",
    )


# Scan input directory
class ScanInputDir:
    """
    Empty class to hold scan input directory components.
    """

    input_dir_input = [
        dbc.Input(
            id="input-dir",
            placeholder="Enter directory path",
            type="text",
        ),
        dcc.Store(
            id="input-dir-store",
            data="",
            storage_type="session",
        ),
    ]

    scan_dir_btn = dbc.Button(
        "Scan Directory",
        id="scan-btn",
        color="secondary",
    )

    scan_dir_loading = html.Div(
        dcc.Loading(
            id="loading-scan",
            type="dot",
            overlay_style={"visibility": "visible", "filter": "blur(2px)"},
            children=[
                html.Div(
                    scan_dir_btn,
                    className="d-flex align-items-center",
                )
            ],
        ),
        className="d-flex align-items-center",
    )

    # Scan input directory
    panel = (
        dbc.Card(
            [
                dbc.CardHeader("Select Input Directory"),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(input_dir_input),
                                dbc.Col(scan_dir_loading),
                            ],
                        ),
                    ],
                ),
            ],
            class_name="mb-2",
        ),
    )


class CheckpointPanel:
    """
    Empty class to hold checkpoint panel components.
    """

    checkpoint_inputs = dbc.Input(
        "checkpoint-file-input",
        type="text",
        placeholder="Checkpoint file path",
    )

    save_button = dbc.Button(
        "Save Checkpoint",
        id="save-checkpoint-btn",
        color="light",
        style={"whiteSpace": "nowrap"},
    )

    load_button = dbc.Button(
        "Load Checkpoint",
        id="load-checkpoint-btn",
        color="light",
        style={"whiteSpace": "nowrap"},
    )

    save_results_button = dbc.Button(
        "Save Results",
        id="save-results-btn",
        color="success",
        style={"whiteSpace": "nowrap"},
    )

    header = dbc.CardHeader(
        [
            "Checkpoint Controls",
            dbc.Switch(
                id="checkpoint-toggle",
                value=False,
                className="float-end",
            ),
        ]
    )

    body = dbc.Collapse(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(checkpoint_inputs, width=4),
                        dbc.Col(save_button, width="auto"),
                        dbc.Col(load_button, width="auto"),
                        dbc.Col(save_results_button, width="auto"),
                    ],
                    class_name="g-2",
                    justify="start",
                ),
            ]
        ),
        id="checkpoint-collapse",
        is_open=True,
    )

    panel = dbc.Card(
        [
            header,
            body,
        ],
        class_name="mb-2",
    )


# Performance monitoring toggle
class PerformancePanel:
    """
    Empty class to hold performance panel components.
    """

    header = dbc.CardHeader(
        [
            "Performance Monitoring",
            dbc.Switch(
                id="perf-toggle",
                value=False,
                className="float-end",
            ),
        ]
    )
    body = dbc.Collapse(
        dbc.CardBody(
            [
                html.Div(id="perf-metrics"),
            ]
        ),
        id="perf-collapse",
        is_open=False,
    )
    panel = dbc.Card(
        [
            header,
            body,
        ],
        className="mb-2",
    )


class GifPanel:
    """
    Empty class to hold GIF panel components.
    """

    # GIF display panel
    header = dbc.CardHeader(
        [
            "GIF Preview",
            dbc.Switch(
                id="gif-toggle",
                value=False,
                className="float-end",
            ),
        ]
    )

    body = dbc.Collapse(
        dbc.CardImg(
            id="gif-display",
            class_name="rounded center",
            style={
                "object-fit": "scale-down",  # Prevents image resizing
            },
        ),
        id="gif-collapse",
        is_open=True,
    )

    panel = dbc.Card(
        [
            header,
            body,
        ],
        class_name="d-flex justify-content-center",  # Center the GIF
    )


class InformationPanel:
    info_list = dbc.ListGroup(
        [
            get_info_item("Subject ", "subject-label"),
            get_info_item("Image ", "image-name-label"),
            get_info_item("Repetition ", "repetition-label"),
            get_info_item("Progress ", "progress-label"),
            dbc.ListGroupItem(id="status-label"),
        ],
        horizontal=True,
    )

    header = dbc.CardHeader(
        [
            "Information",
            dbc.Switch(
                id="info-toggle",
                value=True,
                className="float-end",
            ),
        ]
    )

    body = dbc.CardBody(
        [
            dbc.Collapse(
                info_list,
                id="info-collapse",
                is_open=True,
            ),
        ]
    )

    panel = dbc.Card(
        [
            # header,
            body,
        ],
        className="mb-2",
    )


class KeyboardPanel:
    """
    Empty class to hold keyboard panel components.
    """

    keyboard_list = dbc.ListGroup(
        [
            dbc.ListGroupItem(
                html.Span("Keyboard Shortcuts"),
                active=True,
            ),
            get_keyboard_shortcut_item("←", "Previous"),
            get_keyboard_shortcut_item("→", "Navigate images"),
            get_keyboard_shortcut_item("PageUp", "Previous subject"),
            get_keyboard_shortcut_item("PageDown", "Next subject"),
            get_keyboard_shortcut_item(["␣", "⏎"], "Toggle rejection status"),
            get_keyboard_shortcut_item("+", "Zoom out"),
            get_keyboard_shortcut_item("-", "Zoom in"),
            get_keyboard_shortcut_item("0", "Reset zoom"),
        ]
    )

    button = html.Div(
        [
            dbc.Button(
                "Keyboard Shortcuts",
                id="keyboard-shortcuts-btn",
                color="secondary",
                outline=False,
            ),
        ]
    )

    canvas = dbc.Offcanvas(
        keyboard_list,
        id="keyboard-shortcuts-offcanvas",
        title="Keyboard Shortcuts",
        is_open=False,
        scrollable=True,
        backdrop=False,
        placement="end",
    )

    body = html.Div(
        [
            button,
            canvas,
        ]
    )

    panel = dbc.Card(keyboard_list)


class ImageNavPanel:
    """
    Empty class to hold image navigation panel components.
    """

    header = dbc.CardHeader(
        [
            "Image Navigation",
            dbc.Switch(
                id="image-nav-toggle",
                value=True,
                className="float-end",
            ),
        ]
    )

    next_img_btn = html.Div(
        [
            Keyboard(
                id="next-btn-key",
                eventProps=["n_keydowns"],
                captureKeys=["ArrowRight"],
            ),
            dbc.Button(
                "Next Image",
                id="next-img-btn",
                color="secondary",
                outline=True,
            ),
        ]
    )

    prev_img_btn = html.Div(
        [
            Keyboard(
                id="prev-btn-key",
                eventProps=["n_keydowns"],
                captureKeys=["ArrowLeft"],
            ),
            dbc.Button(
                "Previous Image",
                id="prev-img-btn",
                color="secondary",
                outline=True,
            ),
        ]
    )

    toggle_reject_btn = html.Div(
        [
            Keyboard(
                id="toggle-reject-btn-key",
                eventProps=["n_keydowns"],
                captureKeys=["Enter", " "],
            ),
            dbc.Button(
                "Toggle Rejection",
                id="toggle-reject-btn",
                color="warning",
            ),
        ],
    )

    image_nav_btns = dbc.ButtonGroup(
        [
            prev_img_btn,
            next_img_btn,
            toggle_reject_btn,
        ],
        style={"white-space": "nowrap"},
    )


class NavigationPanel:
    panel = dbc.Row(
        [
            dbc.Col(InformationPanel.info_list),
            dbc.Col(
                ImageNavPanel.image_nav_btns,
                className="float-end",
                style={"display": "flex", "justify-content": "flex-end"},
            ),
        ]
    )


class ImageDisplayPanel:
    """
    Empty class to hold image display panel components.
    """

    # image display panel
    header = dbc.CardHeader(
        "Image Display",
    )

    body = dbc.CardBody(
        [
            dbc.Collapse(
                dbc.CardImg(
                    id="image-display",
                    class_name="rounded center",
                    style={
                        "object-fit": "contain",  # Prevents
                    },
                ),
                is_open=True,
                style={
                    "display": "flex",
                    "justify-content": "center",
                    "overflow": "hidden",
                },
            )
        ]
    )

    panel = dbc.Card(
        [
            header,
            body,
        ],
        className="mb-2",  # Add margin to the bottom
    )


# main panel

# Layout


navigation_panel = (
    dbc.Toast(
        NavigationPanel.panel,
        id="info-toast",
        header=None,
        is_open=True,
        dismissable=False,
        # bottom: 10 positions the toast above the footer
        style={"position": "fixed", "bottom": 10, "left": 10, "width": "auto"},
    ),
)

notifications_container = html.Div(
    [
        html.Div(
            id="toast-container",
            className="position-fixed top-0 end-0 p-3",
            style={"z-index": "1050", "max-width": "350px"},
        ),
        dcc.Store(id="toast-store", data={"toasts": []}, storage_type="memory"),
        dcc.Interval(
            id="interval-component", interval=1000, n_intervals=0
        ),  # 1 second interval
    ]
)

layout_header = dbc.NavbarSimple(
    children=[KeyboardPanel.body],
    brand="Brain-QC Visualizer",
    brand_href="/",
    color="primary",
    dark=True,
    class_name="mt-2 mb-2",
    fluid=True,
)

preload_component = html.Img(
    id="next-image-preload",
    style={"display": "none"},  # Hidden from view
)


layout = dbc.Container(
    [
        dbc.Row(dbc.Col(layout_header)),
        # Directory input
        dbc.Row(
            [
                dbc.Col(ScanInputDir.panel, width=4),
                dbc.Col(CheckpointPanel.panel, width=7),
                dbc.Col(
                    dbc.Card(
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Swap view",
                                    id="swap-view-btn",
                                    color="secondary",
                                    className="ms-2 mt-2 mb-2",
                                ),
                            ],
                            width="auto",
                        ),
                    ),
                    width=1,
                ),
            ]
        ),
        # Information panel
        # dbc.Row(dbc.Col(InformationPanel.panel)),
        # Main content
        dbc.Row(
            [
                # Left column with PNG image display
                dbc.Col(
                    [
                        ImageDisplayPanel.panel,
                        # Zoom controls below image
                    ],
                    id="image-display-viewer",
                    width={"size": 8, " order": 1},
                    style={"width": "66.67%"},
                ),
                # Right column with GIF display
                dbc.Col(
                    [
                        GifPanel.panel,
                        # ImageNavPanel.panel,
                    ],
                    id="gif-display-viewer",
                    width={"size": 4, "order": 2},
                    style={"width": "33.33%"},
                ),
            ],
            class_name="g-2",
        ),
        # Zoom panel
        dbc.Row(dbc.Col(ZoomPanel.panel)),
        # Performance monitoring toggle
        dbc.Row(dbc.Col(PerformancePanel.panel)),
        # Hidden divs for storing state
        # dcc.Store(id="scan-status-store", data=False),
        Keyboard(
            id="keybord-listener",
            useCapture=True,
        ),
        Keyboard(
            id="next-subject-key",
            eventProps=["n_keydowns"],
            captureKeys=["PageDown"],
        ),
        Keyboard(
            id="prev-subject-key",
            eventProps=["n_keydowns"],
            captureKeys=["PageUp"],
        ),
        html.Div(id="init-trigger", style={"display": "none"}),
        dcc.Store(id="session-id-store", data=None, storage_type="session"),
        dcc.Store(id="tab-id-store", data=None, storage_type="session"),
        dcc.Store(id="log-store", data=None, storage_type="memory"),
        dcc.Store(id="exception-store", data=None, storage_type="memory"),
        dcc.Store(id="images-path-store", data=None, storage_type="memory"),
        dcc.Store(id="images-path-len-store", data=None, storage_type="memory"),
        dcc.Store(id="rejected-images-store", data=None, storage_type="memory"),
        dcc.Store(id="current-rejected-status-store", data=None, storage_type="memory"),
        dcc.Store(id="current-index-store", data=None, storage_type="memory"),
        dcc.Store(id="zoom-level-store", data=100, storage_type="memory"),
        dcc.Store(id="launch-scan", data=False, storage_type="memory"),
        dcc.Store(id="image-on-right", data=False, storage_type="session"),
        dcc.Store(id="load-checkpoint", data=False, storage_type="memory"),
        dcc.Store(id="subject-list-store", data=None, storage_type="memory"),
        dcc.Store(id="current-filter-store", data=None, storage_type="memory"),
        # Interval for updating performance metrics
        dcc.Interval(
            id="metrics-interval", interval=2000, n_intervals=0, disabled=True
        ),
        # automatic saving
        dcc.Interval(
            id="auto-save-interval",
            interval=10000,
            n_intervals=0,
            disabled=False,
        ),
        dcc.Store(
            id="auto-save-status",
            data=False,
            storage_type="session",
        ),
        dcc.Store(
            id="auto-save-path",
            data=None,
            storage_type="session",
        ),
        html.Div(navigation_panel),
        notifications_container,
        html.Div(preload_component, style={"display": "none"}),
    ],
    fluid=True,
)
