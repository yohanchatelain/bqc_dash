from dash import html


def Kbd(
    children, size="md", color="gray", style=None, className=None, id=None, **kwargs
):
    """
    A keyboard key component for Dash applications, similar to Mantine's KBD component.

    Parameters:
    ----------
    children : str or list
        The content to display inside the keyboard key.
    size : str, optional (default "md")
        Size of the keyboard key. One of: "xs", "sm", "md", "lg", "xl".
    color : str, optional (default "gray")
        Color scheme. One of: "gray", "dark", "blue", "red", "green".
    style : dict, optional
        Additional inline styles to apply.
    className : str, optional
        Additional CSS classes to apply.
    id : str, optional
        Component ID for callbacks.
    """
    # Size variants
    sizes = {
        "xs": {"fontSize": "10px", "height": "16px", "padding": "0 4px"},
        "sm": {"fontSize": "11px", "height": "18px", "padding": "0 5px"},
        "md": {"fontSize": "12px", "height": "20px", "padding": "0 6px"},
        "lg": {"fontSize": "14px", "height": "24px", "padding": "0 8px"},
        "xl": {"fontSize": "16px", "height": "28px", "padding": "0 10px"},
    }

    # Color variants
    colors = {
        "gray": {
            "backgroundColor": "#f8f9fa",
            "borderColor": "#dee2e6",
            "color": "#212529",
        },
        "dark": {
            "backgroundColor": "#343a40",
            "borderColor": "#212529",
            "color": "#ffffff",
        },
        "blue": {
            "backgroundColor": "#e7f5ff",
            "borderColor": "#74c0fc",
            "color": "#1864ab",
        },
        "red": {
            "backgroundColor": "#fff5f5",
            "borderColor": "#ff8787",
            "color": "#c92a2a",
        },
        "green": {
            "backgroundColor": "#ebfbee",
            "borderColor": "#69db7c",
            "color": "#2b8a3e",
        },
    }

    # Base styles
    base_style = {
        "display": "inline-flex",
        "alignItems": "center",
        "justifyContent": "center",
        "borderWidth": "1px",
        "borderStyle": "solid",
        "borderBottomWidth": "2px",
        "borderRadius": "3px",
        "fontFamily": "monospace",
        "fontWeight": "500",
        "boxShadow": "0 1px 1px rgba(0,0,0,0.1)",
        "margin": "0 4px",
        "minWidth": "20px",
        "lineHeight": "1",
        "userSelect": "none",
        **sizes.get(size, sizes["md"]),
        **colors.get(color, colors["gray"]),
        **(style or {}),
    }

    # Build the class name
    full_class_name = "dash-kbd"
    if className:
        full_class_name += f" {className}"

    if id is None:
        id = f"kbd-{size}-{color}-{hex(hash(str(children)))}"

    return html.Span(
        children, style=base_style, className=full_class_name, id=id, **kwargs
    )
