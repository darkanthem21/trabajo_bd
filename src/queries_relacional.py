# src/queries_relacional.py - ACTUALIZADO CON SOFT DELETE

# Query para obtener una 'página' de productos ACTIVOS con sus nombres de categoría, etc.
GET_PAGINATED_PRODUCTS_SQL = """
SELECT
    p.producto_id, p.nombre, p.sku, p.costo_unitario, p.precio_venta,
    p.stock, c.nombre AS categoria, f.nombre AS fabricante, u.descripcion AS ubicacion
FROM
    "Productos" p
LEFT JOIN "Categorias" c ON p.categoria_id = c.categoria_id
LEFT JOIN "Fabricantes" f ON p.fabricante_id = f.fabricante_id
LEFT JOIN "Ubicaciones" u ON p.ubicacion_id = u.ubicacion_id
WHERE p.eliminado = FALSE
ORDER BY
    p.nombre
LIMIT %s OFFSET %s;
"""

# Query para contar el total de productos ACTIVOS
COUNT_PRODUCTS_SQL = 'SELECT COUNT(*) as total FROM "Productos" WHERE eliminado = FALSE;'

# Query para obtener una 'página' de productos FILTRADOS por nombre o SKU (insensible a acentos) - SOLO ACTIVOS
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
    p.eliminado = FALSE AND
    (unaccent(p.nombre) ILIKE unaccent(%s) OR unaccent(p.sku) ILIKE unaccent(%s))
ORDER BY
    p.nombre
LIMIT %s OFFSET %s;
"""

# Query para contar el total de productos FILTRADOS ACTIVOS (insensible a acentos)
COUNT_FILTERED_PRODUCTS_SQL = """
SELECT COUNT(*) as total FROM "Productos"
WHERE eliminado = FALSE AND
(unaccent(nombre) ILIKE unaccent(%s) OR unaccent(sku) ILIKE unaccent(%s));
"""

# Query para obtener producto por ID (solo activos)
GET_PRODUCT_BY_ID_SQL = 'SELECT * FROM "Productos" WHERE producto_id = %s AND eliminado = FALSE;'

# Query para actualizar producto
UPDATE_PRODUCT_SQL = """
UPDATE "Productos"
SET nombre = %s, sku = %s, costo_unitario = %s, precio_venta = %s, stock = %s,
    categoria_id = %s, fabricante_id = %s, ubicacion_id = %s
WHERE producto_id = %s AND eliminado = FALSE;
"""

# Query para insertar producto
INSERT_PRODUCT_SQL = """
INSERT INTO "Productos" (nombre, sku, costo_unitario, precio_venta, stock, categoria_id, fabricante_id, ubicacion_id, eliminado)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE);
"""

# Query para SOFT DELETE - marcar como eliminado
SOFT_DELETE_PRODUCT_SQL = """
UPDATE "Productos"
SET eliminado = TRUE, fecha_eliminacion = CURRENT_TIMESTAMP
WHERE producto_id = %s;
"""

# Query para verificar si un producto puede ser eliminado (no está en ventas)
CHECK_PRODUCT_IN_SALES_SQL = """
SELECT COUNT(*) as total FROM "DetallesVenta" dv
JOIN "Productos" p ON dv.producto_id = p.producto_id
WHERE p.producto_id = %s;
"""

# Query para HARD DELETE (solo si no está en ventas)
HARD_DELETE_PRODUCT_SQL = 'DELETE FROM "Productos" WHERE producto_id = %s;'

# Queries para dropdowns (solo activos)
GET_ALL_CATEGORIAS_SQL = 'SELECT categoria_id, nombre FROM "Categorias" ORDER BY nombre;'
GET_ALL_FABRICANTES_SQL = 'SELECT fabricante_id, nombre FROM "Fabricantes" ORDER BY nombre;'
GET_ALL_UBICACIONES_SQL = 'SELECT ubicacion_id, descripcion FROM "Ubicaciones" ORDER BY descripcion;'

# Query para último SKU (solo productos activos)
GET_LAST_SKU_SQL = """
SELECT sku FROM "Productos"
WHERE fabricante_id = %s AND categoria_id = %s AND eliminado = FALSE
ORDER BY sku DESC
LIMIT 1;
"""

# NUEVAS QUERIES PARA GESTIÓN DE CATEGORÍAS
GET_PAGINATED_CATEGORIAS_SQL = """
SELECT categoria_id, nombre
FROM "Categorias"
ORDER BY nombre
LIMIT %s OFFSET %s;
"""

COUNT_CATEGORIAS_SQL = 'SELECT COUNT(*) as total FROM "Categorias";'

GET_FILTERED_PAGINATED_CATEGORIAS_SQL = """
SELECT categoria_id, nombre
FROM "Categorias"
WHERE unaccent(nombre) ILIKE unaccent(%s)
ORDER BY nombre
LIMIT %s OFFSET %s;
"""

COUNT_FILTERED_CATEGORIAS_SQL = """
SELECT COUNT(*) as total FROM "Categorias"
WHERE unaccent(nombre) ILIKE unaccent(%s);
"""

GET_CATEGORIA_BY_ID_SQL = 'SELECT * FROM "Categorias" WHERE categoria_id = %s;'

UPDATE_CATEGORIA_SQL = """
UPDATE "Categorias"
SET nombre = %s
WHERE categoria_id = %s;
"""

INSERT_CATEGORIA_SQL = """
INSERT INTO "Categorias" (nombre)
VALUES (%s);
"""

DELETE_CATEGORIA_SQL = 'DELETE FROM "Categorias" WHERE categoria_id = %s;'

# NUEVAS QUERIES PARA GESTIÓN DE FABRICANTES
GET_PAGINATED_FABRICANTES_SQL = """
SELECT fabricante_id, nombre
FROM "Fabricantes"
ORDER BY nombre
LIMIT %s OFFSET %s;
"""

COUNT_FABRICANTES_SQL = 'SELECT COUNT(*) as total FROM "Fabricantes";'

GET_FILTERED_PAGINATED_FABRICANTES_SQL = """
SELECT fabricante_id, nombre
FROM "Fabricantes"
WHERE unaccent(nombre) ILIKE unaccent(%s)
ORDER BY nombre
LIMIT %s OFFSET %s;
"""

COUNT_FILTERED_FABRICANTES_SQL = """
SELECT COUNT(*) as total FROM "Fabricantes"
WHERE unaccent(nombre) ILIKE unaccent(%s);
"""

GET_FABRICANTE_BY_ID_SQL = 'SELECT * FROM "Fabricantes" WHERE fabricante_id = %s;'

UPDATE_FABRICANTE_SQL = """
UPDATE "Fabricantes"
SET nombre = %s
WHERE fabricante_id = %s;
"""

INSERT_FABRICANTE_SQL = """
INSERT INTO "Fabricantes" (nombre)
VALUES (%s);
"""

DELETE_FABRICANTE_SQL = 'DELETE FROM "Fabricantes" WHERE fabricante_id = %s;'

CHECK_FABRICANTE_IN_USE_SQL = """
SELECT COUNT(*) as total FROM "Productos"
WHERE fabricante_id = %s AND eliminado = FALSE;
"""

# NUEVAS QUERIES PARA GESTIÓN DE UBICACIONES
GET_PAGINATED_UBICACIONES_SQL = """
SELECT ubicacion_id, descripcion
FROM "Ubicaciones"
ORDER BY descripcion
LIMIT %s OFFSET %s;
"""

COUNT_UBICACIONES_SQL = 'SELECT COUNT(*) as total FROM "Ubicaciones";'

GET_FILTERED_PAGINATED_UBICACIONES_SQL = """
SELECT ubicacion_id, descripcion
FROM "Ubicaciones"
WHERE unaccent(descripcion) ILIKE unaccent(%s)
ORDER BY descripcion
LIMIT %s OFFSET %s;
"""

COUNT_FILTERED_UBICACIONES_SQL = """
SELECT COUNT(*) as total FROM "Ubicaciones"
WHERE unaccent(descripcion) ILIKE unaccent(%s);
"""

GET_UBICACION_BY_ID_SQL = 'SELECT * FROM "Ubicaciones" WHERE ubicacion_id = %s;'

UPDATE_UBICACION_SQL = """
UPDATE "Ubicaciones"
SET descripcion = %s
WHERE ubicacion_id = %s;
"""

INSERT_UBICACION_SQL = """
INSERT INTO "Ubicaciones" (descripcion)
VALUES (%s);
"""

DELETE_UBICACION_SQL = 'DELETE FROM "Ubicaciones" WHERE ubicacion_id = %s;'

CHECK_UBICACION_IN_USE_SQL = """
SELECT COUNT(*) as total FROM "Productos"
WHERE ubicacion_id = %s AND eliminado = FALSE;
"""
