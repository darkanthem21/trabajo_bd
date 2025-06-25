-- Crear Base Dimensional Corregida
-- Se optimiza la estructura y se aseguran las foreign keys

DROP TABLE IF EXISTS "hechos_stock" CASCADE;
DROP TABLE IF EXISTS "hechos_ventas" CASCADE;
DROP TABLE IF EXISTS "productos" CASCADE;
DROP TABLE IF EXISTS "cliente" CASCADE;
DROP TABLE IF EXISTS "ubicaciones" CASCADE;
DROP TABLE IF EXISTS "categorias" CASCADE;
DROP TABLE IF EXISTS "fabricantes" CASCADE;
DROP TABLE IF EXISTS "dim_movimiento" CASCADE;

-- Dimensiones
CREATE TABLE "fabricantes" (
  "fabricante_id" SERIAL PRIMARY KEY,
  "nombre_fabricante" VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE "categorias" (
  "categoria_id" SERIAL PRIMARY KEY,
  "nombre_categoria" VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE "ubicaciones" (
  "ubicacion_id" SERIAL PRIMARY KEY,
  "codigo_ubicacion" VARCHAR(50) UNIQUE NOT NULL,
  "descripcion_ubicacion" TEXT
);

CREATE TABLE "cliente" (
  "cliente_id" INTEGER PRIMARY KEY,
  "rut" VARCHAR(15) UNIQUE NOT NULL,
  "nombre_cliente" VARCHAR(255) NOT NULL
);

CREATE TABLE "dim_movimiento" (
  "id" SMALLSERIAL PRIMARY KEY,
  "tipo_movimiento" VARCHAR(20) UNIQUE NOT NULL,
  "descripcion_movimiento" VARCHAR(255)
);

-- Tabla de productos (sin SERIAL para permitir IDs específicos del ETL)
CREATE TABLE "productos" (
  "producto_id" INTEGER PRIMARY KEY,
  "nombre_articulo" VARCHAR(255) NOT NULL,
  "fabricante_fk" INTEGER NOT NULL REFERENCES "fabricantes"("fabricante_id"),
  "categoria_fk" INTEGER NOT NULL REFERENCES "categorias"("categoria_id"),
  "sku" VARCHAR(100) UNIQUE,
  "costo" NUMERIC(12, 2) DEFAULT 0,
  "precio" NUMERIC(12, 2) NOT NULL,
  "stock_actual" INTEGER NOT NULL DEFAULT 0,
  "ubicacion_fk" INTEGER REFERENCES "ubicaciones"("ubicacion_id")
);

-- Tablas de hechos
CREATE TABLE "hechos_ventas" (
  "venta_id" SERIAL PRIMARY KEY,
  "nro_boleta" INTEGER NOT NULL,
  "producto_fk" INTEGER NOT NULL REFERENCES "productos"("producto_id"),
  "fecha" TIMESTAMP NOT NULL,
  "cliente_fk" INTEGER REFERENCES "cliente"("cliente_id"),
  "cantidad" INTEGER NOT NULL,
  "costo_unitario" NUMERIC(12, 2) NOT NULL,
  "total_venta" NUMERIC(14, 2) NOT NULL
);

CREATE TABLE "hechos_stock" (
  "movimiento_id" SERIAL PRIMARY KEY,
  "producto_fk" INTEGER NOT NULL REFERENCES "productos"("producto_id"),
  "fecha" TIMESTAMP NOT NULL,
  "ubicacion_fk" INTEGER REFERENCES "ubicaciones"("ubicacion_id"),
  "tipo_movimiento_fk" SMALLINT NOT NULL REFERENCES "dim_movimiento"("id"),
  "cantidad" INTEGER NOT NULL
);

-- Insertar tipos de movimiento predefinidos
INSERT INTO "dim_movimiento" (tipo_movimiento, descripcion_movimiento)
VALUES
  ('ENTRADA_INI', 'Entrada por Inventario Inicial'),
  ('SALIDA_VTA', 'Salida por Venta'),
  ('ENTRADA_COMPRA', 'Entrada por Compra a Proveedor'),
  ('AJUSTE_INV_POS', 'Ajuste de Inventario Positivo'),
  ('AJUSTE_INV_NEG', 'Ajuste de Inventario Negativo')
ON CONFLICT (tipo_movimiento) DO NOTHING;

-- Índices para performance
CREATE INDEX idx_productos_fabricante_fk ON "productos"("fabricante_fk");
CREATE INDEX idx_productos_categoria_fk ON "productos"("categoria_fk");
CREATE INDEX idx_productos_ubicacion_fk ON "productos"("ubicacion_fk");
CREATE INDEX idx_hechos_ventas_fecha ON "hechos_ventas"("fecha");
CREATE INDEX idx_hechos_ventas_producto_fk ON "hechos_ventas"("producto_fk");
CREATE INDEX idx_hechos_stock_fecha ON "hechos_stock"("fecha");
CREATE INDEX idx_hechos_stock_producto_fk ON "hechos_stock"("producto_fk");
CREATE INDEX idx_hechos_stock_tipo ON "hechos_stock"("tipo_movimiento_fk");

\echo "Script crear_base_v2 (corregido) ejecutado con éxito."
