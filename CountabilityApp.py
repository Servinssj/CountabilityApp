import os
import flet as ft

# Diccionario de usuarios
USUARIOS_DB = {
    "admin": {"password": "123", "role": "admin", "nombre": "Administrador"},
    "harry": {"password": "123", "role": "usuario", "nombre": "Harry"},
    "raper": {"password": "123", "role": "usuario", "nombre": "Raper"},
    "tomi": {"password": "123", "role": "usuario", "nombre": "Tomi"},
}

# Base de datos de productos base
productos_db = {
    "P001": {"nombre": "PLAYERA OVERSIZED", "stock": 30, "precio": 500},
    "P002": {"nombre": "PLAYERA BOXY FIT", "stock": 25, "precio": 450},
    "P003": {"nombre": "SUDADERA HOODIE", "stock": 15, "precio": 850},
    "P004": {"nombre": "SUDADERA CREWNECK", "stock": 20, "precio": 750},
}

# Lista global de pedidos
pedidos_db = []

# Opciones de Tallas y Colores predefinidos
TALLAS = ["CH (S)", "M", "G (L)", "XG (XL)"]
COLORES = ["Negro", "Blanco", "Gris", "Beige", "Verde Acid"]

def main(page: ft.Page):
    page.title = "CONTROL DE INVENTARIO // GOTEO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    usuario_actual = {"nombre": "", "role": ""}

    # --- PANTALLA 1: LOGIN ---
    user_input = ft.TextField(
        label="USUARIO",
        width=320,
        border_color="#333333",
        focused_border_color="#00FF66",
        color=ft.Colors.WHITE,
    )
    pass_input = ft.TextField(
        label="CONTRASEÑA",
        password=True,
        can_reveal_password=True,
        width=320,
        border_color="#333333",
        focused_border_color="#00FF66",
        color=ft.Colors.WHITE,
    )
    login_status = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    def iniciar_sesion(e):
        user = user_input.value.strip().lower()
        pwd = pass_input.value.strip()

        if user in USUARIOS_DB and USUARIOS_DB[user]["password"] == pwd:
            usuario_actual["nombre"] = USUARIOS_DB[user]["nombre"]
            usuario_actual["role"] = USUARIOS_DB[user]["role"]
            login_status.value = ""
            mostrar_pantalla_principal()
        else:
            login_status.value = "✖ CREDENCIALES INCORRECTAS"
            login_status.color = "#FF3333"
            page.update()

    login_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("⚡ GOTEO", size=32, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                ft.Text("Sistema de Control e Inventario", size=14, color="#888888", weight=ft.FontWeight.W_600),
                ft.Container(height=10),
                user_input,
                pass_input,
                ft.Container(height=10),
                ft.FilledButton(
                    "ACCEDER ➔",
                    on_click=iniciar_sesion,
                    width=320,
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLACK,
                        bgcolor="#00FF66",
                        shape=ft.RoundedRectangleBorder(radius=4),
                    ),
                ),
                login_status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment(0, 0),
        padding=20,
    )

    # --- PANTALLA 2: PANEL CON PESTAÑAS ---
    def mostrar_pantalla_principal():
        page.clean()

        status_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

        def obtener_opciones_productos():
            return [
                ft.dropdown.Option(k, f"{v['nombre']} // STK: {v['stock']} // ${v['precio']}")
                for k, v in productos_db.items()
            ]

        def cerrar_sesion(e):
            user_input.value = ""
            pass_input.value = ""
            page.clean()
            page.add(login_view)
            page.update()

        # Header común
        header = ft.Row(
            controls=[
                ft.Column([
                    ft.Text(f"// {usuario_actual['nombre'].upper()}", size=18, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                    ft.Text(f"ROLE: {usuario_actual['role'].upper()}", size=12, color="#00FF66", weight=ft.FontWeight.BOLD),
                ]),
                ft.OutlinedButton(
                    "LOGOUT",
                    on_click=cerrar_sesion,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        side=ft.BorderSide(1, "#444444"),
                        shape=ft.RoundedRectangleBorder(radius=4)
                    )
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # -------------------------------------------------------------
        # PESTAÑA 1: VENTAS
        # -------------------------------------------------------------
        v_drop_prod = ft.Dropdown(label="PRODUCTO", width=340, options=obtener_opciones_productos(), border_color="#333333")
        v_drop_talla = ft.Dropdown(label="TALLA", width=160, options=[ft.dropdown.Option(t) for t in TALLAS], border_color="#333333")
        v_drop_color = ft.Dropdown(label="COLOR", width=160, options=[ft.dropdown.Option(c) for c in COLORES], border_color="#333333")
        v_input_diseno = ft.TextField(label="DISEÑO / ESTAMPADO", width=340, border_color="#333333", hint_text="Ej. Logo Frente / Goteo Back")
        v_input_cant = ft.TextField(label="CANTIDAD", value="1", width=160, keyboard_type=ft.KeyboardType.NUMBER, border_color="#333333")

        def registrar_venta(e):
            key = v_drop_prod.value
            if not key or not v_drop_talla.value or not v_drop_color.value or not v_input_diseno.value:
                status_text.value = "⚠️ COMPLETA TODOS LOS CAMPOS DE LA VENTA."
                status_text.color = "#FFCC00"
            else:
                cant = int(v_input_cant.value or 0)
                if cant > productos_db[key]["stock"]:
                    status_text.value = f"✖ STOCK INSUFFICIENT. DISPONIBLE: {productos_db[key]['stock']}"
                    status_text.color = "#FF3333"
                else:
                    productos_db[key]["stock"] -= cant
                    prod_nombre = productos_db[key]["nombre"]
                    status_text.value = f"✔ VENTA: {cant}x {prod_nombre} ({v_drop_talla.value}, {v_drop_color.value}) - '{v_input_diseno.value}'"
                    status_text.color = "#00FF66"
                    actualizar_todos_los_dropdowns()
            page.update()

        tab_ventas = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text("🛒 REGISTRAR VENTA", size=16, weight=ft.FontWeight.BOLD, color="#00FF66"),
                v_drop_prod,
                ft.Row([v_drop_talla, v_drop_color], wrap=True),
                v_input_diseno,
                ft.Row([
                    v_input_cant,
                    ft.FilledButton(
                        "CONFIRMAR VENTA",
                        on_click=registrar_venta,
                        style=ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor="#00FF66", shape=ft.RoundedRectangleBorder(radius=4))
                    )
                ], wrap=True)
            ])
        )

        # -------------------------------------------------------------
        # PESTAÑA 2: AGREGAR STOCK
        # -------------------------------------------------------------
        s_drop_prod = ft.Dropdown(label="PRODUCTO", width=340, options=obtener_opciones_productos(), border_color="#333333")
        s_drop_talla = ft.Dropdown(label="TALLA", width=160, options=[ft.dropdown.Option(t) for t in TALLAS], border_color="#333333")
        s_drop_color = ft.Dropdown(label="COLOR", width=160, options=[ft.dropdown.Option(c) for c in COLORES], border_color="#333333")
        s_input_cant = ft.TextField(label="AÑADIR CANTIDAD", value="1", width=160, keyboard_type=ft.KeyboardType.NUMBER, border_color="#333333")

        def registrar_stock(e):
            key = s_drop_prod.value
            if not key or not s_drop_talla.value or not s_drop_color.value:
                status_text.value = "⚠️ SELECCIONA PRODUCTO, TALLA Y COLOR."
                status_text.color = "#FFCC00"
            else:
                cant = int(s_input_cant.value or 0)
                productos_db[key]["stock"] += cant
                prod_nombre = productos_db[key]["nombre"]
                status_text.value = f"📦 REABASTECIDO: +{cant} unidades de {prod_nombre} [{s_drop_talla.value}/{s_drop_color.value}]. Total: {productos_db[key]['stock']}"
                status_text.color = "#00E5FF"
                actualizar_todos_los_dropdowns()
            page.update()

        tab_stock = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text("📦 AGREGAR STOCK / INVENTARIO", size=16, weight=ft.FontWeight.BOLD, color="#00E5FF"),
                s_drop_prod,
                ft.Row([s_drop_talla, s_drop_color], wrap=True),
                ft.Row([
                    s_input_cant,
                    ft.FilledButton(
                        "+ AÑADIR STOCK",
                        on_click=registrar_stock,
                        style=ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor="#00E5FF", shape=ft.RoundedRectangleBorder(radius=4))
                    )
                ], wrap=True)
            ])
        )

        # -------------------------------------------------------------
        # PESTAÑA 3: PEDIDOS
        # -------------------------------------------------------------
        p_input_cliente = ft.TextField(label="NOMBRE DEL CLIENTE", width=340, border_color="#333333")
        p_drop_prod = ft.Dropdown(label="PRODUCTO", width=340, options=obtener_opciones_productos(), border_color="#333333")
        p_drop_talla = ft.Dropdown(label="TALLA", width=160, options=[ft.dropdown.Option(t) for t in TALLAS], border_color="#333333")
        p_drop_color = ft.Dropdown(label="COLOR", width=160, options=[ft.dropdown.Option(c) for c in COLORES], border_color="#333333")
        p_input_diseno = ft.TextField(label="DISEÑO DETALLADO", width=340, border_color="#333333")
        
        lista_pedidos_ui = ft.Column()

        def renderizar_pedidos():
            lista_pedidos_ui.controls.clear()
            if not pedidos_db:
                lista_pedidos_ui.controls.append(ft.Text("No hay pedidos registrados.", color="#666666"))
            else:
                for idx, ped in enumerate(pedidos_db):
                    lista_pedidos_ui.controls.append(
                        ft.Container(
                            content=ft.Text(f"📋 #{idx+1} | {ped['cliente']} ➔ {ped['producto']} ({ped['talla']}/{ped['color']}) - Dis: {ped['diseno']}", size=13),
                            padding=8,
                            bgcolor="#1E1E1E",
                            border_radius=4
                        )
                    )

        def agregar_pedido(e):
            key = p_drop_prod.value
            if not p_input_cliente.value or not key or not p_drop_talla.value or not p_drop_color.value or not p_input_diseno.value:
                status_text.value = "⚠️ INGRESA TODOS LOS DATOS DEL PEDIDO."
                status_text.color = "#FFCC00"
            else:
                pedidos_db.append({
                    "cliente": p_input_cliente.value.upper(),
                    "producto": productos_db[key]["nombre"],
                    "talla": p_drop_talla.value,
                    "color": p_drop_color.value,
                    "diseno": p_input_diseno.value
                })
                status_text.value = f"📝 PEDIDO REGISTRADO PARA {p_input_cliente.value.upper()}"
                status_text.color = "#FF9900"
                renderizar_pedidos()
            page.update()

        renderizar_pedidos()

        tab_pedidos = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text("📝 REGISTRO DE PEDIDOS", size=16, weight=ft.FontWeight.BOLD, color="#FF9900"),
                p_input_cliente,
                p_drop_prod,
                ft.Row([p_drop_talla, p_drop_color], wrap=True),
                p_input_diseno,
                ft.FilledButton(
                    "GUARDAR PEDIDO",
                    on_click=agregar_pedido,
                    style=ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor="#FF9900", shape=ft.RoundedRectangleBorder(radius=4))
                ),
                ft.Divider(color="#333333"),
                ft.Text("📌 PEDIDOS REGISTRADOS:", size=14, weight=ft.FontWeight.BOLD, color="#888888"),
                lista_pedidos_ui
            ])
        )

        # Helper para actualizar todos los desplegables al modificar el stock
        def actualizar_todos_los_dropdowns():
            nuevas_opciones = obtener_opciones_productos()
            v_drop_prod.options = nuevas_opciones
            s_drop_prod.options = nuevas_opciones
            p_drop_prod.options = nuevas_opciones

        # Lista de pestañas
        tabs_list = [
            ft.Tab(text="VENTAS", icon=ft.Icons.SHOPPING_CART_OUTLINED, content=tab_ventas),
            ft.Tab(text="STOCK", icon=ft.Icons.ADD_BOX_OUTLINED, content=tab_stock),
            ft.Tab(text="PEDIDOS", icon=ft.Icons.ASSIGNMENT_OUTLINED, content=tab_pedidos),
        ]

        # -------------------------------------------------------------
        # PESTAÑA 4: ADMIN (Solo si el rol es admin)
        # -------------------------------------------------------------
        if usuario_actual["role"] == "admin":
            a_drop_prod = ft.Dropdown(label="SELECCIONAR PRODUCTO", width=340, options=obtener_opciones_productos(), border_color="#333333")
            a_input_precio = ft.TextField(label="NUEVO PRECIO ($)", width=160, keyboard_type=ft.KeyboardType.NUMBER, border_color="#333333")

            def cambiar_precio(e):
                key = a_drop_prod.value
                if not key or not a_input_precio.value:
                    status_text.value = "⚠️ SELECCIONA ITEM E INGRESA EL PRECIO."
                    status_text.color = "#FFCC00"
                else:
                    productos_db[key]["precio"] = float(a_input_precio.value)
                    status_text.value = f"💲 PRECIO ACTUALIZADO A ${productos_db[key]['precio']}"
                    status_text.color = "#BD00FF"
                    actualizar_todos_los_dropdowns()
                page.update()

            a_nuevo_id = ft.TextField(label="ID (EJ: P005)", width=120, border_color="#333333")
            a_nuevo_nombre = ft.TextField(label="NOMBRE MODELO", width=200, border_color="#333333")
            a_nuevo_stock = ft.TextField(label="STOCK INICIAL", width=120, value="0", border_color="#333333")
            a_nuevo_precio = ft.TextField(label="PRECIO ($)", width=120, value="0", border_color="#333333")

            def crear_producto(e):
                if not a_nuevo_id.value or not a_nuevo_nombre.value:
                    status_text.value = "⚠️ RELLENA ID Y NOMBRE DEL PRODUCTO."
                    status_text.color = "#FFCC00"
                else:
                    productos_db[a_nuevo_id.value] = {
                        "nombre": a_nuevo_nombre.value.upper(),
                        "stock": int(a_nuevo_stock.value or 0),
                        "precio": float(a_nuevo_precio.value or 0),
                    }
                    status_text.value = f"🔥 NUEVO MODELO '{a_nuevo_nombre.value.upper()}' CREADO."
                    status_text.color = "#BD00FF"
                    actualizar_todos_los_dropdowns()
                page.update()

            tab_admin = ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text("🛠️ PANEL DE ADMINISTRADOR", size=16, weight=ft.FontWeight.BOLD, color="#BD00FF"),
                    ft.Row([
                        a_drop_prod,
                        a_input_precio,
                        ft.FilledButton("ACTUALIZAR PRECIO", on_click=cambiar_precio, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#BD00FF"))
                    ], wrap=True),
                    ft.Divider(color="#333333"),
                    ft.Text("➕ AGREGAR NUEVO MODELO AL CATÁLOGO", size=14, weight=ft.FontWeight.BOLD, color="#888888"),
                    ft.Row([a_nuevo_id, a_nuevo_nombre], wrap=True),
                    ft.Row([
                        a_nuevo_stock,
                        a_nuevo_precio,
                        ft.FilledButton("CREAR PRODUCTO", on_click=crear_producto, style=ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor=ft.Colors.WHITE))
                    ], wrap=True)
                ])
            )
            tabs_list.append(ft.Tab(text="ADMIN", icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, content=tab_admin))

        # Pestaña Principal
        tabs_view = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=tabs_list,
            expand=True
        )

        page.add(
            ft.Column([
                header,
                ft.Divider(color="#222222", thickness=2),
                status_text,
                tabs_view
            ], expand=True)
        )
        page.update()

    page.add(login_view)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.run(main, port=port)