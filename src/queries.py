# Consultas SQL para análisis y ETL

VENTAS_POR_MES_SQL = """
SELECT
    EXTRACT(MONTH FROM fecha)::INTEGER AS mes,
    SUM(total_venta) AS ventas_totales
FROM hechos_ventas
WHERE EXTRACT(YEAR FROM fecha) = %(year)s
GROUP BY mes
ORDER BY mes;
"""

TOP_PRODUCTOS_CANTIDAD_SQL = """
SELECT
    p.nombre_articulo,
    SUM(hv.cantidad) AS cantidad_total_vendida
FROM hechos_ventas hv
JOIN productos p ON hv.producto_fk = p.producto_id
WHERE EXTRACT(YEAR FROM hv.fecha) = %(year)s
GROUP BY p.nombre_articulo
ORDER BY cantidad_total_vendida DESC
LIMIT 5;
"""

VENTAS_POR_CATEGORIA_SQL = """
SELECT
    c.nombre_categoria,
    SUM(hv.total_venta) AS ventas_totales_categoria
FROM hechos_ventas hv
JOIN productos p ON hv.producto_fk = p.producto_id
JOIN categorias c ON p.categoria_fk = c.categoria_id
WHERE EXTRACT(YEAR FROM hv.fecha) = %(year)s
GROUP BY c.nombre_categoria
ORDER BY ventas_totales_categoria DESC;
"""

STOCK_EVOLUCION_SQL = """
SELECT
    p.nombre_articulo,
    DATE(hs.fecha) AS fecha,
    SUM(CASE
        WHEN dm.tipo_movimiento LIKE 'ENTRADA%%' OR dm.tipo_movimiento = 'AJUSTE_INV_POS' THEN hs.cantidad
        ELSE -hs.cantidad
    END) AS variacion_stock
FROM hechos_stock hs
JOIN productos p ON hs.producto_fk = p.producto_id
JOIN dim_movimiento dm ON hs.tipo_movimiento_fk = dm.id
WHERE EXTRACT(YEAR FROM hs.fecha) = %(year)s
GROUP BY p.nombre_articulo, DATE(hs.fecha)
ORDER BY p.nombre_articulo, fecha;
"""

DISTRIBUCION_TIPOS_MOVIMIENTO_SQL = """
SELECT
  dm.tipo_movimiento,
  DATE_TRUNC('month', hs.fecha) AS mes,
  SUM(hs.cantidad) AS total_movimiento
FROM hechos_stock hs
JOIN dim_movimiento dm ON hs.tipo_movimiento_fk = dm.id
WHERE EXTRACT(YEAR FROM hs.fecha) = %(year)s
GROUP BY dm.tipo_movimiento, mes
ORDER BY mes, dm.tipo_movimiento;
"""

MAS_VENDIDO_FECHA_SQL = """
SELECT
    p.nombre_articulo,
    SUM(hv.cantidad) AS total_vendido
FROM hechos_ventas hv
JOIN productos p ON hv.producto_fk = p.producto_id
WHERE hv.fecha BETWEEN %(fecha_inicio)s AND %(fecha_fin)s
GROUP BY p.nombre_articulo
ORDER BY total_vendido DESC
LIMIT 10;
"""

TOP_10_CLIENTES_SQL = """
SELECT
    c.nombre_cliente,
    SUM(hv.total_venta) AS total_ventas
FROM hechos_ventas hv
JOIN cliente c ON hv.cliente_fk = c.cliente_id
GROUP BY c.nombre_cliente
ORDER BY total_ventas DESC
LIMIT 10;
"""

HISTOGRAM_MONTOS_VENTA_SQL = """
SELECT total_venta
FROM hechos_ventas;
"""

STOCK_PROMEDIO_POR_CATEGORIA_SQL = """
SELECT
    c.nombre_categoria,
    AVG(p.stock_actual) AS stock_promedio
FROM productos p
JOIN categorias c ON p.categoria_fk = c.categoria_id
GROUP BY c.nombre_categoria
ORDER BY stock_promedio DESC;
"""

PRODUCTOS_BAJO_STOCK_SQL = """
SELECT
    nombre_articulo,
    stock_actual
FROM productos
WHERE stock_actual < 5
ORDER BY stock_actual ASC;
"""

VENTAS_MES_CATEGORIA_SQL = """
SELECT
    EXTRACT(MONTH FROM hv.fecha)::INTEGER AS mes,
    c.nombre_categoria,
    SUM(hv.total_venta) AS ventas_totales
FROM hechos_ventas hv
JOIN productos p ON hv.producto_fk = p.producto_id
JOIN categorias c ON p.categoria_fk = c.categoria_id
WHERE EXTRACT(YEAR FROM hv.fecha) = %(year)s
GROUP BY mes, c.nombre_categoria
ORDER BY mes, c.nombre_categoria;
"""

PIE_GANANCIA_CATEGORIA_SQL = """
SELECT
    c.nombre_categoria,
    SUM(hv.total_venta - hv.cantidad * COALESCE(hv.costo_unitario, 0)) AS ganancia_total
FROM hechos_ventas hv
JOIN productos p ON hv.producto_fk = p.producto_id
JOIN categorias c ON p.categoria_fk = c.categoria_id
GROUP BY c.nombre_categoria
ORDER BY ganancia_total DESC;
"""
