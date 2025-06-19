# src/gui.py - VERSIÓN COMPLETA CON TODAS LAS FUNCIONALIDADES

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
    page.window_width = 1600
    page.window_height = 900
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

    # --- NAVEGACIÓN CON TABS ---
    def handle_tab_change(e):
        if tabs.selected_index == 0:
            load_products_data()
        elif tabs.selected_index == 1:
            load_categorias_data()
        elif tabs.selected_index == 2:
            load_fabricantes_data()
        elif tabs.selected_index == 3:
            load_ubicaciones_data()

    tabs = ft.Tabs(
        selected_index=0,
        on_change=handle_tab_change,
        tabs=[
            ft.Tab(text="Productos", icon=ft.Icons.INVENTORY),
            ft.Tab(text="Categorías", icon=ft.Icons.CATEGORY),
            ft.Tab(text="Fabricantes", icon=ft.Icons.BUSINESS),
            ft.Tab(text="Ubicaciones", icon=ft.Icons.LOCATION_ON),
        ],
        expand=1
    )

    page_size = 15

    # --- CARGA DE DATOS GENERAL ---
    def load_data_worker():
        load_data_button.disabled = True
        progress_ring.visible = True
        page.update()
        try:
            subprocess.run([sys.executable, "src/inserts_relacional.py"], capture_output=True, text=True, check=True)
            page.snack_bar = ft.SnackBar(content=ft.Text("Datos de prueba cargados con éxito."), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            current_offset_products.value = "0"
            current_offset_categorias.value = "0"
            current_offset_fabricantes.value = "0"
            current_offset_ubicaciones.value = "0"
            populate_dropdowns()
            load_products_data()
            load_categorias_data()
            load_fabricantes_data()
            load_ubicaciones_data()
        except subprocess.CalledProcessError as e:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al cargar datos: {e.stderr[:100]}..."), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
        load_data_button.disabled = False
        progress_ring.visible = False
        page.update()

    def run_data_load(e):
        threading.Thread(target=load_data_worker, daemon=True).start()

    load_data_button = ft.ElevatedButton(
        text="Cargar Datos",
        icon=ft.Icons.UPLOAD,
        on_click=run_data_load,
        tooltip="Puebla la BD con datos de prueba."
    )
    progress_ring = ft.ProgressRing(visible=False, width=16, height=16, stroke_width=2)

    # ===== SECCIÓN DE PRODUCTOS =====
    current_offset_products = ft.Text("0", visible=False)

    def handle_search_change_products(e):
        current_offset_products.value = "0"
        load_products_data()

    search_field_products = ft.TextField(
        label="Buscar por Nombre o SKU",
        prefix_icon=ft.Icons.SEARCH,
        on_change=handle_search_change_products,
        width=350,
        dense=True
    )

    def load_products_data(e=None):
        offset = int(current_offset_products.value)
        search_term = search_field_products.value
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

        pagination_text_products.value = f"Página {current_page} de {total_pages}"
        prev_button_products.disabled = (current_page == 1)
        next_button_products.disabled = (current_page >= total_pages)

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
                                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=show_edit_form_products, data=row['producto_id']),
                                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Eliminar", on_click=show_delete_confirmation_products, data=row['producto_id'])
                            ]))
                        ]
                    )
                )
        page.update()

    def go_to_page_products(e):
        offset = int(current_offset_products.value)
        if e.control.tooltip == "Página Siguiente":
            current_offset_products.value = str(offset + page_size)
        elif e.control.tooltip == "Página Anterior":
            current_offset_products.value = str(offset - page_size)
        load_products_data()

    prev_button_products = ft.IconButton(icon=ft.Icons.NAVIGATE_BEFORE, on_click=go_to_page_products, tooltip="Página Anterior")
    next_button_products = ft.IconButton(icon=ft.Icons.NAVIGATE_NEXT, on_click=go_to_page_products, tooltip="Página Siguiente")
    pagination_text_products = ft.Text()

    # Formulario de productos
    editing_product_id = ft.Text(visible=False)
    nombre_field = ft.TextField(label="Nombre del Producto", col=6)
    sku_field = ft.TextField(label="SKU", read_only=True, hint_text="Se genera...", col=6)
    costo_field = ft.TextField(label="Costo Unitario", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"), col=4)
    precio_field = ft.TextField(label="Precio de Venta", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"), col=4)
    stock_field = ft.TextField(label="Stock", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]*"), col=4)
    categoria_dropdown = ft.Dropdown(label="Categoría", on_change=lambda e: generate_and_set_sku(), col=4)
    fabricante_dropdown = ft.Dropdown(label="Fabricante", on_change=lambda e: generate_and_set_sku(), col=4)
    ubicacion_dropdown = ft.Dropdown(label="Ubicación", col=4)
    form_title_products = ft.Text(style=ft.TextThemeStyle.HEADLINE_SMALL)

    def generate_and_set_sku():
        fab_id_str = fabricante_dropdown.value
        cat_id_str = categoria_dropdown.value
        if not fab_id_str or not cat_id_str:
            sku_field.value = "Seleccione..."
            bottom_sheet_products.update()
            return
        try:
            fab_id = int(fab_id_str)
            cat_id = int(cat_id_str)
        except ValueError:
            return

        fab_text = next((opt.text for opt in fabricante_dropdown.options if opt.key == fab_id), "")
        cat_text = next((opt.text for opt in categoria_dropdown.options if opt.key == cat_id), "")
        fab_prefix = fab_text[:3].upper()
        cat_prefix = cat_text[:3].upper()
        combo_key = f"{fab_prefix}-{cat_prefix}"

        df_last_sku = execute_query(GET_LAST_SKU_SQL, (fab_id, cat_id))
        next_seq = 1
        if df_last_sku is not None and not df_last_sku.empty:
            last_sku = df_last_sku['sku'][0]
            try:
                next_seq = int(last_sku.split('-')[-1]) + 1
            except (ValueError, IndexError):
                next_seq = 1

        new_sku = f"{combo_key}-{next_seq:04d}"
        sku_field.value = new_sku
        bottom_sheet_products.update()

    def populate_dropdowns():
        df_cat = execute_query(GET_ALL_CATEGORIAS_SQL)
        if df_cat is not None:
            categoria_dropdown.options = [ft.dropdown.Option(key=row['categoria_id'], text=row['nombre']) for _, row in df_cat.iterrows()]

        df_fab = execute_query(GET_ALL_FABRICANTES_SQL)
        if df_fab is not None:
            fabricante_dropdown.options = [ft.dropdown.Option(key=row['fabricante_id'], text=row['nombre']) for _, row in df_fab.iterrows()]

        df_ubi = execute_query(GET_ALL_UBICACIONES_SQL)
        if df_ubi is not None:
            ubicacion_dropdown.options = [ft.dropdown.Option(key=row['ubicacion_id'], text=row['descripcion']) for _, row in df_ubi.iterrows()]

    def close_bottom_sheet_products(e):
        bottom_sheet_products.open = False
        bottom_sheet_products.update()

    def save_product(e):
        is_edit_mode = editing_product_id.value is not None

        if not all([nombre_field.value, sku_field.value, costo_field.value, precio_field.value, stock_field.value, categoria_dropdown.value, fabricante_dropdown.value, ubicacion_dropdown.value]):
            page.snack_bar = ft.SnackBar(content=ft.Text("Todos los campos son obligatorios."), bgcolor=ft.Colors.ERROR)
            page.snack_bar.open = True
            page.update()
            return

        if is_edit_mode:
            params = (nombre_field.value, sku_field.value, float(costo_field.value), float(precio_field.value), int(stock_field.value), int(categoria_dropdown.value), int(fabricante_dropdown.value), int(ubicacion_dropdown.value), int(editing_product_id.value))
            success, msg = execute_mod_query(UPDATE_PRODUCT_SQL, params)
            result_msg = f"Producto '{nombre_field.value}' actualizado."
        else:
            params = (nombre_field.value, sku_field.value, float(costo_field.value), float(precio_field.value), int(stock_field.value), int(categoria_dropdown.value), int(fabricante_dropdown.value), int(ubicacion_dropdown.value))
            success, msg = execute_mod_query(INSERT_PRODUCT_SQL, params)
            result_msg = f"Producto '{nombre_field.value}' agregado."

        if success:
            page.snack_bar = ft.SnackBar(content=ft.Text(result_msg), bgcolor=ft.Colors.GREEN)
            load_products_data()
            close_bottom_sheet_products(None)
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al guardar: {msg}"), bgcolor=ft.Colors.ERROR)

        page.snack_bar.open = True
        page.update()

    def show_add_form_products(e):
        editing_product_id.value = None
        form_title_products.value = "Agregar Nuevo Producto"
        nombre_field.value = ""
        sku_field.value = ""
        costo_field.value = ""
        precio_field.value = ""
        stock_field.value = ""
        categoria_dropdown.value = None
        fabricante_dropdown.value = None
        ubicacion_dropdown.value = None
        bottom_sheet_products.open = True
        bottom_sheet_products.update()

    def show_edit_form_products(e):
        product_id = e.control.data
        df_prod = execute_query(GET_PRODUCT_BY_ID_SQL, (product_id,))
        if df_prod is not None and not df_prod.empty:
            prod = df_prod.iloc[0]
            editing_product_id.value = str(prod['producto_id'])
            form_title_products.value = f"Editando Producto ID: {prod['producto_id']}"
            nombre_field.value = prod['nombre']
            sku_field.value = prod['sku']
            costo_field.value = str(int(prod['costo_unitario']))
            precio_field.value = str(int(prod['precio_venta']))
            stock_field.value = str(prod['stock'])
            categoria_dropdown.value = str(prod['categoria_id'])
            fabricante_dropdown.value = str(prod['fabricante_id'])
            ubicacion_dropdown.value = str(prod['ubicacion_id'])
            bottom_sheet_products.open = True
            bottom_sheet_products.update()

    bottom_sheet_products = ft.BottomSheet(
        ft.Container(
            content=ft.Column([
                form_title_products,
                ft.ResponsiveRow([nombre_field, sku_field]),
                ft.ResponsiveRow([costo_field, precio_field, stock_field]),
                ft.ResponsiveRow([categoria_dropdown, fabricante_dropdown, ubicacion_dropdown]),
                ft.Row([
                    ft.FilledButton("Guardar", on_click=save_product),
                    ft.TextButton("Cancelar", on_click=close_bottom_sheet_products)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            padding=20
        ),
        open=False
    )
    page.overlay.append(bottom_sheet_products)

    def confirmed_delete_products(e):
        product_id = e.control.data

        success, message = execute_mod_query(SOFT_DELETE_PRODUCT_SQL, (product_id,))
        if success:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Producto ID {product_id} marcado como eliminado"),
                bgcolor=ft.Colors.ORANGE
            )
            load_products_data()
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al eliminar: {message}"),
                bgcolor=ft.Colors.ERROR
            )

        delete_confirm_card_products.visible = False
        page.snack_bar.open = True
        page.update()

    def cancel_delete_products(e):
        delete_confirm_card_products.visible = False
        page.update()

    delete_confirm_text_products = ft.Text()
    delete_confirm_button_products = ft.FilledButton("Confirmar Borrado", on_click=confirmed_delete_products, bgcolor=ft.Colors.RED_400)
    delete_confirm_card_products = ft.Card(
        visible=False,
        color=ft.Colors.ERROR_CONTAINER,
        content=ft.Container(
            ft.Row([
                delete_confirm_text_products,
                delete_confirm_button_products,
                ft.TextButton("Cancelar", on_click=cancel_delete_products)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10
        )
    )

    def show_delete_confirmation_products(e):
        product_id = e.control.data
        df_prod = execute_query(GET_PRODUCT_BY_ID_SQL, (product_id,))
        prod_name = df_prod['nombre'][0] if df_prod is not None and not df_prod.empty else ""

        delete_confirm_text_products.value = f"¿Seguro que quieres eliminar '{prod_name}' (ID: {product_id})?"

        delete_confirm_button_products.data = product_id
        delete_confirm_card_products.visible = True
        page.update()

    products_datatable = ft.DataTable(
        heading_row_color=ft.Colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("SKU")),
            ft.DataColumn(ft.Text("Costo")),
            ft.DataColumn(ft.Text("Precio Venta")),
            ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Categoría")),
            ft.DataColumn(ft.Text("Fabricante")),
            ft.DataColumn(ft.Text("Ubicación")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
        expand=True
    )

    # ===== SECCIÓN DE CATEGORÍAS =====
    current_offset_categorias = ft.Text("0", visible=False)

    def handle_search_change_categorias(e):
        current_offset_categorias.value = "0"
        load_categorias_data()

    search_field_categorias = ft.TextField(
        label="Buscar por Nombre",
        prefix_icon=ft.Icons.SEARCH,
        on_change=handle_search_change_categorias,
        width=350,
        dense=True
    )

    def load_categorias_data(e=None):
        offset = int(current_offset_categorias.value)
        search_term = search_field_categorias.value
        sql_search_term = f"%{search_term}%"

        query_params = ()
        if search_term:
            count_query = COUNT_FILTERED_CATEGORIAS_SQL
            data_query = GET_FILTERED_PAGINATED_CATEGORIAS_SQL
            query_params = (sql_search_term,)
        else:
            count_query = COUNT_CATEGORIAS_SQL
            data_query = GET_PAGINATED_CATEGORIAS_SQL

        df_count = execute_query(count_query, query_params)
        total_records = df_count['total'][0] if df_count is not None and not df_count.empty else 0
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        current_page = (offset // page_size) + 1

        pagination_text_categorias.value = f"Página {current_page} de {total_pages}"
        prev_button_categorias.disabled = (current_page == 1)
        next_button_categorias.disabled = (current_page >= total_pages)

        paginated_params = query_params + (page_size, offset)
        df = execute_query(data_query, paginated_params)

        categorias_datatable.rows.clear()
        if df is not None and not df.empty:
            for index, row in df.iterrows():
                categorias_datatable.rows.append(
                    ft.DataRow(
                        color=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY) if index % 2 == 0 else None,
                        cells=[
                            ft.DataCell(ft.Text(str(row['categoria_id']))),
                            ft.DataCell(ft.Text(row['nombre'], width=400, no_wrap=True, tooltip=row['nombre'])),
                            ft.DataCell(ft.Row([
                                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=show_edit_form_categorias, data=row['categoria_id']),
                                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Eliminar", on_click=show_delete_confirmation_categorias, data=row['categoria_id'])
                            ]))
                        ]
                    )
                )
        page.update()

    def go_to_page_categorias(e):
        offset = int(current_offset_categorias.value)
        if e.control.tooltip == "Página Siguiente":
            current_offset_categorias.value = str(offset + page_size)
        elif e.control.tooltip == "Página Anterior":
            current_offset_categorias.value = str(offset - page_size)
        load_categorias_data()

    prev_button_categorias = ft.IconButton(icon=ft.Icons.NAVIGATE_BEFORE, on_click=go_to_page_categorias, tooltip="Página Anterior")
    next_button_categorias = ft.IconButton(icon=ft.Icons.NAVIGATE_NEXT, on_click=go_to_page_categorias, tooltip="Página Siguiente")
    pagination_text_categorias = ft.Text()

    editing_categoria_id = ft.Text(visible=False)
    nombre_categoria_field = ft.TextField(label="Nombre de la Categoría", col=12)
    form_title_categorias = ft.Text(style=ft.TextThemeStyle.HEADLINE_SMALL)

    def close_bottom_sheet_categorias(e):
        bottom_sheet_categorias.open = False
        bottom_sheet_categorias.update()

    def save_categoria(e):
        is_edit_mode = editing_categoria_id.value is not None

        if not nombre_categoria_field.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("El nombre es obligatorio."), bgcolor=ft.Colors.ERROR)
            page.snack_bar.open = True
            page.update()
            return

        if is_edit_mode:
            params = (nombre_categoria_field.value, int(editing_categoria_id.value))
            success, msg = execute_mod_query(UPDATE_CATEGORIA_SQL, params)
            result_msg = f"Categoría '{nombre_categoria_field.value}' actualizada."
        else:
            params = (nombre_categoria_field.value,)
            success, msg = execute_mod_query(INSERT_CATEGORIA_SQL, params)
            result_msg = f"Categoría '{nombre_categoria_field.value}' agregada."

        if success:
            page.snack_bar = ft.SnackBar(content=ft.Text(result_msg), bgcolor=ft.Colors.GREEN)
            load_categorias_data()
            populate_dropdowns()  # Actualizar dropdowns de productos
            close_bottom_sheet_categorias(None)
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al guardar: {msg}"), bgcolor=ft.Colors.ERROR)

        page.snack_bar.open = True
        page.update()

    def show_add_form_categorias(e):
        editing_categoria_id.value = None
        form_title_categorias.value = "Agregar Nueva Categoría"
        nombre_categoria_field.value = ""
        bottom_sheet_categorias.open = True
        bottom_sheet_categorias.update()

    def show_edit_form_categorias(e):
        categoria_id = e.control.data
        df_cat = execute_query(GET_CATEGORIA_BY_ID_SQL, (categoria_id,))
        if df_cat is not None and not df_cat.empty:
            cat = df_cat.iloc[0]
            editing_categoria_id.value = str(cat['categoria_id'])
            form_title_categorias.value = f"Editando Categoría ID: {cat['categoria_id']}"
            nombre_categoria_field.value = cat['nombre']
            bottom_sheet_categorias.open = True
            bottom_sheet_categorias.update()

    bottom_sheet_categorias = ft.BottomSheet(
        ft.Container(
            content=ft.Column([
                form_title_categorias,
                ft.ResponsiveRow([nombre_categoria_field]),
                ft.Row([
                    ft.FilledButton("Guardar", on_click=save_categoria),
                    ft.TextButton("Cancelar", on_click=close_bottom_sheet_categorias)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            padding=20
        ),
        open=False
    )
    page.overlay.append(bottom_sheet_categorias)

    def confirmed_delete_categorias(e):
        categoria_id = e.control.data

        # Verificar si la categoría está en uso
        df_check = execute_query(CHECK_CATEGORIA_IN_USE_SQL, (categoria_id,))
        if df_check is not None and not df_check.empty and df_check['total'][0] > 0:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"No se puede eliminar: la categoría está en uso por {df_check['total'][0]} productos."),
                bgcolor=ft.Colors.ERROR
            )
        else:
            success, message = execute_mod_query(DELETE_CATEGORIA_SQL, (categoria_id,))
            if success:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Categoría ID {categoria_id} eliminada"),
                    bgcolor=ft.Colors.GREEN
                )
                load_categorias_data()
                populate_dropdowns()  # Actualizar dropdowns de productos
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error al eliminar: {message}"),
                    bgcolor=ft.Colors.ERROR
                )

        delete_confirm_card_categorias.visible = False
        page.snack_bar.open = True
        page.update()

    def cancel_delete_categorias(e):
        delete_confirm_card_categorias.visible = False
        page.update()

    delete_confirm_text_categorias = ft.Text()
    delete_confirm_button_categorias = ft.FilledButton("Confirmar Borrado", on_click=confirmed_delete_categorias, bgcolor=ft.Colors.RED_400)
    delete_confirm_card_categorias = ft.Card(
        visible=False,
        color=ft.Colors.ERROR_CONTAINER,
        content=ft.Container(
            ft.Row([
                delete_confirm_text_categorias,
                delete_confirm_button_categorias,
                ft.TextButton("Cancelar", on_click=cancel_delete_categorias)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10
        )
    )

    def show_delete_confirmation_categorias(e):
        categoria_id = e.control.data
        df_cat = execute_query(GET_CATEGORIA_BY_ID_SQL, (categoria_id,))
        cat_name = df_cat['nombre'][0] if df_cat is not None and not df_cat.empty else ""

        # Verificar si está en uso
        df_check = execute_query(CHECK_CATEGORIA_IN_USE_SQL, (categoria_id,))
        in_use = df_check is not None and not df_check.empty and df_check['total'][0] > 0

        if in_use:
            delete_confirm_text_categorias.value = f"'{cat_name}' está en uso por {df_check['total'][0]} productos. No se puede eliminar."
        else:
            delete_confirm_text_categorias.value = f"¿Seguro que quieres eliminar '{cat_name}' (ID: {categoria_id})?"

        delete_confirm_button_categorias.data = categoria_id
        delete_confirm_card_categorias.visible = True
        page.update()

    categorias_datatable = ft.DataTable(
        heading_row_color=ft.Colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
        expand=True
    )

    # ===== SECCIÓN DE FABRICANTES =====
    current_offset_fabricantes = ft.Text("0", visible=False)

    def handle_search_change_fabricantes(e):
        current_offset_fabricantes.value = "0"
        load_fabricantes_data()

    search_field_fabricantes = ft.TextField(
        label="Buscar por Nombre",
        prefix_icon=ft.Icons.SEARCH,
        on_change=handle_search_change_fabricantes,
        width=350,
        dense=True
    )

    def load_fabricantes_data(e=None):
        offset = int(current_offset_fabricantes.value)
        search_term = search_field_fabricantes.value
        sql_search_term = f"%{search_term}%"

        query_params = ()
        if search_term:
            count_query = COUNT_FILTERED_FABRICANTES_SQL
            data_query = GET_FILTERED_PAGINATED_FABRICANTES_SQL
            query_params = (sql_search_term,)
        else:
            count_query = COUNT_FABRICANTES_SQL
            data_query = GET_PAGINATED_FABRICANTES_SQL

        df_count = execute_query(count_query, query_params)
        total_records = df_count['total'][0] if df_count is not None and not df_count.empty else 0
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        current_page = (offset // page_size) + 1

        pagination_text_fabricantes.value = f"Página {current_page} de {total_pages}"
        prev_button_fabricantes.disabled = (current_page == 1)
        next_button_fabricantes.disabled = (current_page >= total_pages)

        paginated_params = query_params + (page_size, offset)
        df = execute_query(data_query, paginated_params)

        fabricantes_datatable.rows.clear()
        if df is not None and not df.empty:
            for index, row in df.iterrows():
                fabricantes_datatable.rows.append(
                    ft.DataRow(
                        color=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY) if index % 2 == 0 else None,
                        cells=[
                            ft.DataCell(ft.Text(str(row['fabricante_id']))),
                            ft.DataCell(ft.Text(row['nombre'], width=400, no_wrap=True, tooltip=row['nombre'])),
                            ft.DataCell(ft.Row([
                                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=show_edit_form_fabricantes, data=row['fabricante_id']),
                                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Eliminar", on_click=show_delete_confirmation_fabricantes, data=row['fabricante_id'])
                            ]))
                        ]
                    )
                )
        page.update()

    def go_to_page_fabricantes(e):
        offset = int(current_offset_fabricantes.value)
        if e.control.tooltip == "Página Siguiente":
            current_offset_fabricantes.value = str(offset + page_size)
        elif e.control.tooltip == "Página Anterior":
            current_offset_fabricantes.value = str(offset - page_size)
        load_fabricantes_data()

    prev_button_fabricantes = ft.IconButton(icon=ft.Icons.NAVIGATE_BEFORE, on_click=go_to_page_fabricantes, tooltip="Página Anterior")
    next_button_fabricantes = ft.IconButton(icon=ft.Icons.NAVIGATE_NEXT, on_click=go_to_page_fabricantes, tooltip="Página Siguiente")
    pagination_text_fabricantes = ft.Text()

    # Formulario de fabricantes
    editing_fabricante_id = ft.Text(visible=False)
    nombre_fabricante_field = ft.TextField(label="Nombre del Fabricante", col=12)
    form_title_fabricantes = ft.Text(style=ft.TextThemeStyle.HEADLINE_SMALL)

    def close_bottom_sheet_fabricantes(e):
        bottom_sheet_fabricantes.open = False
        bottom_sheet_fabricantes.update()

    def save_fabricante(e):
        is_edit_mode = editing_fabricante_id.value is not None

        if not nombre_fabricante_field.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("El nombre es obligatorio."), bgcolor=ft.Colors.ERROR)
            page.snack_bar.open = True
            page.update()
            return

        if is_edit_mode:
            params = (nombre_fabricante_field.value, int(editing_fabricante_id.value))
            success, msg = execute_mod_query(UPDATE_FABRICANTE_SQL, params)
            result_msg = f"Fabricante '{nombre_fabricante_field.value}' actualizado."
        else:
            params = (nombre_fabricante_field.value,)
            success, msg = execute_mod_query(INSERT_FABRICANTE_SQL, params)
            result_msg = f"Fabricante '{nombre_fabricante_field.value}' agregado."

        if success:
            page.snack_bar = ft.SnackBar(content=ft.Text(result_msg), bgcolor=ft.Colors.GREEN)
            load_fabricantes_data()
            populate_dropdowns()  # Actualizar dropdowns de productos
            close_bottom_sheet_fabricantes(None)
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al guardar: {msg}"), bgcolor=ft.Colors.ERROR)

        page.snack_bar.open = True
        page.update()

    def show_add_form_fabricantes(e):
        editing_fabricante_id.value = None
        form_title_fabricantes.value = "Agregar Nuevo Fabricante"
        nombre_fabricante_field.value = ""
        bottom_sheet_fabricantes.open = True
        bottom_sheet_fabricantes.update()

    def show_edit_form_fabricantes(e):
        fabricante_id = e.control.data
        df_fab = execute_query(GET_FABRICANTE_BY_ID_SQL, (fabricante_id,))
        if df_fab is not None and not df_fab.empty:
            fab = df_fab.iloc[0]
            editing_fabricante_id.value = str(fab['fabricante_id'])
            form_title_fabricantes.value = f"Editando Fabricante ID: {fab['fabricante_id']}"
            nombre_fabricante_field.value = fab['nombre']
            bottom_sheet_fabricantes.open = True
            bottom_sheet_fabricantes.update()

    bottom_sheet_fabricantes = ft.BottomSheet(
        ft.Container(
            content=ft.Column([
                form_title_fabricantes,
                ft.ResponsiveRow([nombre_fabricante_field]),
                ft.Row([
                    ft.FilledButton("Guardar", on_click=save_fabricante),
                    ft.TextButton("Cancelar", on_click=close_bottom_sheet_fabricantes)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            padding=20
        ),
        open=False
    )
    page.overlay.append(bottom_sheet_fabricantes)

    def confirmed_delete_fabricantes(e):
        fabricante_id = e.control.data

        # Verificar si el fabricante está en uso
        df_check = execute_query(CHECK_FABRICANTE_IN_USE_SQL, (fabricante_id,))
        if df_check is not None and not df_check.empty and df_check['total'][0] > 0:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"No se puede eliminar: el fabricante está en uso por {df_check['total'][0]} productos."),
                bgcolor=ft.Colors.ERROR
            )
        else:
            success, message = execute_mod_query(DELETE_FABRICANTE_SQL, (fabricante_id,))
            if success:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Fabricante ID {fabricante_id} eliminado"),
                    bgcolor=ft.Colors.GREEN
                )
                load_fabricantes_data()
                populate_dropdowns()  # Actualizar dropdowns de productos
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error al eliminar: {message}"),
                    bgcolor=ft.Colors.ERROR
                )

        delete_confirm_card_fabricantes.visible = False
        page.snack_bar.open = True
        page.update()

    def cancel_delete_fabricantes(e):
        delete_confirm_card_fabricantes.visible = False
        page.update()

    delete_confirm_text_fabricantes = ft.Text()
    delete_confirm_button_fabricantes = ft.FilledButton("Confirmar Borrado", on_click=confirmed_delete_fabricantes, bgcolor=ft.Colors.RED_400)
    delete_confirm_card_fabricantes = ft.Card(
        visible=False,
        color=ft.Colors.ERROR_CONTAINER,
        content=ft.Container(
            ft.Row([
                delete_confirm_text_fabricantes,
                delete_confirm_button_fabricantes,
                ft.TextButton("Cancelar", on_click=cancel_delete_fabricantes)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10
        )
    )

    def show_delete_confirmation_fabricantes(e):
        fabricante_id = e.control.data
        df_fab = execute_query(GET_FABRICANTE_BY_ID_SQL, (fabricante_id,))
        fab_name = df_fab['nombre'][0] if df_fab is not None and not df_fab.empty else ""

        # Verificar si está en uso
        df_check = execute_query(CHECK_FABRICANTE_IN_USE_SQL, (fabricante_id,))
        in_use = df_check is not None and not df_check.empty and df_check['total'][0] > 0

        if in_use:
            delete_confirm_text_fabricantes.value = f"'{fab_name}' está en uso por {df_check['total'][0]} productos. No se puede eliminar."
        else:
            delete_confirm_text_fabricantes.value = f"¿Seguro que quieres eliminar '{fab_name}' (ID: {fabricante_id})?"

        delete_confirm_button_fabricantes.data = fabricante_id
        delete_confirm_card_fabricantes.visible = True
        page.update()

    fabricantes_datatable = ft.DataTable(
        heading_row_color=ft.Colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
        expand=True
    )

    # ===== SECCIÓN DE UBICACIONES =====
    current_offset_ubicaciones = ft.Text("0", visible=False)

    def handle_search_change_ubicaciones(e):
        current_offset_ubicaciones.value = "0"
        load_ubicaciones_data()

    search_field_ubicaciones = ft.TextField(
        label="Buscar por Descripción",
        prefix_icon=ft.Icons.SEARCH,
        on_change=handle_search_change_ubicaciones,
        width=350,
        dense=True
    )

    def load_ubicaciones_data(e=None):
        offset = int(current_offset_ubicaciones.value)
        search_term = search_field_ubicaciones.value
        sql_search_term = f"%{search_term}%"

        query_params = ()
        if search_term:
            count_query = COUNT_FILTERED_UBICACIONES_SQL
            data_query = GET_FILTERED_PAGINATED_UBICACIONES_SQL
            query_params = (sql_search_term,)
        else:
            count_query = COUNT_UBICACIONES_SQL
            data_query = GET_PAGINATED_UBICACIONES_SQL

        df_count = execute_query(count_query, query_params)
        total_records = df_count['total'][0] if df_count is not None and not df_count.empty else 0
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        current_page = (offset // page_size) + 1

        pagination_text_ubicaciones.value = f"Página {current_page} de {total_pages}"
        prev_button_ubicaciones.disabled = (current_page == 1)
        next_button_ubicaciones.disabled = (current_page >= total_pages)

        paginated_params = query_params + (page_size, offset)
        df = execute_query(data_query, paginated_params)

        ubicaciones_datatable.rows.clear()
        if df is not None and not df.empty:
            for index, row in df.iterrows():
                ubicaciones_datatable.rows.append(
                    ft.DataRow(
                        color=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY) if index % 2 == 0 else None,
                        cells=[
                            ft.DataCell(ft.Text(str(row['ubicacion_id']))),
                            ft.DataCell(ft.Text(row['descripcion'], width=400, no_wrap=True, tooltip=row['descripcion'])),
                            ft.DataCell(ft.Row([
                                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=show_edit_form_ubicaciones, data=row['ubicacion_id']),
                                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Eliminar", on_click=show_delete_confirmation_ubicaciones, data=row['ubicacion_id'])
                            ]))
                        ]
                    )
                )
        page.update()

    def go_to_page_ubicaciones(e):
        offset = int(current_offset_ubicaciones.value)
        if e.control.tooltip == "Página Siguiente":
            current_offset_ubicaciones.value = str(offset + page_size)
        elif e.control.tooltip == "Página Anterior":
            current_offset_ubicaciones.value = str(offset - page_size)
        load_ubicaciones_data()

    prev_button_ubicaciones = ft.IconButton(icon=ft.Icons.NAVIGATE_BEFORE, on_click=go_to_page_ubicaciones, tooltip="Página Anterior")
    next_button_ubicaciones = ft.IconButton(icon=ft.Icons.NAVIGATE_NEXT, on_click=go_to_page_ubicaciones, tooltip="Página Siguiente")
    pagination_text_ubicaciones = ft.Text()

    # Formulario de ubicaciones
    editing_ubicacion_id = ft.Text(visible=False)
    descripcion_ubicacion_field = ft.TextField(label="Descripción de la Ubicación", col=12)
    form_title_ubicaciones = ft.Text(style=ft.TextThemeStyle.HEADLINE_SMALL)

    def close_bottom_sheet_ubicaciones(e):
        bottom_sheet_ubicaciones.open = False
        bottom_sheet_ubicaciones.update()

    def save_ubicacion(e):
        is_edit_mode = editing_ubicacion_id.value is not None

        if not descripcion_ubicacion_field.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("La descripción es obligatoria."), bgcolor=ft.Colors.ERROR)
            page.snack_bar.open = True
            page.update()
            return

        if is_edit_mode:
            params = (descripcion_ubicacion_field.value, int(editing_ubicacion_id.value))
            success, msg = execute_mod_query(UPDATE_UBICACION_SQL, params)
            result_msg = f"Ubicación '{descripcion_ubicacion_field.value}' actualizada."
        else:
            params = (descripcion_ubicacion_field.value,)
            success, msg = execute_mod_query(INSERT_UBICACION_SQL, params)
            result_msg = f"Ubicación '{descripcion_ubicacion_field.value}' agregada."

        if success:
            page.snack_bar = ft.SnackBar(content=ft.Text(result_msg), bgcolor=ft.Colors.GREEN)
            load_ubicaciones_data()
            populate_dropdowns()  # Actualizar dropdowns de productos
            close_bottom_sheet_ubicaciones(None)
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al guardar: {msg}"), bgcolor=ft.Colors.ERROR)

        page.snack_bar.open = True
        page.update()

    def show_add_form_ubicaciones(e):
        editing_ubicacion_id.value = None
        form_title_ubicaciones.value = "Agregar Nueva Ubicación"
        descripcion_ubicacion_field.value = ""
        bottom_sheet_ubicaciones.open = True
        bottom_sheet_ubicaciones.update()

    def show_edit_form_ubicaciones(e):
        ubicacion_id = e.control.data
        df_ubi = execute_query(GET_UBICACION_BY_ID_SQL, (ubicacion_id,))
        if df_ubi is not None and not df_ubi.empty:
            ubi = df_ubi.iloc[0]
            editing_ubicacion_id.value = str(ubi['ubicacion_id'])
            form_title_ubicaciones.value = f"Editando Ubicación ID: {ubi['ubicacion_id']}"
            descripcion_ubicacion_field.value = ubi['descripcion']
            bottom_sheet_ubicaciones.open = True
            bottom_sheet_ubicaciones.update()

    bottom_sheet_ubicaciones = ft.BottomSheet(
        ft.Container(
            content=ft.Column([
                form_title_ubicaciones,
                ft.ResponsiveRow([descripcion_ubicacion_field]),
                ft.Row([
                    ft.FilledButton("Guardar", on_click=save_ubicacion),
                    ft.TextButton("Cancelar", on_click=close_bottom_sheet_ubicaciones)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            padding=20
        ),
        open=False
    )
    page.overlay.append(bottom_sheet_ubicaciones)

    def confirmed_delete_ubicaciones(e):
        ubicacion_id = e.control.data

        # Verificar si la ubicación está en uso
        df_check = execute_query(CHECK_UBICACION_IN_USE_SQL, (ubicacion_id,))
        if df_check is not None and not df_check.empty and df_check['total'][0] > 0:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"No se puede eliminar: la ubicación está en uso por {df_check['total'][0]} productos."),
                bgcolor=ft.Colors.ERROR
            )
        else:
            success, message = execute_mod_query(DELETE_UBICACION_SQL, (ubicacion_id,))
            if success:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Ubicación ID {ubicacion_id} eliminada"),
                    bgcolor=ft.Colors.GREEN
                )
                load_ubicaciones_data()
                populate_dropdowns()  # Actualizar dropdowns de productos
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error al eliminar: {message}"),
                    bgcolor=ft.Colors.ERROR
                )

        delete_confirm_card_ubicaciones.visible = False
        page.snack_bar.open = True
        page.update()

    def cancel_delete_ubicaciones(e):
        delete_confirm_card_ubicaciones.visible = False
        page.update()

    delete_confirm_text_ubicaciones = ft.Text()
    delete_confirm_button_ubicaciones = ft.FilledButton("Confirmar Borrado", on_click=confirmed_delete_ubicaciones, bgcolor=ft.Colors.RED_400)
    delete_confirm_card_ubicaciones = ft.Card(
        visible=False,
        color=ft.Colors.ERROR_CONTAINER,
        content=ft.Container(
            ft.Row([
                delete_confirm_text_ubicaciones,
                delete_confirm_button_ubicaciones,
                ft.TextButton("Cancelar", on_click=cancel_delete_ubicaciones)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10
        )
    )

    def show_delete_confirmation_ubicaciones(e):
        ubicacion_id = e.control.data
        df_ubi = execute_query(GET_UBICACION_BY_ID_SQL, (ubicacion_id,))
        ubi_name = df_ubi['descripcion'][0] if df_ubi is not None and not df_ubi.empty else ""

        # Verificar si está en uso
        df_check = execute_query(CHECK_UBICACION_IN_USE_SQL, (ubicacion_id,))
        in_use = df_check is not None and not df_check.empty and df_check['total'][0] > 0

        if in_use:
            delete_confirm_text_ubicaciones.value = f"'{ubi_name}' está en uso por {df_check['total'][0]} productos. No se puede eliminar."
        else:
            delete_confirm_text_ubicaciones.value = f"¿Seguro que quieres eliminar '{ubi_name}' (ID: {ubicacion_id})?"

        delete_confirm_button_ubicaciones.data = ubicacion_id
        delete_confirm_card_ubicaciones.visible = True
        page.update()

    ubicaciones_datatable = ft.DataTable(
        heading_row_color=ft.Colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
        expand=True
    )

    # --- LAYOUT PRINCIPAL ---
    products_tab_content = ft.Column(
        expand=True,
        spacing=15,
        controls=[
            ft.Row(controls=[
                ft.ElevatedButton(text="Agregar Producto", icon=ft.Icons.ADD, on_click=show_add_form_products),
                ft.ElevatedButton(text="Refrescar", icon=ft.Icons.REFRESH, on_click=load_products_data),
                load_data_button,
                progress_ring,
            ], alignment=ft.MainAxisAlignment.START),
            delete_confirm_card_products,
            ft.Card(
                expand=True,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([search_field_products], alignment=ft.MainAxisAlignment.END),
                        ft.Divider(),
                        products_datatable,
                        ft.Row([pagination_text_products, prev_button_products, next_button_products], alignment=ft.MainAxisAlignment.CENTER)
                    ]),
                    padding=20
                )
            )
        ]
    )

    categorias_tab_content = ft.Column(
        expand=True,
        spacing=15,
        controls=[
            ft.Row(controls=[
                ft.ElevatedButton(text="Agregar Categoría", icon=ft.Icons.ADD, on_click=show_add_form_categorias),
                ft.ElevatedButton(text="Refrescar", icon=ft.Icons.REFRESH, on_click=load_categorias_data),
            ], alignment=ft.MainAxisAlignment.START),
            delete_confirm_card_categorias,
            ft.Card(
                expand=True,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([search_field_categorias], alignment=ft.MainAxisAlignment.END),
                        ft.Divider(),
                        categorias_datatable,
                        ft.Row([pagination_text_categorias, prev_button_categorias, next_button_categorias], alignment=ft.MainAxisAlignment.CENTER)
                    ]),
                    padding=20
                )
            )
        ]
    )

    fabricantes_tab_content = ft.Column(
        expand=True,
        spacing=15,
        controls=[
            ft.Row(controls=[
                ft.ElevatedButton(text="Agregar Fabricante", icon=ft.Icons.ADD, on_click=show_add_form_fabricantes),
                ft.ElevatedButton(text="Refrescar", icon=ft.Icons.REFRESH, on_click=load_fabricantes_data),
            ], alignment=ft.MainAxisAlignment.START),
            delete_confirm_card_fabricantes,
            ft.Card(
                expand=True,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([search_field_fabricantes], alignment=ft.MainAxisAlignment.END),
                        ft.Divider(),
                        fabricantes_datatable,
                        ft.Row([pagination_text_fabricantes, prev_button_fabricantes, next_button_fabricantes], alignment=ft.MainAxisAlignment.CENTER)
                    ]),
                    padding=20
                )
            )
        ]
    )

    ubicaciones_tab_content = ft.Column(
        expand=True,
        spacing=15,
        controls=[
            ft.Row(controls=[
                ft.ElevatedButton(text="Agregar Ubicación", icon=ft.Icons.ADD, on_click=show_add_form_ubicaciones),
                ft.ElevatedButton(text="Refrescar", icon=ft.Icons.REFRESH, on_click=load_ubicaciones_data),
            ], alignment=ft.MainAxisAlignment.START),
            delete_confirm_card_ubicaciones,
            ft.Card(
                expand=True,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([search_field_ubicaciones], alignment=ft.MainAxisAlignment.END),
                        ft.Divider(),
                        ubicaciones_datatable,
                        ft.Row([pagination_text_ubicaciones, prev_button_ubicaciones, next_button_ubicaciones], alignment=ft.MainAxisAlignment.CENTER)
                    ]),
                    padding=20
                )
            )
        ]
    )

    # Configurar contenido de las tabs
    tabs.tabs[0].content = products_tab_content
    tabs.tabs[1].content = categorias_tab_content
    tabs.tabs[2].content = fabricantes_tab_content
    tabs.tabs[3].content = ubicaciones_tab_content

    page.add(tabs)
    populate_dropdowns()
    load_products_data()

if __name__ == "__main__":
    if check_db_config():
        ft.app(target=main)
    else:
        print("CRITICAL: La configuración de la base de datos es inválida.")
