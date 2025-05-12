# Consulta 1: Ventas totales por mes para un año dado
VENTAS_POR_MES_SQL = """
SELECT
    EXTRACT(MONTH FROM fecha)::INTEGER AS mes,
    SUM(total_venta) AS ventas_totales -- total_venta ya está en CLP (entero)
FROM
    hechos_ventas
WHERE
    EXTRACT(YEAR FROM fecha) = %(year)s -- Parámetro para el año
GROUP BY
    mes
ORDER BY
    mes;
"""

# Consulta 2: Top 5 productos más vendidos (por cantidad) en un año dado
TOP_PRODUCTOS_CANTIDAD_SQL = """
SELECT
    p.nombre_articulo,
    SUM(hv.cantidad) AS cantidad_total_vendida
FROM
    hechos_ventas hv
JOIN
    productos p ON hv.producto_fk = p.producto_id
WHERE
    EXTRACT(YEAR FROM hv.fecha) = %(year)s -- Parámetro para el año
GROUP BY
    p.nombre_articulo
ORDER BY
    cantidad_total_vendida DESC
LIMIT 5;
"""

# Consulta 3: Ventas totales por categoría de producto en un año dado
VENTAS_POR_CATEGORIA_SQL = """
SELECT
    c.nombre_categoria,
    SUM(hv.total_venta) AS ventas_totales_categoria -- total_venta ya está en CLP (entero)
FROM
    hechos_ventas hv
JOIN
    productos p ON hv.producto_fk = p.producto_id
JOIN
    categorias c ON p.categoria_fk = c.categoria_id
WHERE
    EXTRACT(YEAR FROM hv.fecha) = %(year)s -- Parámetro para el año
GROUP BY
    c.nombre_categoria
ORDER BY
    ventas_totales_categoria DESC;
"""
