"""
Tkinter styling utilities.

Defines a modern dark‑themed colour palette and configures ttk styles
so every view in the application shares a consistent, polished look.
"""

import tkinter as tk
from tkinter import ttk


# ── Colour Palette ──────────────────────────────────────────────────────
COLORS = {
    "bg_dark":       "#1a1a2e",
    "bg_medium":     "#16213e",
    "bg_light":      "#0f3460",
    "accent":        "#e94560",
    "accent_hover":  "#ff6b6b",
    "text_primary":  "#eaeaea",
    "text_secondary":"#a0a0b0",
    "text_dark":     "#1a1a2e",
    "success":       "#2ecc71",
    "warning":       "#f39c12",
    "danger":        "#e74c3c",
    "card_bg":       "#1e2a4a",
    "entry_bg":      "#243b5e",
    "entry_fg":      "#eaeaea",
    "border":        "#2c3e6b",
    "sidebar_bg":    "#0d1b2a",
    "sidebar_hover": "#1b2838",
    "treeview_bg":   "#162040",
    "treeview_fg":   "#eaeaea",
    "treeview_sel":  "#e94560",
    "heading_bg":    "#0f3460",
}

# ── Font Definitions ────────────────────────────────────────────────────
FONTS = {
    "heading":     ("Segoe UI", 22, "bold"),
    "subheading":  ("Segoe UI", 16, "bold"),
    "body":        ("Segoe UI", 11),
    "body_bold":   ("Segoe UI", 11, "bold"),
    "small":       ("Segoe UI", 9),
    "button":      ("Segoe UI", 11, "bold"),
    "entry":       ("Segoe UI", 11),
    "sidebar":     ("Segoe UI", 12),
    "card_value":  ("Segoe UI", 28, "bold"),
    "card_label":  ("Segoe UI", 10),
}


def configure_styles(root: tk.Tk) -> ttk.Style:
    """
    Apply the application‑wide dark theme to *root* and return the
    configured ``ttk.Style`` object.

    Args:
        root: The main Tk window.

    Returns:
        The ``ttk.Style`` instance (also applied globally).
    """
    root.configure(bg=COLORS["bg_dark"])
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── General ──
    style.configure(".", background=COLORS["bg_dark"], foreground=COLORS["text_primary"],
                     font=FONTS["body"])

    # ── TFrame ──
    style.configure("TFrame", background=COLORS["bg_dark"])
    style.configure("Card.TFrame", background=COLORS["card_bg"],
                     relief="flat", borderwidth=0)
    style.configure("Sidebar.TFrame", background=COLORS["sidebar_bg"])

    # ── TLabel ──
    style.configure("TLabel", background=COLORS["bg_dark"],
                     foreground=COLORS["text_primary"], font=FONTS["body"])
    style.configure("Heading.TLabel", font=FONTS["heading"],
                     foreground=COLORS["text_primary"], background=COLORS["bg_dark"])
    style.configure("Subheading.TLabel", font=FONTS["subheading"],
                     foreground=COLORS["text_primary"], background=COLORS["bg_dark"])
    style.configure("Card.TLabel", background=COLORS["card_bg"],
                     foreground=COLORS["text_primary"])
    style.configure("CardValue.TLabel", background=COLORS["card_bg"],
                     foreground=COLORS["accent"], font=FONTS["card_value"])
    style.configure("CardLabel.TLabel", background=COLORS["card_bg"],
                     foreground=COLORS["text_secondary"], font=FONTS["card_label"])
    style.configure("Sidebar.TLabel", background=COLORS["sidebar_bg"],
                     foreground=COLORS["text_primary"], font=FONTS["sidebar"])
    style.configure("Success.TLabel", foreground=COLORS["success"])
    style.configure("Warning.TLabel", foreground=COLORS["warning"])
    style.configure("Danger.TLabel", foreground=COLORS["danger"])

    # ── TButton ──
    style.configure("TButton", font=FONTS["button"],
                     background=COLORS["accent"], foreground="#ffffff",
                     padding=(16, 8), borderwidth=0)
    style.map("TButton",
              background=[("active", COLORS["accent_hover"]),
                          ("disabled", COLORS["bg_light"])],
              foreground=[("disabled", COLORS["text_secondary"])])

    style.configure("Success.TButton", background=COLORS["success"])
    style.map("Success.TButton",
              background=[("active", "#27ae60")])

    style.configure("Danger.TButton", background=COLORS["danger"])
    style.map("Danger.TButton",
              background=[("active", "#c0392b")])

    style.configure("Sidebar.TButton", font=FONTS["sidebar"],
                     background=COLORS["sidebar_bg"], foreground=COLORS["text_primary"],
                     padding=(20, 12), borderwidth=0, anchor="w")
    style.map("Sidebar.TButton",
              background=[("active", COLORS["sidebar_hover"])])

    # ── TEntry ──
    style.configure("TEntry", font=FONTS["entry"],
                     fieldbackground=COLORS["entry_bg"],
                     foreground=COLORS["entry_fg"],
                     insertcolor=COLORS["text_primary"],
                     borderwidth=1, padding=8)
    style.map("TEntry",
              fieldbackground=[("focus", COLORS["bg_light"])])

    # ── Treeview ──
    style.configure("Treeview",
                     background=COLORS["treeview_bg"],
                     foreground=COLORS["treeview_fg"],
                     fieldbackground=COLORS["treeview_bg"],
                     font=FONTS["body"],
                     rowheight=32,
                     borderwidth=0)
    style.configure("Treeview.Heading",
                     background=COLORS["heading_bg"],
                     foreground=COLORS["text_primary"],
                     font=FONTS["body_bold"],
                     borderwidth=0)
    style.map("Treeview",
              background=[("selected", COLORS["treeview_sel"])],
              foreground=[("selected", "#ffffff")])
    style.map("Treeview.Heading",
              background=[("active", COLORS["bg_light"])])

    # ── Scrollbar ──
    style.configure("Vertical.TScrollbar",
                     background=COLORS["bg_light"],
                     troughcolor=COLORS["bg_dark"],
                     borderwidth=0, arrowsize=14)

    # ── Combobox ──
    style.configure("TCombobox",
                     fieldbackground=COLORS["entry_bg"],
                     foreground=COLORS["entry_fg"],
                     font=FONTS["entry"])
    style.map("TCombobox",
              fieldbackground=[("readonly", COLORS["entry_bg"])])

    # ── Separator ──
    style.configure("TSeparator", background=COLORS["border"])

    return style


# ── Helper widget factories ─────────────────────────────────────────────

def create_card_frame(parent, **kwargs) -> ttk.Frame:
    """Return a styled card frame with rounded‑feel padding."""
    frame = ttk.Frame(parent, style="Card.TFrame", padding=20, **kwargs)
    return frame


def create_styled_button(parent, text: str, command=None,
                          style_name: str = "TButton", **kwargs) -> ttk.Button:
    """Return a themed button wired to *command*."""
    button = ttk.Button(parent, text=text, command=command,
                         style=style_name, **kwargs)
    return button


def create_entry_with_label(parent, label_text: str, show: str = "",
                             row: int = 0) -> tuple[ttk.Label, ttk.Entry]:
    """
    Create a label + entry pair and grid them at *row*.

    Returns:
        ``(label_widget, entry_widget)``
    """
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=0, sticky="w", padx=5, pady=6)
    entry = ttk.Entry(parent, show=show, width=30)
    entry.grid(row=row, column=1, sticky="ew", padx=5, pady=6)
    return label, entry
