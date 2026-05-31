import flet as ft
from utils.theme import (
    BG, SURFACE, CARD, PRIMARY, ACCENT, TEXT_DARK, TEXT_MID,
    TEXT_LIGHT, SUCCESS, DANGER, BORDER, INFO, FONT_HEAD, FONT_BODY,
    CATEGORIES, ROLES, make_textfield, make_card,
)

#Helpers

def _full_border(color=BORDER):
    return ft.Border(
        top=ft.BorderSide(1, color),
        right=ft.BorderSide(1, color),
        bottom=ft.BorderSide(1, color),
        left=ft.BorderSide(1, color),
    )


def _snack(page: ft.Page, msg: str, color=SUCCESS):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(msg, color="white", font_family=FONT_BODY, size=12),
        bgcolor=color,
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()


def _set_status(ref: ft.Ref, msg: str, color: str, page: ft.Page):
    ref.current.value = msg
    ref.current.color = color
    page.update()


#Main builder

def build_inventory_view(page: ft.Page, product_ctrl, auth_ctrl, on_logout) -> ft.View:

    # state
    editing_id     = {"value": None}
    active_section = {"value": "products"}

    # refs — form
    r_code    = ft.Ref[ft.TextField]()
    r_name    = ft.Ref[ft.TextField]()
    r_cat     = ft.Ref[ft.Dropdown]()
    r_price   = ft.Ref[ft.TextField]()
    r_stock   = ft.Ref[ft.TextField]()
    r_search  = ft.Ref[ft.TextField]()
    r_table   = ft.Ref[ft.DataTable]()
    r_status  = ft.Ref[ft.Text]()
    r_ftitle  = ft.Ref[ft.Text]()
    r_savebtn = ft.Ref[ft.ElevatedButton]()

    # refs — binary search
    r_bs_code = ft.Ref[ft.TextField]()
    r_bs_log  = ft.Ref[ft.Column]()

    # refs — users
    r_new_user = ft.Ref[ft.TextField]()
    r_new_pass = ft.Ref[ft.TextField]()
    r_new_role = ft.Ref[ft.Dropdown]()
    r_user_tbl = ft.Ref[ft.DataTable]()

    # refs — nav containers
    r_nav  = {k: ft.Ref[ft.Container]() for k in ("products", "binary_search", "users")}
    r_panel = {k: ft.Ref[ft.Container]() for k in ("products", "binary_search", "users")}

    can_write = auth_ctrl.can_write()
    is_admin  = auth_ctrl.is_admin()

    NAV_ITEMS = [
        ("products",      ft.Icons.INVENTORY_2_ROUNDED, "Products"),
        ("binary_search", ft.Icons.SEARCH_ROUNDED,      "Binary Search"),
    ]
    if is_admin:
        NAV_ITEMS.append(("users", ft.Icons.PEOPLE_ROUNDED, "Users"))

    #Navigation

    def switch_section(sid):
        old = active_section["value"]
        #deactivate old
        if r_nav[old].current:
            r_nav[old].current.bgcolor = "transparent"
            row_ctrl = r_nav[old].current.content.controls
            row_ctrl[0].color = TEXT_LIGHT  #icon
            row_ctrl[1].color = TEXT_LIGHT  #text
        if r_panel[old].current:
            r_panel[old].current.visible = False
        #activate new
        active_section["value"] = sid
        if r_nav[sid].current:
            r_nav[sid].current.bgcolor = "#FDE8DA"
            row_ctrl = r_nav[sid].current.content.controls
            row_ctrl[0].color = PRIMARY
            row_ctrl[1].color = PRIMARY
        if r_panel[sid].current:
            r_panel[sid].current.visible = True
        page.update()

    #Product table

    def refresh_table(query=""):
        rows = product_ctrl.get_products(query)
        r_table.current.rows.clear()
        for r in rows:
            pid      = r[0]
            code     = r[1]
            name     = r[2]
            cat      = r[3]
            price    = r[4]
            stock    = r[5]
            added_by = r[6] if len(r) > 6 else "—"
            low      = stock < 5

            actions = ft.Row(tight=True)
            if can_write:
                actions.controls.append(
                    ft.IconButton(
                        ft.Icons.EDIT_ROUNDED,
                        icon_color=ACCENT, icon_size=18, tooltip="Edit",
                        on_click=lambda e, rid=pid: on_edit(rid),
                    )
                )
            if is_admin:
                actions.controls.append(
                    ft.IconButton(
                        ft.Icons.DELETE_ROUNDED,
                        icon_color=DANGER, icon_size=18, tooltip="Delete",
                        on_click=lambda e, rid=pid: on_delete(rid),
                    )
                )

            r_table.current.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(pid),  color=TEXT_MID,  size=12, font_family=FONT_BODY)),
                ft.DataCell(ft.Text(code,       color=TEXT_DARK, size=12, font_family=FONT_BODY)),
                ft.DataCell(ft.Text(name,       color=TEXT_DARK, size=13,
                                    weight=ft.FontWeight.W_600, font_family=FONT_BODY)),
                ft.DataCell(ft.Container(
                    content=ft.Text(cat, color=PRIMARY, size=11,
                                    font_family=FONT_BODY, weight=ft.FontWeight.W_600),
                    bgcolor="#FDE8DA",
                    padding=ft.padding.symmetric(4, 8),
                    border_radius=12,
                )),
                ft.DataCell(ft.Text(f"P{price:,.2f}", color=SUCCESS, size=12,
                                    font_family=FONT_BODY, weight=ft.FontWeight.W_600)),
                ft.DataCell(ft.Row(
                    controls=[
                        ft.Text(str(stock),
                                color=DANGER if low else TEXT_DARK, size=12,
                                font_family=FONT_BODY, weight=ft.FontWeight.W_600),
                        ft.Text(" !", color=DANGER, size=11) if low else ft.Text(""),
                    ],
                    tight=True,
                )),
                ft.DataCell(ft.Text(str(added_by), color=TEXT_MID, size=11,
                                    font_family=FONT_BODY)),
                ft.DataCell(actions),
            ]))
        page.update()

    #CRUD

    def on_save(e):
        errs = product_ctrl.validate(
            r_code.current.value  or "",
            r_name.current.value  or "",
            r_cat.current.value,
            r_price.current.value or "",
            r_stock.current.value or "",
        )
        if errs:
            msg = "  |  ".join(errs)
            _snack(page, msg, DANGER)
            _set_status(r_status, msg, DANGER, page)
            return

        if editing_id["value"] is None:
            ok, msg = product_ctrl.add_product(
                r_code.current.value, r_name.current.value,
                r_cat.current.value,  r_price.current.value,
                r_stock.current.value, auth_ctrl.user_id,
            )
        else:
            ok, msg = product_ctrl.update_product(
                editing_id["value"],
                r_code.current.value, r_name.current.value,
                r_cat.current.value,  r_price.current.value,
                r_stock.current.value,
            )

        _snack(page, msg, SUCCESS if ok else DANGER)
        _set_status(r_status, msg, SUCCESS if ok else DANGER, page)
        if ok:
            clear_form()
            refresh_table()

    def on_edit(pid):
        row = product_ctrl.model.get_by_id(pid)
        if not row:
            return
        editing_id["value"]        = pid
        r_code.current.value       = row["prodCode"]
        r_name.current.value       = row["prodName"]
        r_cat.current.value        = row["category"]
        r_price.current.value      = str(row["price"])
        r_stock.current.value      = str(row["stock"])
        r_ftitle.current.value     = f"Editing: {row['prodName']}"
        r_savebtn.current.text     = "Update Product"
        r_savebtn.current.bgcolor  = ACCENT
        _set_status(r_status, f"Editing: {row['prodName']}", ACCENT, page)
        switch_section("products")

    def on_delete(pid):
        row  = product_ctrl.model.get_by_id(pid)
        name = row["prodName"] if row else f"ID {pid}"

        def confirm(e):
            ok, msg = product_ctrl.delete_product(pid)
            dlg.open = False
            page.update()
            _snack(page, msg, SUCCESS if ok else DANGER)
            _set_status(r_status, msg, SUCCESS if ok else DANGER, page)
            refresh_table()

        def cancel(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete", color=DANGER,
                          font_family=FONT_HEAD, weight=ft.FontWeight.BOLD),
            content=ft.Text(f"Delete '{name}' from inventory?",
                            color=TEXT_DARK, font_family=FONT_BODY),
            actions=[
                ft.TextButton("Cancel", on_click=cancel,
                              style=ft.ButtonStyle(color=TEXT_MID)),
                ft.ElevatedButton("Delete", bgcolor=DANGER, color="white",
                                  on_click=confirm),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def clear_form():
        r_code.current.value      = ""
        r_name.current.value      = ""
        r_cat.current.value       = None
        r_price.current.value     = ""
        r_stock.current.value     = ""
        editing_id["value"]       = None
        r_ftitle.current.value    = "Add New Product"
        r_savebtn.current.text    = "Add Product"
        r_savebtn.current.bgcolor = PRIMARY
        page.update()

    def on_clear(e):
        clear_form()
        _set_status(r_status, "Form cleared.", TEXT_MID, page)

    def on_search(e):
        refresh_table(r_search.current.value or "")

    #Binary Search

    def on_binary_search(e):
        target = (r_bs_code.current.value or "").strip()
        if not target:
            _snack(page, "Enter a product code to search.", DANGER)
            return
        idx, steps, found = product_ctrl.binary_search_by_code(target)
        r_bs_log.current.controls.clear()
        for step in steps:
            if "Found" in step:
                color = SUCCESS
            elif "not found" in step:
                color = DANGER
            else:
                color = TEXT_MID
            r_bs_log.current.controls.append(
                ft.Text(step, color=color, size=11,
                        font_family=FONT_BODY, selectable=True)
            )
        result = (f"Found: {found['prodName']}" if found
                  else f"'{target}' not found.")
        _snack(page, result, SUCCESS if found else DANGER)
        page.update()

    #CSV Import

    def on_import_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        ok_count, errors = product_ctrl.import_csv(
            e.files[0].path, auth_ctrl.user_id
        )
        if errors:
            _snack(page, f"{len(errors)} row(s) skipped: " + "; ".join(errors[:2]), DANGER)
        if ok_count:
            msg = f"Imported {ok_count} product(s)."
            _snack(page, msg, SUCCESS)
            _set_status(r_status, msg, SUCCESS, page)
        refresh_table()

    csv_picker = ft.FilePicker(on_result=on_import_result)
    page.overlay.append(csv_picker)

    #Excel Export

    def on_export(e):
        ok, msg = product_ctrl.export_excel(r_search.current.value or "")
        _snack(page, msg, SUCCESS if ok else DANGER)
        _set_status(r_status, msg, SUCCESS if ok else DANGER, page)

    #User management

    def refresh_users():
        if not is_admin or not r_user_tbl.current:
            return
        r_user_tbl.current.rows.clear()
        for u in product_ctrl.model.conn.execute(
            "SELECT userID, username, role FROM USERS ORDER BY username"
        ).fetchall():
            uid, uname, urole = u[0], u[1], u[2]
            badge_bg = "#FDE8DA" if urole == "admin" else "#E8F8E8" if urole == "staff" else "#F0F0F0"
            badge_fg = PRIMARY   if urole == "admin" else SUCCESS   if urole == "staff" else TEXT_MID
            r_user_tbl.current.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(uid), color=TEXT_MID, size=12, font_family=FONT_BODY)),
                ft.DataCell(ft.Text(uname, color=TEXT_DARK, size=12,
                                    weight=ft.FontWeight.W_600, font_family=FONT_BODY)),
                ft.DataCell(ft.Container(
                    content=ft.Text(urole, color=badge_fg, size=11, font_family=FONT_BODY),
                    bgcolor=badge_bg,
                    padding=ft.padding.symmetric(3, 8),
                    border_radius=10,
                )),
                ft.DataCell(ft.IconButton(
                    ft.Icons.DELETE_ROUNDED, icon_color=DANGER, icon_size=16,
                    tooltip="Remove",
                    on_click=lambda e, uid=uid, un=uname: on_delete_user(uid, un),
                )),
            ]))
        page.update()

    def on_add_user(e):
        uname = (r_new_user.current.value or "").strip()
        upass = (r_new_pass.current.value or "").strip()
        urole = r_new_role.current.value
        if not uname or not upass or not urole:
            _snack(page, "Fill all user fields.", DANGER)
            return
        try:
            from models.user_model import UserModel
            UserModel(product_ctrl.model.conn).add(uname, upass, urole)
            r_new_user.current.value = ""
            r_new_pass.current.value = ""
            r_new_role.current.value = None
            _snack(page, f"User '{uname}' added.", SUCCESS)
            _set_status(r_status, f"User '{uname}' added.", SUCCESS, page)
            refresh_users()
        except ValueError as ex:
            #if there is a duplicate username - show AlertDialog
            def close_dlg(e):
                err_dlg.open = False
                page.update()
            err_dlg = ft.AlertDialog(
                title=ft.Text("Cannot Add User", color=DANGER,
                              font_family=FONT_HEAD, weight=ft.FontWeight.BOLD),
                content=ft.Text(str(ex), color=TEXT_DARK, font_family=FONT_BODY),
                actions=[
                    ft.ElevatedButton("OK", bgcolor=PRIMARY, color="white",
                                      on_click=close_dlg),
                ],
            )
            page.overlay.append(err_dlg)
            err_dlg.open = True
            page.update()

    def on_delete_user(uid, uname):
        from models.user_model import UserModel
        UserModel(product_ctrl.model.conn).delete(uid)
        _snack(page, f"User '{uname}' removed.", SUCCESS)
        _set_status(r_status, f"User '{uname}' removed.", SUCCESS, page)
        refresh_users()


    #UI BUILD

    #Header

    role_color = DANGER if auth_ctrl.role == "admin" \
                 else SUCCESS if auth_ctrl.role == "staff" \
                 else TEXT_MID

    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Martus Store", color="white", size=22,
                                weight=ft.FontWeight.BOLD, font_family=FONT_HEAD),
                        ft.Text("Sari-Sari Store Inventory System",
                                color="#FFD9C4", size=11, font_family=FONT_BODY),
                    ],
                    spacing=0,
                ),
                ft.Container(expand=True),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(f"  {auth_ctrl.current_user['username']}",
                                        color="white", size=12, font_family=FONT_BODY),
                                ft.Container(
                                    content=ft.Text(
                                        auth_ctrl.role.upper(),
                                        color="white", size=10,
                                        font_family=FONT_BODY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=role_color,
                                    padding=ft.padding.symmetric(3, 8),
                                    border_radius=10,
                                ),
                            ],
                            spacing=4,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                        ),
                        ft.IconButton(
                            ft.Icons.LOGOUT_ROUNDED,
                            icon_color="white", icon_size=20, tooltip="Logout",
                            on_click=lambda e: on_logout(),
                        ),
                    ],
                    spacing=8,
                ),
            ],
        ),
        bgcolor=PRIMARY,
        padding=ft.padding.symmetric(14, 20),
        shadow=ft.BoxShadow(
            blur_radius=10, color="#88000000", offset=ft.Offset(0, 3)
        ),
    )

    #Sidebar nav items

    def make_nav_item(sid, icon, label):
        is_active = (sid == "products")
        return ft.Container(
            ref=r_nav[sid],
            content=ft.Row(
                controls=[
                    ft.Icon(icon,
                            color=PRIMARY if is_active else TEXT_LIGHT,
                            size=20),
                    ft.Text(label,
                            color=PRIMARY if is_active else TEXT_LIGHT,
                            size=13, font_family=FONT_BODY,
                            weight=ft.FontWeight.W_600 if is_active
                                   else ft.FontWeight.NORMAL),
                ],
                spacing=12,
            ),
            bgcolor="#FDE8DA" if is_active else "transparent",
            padding=ft.padding.symmetric(12, 16),
            border_radius=10,
            ink=True,
            on_click=lambda e, s=sid: switch_section(s),
        )

    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("MENU", color=TEXT_LIGHT, size=10,
                                    font_family=FONT_BODY,
                                    weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(left=16, top=16, bottom=8),
                ),
                *[make_nav_item(sid, icon, label)
                  for sid, icon, label in NAV_ITEMS],
            ],
            spacing=4,
        ),
        width=200,
        bgcolor=SURFACE,
        border=ft.Border(right=ft.BorderSide(1, BORDER)),
    )

    #Products panel

    code_f  = make_textfield("Product Code", r_code,  "e.g. P011", width=140)
    name_f  = make_textfield("Product Name", r_name,  "e.g. Milo", width=220)
    price_f = make_textfield("Price",        r_price, "0.00",
                             ft.KeyboardType.NUMBER, 140)
    stock_f = make_textfield("Stock (pcs)",  r_stock, "0",
                             ft.KeyboardType.NUMBER, 140)
    for fld in (code_f, name_f, price_f, stock_f):
        fld.disabled = not can_write

    cat_dd = ft.Dropdown(
        ref=r_cat, label="Category", width=180,
        options=[ft.dropdown.Option(c) for c in CATEGORIES],
        text_style=ft.TextStyle(font_family=FONT_BODY, color=TEXT_DARK, size=12),
        label_style=ft.TextStyle(color=TEXT_MID, size=11, font_family=FONT_BODY),
        border_color=BORDER, focused_border_color=PRIMARY,
        filled=True, fill_color=SURFACE,
        border_radius=8, content_padding=10,
        disabled=not can_write,
    )

    form_card = make_card(
        ft.Column(
            controls=[
                ft.Text("Add New Product", ref=r_ftitle, color=PRIMARY, size=14,
                        weight=ft.FontWeight.BOLD, font_family=FONT_HEAD),
                ft.Divider(color=BORDER, height=8),
                ft.Row(controls=[code_f, name_f, cat_dd], spacing=10, wrap=True),
                ft.Row(controls=[price_f, stock_f], spacing=10),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            ref=r_savebtn, text="Add Product",
                            icon=ft.Icons.ADD_CIRCLE_ROUNDED,
                            bgcolor=PRIMARY, color="white",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                            on_click=on_save,
                            visible=can_write,
                        ),
                        ft.OutlinedButton(
                            "Clear",
                            icon=ft.Icons.CLEAR_ROUNDED,
                            style=ft.ButtonStyle(
                                color=TEXT_MID,
                                side=ft.BorderSide(1, BORDER),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=on_clear,
                            visible=can_write,
                        ),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Import CSV",
                            icon=ft.Icons.UPLOAD_FILE_ROUNDED,
                            bgcolor=INFO, color="white",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                            on_click=lambda e: csv_picker.pick_files(
                                allowed_extensions=["csv"],
                                dialog_title="Select CSV file",
                            ),
                            visible=can_write,
                        ),
                        ft.ElevatedButton(
                            "Export Excel",
                            icon=ft.Icons.DOWNLOAD_ROUNDED,
                            bgcolor=ACCENT, color=TEXT_DARK,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                            on_click=on_export,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            spacing=8,
        ),
        margin=ft.margin.only(bottom=8),
    )

    search_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SEARCH_ROUNDED, color=TEXT_LIGHT, size=18),
                ft.TextField(
                    ref=r_search,
                    hint_text="Search by ID, code, name or category...",
                    border=ft.InputBorder.NONE,
                    expand=True,
                    on_change=on_search,
                    text_style=ft.TextStyle(font_family=FONT_BODY,
                                            color=TEXT_DARK, size=12),
                    hint_style=ft.TextStyle(color=TEXT_LIGHT, size=12),
                    content_padding=ft.padding.only(left=4, bottom=8),
                ),
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE,
        border_radius=10,
        border=_full_border(),
        padding=ft.padding.only(left=12, right=12, top=2, bottom=2),
        margin=ft.margin.only(bottom=8),
    )

    table = ft.DataTable(
        ref=r_table,
        columns=[
            ft.DataColumn(ft.Text("ID",          size=11, color=TEXT_MID,  font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Code",         size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Product Name", size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Category",     size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Price",        size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Stock",        size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Added By",     size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions",      size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=_full_border(),
        border_radius=10,
        vertical_lines=ft.BorderSide(0.5, BORDER),
        horizontal_lines=ft.BorderSide(0.5, BORDER),
        heading_row_color="#FEF0E6",
        heading_row_height=40,
        data_row_min_height=42,
        data_row_max_height=42,
        column_spacing=12,
    )

    table_card = make_card(
        ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Product List",
                                color=TEXT_MID, size=11, font_family=FONT_BODY,
                                weight=ft.FontWeight.W_600),
                        ft.Container(expand=True),
                        ft.Text("! = Low Stock (< 5 pcs)", color=DANGER,
                                size=10, font_family=FONT_BODY),
                    ],
                ),
                ft.Column(controls=[table], scroll=ft.ScrollMode.AUTO),
            ],
            spacing=6,
        ),
    )

    panel_products = ft.Container(
        ref=r_panel["products"],
        content=ft.Column(
            controls=[form_card, search_bar, table_card],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        visible=True,
        padding=16,
        expand=True,
    )

    #Binary Search panel

    panel_bsearch = ft.Container(
        ref=r_panel["binary_search"],
        content=ft.Column(
            controls=[
                make_card(ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.MANAGE_SEARCH_ROUNDED,
                                        color=INFO, size=22),
                                ft.Text("Binary Search by Product Code",
                                        color=INFO, size=15,
                                        weight=ft.FontWeight.BOLD,
                                        font_family=FONT_HEAD),
                            ],
                            spacing=8,
                        ),
                        ft.Divider(color=BORDER, height=6),
                        ft.Text(
                            "Binary Search is O(log n): it halves the search space at each step, "
                            "making it far faster than a linear scan O(n) on large datasets. "
                            "Products must be sorted by code — they are always kept in "
                            "ORDER BY prodCode ASC.",
                            color=TEXT_MID, size=11, font_family=FONT_BODY,
                        ),
                        ft.Row(
                            controls=[
                                make_textfield("Product Code", r_bs_code,
                                               "e.g. P003", width=240),
                                ft.ElevatedButton(
                                    "Run Search",
                                    icon=ft.Icons.SEARCH_ROUNDED,
                                    bgcolor=INFO, color="white",
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    on_click=on_binary_search,
                                ),
                            ],
                            spacing=12,
                        ),
                        ft.Text("Step-by-Step Log:", color=TEXT_MID, size=11,
                                font_family=FONT_BODY, weight=ft.FontWeight.W_600),
                        ft.Container(
                            content=ft.Column(
                                ref=r_bs_log,
                                controls=[],
                                scroll=ft.ScrollMode.AUTO,
                                spacing=2,
                            ),
                            height=300,
                            bgcolor="#F8F4F0",
                            border=_full_border(),
                            border_radius=8,
                            padding=12,
                        ),
                    ],
                    spacing=10,
                )),
            ],
            spacing=0,
        ),
        visible=False,
        padding=16,
        expand=True,
    )

    #Users panel

    if is_admin:
        user_table = ft.DataTable(
            ref=r_user_tbl,
            columns=[
                ft.DataColumn(ft.Text("ID",       size=11, color=TEXT_MID,  font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Username", size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Role",     size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Remove",   size=11, color=TEXT_DARK, font_family=FONT_HEAD, weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=_full_border(),
            border_radius=8,
            heading_row_color="#FEF0E6",
            heading_row_height=36,
            data_row_min_height=36,
            data_row_max_height=36,
        )
        nu_f = make_textfield("New Username", r_new_user, width=160)
        np_f = make_textfield("Password",     r_new_pass, width=160, password=True)
        nr_d = ft.Dropdown(
            ref=r_new_role, label="Role", width=120,
            options=[ft.dropdown.Option(r) for r in ROLES],
            text_style=ft.TextStyle(font_family=FONT_BODY, color=TEXT_DARK, size=12),
            label_style=ft.TextStyle(color=TEXT_MID, size=11, font_family=FONT_BODY),
            border_color=BORDER, focused_border_color=PRIMARY,
            filled=True, fill_color=SURFACE,
            border_radius=8, content_padding=10,
        )
        panel_users = ft.Container(
            ref=r_panel["users"],
            content=ft.Column(
                controls=[
                    make_card(ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.PEOPLE_ROUNDED,
                                            color=PRIMARY, size=20),
                                    ft.Text("User Management", color=PRIMARY,
                                            size=15, weight=ft.FontWeight.BOLD,
                                            font_family=FONT_HEAD),
                                ],
                                spacing=8,
                            ),
                            ft.Divider(color=BORDER, height=6),
                            ft.Text(
                                "Roles: admin (full access), "
                                "staff (add/edit), viewer (read-only).",
                                color=TEXT_MID, size=11, font_family=FONT_BODY,
                            ),
                            ft.Row(
                                controls=[
                                    nu_f, np_f, nr_d,
                                    ft.ElevatedButton(
                                        "Add User",
                                        icon=ft.Icons.PERSON_ADD_ROUNDED,
                                        bgcolor=PRIMARY, color="white",
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8)
                                        ),
                                        on_click=on_add_user,
                                    ),
                                ],
                                spacing=10,
                                wrap=True,
                            ),
                            ft.Divider(color=BORDER, height=8),
                            ft.Text("Existing accounts:", color=TEXT_MID,
                                    size=11, font_family=FONT_BODY),
                            ft.Column(
                                controls=[user_table],
                                scroll=ft.ScrollMode.AUTO,
                                height=280,
                            ),
                        ],
                        spacing=8,
                    )),
                ],
                spacing=0,
            ),
            visible=False,
            padding=16,
            expand=True,
        )
    else:
        panel_users = ft.Container(ref=r_panel["users"], visible=False)

    #Status bar

    status_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED,
                        color=TEXT_LIGHT, size=14),
                ft.Text("Ready.", ref=r_status, color=TEXT_MID,
                        size=11, font_family=FONT_BODY, expand=True),
            ],
            spacing=6,
        ),
        bgcolor=SURFACE,
        border=ft.Border(top=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(8, 20),
    )

    #Assemble

    body = ft.Row(
        controls=[
            sidebar,
            ft.Container(
                content=ft.Stack(
                    controls=[panel_products, panel_bsearch, panel_users]
                ),
                expand=True,
                bgcolor=BG,
            ),
        ],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    view = ft.View(
        "/inventory",
        controls=[
            ft.Column(
                controls=[header, body, status_bar],
                spacing=0,
                expand=True,
            )
        ],
        bgcolor=BG,
        padding=0,
    )

    #Initial load
    refresh_table()
    if is_admin:
        refresh_users()

    return view
