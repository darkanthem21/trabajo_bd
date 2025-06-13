# src/queries_relacional.py

# Query para obtener una 'página' de productos con sus nombres de categoría, etc.
GET_PAGINATED_PRODUCTS_SQL = """
SELECT
    p.producto_id, p.nombre, p.sku, p.costo_unitario, p.precio_venta,
    p.stock, c.nombre AS categoria, f.nombre AS fabricante, u.descripcion AS ubicacion
FROM
    "Productos" p
LEFT JOIN "Categorias" c ON p.categoria_id = c.categoria_id
LEFT JOIN "Fabricantes" f ON p.fabricante_id = f.fabricante_id
LEFT JOIN "Ubicaciones" u ON p.ubicacion_id = u.ubicacion_id
ORDER BY
    p.nombre
LIMIT %s OFFSET %s;
"""

# Query para contar el total de productos
COUNT_PRODUCTS_SQL = 'SELECT COUNT(*) as total FROM "Productos";'


# --- QUERIES PARA BÚSQUEDA (ACTUALIZADAS CON UNACCENT) ---

# Query para obtener una 'página' de productos FILTRADOS por nombre o SKU (insensible a acentos)
GET_FILTERED_PAGINATED_PRODUCTS_SQL = """
SELECT
    p.producto_id, p.nombre, p.sku, p.costo_unitario, p.precio_venta,
    p.stock, c.nombre AS categoria, f.nombre AS fabricante, u.descripcion AS ubicacion
FROM
    "Productos" p
LEFT JOIN "Categorias" c ON p.categoria_id = c.categoria_id
LEFT JOIN "Fabricantes" f ON p.fabricante_id = f.fabricante_id
LEFT JOIN "Ubicaciones" u ON p.ubicacion_id = u.ubicacion_id
WHERE
    unaccent(p.nombre) ILIKE unaccent(%s) OR unaccent(p.sku) ILIKE unaccent(%s)
ORDER BY
    p.nombre
LIMIT %s OFFSET %s;
"""

# Query para contar el total de productos FILTRADOS (insensible a acentos)
COUNT_FILTERED_PRODUCTS_SQL = 'SELECT COUNT(*) as total FROM "Productos" WHERE unaccent(nombre) ILIKE unaccent(%s) OR unaccent(sku) ILIKE unaccent(%s);'


# --- RESTO DE QUERIES (SIN CAMBIOS) ---
GET_PRODUCT_BY_ID_SQL = 'SELECT * FROM "Productos" WHERE producto_id = %s;'
UPDATE_PRODUCT_SQL = """
UPDATE "Productos"
SET nombre = %s, sku = %s, costo_unitario = %s, precio_venta = %s, stock = %s, categoria_id = %s, fabricante_id = %s, ubicacion_id = %s
WHERE producto_id = %s;
"""
INSERT_PRODUCT_SQL = """
INSERT INTO "Productos" (nombre, sku, costo_unitario, precio_venta, stock, categoria_id, fabricante_id, ubicacion_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""
DELETE_PRODUCT_SQL = 'DELETE FROM "Productos" WHERE producto_id = %s;'
GET_ALL_CATEGORIAS_SQL = 'SELECT categoria_id, nombre FROM "Categorias" ORDER BY nombre;'
GET_ALL_FABRICANTES_SQL = 'SELECT fabricante_id, nombre FROM "Fabricantes" ORDER BY nombre;'
GET_ALL_UBICACIONES_SQL = 'SELECT ubicacion_id, descripcion FROM "Ubicaciones" ORDER BY descripcion;'
GET_LAST_SKU_SQL = """
SELECT sku FROM "Productos"
WHERE fabricante_id = %s AND categoria_id = %s
ORDER BY sku DESC
LIMIT 1;
"""
