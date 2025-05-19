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

# Consulta 4: Evolución del stock total por día en un año dado (solo 2 columnas)
STOCK_EVOLUCION_SQL = """
SELECT
    p.nombre_articulo,
    DATE(hs.fecha) AS fecha,
    SUM(CASE
        WHEN dm.tipo_movimiento LIKE 'ENTRADA%%' OR dm.tipo_movimiento = 'AJUSTE_INV_POS' THEN hs.cantidad
        ELSE -hs.cantidad
    END) AS variacion_stock
FROM
    hechos_stock hs
JOIN
    productos p ON hs.producto_fk = p.producto_id
JOIN
    dim_movimiento dm ON hs.tipo_movimiento_fk = dm.id
WHERE
    EXTRACT(YEAR FROM hs.fecha) = %(year)s
GROUP BY
    p.nombre_articulo, DATE(hs.fecha)
ORDER BY
    p.nombre_articulo, fecha;
"""
# Consulta 5 Distribucion de tipos de movimientode stock por año

DISTRIBUCION_TIPOS_MOVIMIENTO_SQL = """SELECT
  dm.tipo_movimiento,
  DATE_TRUNC('month', hs.fecha) AS mes,
  SUM(hs.cantidad) AS total_movimiento
FROM
  hechos_stock hs
JOIN dim_movimiento dm ON hs.tipo_movimiento_fk = dm.id
WHERE
  EXTRACT(YEAR FROM hs.fecha) = %(year)s
GROUP BY
  dm.tipo_movimiento, mes
ORDER BY
  mes, dm.tipo_movimiento;
"""

# Consulta 6 Obtener los productos mas vendidos en rango de fechas
MAS_VENDIDO_FECHA_SQL = """
SELECT
    p.nombre_articulo,
    SUM(hv.cantidad) AS total_vendido
FROM
    hechos_ventas hv
JOIN
    productos p ON hv.producto_fk = p.producto_id
WHERE
    hv.fecha BETWEEN %(fecha_inicio)s AND %(fecha_fin)s  -- Usar parámetros
GROUP BY
    p.nombre_articulo
ORDER BY
    total_vendido DESC
LIMIT 10;
"""

# Consulta 7

VENTAS_POR_CLIENTE_SQL = """
SELECT
    c.nombre_cliente,
    SUM(hv.total_venta) AS total_ventas
FROM
    hechos_ventas hv
JOIN
    cliente c ON hv.cliente_fk = c.cliente_id
WHERE
    EXTRACT(YEAR FROM hv.fecha) = %(year)s  -- Opcional: Filtrar por año
GROUP BY
    c.nombre_cliente
ORDER BY
    total_ventas DESC;
"""
