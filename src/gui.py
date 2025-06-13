# src/gui.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
import subprocess
import threading
import math
from src.database import execute_query, execute_mod_query
from src.queries_relacional import *
from src.config import check_db_config

def main(page: ft.Page):
    page.title = "LUBRI-EXPRESS - Gestión de Inventario"
    page.window_width = 1920
    page.window_height = 1080

    # --- MEJORA ESTÉTICA: Centrado y Padding ---
    page.padding = ft.padding.all(20)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- TEMAS DE COLOR Y APPBAR ---
    def change_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        theme_switch.label = "Modo Claro" if page.theme_mode == ft.ThemeMode.DARK else "Modo Oscuro"
        page.update()

    theme_switch = ft.Switch(label="Modo Oscuro", on_change=change_theme, value=(page.theme_mode == ft.ThemeMode.DARK))

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.CAR_REPAIR),
        title=ft.Text("LUBRI-EXPRESS - Gestión de Inventario"),
        center_title=False,
        bgcolor=ft.Colors.PRIMARY_CONTAINER,
        actions=[theme_switch, ft.VerticalDivider()]
    )

    page.theme = ft.Theme(color_scheme_seed="indigo")
    page.dark_theme = ft.Theme(color_scheme_seed="indigo")

    # --- LÓGICA DE PAGINACIÓN Y BÚSQUEDA ---
    page_size = 15
    current_offset = ft.Text("0", visible=False)

    def handle_search_change(e):
        current_offset.value = "0"
        load_products_data()

    search_field = ft.TextField(
        label="Buscar por Nombre o SKU",
        prefix_icon=ft.Icons.SEARCH,
        on_change=handle_search_change,
        width=350,
        dense=True
    )

    def load_products_data(e=None):
        offset = int(current_offset.value)
        search_term = search_field.value
        sql_search_term = f"%{search_term}%"

        query_params = ()
        if search_term:
            count_query = COUNT_FILTERED_PRODUCTS_SQL
            data_query = GET_FILTERED_PAGINATED_PRODUCTS_SQL
            query_params = (sql_search_term, sql_search_term)
        else:
            count_query = COUNT_PRODUCTS_SQL
            data_query = GET_PAGINATED_PRODUCTS_SQL

        df_count = execute_query(count_query, query_params)
        total_records = df_count['total'][0] if df_count is not None and not df_count.empty else 0
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        current_page = (offset // page_size) + 1

        pagination_text.value = f"Página {current_page} de {total_pages}"
        prev_button.disabled = (current_page == 1)
        next_button.disabled = (current_page >= total_pages)

        paginated_params = query_params + (page_size, offset)
        df = execute_query(data_query, paginated_params)

        products_datatable.rows.clear()
        if df is not None and not df.empty:
            for index, row in df.iterrows():
                products_datatable.rows.append(
                    ft.DataRow(
                        color=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY) if index % 2 == 0 else None,
                        cells=[
                            ft.DataCell(ft.Text(str(row['producto_id']))),
                            ft.DataCell(ft.Text(row['nombre'], width=300, no_wrap=True, tooltip=row['nombre'])),
                            ft.DataCell(ft.Text(row['sku'])),
                            ft.DataCell(ft.Text(f"${int(row['costo_unitario']):,}".replace(",", "."))),
                            ft.DataCell(ft.Text(f"${int(row['precio_venta']):,}".replace(",", "."))),
                            ft.DataCell(ft.Text(str(row['stock']))),
                            ft.DataCell(ft.Text(row['categoria'])),
                            ft.DataCell(ft.Text(row['fabricante'])),
                            ft.DataCell(ft.Text(row['ubicacion'])),
                            ft.DataCell(ft.Row([
                                    ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=show_edit_form, data=row['producto_id']),
                                    ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Eliminar", on_click=show_delete_confirmation, data=row['producto_id'])
                                ]))]))
        page.update()

    def go_to_page(e):
        offset = int(current_offset.value)
        if e.control.tooltip == "Página Siguiente": current_offset.value = str(offset + page_size)
        elif e.control.tooltip == "Página Anterior": current_offset.value = str(offset - page_size)
        load_products_data()

    prev_button = ft.IconButton(icon=ft.Icons.NAVIGATE_BEFORE, on_click=go_to_page, tooltip="Página Anterior")
    next_button = ft.IconButton(icon=ft.Icons.NAVIGATE_NEXT, on_click=go_to_page, tooltip="Página Siguiente")
    pagination_text = ft.Text()

    def load_data_worker():
        load_data_button.disabled = True; progress_ring.visible = True; page.update()
        try:
            subprocess.run([sys.executable, "src/inserts_relacional.py"], capture_output=True, text=True, check=True)
            page.snack_bar = ft.SnackBar(content=ft.Text("Datos de prueba cargados con éxito."), bgcolor=ft.Colors.GREEN); page.snack_bar.open = True
            current_offset.value = "0"; populate_dropdowns(); load_products_data()
        except subprocess.CalledProcessError as e:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al cargar datos: {e.stderr[:100]}..."), bgcolor=ft.Colors.RED); page.snack_bar.open = True
        load_data_button.disabled = False; progress_ring.visible = False; page.update()
    def run_data_load(e):
        threading.Thread(target=load_data_worker, daemon=True).start()
    load_data_button = ft.ElevatedButton(text="Cargar Datos", icon=ft.Icons.UPLOAD, on_click=run_data_load, tooltip="Puebla la BD con datos de prueba.")
    progress_ring = ft.ProgressRing(visible=False, width=16, height=16, stroke_width=2)
    editing_product_id = ft.Text(visible=False)
    nombre_field = ft.TextField(label="Nombre del Producto", col=6); sku_field = ft.TextField(label="SKU", read_only=True, hint_text="Se genera...", col=6)
    costo_field = ft.TextField(label="Costo Unitario", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"), col=4)
    precio_field = ft.TextField(label="Precio de Venta", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"), col=4)
    stock_field = ft.TextField(label="Stock", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"), col=4)
    categoria_dropdown = ft.Dropdown(label="Categoría", on_change=lambda e: generate_and_set_sku(), col=4)
    fabricante_dropdown = ft.Dropdown(label="Fabricante", on_change=lambda e: generate_and_set_sku(), col=4)
    ubicacion_dropdown = ft.Dropdown(label="Ubicación", col=4)
    form_title = ft.Text(style=ft.TextThemeStyle.HEADLINE_SMALL)

    def generate_and_set_sku():
        # ...
        fab_id_str = fabricante_dropdown.value; cat_id_str = categoria_dropdown.value
        if not fab_id_str or not cat_id_str: sku_field.value = "Seleccione..."; bottom_sheet.update(); return
        try: fab_id = int(fab_id_str); cat_id = int(cat_id_str)
        except ValueError: return
        fab_text = next((opt.text for opt in fabricante_dropdown.options if opt.key == fab_id), ""); cat_text = next((opt.text for opt in categoria_dropdown.options if opt.key == cat_id), "")
        fab_prefix = fab_text[:3].upper(); cat_prefix = cat_text[:3].upper(); combo_key = f"{fab_prefix}-{cat_prefix}"
        df_last_sku = execute_query(GET_LAST_SKU_SQL, (fab_id, cat_id))
        next_seq = 1
        if df_last_sku is not None and not df_last_sku.empty:
            last_sku = df_last_sku['sku'][0]
            try: next_seq = int(last_sku.split('-')[-1]) + 1
            except (ValueError, IndexError): next_seq = 1
        new_sku = f"{combo_key}-{next_seq:04d}"; sku_field.value = new_sku; bottom_sheet.update()

    def populate_dropdowns():
        # ...
        df_cat = execute_query(GET_ALL_CATEGORIAS_SQL);
        if df_cat is not None: categoria_dropdown.options = [ft.dropdown.Option(key=row['categoria_id'], text=row['nombre']) for _, row in df_cat.iterrows()]
        df_fab = execute_query(GET_ALL_FABRICANTES_SQL);
        if df_fab is not None: fabricante_dropdown.options = [ft.dropdown.Option(key=row['fabricante_id'], text=row['nombre']) for _, row in df_fab.iterrows()]
        df_ubi = execute_query(GET_ALL_UBICACIONES_SQL);
        if df_ubi is not None: ubicacion_dropdown.options = [ft.dropdown.Option(key=row['ubicacion_id'], text=row['descripcion']) for _, row in df_ubi.iterrows()]

    def close_bottom_sheet(e):
        bottom_sheet.open = False; bottom_sheet.update()

    def save_product(e):
        # ...
        is_edit_mode = editing_product_id.value is not None
        if not all([nombre_field.value, sku_field.value, costo_field.value, precio_field.value, stock_field.value, categoria_dropdown.value, fabricante_dropdown.value, ubicacion_dropdown.value]):
            page.snack_bar = ft.SnackBar(content=ft.Text("Todos los campos son obligatorios."), bgcolor=ft.Colors.ERROR); page.snack_bar.open = True; page.update(); return
        if is_edit_mode:
            params = (nombre_field.value, sku_field.value, float(costo_field.value), float(precio_field.value), int(stock_field.value), int(categoria_dropdown.value), int(fabricante_dropdown.value), int(ubicacion_dropdown.value), int(editing_product_id.value))
            success, msg = execute_mod_query(UPDATE_PRODUCT_SQL, params); result_msg = f"Producto '{nombre_field.value}' actualizado."
        else:
            params = (nombre_field.value, sku_field.value, float(costo_field.value), float(precio_field.value), int(stock_field.value), int(categoria_dropdown.value), int(fabricante_dropdown.value), int(ubicacion_dropdown.value))
            success, msg = execute_mod_query(INSERT_PRODUCT_SQL, params); result_msg = f"Producto '{nombre_field.value}' agregado."
        if success: page.snack_bar = ft.SnackBar(content=ft.Text(result_msg), bgcolor=ft.Colors.GREEN); load_products_data(); close_bottom_sheet(None)
        else: page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al guardar: {msg}"), bgcolor=ft.Colors.ERROR)
        page.snack_bar.open = True; page.update()

    def show_add_form(e):
        editing_product_id.value = None; form_title.value = "Agregar Nuevo Producto"
        nombre_field.value = ""; sku_field.value = ""; costo_field.value = ""; precio_field.value = ""; stock_field.value = ""
        categoria_dropdown.value = None; fabricante_dropdown.value = None; ubicacion_dropdown.value = None
        bottom_sheet.open = True; bottom_sheet.update()

    def show_edit_form(e):
        product_id = e.control.data; df_prod = execute_query(GET_PRODUCT_BY_ID_SQL, (product_id,))
        if df_prod is not None and not df_prod.empty:
            prod = df_prod.iloc[0]
            editing_product_id.value = str(prod['producto_id']); form_title.value = f"Editando Producto ID: {prod['producto_id']}"
            nombre_field.value = prod['nombre']; sku_field.value = prod['sku']; costo_field.value = str(int(prod['costo_unitario'])); precio_field.value = str(int(prod['precio_venta'])); stock_field.value = str(prod['stock'])
            categoria_dropdown.value = str(prod['categoria_id']); fabricante_dropdown.value = str(prod['fabricante_id']); ubicacion_dropdown.value = str(prod['ubicacion_id'])
            bottom_sheet.open = True; bottom_sheet.update()

    bottom_sheet = ft.BottomSheet(
        ft.Container(
            content=ft.Column([
                form_title, ft.ResponsiveRow([nombre_field, sku_field]),
                ft.ResponsiveRow([costo_field, precio_field, stock_field]),
                ft.ResponsiveRow([categoria_dropdown, fabricante_dropdown, ubicacion_dropdown]),
                ft.Row([ft.FilledButton("Guardar", on_click=save_product), ft.TextButton("Cancelar", on_click=close_bottom_sheet)], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            padding=20
        ),
        open=False
    )
    page.overlay.append(bottom_sheet)

    def confirmed_delete(e):
        product_id = e.control.data; success, message = execute_mod_query(DELETE_PRODUCT_SQL, (product_id,))
        if success: page.snack_bar = ft.SnackBar(content=ft.Text(f"Producto ID {product_id} eliminado"), bgcolor=ft.Colors.GREEN); load_products_data()
        else: page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al eliminar: {message}"), bgcolor=ft.Colors.ERROR)
        delete_confirm_card.visible = False; page.snack_bar.open = True; page.update()
    def cancel_delete(e):
        delete_confirm_card.visible = False; page.update()
    delete_confirm_text = ft.Text(); delete_confirm_button = ft.FilledButton("Confirmar Borrado", on_click=confirmed_delete, bgcolor=ft.Colors.RED_400)
    delete_confirm_card = ft.Card(visible=False, color=ft.Colors.ERROR_CONTAINER, content=ft.Container(ft.Row([delete_confirm_text, delete_confirm_button, ft.TextButton("Cancelar", on_click=cancel_delete)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=10))
    def show_delete_confirmation(e):
        product_id = e.control.data; df_prod = execute_query(GET_PRODUCT_BY_ID_SQL, (product_id,))
        prod_name = df_prod['nombre'][0] if df_prod is not None and not df_prod.empty else ""
        delete_confirm_text.value = f"¿Seguro que quieres eliminar '{prod_name}' (ID: {product_id})?"; delete_confirm_button.data = product_id
        delete_confirm_card.visible = True; page.update()

    products_datatable = ft.DataTable(
        heading_row_color=ft.Colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("SKU")),
            ft.DataColumn(ft.Text("Costo")), ft.DataColumn(ft.Text("Precio Venta")), ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Categoría")), ft.DataColumn(ft.Text("Fabricante")), ft.DataColumn(ft.Text("Ubicación")),
            ft.DataColumn(ft.Text("Acciones")),
        ], rows=[], expand=True)

    layout = ft.Column(
        expand=True, spacing=15, controls=[
            ft.Row(controls=[
                    ft.ElevatedButton(text="Agregar Producto", icon=ft.Icons.ADD, on_click=show_add_form),
                    ft.ElevatedButton(text="Refrescar", icon=ft.Icons.REFRESH, on_click=load_products_data),
                    load_data_button,
                    progress_ring,
                ], alignment=ft.MainAxisAlignment.START
            ),
            delete_confirm_card,
            ft.Card(
                expand=True,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([search_field], alignment=ft.MainAxisAlignment.END),
                        ft.Divider(),
                        products_datatable,
                        ft.Row([pagination_text, prev_button, next_button], alignment=ft.MainAxisAlignment.CENTER)
                    ]),
                    padding=20
                )
            )
        ]
    )

    page.add(layout); populate_dropdowns(); load_products_data()

if __name__ == "__main__":
    if check_db_config(): ft.app(target=main)
    else: print("CRITICAL: La configuración de la base de datos es inválida.")
