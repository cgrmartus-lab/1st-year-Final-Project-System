import flet as ft

#Colour Palette
BG         = "#FFF8F0"
SURFACE    = "#FFFFFF"
CARD       = "#FFFDF9"
PRIMARY    = "#D4430A"
PRIMARY_LT = "#F4794A"
ACCENT     = "#F5A623"
TEXT_DARK  = "#2C1810"
TEXT_MID   = "#7A5C4F"
TEXT_LIGHT = "#BFA89A"
SUCCESS    = "#3D8B37"
DANGER     = "#C0392B"
BORDER     = "#E8D5C4"
INFO       = "#2471A3"

#FONTS
FONT_HEAD = "Georgia"
FONT_BODY = "Verdana"

#Data lists
CATEGORIES = [
    "Beverages", "Snacks", "Canned Goods", "Personal Care",
    "Condiments", "Dairy", "Frozen", "Household",
    "Tobacco Products", "Others",
]

ROLES = ["admin", "staff", "viewer"]


#Widget helpers
def make_textfield(label: str, ref, hint: str = "",
                   keyboard=ft.KeyboardType.TEXT,
                   width: int = 180,
                   password: bool = False) -> ft.TextField:
    return ft.TextField(
        ref=ref,
        label=label,
        hint_text=hint,
        keyboard_type=keyboard,
        width=width,
        password=password,
        can_reveal_password=password,
        text_style=ft.TextStyle(font_family=FONT_BODY, color=TEXT_DARK, size=12),
        label_style=ft.TextStyle(color=TEXT_MID, size=11, font_family=FONT_BODY),
        border_color=BORDER,
        focused_border_color=PRIMARY,
        filled=True,
        fill_color=SURFACE,
        border_radius=8,
        content_padding=10,
    )


def make_card(content, margin=None) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=CARD,
        border_radius=12,
        border=ft.Border(
            top=ft.BorderSide(1, BORDER),
            right=ft.BorderSide(1, BORDER),
            bottom=ft.BorderSide(1, BORDER),
            left=ft.BorderSide(1, BORDER),
        ),
        shadow=ft.BoxShadow(
            blur_radius=8,
            color="#18000000",
            offset=ft.Offset(0, 2),
        ),
        padding=16,
        margin=margin,
    )
