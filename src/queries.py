# Consultas SQL para análisis y ETL - Modelo Estrella Puro

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
JOIN dim_producto p ON hv.producto_id = p.producto_id
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
JOIN dim_producto p ON hv.producto_id = p.producto_id
JOIN dim_categoria c ON p.categoria_id = c.categoria_id
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
JOIN dim_producto p ON hs.producto_id = p.producto_id
JOIN dim_movimiento dm ON hs.tipo_movimiento_id = dm.id
WHERE EXTRACT(YEAR FROM hs.fecha) = %(year)s
GROUP BY p.nombre_articulo, DATE(hs.fecha)
ORDER BY p.nombre_articulo, fecha LIMIT 10;
"""

DISTRIBUCION_TIPOS_MOVIMIENTO_SQL = """
SELECT
  dm.tipo_movimiento,
  DATE_TRUNC('month', hs.fecha) AS mes,
  ABS(SUM(hs.cantidad)) AS total_movimiento
FROM hechos_stock hs
JOIN dim_movimiento dm ON hs.tipo_movimiento_id = dm.id
WHERE EXTRACT(YEAR FROM hs.fecha) = %(year)s
GROUP BY dm.tipo_movimiento, mes
ORDER BY mes, dm.tipo_movimiento;
"""

MAS_VENDIDO_FECHA_SQL = """
SELECT
    p.nombre_articulo,
    SUM(hv.cantidad) AS total_vendido
FROM hechos_ventas hv
JOIN dim_producto p ON hv.producto_id = p.producto_id
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
JOIN dim_cliente c ON hv.cliente_id = c.cliente_id
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
    AVG(stock) AS stock_promedio
FROM (
    SELECT
        p.categoria_id,
        SUM(hs.cantidad) AS stock
    FROM hechos_stock hs
    JOIN dim_producto p ON hs.producto_id = p.producto_id
    GROUP BY p.categoria_id, p.producto_id
) sub
JOIN dim_categoria c ON sub.categoria_id = c.categoria_id
GROUP BY c.nombre_categoria
ORDER BY stock_promedio DESC;
"""

PRODUCTOS_BAJO_STOCK_SQL = """
SELECT
    p.nombre_articulo,
    SUM(hs.cantidad) AS stock_actual
FROM hechos_stock hs
JOIN dim_producto p ON hs.producto_id = p.producto_id
GROUP BY p.producto_id, p.nombre_articulo
HAVING SUM(hs.cantidad) < 5
ORDER BY stock_actual ASC;
"""

VENTAS_MES_CATEGORIA_SQL = """
SELECT
    EXTRACT(MONTH FROM hv.fecha)::INTEGER AS mes,
    c.nombre_categoria,
    SUM(hv.total_venta) AS ventas_totales
FROM hechos_ventas hv
JOIN dim_producto p ON hv.producto_id = p.producto_id
JOIN dim_categoria c ON p.categoria_id = c.categoria_id
WHERE EXTRACT(YEAR FROM hv.fecha) = %(year)s
GROUP BY mes, c.nombre_categoria
ORDER BY mes, c.nombre_categoria;
"""

PIE_GANANCIA_CATEGORIA_SQL = """
SELECT
    c.nombre_categoria,
    SUM(hv.total_venta - hv.cantidad * COALESCE(hv.costo_unitario, 0)) AS ganancia_total
FROM hechos_ventas hv
JOIN dim_producto p ON hv.producto_id = p.producto_id
JOIN dim_categoria c ON p.categoria_id = c.categoria_id
GROUP BY c.nombre_categoria
ORDER BY ganancia_total DESC;
"""
