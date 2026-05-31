import flet as ft

from models.database             import get_connection, initialise
from models.product_model        import ProductModel
from models.user_model           import UserModel
from controllers.auth_controller    import AuthController
from controllers.product_controller import ProductController
from views.login_view     import build_login_view
from views.inventory_view import build_inventory_view


def main(page: ft.Page):
    page.title   = "Tindahan Inventory DMS"
    page.bgcolor = "#FFF8F0"
    page.padding = 0

    #Window size
    try:
        page.window.width     = 1100
        page.window.height    = 820
        page.window.resizable = True
    except Exception:
        pass

    #Bootstrap
    conn       = get_connection()
    initialise(conn)
    prod_model = ProductModel(conn)
    user_model = UserModel(conn)
    auth_ctrl  = AuthController(user_model)
    prod_ctrl  = ProductController(prod_model)

    #Router
    def route_change(e):
        page.views.clear()
        if page.route == "/inventory" and auth_ctrl.current_user:
            page.views.append(
                build_inventory_view(page, prod_ctrl, auth_ctrl, on_logout)
            )
        else:
            page.views.append(
                build_login_view(page, auth_ctrl, on_login_success)
            )
        page.update()

    def on_login_success():
        page.go("/inventory")

    def on_logout():
        auth_ctrl.logout()
        page.go("/login")

    page.on_route_change = route_change
    page.go("/login")


ft.app(target=main)
