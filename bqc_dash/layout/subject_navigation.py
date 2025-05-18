import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_extensions import Keyboard

from bqc_dash.layout.kbd import Kbd

class SubjectNavigationPanel:
    """
    Panel for subject navigation and filtering controls.
    """
    
    # Next Subject button with keyboard shortcut
    next_subject_btn = html.Div(
        [
            Keyboard(
                id="next-subject-key",
                eventProps=["n_keydowns"],
                captureKeys=["PageDown"],
            ),
            dbc.Button(
                "Next Subject",
                id="next-subject-btn",
                color="primary",
                className="me-2",
                disabled=True,
            ),
        ]
    )
    
    # Previous Subject button with keyboard shortcut
    prev_subject_btn = html.Div(
        [
            Keyboard(
                id="prev-subject-key",
                eventProps=["n_keydowns"],
                captureKeys=["PageUp"],
            ),
            dbc.Button(
                "Previous Subject",
                id="prev-subject-btn",
                color="primary",
                className="me-2",
                disabled=True,
            ),
        ]
    )
    
    # Subject filtering control
    subject_filter = dbc.InputGroup(
        [
            dbc.InputGroupText("Filter Subjects"),
            dbc.Input(
                id="subject-filter-input",
                placeholder="Enter pattern (regex supported)",
                type="text",
            ),
            dbc.Button("Apply", id="apply-filter-btn", color="secondary", className="me-1"),
            dbc.Button("Clear", id="clear-filter-btn", color="secondary"),
        ],
        className="mb-2",
    )
    
    # Current subject display
    current_subject = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("Current Subject:"),
                    html.H4(id="current-subject-label", className="card-title"),
                ]
            )
        ],
        className="mb-2",
    )
    
    # Navigation buttons group
    navigation_buttons = dbc.ButtonGroup(
        [
            prev_subject_btn,
            next_subject_btn,
        ],
        className="mb-2",
    )
    
    # Panel layout
    panel = dbc.Card(
        [
            dbc.CardHeader("Subject Navigation"),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(current_subject, width=6),
                            dbc.Col(navigation_buttons, width=6),
                        ]
                    ),
                    dbc.Row(subject_filter),
                    # Add shortcut info
                    dbc.Row(
                        dbc.Alert(
                            [
                                "Keyboard shortcuts: ",
                                Kbd("PageDown"), " Next Subject, ",
                                Kbd("PageUp"), " Previous Subject"
                            ],
                            color="info",
                            className="mt-2 small",
                        )
                    ),
                ]
            ),
        ],
        className="mb-3",
    )

    # Panel layout with toggle
    toggle_panel = dbc.Card(
        [
            dbc.CardHeader(
                [
                    "Subject Navigation",
                    dbc.Switch(
                        id="subject-nav-toggle",
                        value=True,
                        className="float-end",
                    ),
                ]
            ),
            dbc.CardBody(
                [
                    dbc.Collapse(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(current_subject, width=6),
                                    dbc.Col(navigation_buttons, width=6),
                                ]
                            ),
                            dbc.Row(subject_filter),
                            # Add shortcut info
                            dbc.Row(
                                dbc.Alert(
                                    [
                                        "Keyboard shortcuts: ",
                                        Kbd("PageDown"), " Next Subject, ",
                                        Kbd("PageUp"), " Previous Subject"
                                    ],
                                    color="info",
                                    className="mt-2 small",
                                )
                            ),
                        ],
                        id="subject-nav-collapse",
                        is_open=True,
                    ),
                ]
            ),
        ],
        className="mb-3",
    )