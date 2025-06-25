-- Crear Base Relacional Corregida
-- Se mantiene la estructura original pero se asegura compatibilidad con ETL

DROP TABLE IF EXISTS "DetallesVenta" CASCADE;
DROP TABLE IF EXISTS "Ventas" CASCADE;
DROP TABLE IF EXISTS "MovimientosInventario" CASCADE;
DROP TABLE IF EXISTS "Productos" CASCADE;
DROP TABLE IF EXISTS "Clientes" CASCADE;
DROP TABLE IF EXISTS "Categorias" CASCADE;
DROP TABLE IF EXISTS "Fabricantes" CASCADE;
DROP TABLE IF EXISTS "Ubicaciones" CASCADE;

-- Crear extensión para búsquedas sin acentos
CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TABLE "Categorias" (
  "categoria_id" SERIAL PRIMARY KEY,
  "nombre" VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE "Fabricantes" (
  "fabricante_id" SERIAL PRIMARY KEY,
  "nombre" VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE "Ubicaciones" (
  "ubicacion_id" SERIAL PRIMARY KEY,
  "descripcion" VARCHAR(255) NOT NULL
);

CREATE TABLE "Clientes" (
  "rut" VARCHAR(15) PRIMARY KEY,
  "nombre_completo" VARCHAR(255) NOT NULL
);

-- Tabla Principal de Productos
CREATE TABLE "Productos" (
  "producto_id" SERIAL PRIMARY KEY,
  "nombre" VARCHAR(255) NOT NULL,
  "sku" VARCHAR(100) UNIQUE,
  "costo_unitario" DECIMAL(12, 2) DEFAULT 0.00,
  "precio_venta" DECIMAL(12, 2) NOT NULL,
  "stock" INT NOT NULL DEFAULT 0,
  "categoria_id" INT NOT NULL REFERENCES "Categorias"("categoria_id"),
  "fabricante_id" INT NOT NULL REFERENCES "Fabricantes"("fabricante_id"),
  "ubicacion_id" INT REFERENCES "Ubicaciones"("ubicacion_id"),
  "eliminado" BOOLEAN DEFAULT FALSE,
  "fecha_eliminacion" TIMESTAMP NULL
);

-- Tablas Transaccionales
CREATE TABLE "Ventas" (
  "venta_id" SERIAL PRIMARY KEY,
  "boleta_numero" VARCHAR(50),
  "fecha" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "cliente_rut" VARCHAR(15) REFERENCES "Clientes"("rut")
);

CREATE TABLE "DetallesVenta" (
  "detalle_id" SERIAL PRIMARY KEY,
  "venta_id" INT NOT NULL REFERENCES "Ventas"("venta_id") ON DELETE CASCADE,
  "producto_id" INT NOT NULL REFERENCES "Productos"("producto_id"),
  "cantidad" INT NOT NULL,
  "precio_unitario" DECIMAL(12, 2) NOT NULL,
  "subtotal" DECIMAL(14, 2) NOT NULL
);

CREATE TABLE "MovimientosInventario" (
  "movimiento_id" SERIAL PRIMARY KEY,
  "fecha_movimiento" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "tipo" VARCHAR(50) NOT NULL, -- 'compra_inicial', 'venta_cliente', 'compra_proveedor', 'ajuste_positivo', 'ajuste_negativo'
  "cantidad" INT NOT NULL,
  "producto_id" INT NOT NULL REFERENCES "Productos"("producto_id"),
  "ubicacion_id" INT REFERENCES "Ubicaciones"("ubicacion_id")
);

CREATE INDEX idx_productos_eliminado ON "Productos"("eliminado") WHERE eliminado = FALSE;
CREATE INDEX idx_productos_categoria ON "Productos"("categoria_id");
CREATE INDEX idx_productos_fabricante ON "Productos"("fabricante_id");
CREATE INDEX idx_ventas_fecha ON "Ventas"("fecha");
CREATE INDEX idx_movimientos_fecha ON "MovimientosInventario"("fecha_movimiento");
CREATE INDEX idx_movimientos_tipo ON "MovimientosInventario"("tipo");

\echo "Script crear_base_relacional.sql ejecutado con éxito."
