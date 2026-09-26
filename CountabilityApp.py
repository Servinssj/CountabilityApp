import flet as ft
import os
# Simulador de datos (En producción te conectas a Supabase / SQLite)
productos_db = {
    "P001": {"nombre": "Camisa Oversized", "stock": 20, "precio": 500},
    "P002": {"nombre": "Calidad Goteo", "stock": 40, "precio": 500},
}

def main(page: ft.Page):
    page.title = "Control de Inventario"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Componentes de la interfaz
    dropdown_prod = ft.Dropdown(
        label="Seleccionar Producto",
        options=[
            ft.dropdown.Option(key, f"{val['nombre']} (Stock: {val['stock']})")
            for key, val in productos_db.items()
        ],
        width=300,
    )

    cant_input = ft.TextField(label="Cantidad Vendida", value="1", width=300, keyboard_type=ft.KeyboardType.NUMBER)
    status_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)

    # Lógica de actualización de inventario
    def registrar_venta(e):
            selected_key = dropdown_prod.value
            if not selected_key:
                status_text.value = "⚠️ Selecciona un producto."
                status_text.color = ft.Colors.ORANGE_700  # O también: status_text.color = "orange"
                page.update()
                return

            cantidad = int(cant_input.value)
            stock_actual = productos_db[selected_key]["stock"]

            if cantidad > stock_actual:
                status_text.value = f"❌ Stock insuficiente. Quedan {stock_actual} unidades."
                status_text.color = ft.Colors.RED  # O también: status_text.color = "red"
            else:
                productos_db[selected_key]["stock"] -= cantidad
                nuevo_stock = productos_db[selected_key]["stock"]
                
                status_text.value = f"✅ Venta registrada. Nuevo stock: {nuevo_stock}"
                status_text.color = ft.Colors.GREEN  # <--- AQUÍ ESTABA EL ERROR (Cambia a Colors con C mayúscula)
                
                dropdown_prod.options = [
                    ft.dropdown.Option(k, f"{v['nombre']} (Stock: {v['stock']})")
                    for k, v in productos_db.items()
                ]

            page.update()

    # Layout de la app móvil
    page.add(
        ft.Text("📦 Registrar Salida / Venta", size=22, weight=ft.FontWeight.BOLD),
        dropdown_prod,
        cant_input,
        ft.FilledButton(
            "Confirmar Venta",
            on_click=registrar_venta,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
            ),
        ),
        status_text
    )

if __name__ == "__main__":
    # Lee el puerto configurado por el servidor hosting o usa el 8080 por defecto
    port = int(os.environ.get("PORT", 8080))
    ft.run(main, port=port)