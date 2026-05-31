import flet as ft
from utils.theme import (
    BG, SURFACE, PRIMARY, TEXT_MID, TEXT_LIGHT, DANGER, BORDER,
    FONT_HEAD, FONT_BODY, make_textfield,
)


def build_login_view(page: ft.Page, auth_ctrl, on_login_success) -> ft.View:
    ref_user = ft.Ref[ft.TextField]()
    ref_pass = ft.Ref[ft.TextField]()
    ref_err  = ft.Ref[ft.Text]()

    def do_login(e):
        ok, msg = auth_ctrl.login(
            ref_user.current.value or "",
            ref_pass.current.value or "",
        )
        if ok:
            on_login_success()
        else:
            ref_err.current.value   = msg
            ref_err.current.visible = True
            page.update()

    def on_key(e: ft.KeyboardEvent):
        if e.key == "Enter":
            do_login(e)

    page.on_keyboard_event = on_key

    user_field = make_textfield(
        "Username", ref_user, "Enter your username", width=320
    )
    pass_field = make_textfield(
        "Password", ref_pass, "Enter your password",
        width=320, password=True,
    )

    card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Martus Store",
                    color=PRIMARY, size=26,
                    weight=ft.FontWeight.BOLD,
                    font_family=FONT_HEAD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Sari-Sari Store Inventory System",
                    color=TEXT_MID, size=12,
                    font_family=FONT_BODY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(color=BORDER, height=20),
                user_field,
                pass_field,
                ft.Text(
                    "", ref=ref_err,
                    color=DANGER, size=11,
                    font_family=FONT_BODY,
                    visible=False,
                ),
                ft.ElevatedButton(
                    "Sign In",
                    icon=ft.Icons.LOGIN_ROUNDED,
                    bgcolor=PRIMARY, color="white", width=320,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=do_login,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        bgcolor=SURFACE,
        padding=36,
        border_radius=16,
        border=ft.Border(
            top=ft.BorderSide(1, BORDER),
            right=ft.BorderSide(1, BORDER),
            bottom=ft.BorderSide(1, BORDER),
            left=ft.BorderSide(1, BORDER),
        ),
        shadow=ft.BoxShadow(
            blur_radius=24,
            color="#22000000",
            offset=ft.Offset(0, 6),
        ),
        width=400,
    )

    return ft.View(
        "/login",
        controls=[
            ft.Container(
                content=card,
                expand=True,
                alignment=ft.alignment.center,
                bgcolor=BG,
            )
        ],
        bgcolor=BG,
        padding=0,
    )
