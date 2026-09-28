import os
import flet as ft

USUARIOS_DB = {
    "servin": {"password": "123", "role": "admin", "nombre": "Administrador"},
    "harry": {"password": "123", "role": "usuario", "nombre": "Harry"},
    "raper": {"password": "123", "role": "usuario", "nombre": "Raper"},
    "tomi": {"password": "123", "role": "usuario", "nombre": "Tomi"},
}

productos_db = {
    "P001": {"nombre": "PLAYERA REGULAR - JHK", "stock": 30, "precio": 500, "es_dtf": False},
    "P002": {"nombre": "PLAYERA OVERSIZED - JHK", "stock": 25, "precio": 450, "es_dtf": False},
    "P003": {"nombre": "PLAYERA OVERSIZED - JHK", "stock": 25, "precio": 450, "es_dtf": False},
    "P004": {"nombre": "HOODIE - JHK", "stock": 15, "precio": 850, "es_dtf": False},
    "P005": {"nombre": "SUETER - JHK", "stock": 20, "precio": 750, "es_dtf": False},
    "P006": {"nombre": "PLAYERA MALAGA - CBK (Regular)", "stock": 10, "precio": 950, "es_dtf": False},
    "P007": {"nombre": "PLAYERA MÉRIDA - CBK (Oversized)", "stock": 10, "precio": 950, "es_dtf": False},
    "P008": {"nombre": "PLAYERA MALAGA - CBK (Mineral Wash)", "stock": 10, "precio": 950, "es_dtf": False},
    "P009": {"nombre": "PLAYERA TAMPA - CBK (BOXY)", "stock": 10, "precio": 950, "es_dtf": False},
    "P_DTF": {"nombre": "IMPRESIÓN DTF (MEDIDA ESPECIAL)", "stock": 0, "precio": 0, "es_dtf": True},
}

pedidos_db = []
historial_db = []
finanzas_db = {
    "total_ingresado_ventas": 0.0,
    "total_invertido_stock": sum(p["stock"] * p["precio"] for p in productos_db.values() if not p.get("es_dtf")),
    "total_gastos_dtf": 0.0
}

COLORES_HEX = {
    "Negro": "#000000",
    "Blanco": "#FFFFFF",
    "Gris": "#808080",
    "Beige": "#F5F5DC",
    "Verde Acid": "#7FFF00",
}

TALLAS = ["CH (S)", "M", "G (L)", "XG (XL)"]
TIPOS_DTF = ["Textil", "UV"]
METODOS_PAGO = ["Efectivo", "Transferencia"]

def main(page: ft.Page):
    page.title = "CONTROL DE INVENTARIO // GOTEO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    usuario_actual = {"nombre": "", "role": ""}

    user_input = ft.TextField(label="USUARIO", width=320, color="white")
    pass_input = ft.TextField(label="CONTRASEÑA", password=True, can_reveal_password=True, width=320, color="white")
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
                ft.Text("⚡ GOTEO", size=32, weight=ft.FontWeight.W_900, color="white"),
                ft.Text("Sistema de Control e Inventario", size=14, color="#888888", weight=ft.FontWeight.W_600),
                ft.Container(height=10),
                user_input,
                pass_input,
                ft.Container(height=10),
                ft.Button(
                    "ACCEDER ➔",
                    on_click=iniciar_sesion,
                    width=320,
                    style=ft.ButtonStyle(color="black", bgcolor="#00FF66", shape=ft.RoundedRectangleBorder(radius=4)),
                ),
                login_status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment(0, 0),
        padding=20,
    )

    def mostrar_pantalla_principal():
        page.clean()

        status_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

        def obtener_opciones_productos():
            return [
                ft.dropdown.Option(k, f"{v['nombre']} " + (f"// ${v['precio']}" if not v.get("es_dtf") else "// SOBRE PEDIDO"))
                for k, v in productos_db.items()
            ]

        def cerrar_sesion(e):
            user_input.value = ""
            pass_input.value = ""
            page.clean()
            page.add(login_view)
            page.update()

        header = ft.Row(
            controls=[
                ft.Column([
                    ft.Text(f"// {usuario_actual['nombre'].upper()}", size=18, weight=ft.FontWeight.W_900, color="white"),
                    ft.Text(f"ROLE: {usuario_actual['role'].upper()}", size=12, color="#00FF66", weight=ft.FontWeight.BOLD),
                ]),
                ft.Button(
                    "LOGOUT",
                    on_click=cerrar_sesion,
                    style=ft.ButtonStyle(color="white", side=ft.BorderSide(1, "#444444"), shape=ft.RoundedRectangleBorder(radius=4))
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        def crear_selector_color(val_inicial="Negro"):
            dropdown = ft.Dropdown(
                label="COLOR",
                width=180,
                options=[ft.dropdown.Option(c) for c in COLORES_HEX.keys()],
                value=val_inicial,
                color="white",
                border_color="#666666",
                focused_border_color="#00FF66"
            )

            def on_color_change(e):
                c_name = dropdown.value
                if c_name in COLORES_HEX:
                    hex_val = COLORES_HEX[c_name]
                    dropdown.color = "white" if c_name == "Negro" else hex_val
                    dropdown.border_color = hex_val
                    dropdown.focused_border_color = hex_val
                    dropdown.update()

            dropdown.on_change = on_color_change
            return dropdown

        lista_pedidos_ui = ft.Column()
        lista_ventas_pedidos_ui = ft.Column()
        lista_historial_ui = ft.Column(spacing=10)

        txt_ventas_total = ft.Text("$0.00", size=26, weight=ft.FontWeight.BOLD, color="#00FF66")
        txt_stock_total = ft.Text("$0.00", size=26, weight=ft.FontWeight.BOLD, color="#00E5FF")
        txt_balance_neto = ft.Text("$0.00", size=26, weight=ft.FontWeight.BOLD, color="white")
        container_balance = ft.Container(
            padding=15, bgcolor="#1E1E1E", border_radius=8, width=280,
            border=ft.Border.all(1, "#333333"),
            content=ft.Column([
                ft.Text("📊 BALANCE NETO (VENTAS - INVERSIÓN)", size=12, color="#CCCCCC", weight=ft.FontWeight.BOLD),
                txt_balance_neto
            ])
        )

        def renderizar_finanzas():
            v_total = finanzas_db["total_ingresado_ventas"]
            # Inversión total acumula tanto stock como compras de DTF
            inversion_total = finanzas_db["total_invertido_stock"] + finanzas_db["total_gastos_dtf"]
            balance = v_total - inversion_total
            
            txt_ventas_total.value = f"${v_total:,.2f}"
            txt_stock_total.value = f"${inversion_total:,.2f}"
            
            if balance >= 0:
                txt_balance_neto.value = f"+${balance:,.2f}"
                txt_balance_neto.color = "#00FF66"
                container_balance.border = ft.Border.all(1, "#00FF66")
            else:
                txt_balance_neto.value = f"-${abs(balance):,.2f}"
                txt_balance_neto.color = "#FF3333"
                container_balance.border = ft.Border.all(1, "#FF3333")

        def renderizar_historial():
            lista_historial_ui.controls.clear()
            if not historial_db:
                lista_historial_ui.controls.append(ft.Text("No hay registros de actividad aún.", color="#888888", size=14))
            else:
                for h in reversed(historial_db):
                    icon_map = {"pedido": "📝", "venta": "🛒", "stock": "📦", "gasto": "💸"}
                    color_map = {"pedido": "#FF9900", "venta": "#00FF66", "stock": "#00E5FF", "gasto": "#FF3333"}
                    
                    lista_historial_ui.controls.append(
                        ft.Container(
                            padding=12,
                            bgcolor="#1E1E1E",
                            border=ft.Border.all(1, "#333333"),
                            border_radius=6,
                            content=ft.Row([
                                ft.Text(f"{icon_map.get(h['tipo'], '📌')} [{h['tipo'].upper()}]", color=color_map.get(h['tipo'], "white"), weight=ft.FontWeight.BOLD, size=13),
                                ft.Text(f"USUARIO: {h['usuario']}", color="white", weight=ft.FontWeight.BOLD, size=13),
                                ft.Text(f"| {h['detalle']}", color="#EEEEEE", size=13)
                            ], wrap=True)
                        )
                    )

        # PESTAÑA VENTAS
        def renderizar_ventas_pedidos():
            lista_ventas_pedidos_ui.controls.clear()
            
            if not pedidos_db:
                lista_ventas_pedidos_ui.controls.append(ft.Text("No hay pedidos pendientes por cobrar.", color="#888888"))
            else:
                for idx, ped in enumerate(pedidos_db):
                    es_dtf = ped.get("es_dtf", False)
                    
                    if not es_dtf:
                        prod_info = productos_db.get(ped["prod_key"], {"precio": 0})
                        precio_inicial = prod_info["precio"] * ped.get("cantidad", 1)
                        detalle_texto = f"📦 {ped['cantidad']}x {ped['producto']} [{ped['talla']} / {ped['color']}] | Diseño: {ped['diseno']}"
                    else:
                        precio_inicial = 0.0
                        detalle_texto = f"🖨️ DTF (CANTIDAD EN METROS: {ped.get('cantidad', 1)}m)"

                    drop_pago = ft.Dropdown(
                        label="TIPO DE PAGO",
                        width=180,
                        options=[ft.dropdown.Option(p) for p in METODOS_PAGO],
                        border_color="#00FF66",
                        color="white"
                    )

                    input_precio_final = ft.TextField(
                        label="PRECIO / COSTO ($)",
                        value=str(precio_inicial) if precio_inicial > 0 else "",
                        width=160,
                        keyboard_type=ft.KeyboardType.NUMBER,
                        color="white"
                    )

                    def concretar_venta(e, pedido_index=idx, selector_pago=drop_pago, campo_precio=input_precio_final):
                        if not selector_pago.value:
                            status_text.value = "⚠️ DEBES SELECCIONAR UN TIPO DE PAGO."
                            status_text.color = "#FFCC00"
                            page.update()
                            return

                        p = pedidos_db[pedido_index]
                        prod_key = p["prod_key"]
                        cant = p.get("cantidad", 1)
                        es_dtf_item = p.get("es_dtf", False)

                        try:
                            monto_venta = float(campo_precio.value or 0)
                        except ValueError:
                            monto_venta = 0.0

                        if not es_dtf_item and cant > productos_db[prod_key]["stock"]:
                            status_text.value = f"✖ STOCK INSUFICIENTE. DISPONIBLE: {productos_db[prod_key]['stock']}"
                            status_text.color = "#FF3333"
                        else:
                            if not es_dtf_item:
                                productos_db[prod_key]["stock"] -= cant
                            else:
                                # SI ES DTF, SUMA AL TOTAL DE INVERSIÓN/COSTO DTF
                                finanzas_db["total_gastos_dtf"] += monto_venta

                            metodo_pago = selector_pago.value
                            vendedor = usuario_actual["nombre"].upper()
                            
                            finanzas_db["total_ingresado_ventas"] += monto_venta
                            
                            historial_db.append({
                                "tipo": "venta",
                                "usuario": vendedor,
                                "detalle": f"Venta/Cobro completado a {p['cliente']} ({p['producto']}) - Pago: {metodo_pago} - Total: ${monto_venta}"
                            })

                            pedidos_db.pop(pedido_index)
                            
                            status_text.value = f"✔ PROCESADO | Cliente: {p['cliente']} | Total: ${monto_venta}"
                            status_text.color = "#00FF66"
                            
                            actualizar_todos_los_dropdowns()
                            renderizar_pedidos()
                            renderizar_ventas_pedidos()
                            renderizar_finanzas()
                            if usuario_actual["role"] == "admin":
                                renderizar_historial()
                        page.update()

                    item_row = ft.Container(
                        padding=12,
                        bgcolor="#1E1E1E",
                        border_radius=6,
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Text(f"👤 CLIENTE: {ped['cliente']}", size=14, weight=ft.FontWeight.BOLD, color="white"),
                                    ft.Text(detalle_texto, size=13, color="#CCCCCC"),
                                ]),
                                ft.Column([
                                    input_precio_final,
                                    drop_pago,
                                    ft.Button("CONFIRMAR VENTA", on_click=concretar_venta, style=ft.ButtonStyle(color="black", bgcolor="#00FF66", shape=ft.RoundedRectangleBorder(radius=4)))
                                ], horizontal_alignment=ft.CrossAxisAlignment.END)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ])
                    )
                    lista_ventas_pedidos_ui.controls.append(item_row)

        tab_ventas = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text("🛒 COMPLETAR VENTA DE PEDIDOS", size=16, weight=ft.FontWeight.BOLD, color="#00FF66"),
                ft.Text("Selecciona el tipo de pago y confirma para procesar los ingresos y/o costos:", size=13, color="#888888"),
                ft.Divider(color="#333333"),
                lista_ventas_pedidos_ui
            ])
        )

        # PESTAÑA STOCK
        s_drop_prod = ft.Dropdown(
            label="PRODUCTO", 
            width=340, 
            options=[ft.dropdown.Option(k, f"{v['nombre']} // ${v['precio']}") for k, v in productos_db.items() if not v.get("es_dtf")], 
            color="white"
        )
        s_drop_talla = ft.Dropdown(label="TALLA", width=160, options=[ft.dropdown.Option(t) for t in TALLAS], color="white")
        s_drop_color = crear_selector_color()
        s_input_cant = ft.TextField(label="AÑADIR CANTIDAD", value="1", width=160, keyboard_type=ft.KeyboardType.NUMBER, color="white")

        def registrar_stock(e):
            key = s_drop_prod.value
            if not key or not s_drop_talla.value or not s_drop_color.value:
                status_text.value = "⚠️ SELECCIONA PRODUCTO, TALLA Y COLOR."
                status_text.color = "#FFCC00"
            else:
                cant = int(s_input_cant.value or 0)
                productos_db[key]["stock"] += cant
                prod_nombre = productos_db[key]["nombre"]
                
                costo_adicional = productos_db[key]["precio"] * cant
                finanzas_db["total_invertido_stock"] += costo_adicional

                historial_db.append({
                    "tipo": "stock",
                    "usuario": usuario_actual["nombre"].upper(),
                    "detalle": f"Agregó +{cant} unidades a {prod_nombre} [{s_drop_talla.value}/{s_drop_color.value}] (Valor: ${costo_adicional})"
                })

                status_text.value = f"📦 REABASTECIDO: +{cant} unidades de {prod_nombre}. Total stock: {productos_db[key]['stock']}"
                status_text.color = "#00E5FF"
                actualizar_todos_los_dropdowns()
                renderizar_finanzas()
                if usuario_actual["role"] == "admin":
                    renderizar_historial()
            page.update()

        tab_stock = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text("📦 AGREGAR STOCK / INVENTARIO", size=16, weight=ft.FontWeight.BOLD, color="#00E5FF"),
                s_drop_prod,
                ft.Row([s_drop_talla, s_drop_color], wrap=True),
                ft.Row([
                    s_input_cant,
                    ft.Button("+ AÑADIR STOCK", on_click=registrar_stock, style=ft.ButtonStyle(color="black", bgcolor="#00E5FF", shape=ft.RoundedRectangleBorder(radius=4)))
                ], wrap=True)
            ])
        )

        # -------------------------------------------------------------
        # PESTAÑA PEDIDOS
        # -------------------------------------------------------------
        p_input_cliente = ft.TextField(label="NOMBRE DEL CLIENTE", width=340, color="white")
        p_input_cant = ft.TextField(label="CANTIDAD", value="1", width=160, keyboard_type=ft.KeyboardType.NUMBER, color="white")
        
        p_drop_talla = ft.Dropdown(label="TALLA", width=160, options=[ft.dropdown.Option(t) for t in TALLAS], color="white")
        p_drop_color = crear_selector_color()
        p_input_diseno = ft.TextField(label="DISEÑO DETALLADO", width=340, color="white")

        p_drop_prod = ft.Dropdown(
            label="PRODUCTO",
            width=340,
            options=obtener_opciones_productos(),
            color="white"
        )

        dinamic_form_area = ft.Column()

        def redefinir_formulario_pedido(e=None):
            val = p_drop_prod.value
            es_dtf = productos_db.get(val, {}).get("es_dtf", False) if val else False
            
            dinamic_form_area.controls.clear()
            
            if es_dtf:
                p_input_cant.label = "CANTIDAD EN METROS"
                dinamic_form_area.controls.append(
                    ft.Column([
                        p_input_cant
                    ])
                )
            else:
                p_input_cant.label = "CANTIDAD"
                dinamic_form_area.controls.append(
                    ft.Column([
                        ft.Row([p_drop_talla, p_drop_color, p_input_cant], wrap=True),
                        p_input_diseno
                    ])
                )
            page.update()

        p_drop_prod.on_change = redefinir_formulario_pedido
        redefinir_formulario_pedido()
        
        def renderizar_pedidos():
            lista_pedidos_ui.controls.clear()
            if not pedidos_db:
                lista_pedidos_ui.controls.append(ft.Text("No hay pedidos registrados.", color="#888888"))
            else:
                for idx, ped in enumerate(pedidos_db):
                    if ped.get("es_dtf"):
                        txt_info = f"🖨️ #{idx+1} | {ped['cliente']} ➔ IMPRESIÓN DTF ({ped['cantidad']} METROS) [Pendiente por Cobrar]"
                    else:
                        precio_u = productos_db.get(ped['prod_key'], {}).get('precio', 0)
                        txt_info = (f"📋 #{idx+1} | {ped['cliente']} ➔ {ped['cantidad']}x {ped['producto']} "
                                    f"({ped['talla']}/{ped['color']}) - Dis: {ped['diseno']} [Total: ${precio_u * ped['cantidad']}]")

                    lista_pedidos_ui.controls.append(
                        ft.Container(
                            content=ft.Text(txt_info, size=13, color="white"),
                            padding=8,
                            bgcolor="#1E1E1E",
                            border_radius=4
                        )
                    )

        def agregar_pedido(e):
            cliente_val = p_input_cliente.value.strip() if p_input_cliente.value else ""
            key = p_drop_prod.value

            if not cliente_val or not key:
                status_text.value = "⚠️ COMPLETA AL MENOS CLIENTE Y PRODUCTO."
                status_text.color = "#FFCC00"
                page.update()
                return

            es_dtf = productos_db[key].get("es_dtf", False)

            if es_dtf:
                cant_val = float(p_input_cant.value.strip() or 1)
                nuevo_pedido = {
                    "cliente": cliente_val.upper(),
                    "prod_key": key,
                    "producto": productos_db[key]["nombre"],
                    "es_dtf": True,
                    "cantidad": cant_val,
                }

                historial_db.append({
                    "tipo": "pedido",
                    "usuario": usuario_actual["nombre"].upper(),
                    "detalle": f"Pedido DTF registrado para {nuevo_pedido['cliente']} ({nuevo_pedido['cantidad']}m)"
                })

            else:
                if not p_input_diseno.value:
                    status_text.value = "⚠️ INGRESA EL DISEÑO DETALLADO."
                    status_text.color = "#FFCC00"
                    page.update()
                    return

                nuevo_pedido = {
                    "cliente": cliente_val.upper(),
                    "prod_key": key,
                    "producto": productos_db[key]["nombre"],
                    "talla": p_drop_talla.value or "M",
                    "color": p_drop_color.value or "Negro",
                    "diseno": p_input_diseno.value.strip(),
                    "cantidad": int(p_input_cant.value.strip() or 1),
                    "es_dtf": False
                }

                historial_db.append({
                    "tipo": "pedido",
                    "usuario": usuario_actual["nombre"].upper(),
                    "detalle": f"Registró pedido para {nuevo_pedido['cliente']} ({nuevo_pedido['producto']})"
                })

            pedidos_db.append(nuevo_pedido)

            status_text.value = f"📝 PEDIDO REGISTRADO PARA {nuevo_pedido['cliente']}"
            status_text.color = "#FF9900"
            
            p_input_cliente.value = ""
            p_drop_prod.value = None
            p_drop_talla.value = None
            p_drop_color.value = "Negro"
            p_input_diseno.value = ""
            p_input_cant.value = "1"
            
            redefinir_formulario_pedido()
            renderizar_pedidos()
            renderizar_ventas_pedidos()
            renderizar_finanzas()
            if usuario_actual["role"] == "admin":
                renderizar_historial()

            def cerrar_popup(ev):
                popup.open = False
                page.update()

            detalles_popup = (
                f"• Detalle: IMPRESIÓN DTF ({nuevo_pedido.get('cantidad')} METROS)"
            ) if es_dtf else (
                f"• Producto: {nuevo_pedido['cantidad']}x {nuevo_pedido['producto']}\n"
                f"• Talla: {nuevo_pedido['talla']} | Color: {nuevo_pedido['color']}\n"
                f"• Importe Est.: ${productos_db[key]['precio'] * nuevo_pedido['cantidad']}"
            )

            popup = ft.AlertDialog(
                modal=True,
                title=ft.Text("¡Pedido Registrado!", weight=ft.FontWeight.BOLD, color="#00FF66"),
                content=ft.Text(f"Se guardó correctamente el pedido para:\n\n• Cliente: {nuevo_pedido['cliente']}\n{detalles_popup}", color="white"),
                actions=[ft.Button("ACEPTAR", on_click=cerrar_popup, style=ft.ButtonStyle(color="black", bgcolor="#00FF66"))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            page.overlay.append(popup)
            popup.open = True
            page.update()

        tab_pedidos = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text("📝 REGISTRO DE PEDIDOS", size=16, weight=ft.FontWeight.BOLD, color="#FF9900"),
                p_input_cliente,
                p_drop_prod,
                dinamic_form_area,
                ft.Button("GUARDAR PEDIDO", on_click=agregar_pedido, style=ft.ButtonStyle(color="black", bgcolor="#FF9900", shape=ft.RoundedRectangleBorder(radius=4))),
                ft.Divider(color="#333333"),
                ft.Text("📌 PEDIDOS REGISTRADOS:", size=14, weight=ft.FontWeight.BOLD, color="#888888"),
                lista_pedidos_ui
            ])
        )

        # FINANZAS ACTUALIZADO
        tab_finanzas = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text("📊 BALANCE DE INGRESOS, INVERSIÓN Y GANANCIAS", size=16, weight=ft.FontWeight.BOLD, color="#00FF66"),
                ft.Text("Resumen financiero general:", size=13, color="#888888"),
                ft.Divider(color="#333333"),
                ft.Row([
                    ft.Container(
                        padding=15, bgcolor="#1E1E1E", border_radius=8, width=280,
                        border=ft.Border.all(1, "#333333"),
                        content=ft.Column([
                            ft.Text("💵 INGRESOS POR VENTAS", size=12, color="#CCCCCC", weight=ft.FontWeight.BOLD),
                            txt_ventas_total
                        ])
                    ),
                    ft.Container(
                        padding=15, bgcolor="#1E1E1E", border_radius=8, width=280,
                        border=ft.Border.all(1, "#333333"),
                        content=ft.Column([
                            ft.Text("📦 INVERSIÓN TOTAL (STOCK + DTF)", size=12, color="#CCCCCC", weight=ft.FontWeight.BOLD),
                            txt_stock_total
                        ])
                    ),
                    container_balance,
                ], wrap=True, spacing=15)
            ], spacing=10)
        )

        def actualizar_todos_los_dropdowns():
            nuevas_opciones = obtener_opciones_productos()
            s_drop_prod.options = [ft.dropdown.Option(k, f"{v['nombre']} // ${v['precio']}") for k, v in productos_db.items() if not v.get("es_dtf")]
            p_drop_prod.options = nuevas_opciones

        renderizar_pedidos()
        renderizar_ventas_pedidos()
        renderizar_finanzas()

        tabs_map = {
            0: tab_ventas,
            1: tab_stock,
            2: tab_pedidos,
            3: tab_finanzas
        }

        btn_ventas = ft.Button("VENTAS", style=ft.ButtonStyle(color="white", bgcolor="#1A1A1A"))
        btn_stock = ft.Button("STOCK", style=ft.ButtonStyle(color="white", bgcolor="#1A1A1A"))
        btn_pedidos = ft.Button("PEDIDOS", style=ft.ButtonStyle(color="white", bgcolor="#1A1A1A"))
        btn_finanzas = ft.Button("FINANZAS", style=ft.ButtonStyle(color="white", bgcolor="#1A1A1A"))

        tab_buttons = [btn_ventas, btn_stock, btn_pedidos, btn_finanzas]

        # PESTAÑAS ADMIN
        if usuario_actual["role"] == "admin":
            renderizar_historial()

            a_drop_prod = ft.Dropdown(label="SELECCIONAR PRODUCTO", width=340, options=obtener_opciones_productos(), color="white")
            a_input_precio = ft.TextField(label="NUEVO PRECIO ($)", width=160, keyboard_type=ft.KeyboardType.NUMBER, color="white")

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
                    renderizar_ventas_pedidos()
                    renderizar_finanzas()
                page.update()

            a_nuevo_id = ft.TextField(label="ID (EJ: P005)", width=120, color="white")
            a_nuevo_nombre = ft.TextField(label="NOMBRE MODELO", width=200, color="white")
            a_nuevo_stock = ft.TextField(label="STOCK INICIAL", width=120, value="0", color="white")
            a_nuevo_precio = ft.TextField(label="PRECIO ($)", width=120, value="0", color="white")

            def crear_producto(e):
                if not a_nuevo_id.value or not a_nuevo_nombre.value:
                    status_text.value = "⚠️ RELLENA ID Y NOMBRE DEL PRODUCTO."
                    status_text.color = "#FFCC00"
                else:
                    productos_db[a_nuevo_id.value] = {
                        "nombre": a_nuevo_nombre.value.upper(),
                        "stock": int(a_nuevo_stock.value or 0),
                        "precio": float(a_nuevo_precio.value or 0),
                        "es_dtf": False
                    }
                    finanzas_db["total_invertido_stock"] += int(a_nuevo_stock.value or 0) * float(a_nuevo_precio.value or 0)
                    status_text.value = f"🔥 NUEVO MODELO '{a_nuevo_nombre.value.upper()}' CREADO."
                    status_text.color = "#BD00FF"
                    actualizar_todos_los_dropdowns()
                    renderizar_finanzas()
                page.update()

            tab_historial = ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text("📜 HISTORIAL DE ACTIVIDAD COMPLETO", size=16, weight=ft.FontWeight.BOLD, color="#BD00FF"),
                    ft.Text("Registro detallado de acciones realizadas por cada usuario:", size=13, color="#888888"),
                    ft.Divider(color="#333333"),
                    lista_historial_ui
                ])
            )

            tab_admin = ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text("🛠️ PANEL DE ADMINISTRADOR", size=16, weight=ft.FontWeight.BOLD, color="#BD00FF"),
                    ft.Row([
                        a_drop_prod,
                        a_input_precio,
                        ft.Button("ACTUALIZAR PRECIO", on_click=cambiar_precio, style=ft.ButtonStyle(color="white", bgcolor="#BD00FF"))
                    ], wrap=True),
                    ft.Divider(color="#333333"),
                    ft.Text("➕ AGREGAR NUEVO MODELO AL CATÁLOGO", size=14, weight=ft.FontWeight.BOLD, color="#888888"),
                    ft.Row([a_nuevo_id, a_nuevo_nombre], wrap=True),
                    ft.Row([
                        a_nuevo_stock,
                        a_nuevo_precio,
                        ft.Button("CREAR PRODUCTO", on_click=crear_producto, style=ft.ButtonStyle(color="black", bgcolor="white"))
                    ], wrap=True)
                ])
            )

            btn_historial = ft.Button("HISTORIAL", style=ft.ButtonStyle(color="white", bgcolor="#1A1A1A"))
            btn_admin = ft.Button("ADMIN", style=ft.ButtonStyle(color="white", bgcolor="#1A1A1A"))
            
            tab_buttons.extend([btn_historial, btn_admin])
            tabs_map[4] = tab_historial
            tabs_map[5] = tab_admin

        content_area = ft.Container(content=tab_ventas)

        def select_tab(idx):
            content_area.content = tabs_map[idx]
            page.update()

        btn_ventas.on_click = lambda e: select_tab(0)
        btn_stock.on_click = lambda e: select_tab(1)
        btn_pedidos.on_click = lambda e: select_tab(2)
        btn_finanzas.on_click = lambda e: select_tab(3)
        if usuario_actual["role"] == "admin":
            tab_buttons[4].on_click = lambda e: select_tab(4)
            tab_buttons[5].on_click = lambda e: select_tab(5)

        nav_bar = ft.Row(controls=tab_buttons, spacing=8, wrap=True)

        page.add(
            ft.Column([
                header,
                ft.Divider(color="#222222", thickness=2),
                status_text,
                nav_bar,
                ft.Divider(color="#333333", thickness=1),
                content_area
            ])
        )
        page.update()

    page.add(login_view)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.run(main, port=port)