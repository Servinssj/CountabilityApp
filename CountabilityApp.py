import os
import flet as ft

# Diccionario de usuarios
USUARIOS_DB = {
    "admin": {"password": "123", "role": "admin", "nombre": "Administrador"},
    "harry": {"password": "123", "role": "usuario", "nombre": "Harry"},
    "raper": {"password": "123", "role": "usuario", "nombre": "Raper"},
    "tomi": {"password": "123", "role": "usuario", "nombre": "Tomi"},
}

# Simulador de datos de productos
productos_db = {
    "P001": {"nombre": "CAMISA OVERSIZED", "stock": 20, "precio": 500},
    "P002": {"nombre": "CALIDAD GOTEO", "stock": 40, "precio": 500},
    "P003": {"nombre": "CALIDAD BOXY", "stock": 40, "precio": 500},
}

def main(page: ft.Page):
    page.title = "CONTROL DE INVENTARIO // GOTEO "
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"  # Fondo negro/gris muy oscuro
    page.padding = 24

    # Variable para guardar el usuario logueado
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
                ft.Text("⚡ STREETLAB", size=32, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                ft.Text("// ENTER SYSTEM", size=14, color="#888888", weight=ft.FontWeight.W_600),
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
                        bgcolor="#00FF66",  # Verde Neón
                        shape=ft.RoundedRectangleBorder(radius=4),
                    ),
                ),
                login_status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment(0, 0),  # Corregido para compatibilidad con Flet reciente
        padding=20,
    )

    # --- PANTALLA 2: PANEL PRINCIPAL ---
    def mostrar_pantalla_principal():
        page.clean()

        dropdown_prod = ft.Dropdown(
            label="SELECCIONAR ITEM",
            border_color="#333333",
            focused_border_color="#00FF66",
            options=[
                ft.dropdown.Option(k, f"{v['nombre']} // STK: {v['stock']} // ${v['precio']}")
                for k, v in productos_db.items()
            ],
            width=340,
        )
        status_text = ft.Text("", size=15, weight=ft.FontWeight.BOLD)

        def actualizar_dropdown():
            dropdown_prod.options = [
                ft.dropdown.Option(k, f"{v['nombre']} // STK: {v['stock']} // ${v['precio']}")
                for k, v in productos_db.items()
            ]

        # Lógica de Venta
        cant_venta = ft.TextField(
            label="CANTIDAD VENDIDA",
            value="1",
            width=180,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color="#333333",
            focused_border_color="#00FF66",
        )
        def registrar_venta(e):
            key = dropdown_prod.value
            if not key:
                status_text.value = "⚠️ SELECCIONA UN PRODUCTO."
                status_text.color = "#FFCC00"
            else:
                cant = int(cant_venta.value or 0)
                if cant > productos_db[key]["stock"]:
                    status_text.value = f"✖ STOCK INSUFICIENTE. DISPONIBLE: {productos_db[key]['stock']}"
                    status_text.color = "#FF3333"
                else:
                    productos_db[key]["stock"] -= cant
                    status_text.value = f"✔ VENTA REGISTRADA. NUEVO STOCK: {productos_db[key]['stock']}"
                    status_text.color = "#00FF66"
                    actualizar_dropdown()
            page.update()

        # Lógica de Reabastecimiento
        cant_entrada = ft.TextField(
            label="AÑADIR STOCK",
            value="1",
            width=180,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color="#333333",
            focused_border_color="#00FF66",
        )
        def registrar_entrada(e):
            key = dropdown_prod.value
            if not key:
                status_text.value = "⚠️ SELECCIONA UN PRODUCTO."
                status_text.color = "#FFCC00"
            else:
                cant = int(cant_entrada.value or 0)
                productos_db[key]["stock"] += cant
                status_text.value = f"📦 INVENTARIO ACTUALIZADO: {productos_db[key]['stock']} UNIDADES."
                status_text.color = "#00E5FF"
                actualizar_dropdown()
            page.update()

        def cerrar_sesion(e):
            user_input.value = ""
            pass_input.value = ""
            page.clean()
            page.add(login_view)
            page.update()

        # Header
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

        vistas_usuario = [
            header,
            ft.Divider(color="#222222", thickness=2),
            ft.Text("⚡ OPERACIONES DE STOCK", size=16, weight=ft.FontWeight.BOLD, color="#888888"),
            dropdown_prod,
            ft.Container(height=5),
            ft.Row([
                cant_venta,
                ft.FilledButton(
                    "REGISTRAR VENTA",
                    on_click=registrar_venta,
                    style=ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor="#00FF66", shape=ft.RoundedRectangleBorder(radius=4))
                )
            ]),
            ft.Row([
                cant_entrada,
                ft.FilledButton(
                    "+ INVENTARIO",
                    on_click=registrar_entrada,
                    style=ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor="#00E5FF", shape=ft.RoundedRectangleBorder(radius=4))
                )
            ]),
            ft.Container(height=5),
            status_text,
        ]

        # VISTA EXCLUSIVA DE ADMIN
        if usuario_actual["role"] == "admin":
            precio_edit = ft.TextField(
                label="NUEVO PRECIO ($)",
                width=180,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_color="#333333",
                focused_border_color="#BD00FF"
            )
            
            def cambiar_precio(e):
                key = dropdown_prod.value
                if not key or not precio_edit.value:
                    status_text.value = "⚠️ SELECCIONA ITEM E INGRESA PRECIO."
                    status_text.color = "#FFCC00"
                else:
                    productos_db[key]["precio"] = float(precio_edit.value)
                    status_text.value = f"💲 PRECIO ACTUALIZADO: ${productos_db[key]['precio']}"
                    status_text.color = "#BD00FF"
                    actualizar_dropdown()
                page.update()

            nuevo_id = ft.TextField(label="ID (EJ: P004)", width=120, border_color="#333333")
            nuevo_nombre = ft.TextField(label="NOMBRE ITEM", width=180, border_color="#333333")
            nuevo_stock = ft.TextField(label="STOCK INICIAL", width=120, value="0", border_color="#333333")
            nuevo_precio = ft.TextField(label="PRECIO ($)", width=120, value="0", border_color="#333333")

            def agregar_producto(e):
                if not nuevo_id.value or not nuevo_nombre.value:
                    status_text.value = "⚠️ COMPLETA LOS CAMPOS OBLIGATORIOS."
                    status_text.color = "#FFCC00"
                else:
                    productos_db[nuevo_id.value] = {
                        "nombre": nuevo_nombre.value.upper(),
                        "stock": int(nuevo_stock.value or 0),
                        "precio": float(nuevo_precio.value or 0),
                    }
                    status_text.value = f"🔥 ITEM '{nuevo_nombre.value.upper()}' AÑADIDO AL CATALOGO."
                    status_text.color = "#00FF66"
                    actualizar_dropdown()
                page.update()

            vistas_admin = [
                ft.Divider(color="#222222", thickness=2),
                ft.Text("🛠️ PANEL DE CONTROL // ADMIN", size=16, weight=ft.FontWeight.BOLD, color="#BD00FF"),
                ft.Row([
                    precio_edit,
                    ft.FilledButton(
                        "EDITAR PRECIO",
                        on_click=cambiar_precio,
                        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#BD00FF", shape=ft.RoundedRectangleBorder(radius=4))
                    )
                ]),
                ft.Container(height=10),
                ft.Text("➕ AÑADIR NUEVO ITEM AL DROPLIST", size=14, weight=ft.FontWeight.BOLD, color="#888888"),
                ft.Row([nuevo_id, nuevo_nombre]),
                ft.Row([
                    nuevo_stock,
                    nuevo_precio,
                    ft.FilledButton(
                        "CREAR ITEM",
                        on_click=agregar_producto,
                        style=ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=4))
                    )
                ]),
            ]
            vistas_usuario.extend(vistas_admin)

        page.add(ft.Column(controls=vistas_usuario, scroll=ft.ScrollMode.AUTO))
        page.update()

    page.add(login_view)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.run(main, port=port)
