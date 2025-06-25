-- Modelo Estrella para Análisis de Lubricentro

DROP TABLE IF EXISTS "hechos_stock" CASCADE;
DROP TABLE IF EXISTS "hechos_ventas" CASCADE;
DROP TABLE IF EXISTS "dim_producto" CASCADE;
DROP TABLE IF EXISTS "dim_fabricante" CASCADE;
DROP TABLE IF EXISTS "dim_categoria" CASCADE;
DROP TABLE IF EXISTS "dim_ubicacion" CASCADE;
DROP TABLE IF EXISTS "dim_cliente" CASCADE;
DROP TABLE IF EXISTS "dim_movimiento" CASCADE;

-- Dimensiones
CREATE TABLE "dim_fabricante" (
  "fabricante_id" SERIAL PRIMARY KEY,
  "nombre_fabricante" VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE "dim_categoria" (
  "categoria_id" SERIAL PRIMARY KEY,
  "nombre_categoria" VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE "dim_ubicacion" (
  "ubicacion_id" SERIAL PRIMARY KEY,
  "codigo_ubicacion" VARCHAR(50) UNIQUE NOT NULL,
  "descripcion_ubicacion" TEXT
);

CREATE TABLE "dim_cliente" (
  "cliente_id" INTEGER PRIMARY KEY,
  "rut" VARCHAR(15) UNIQUE NOT NULL,
  "nombre_cliente" VARCHAR(255) NOT NULL
);

CREATE TABLE "dim_movimiento" (
  "id" SMALLSERIAL PRIMARY KEY,
  "tipo_movimiento" VARCHAR(20) UNIQUE NOT NULL,
  "descripcion_movimiento" VARCHAR(255)
);

CREATE TABLE "dim_producto" (
  "producto_id" INTEGER PRIMARY KEY,
  "nombre_articulo" VARCHAR(255) NOT NULL,
  "sku" VARCHAR(100) UNIQUE,
  "fabricante_id" INTEGER REFERENCES "dim_fabricante"("fabricante_id"),
  "categoria_id" INTEGER REFERENCES "dim_categoria"("categoria_id"),
  "ubicacion_id" INTEGER REFERENCES "dim_ubicacion"("ubicacion_id"),
  "costo" NUMERIC(12, 2) DEFAULT 0,
  "precio" NUMERIC(12, 2) NOT NULL
);

-- Hechos
CREATE TABLE "hechos_ventas" (
  "venta_id" SERIAL PRIMARY KEY,
  "fecha" TIMESTAMP NOT NULL,
  "producto_id" INTEGER NOT NULL REFERENCES "dim_producto"("producto_id"),
  "cliente_id" INTEGER REFERENCES "dim_cliente"("cliente_id"),
  "cantidad" INTEGER NOT NULL,
  "costo_unitario" NUMERIC(12, 2) NOT NULL,
  "total_venta" NUMERIC(14, 2) NOT NULL,
  "nro_boleta" INTEGER NOT NULL
);

CREATE TABLE "hechos_stock" (
  "movimiento_id" SERIAL PRIMARY KEY,
  "fecha" TIMESTAMP NOT NULL,
  "producto_id" INTEGER NOT NULL REFERENCES "dim_producto"("producto_id"),
  "ubicacion_id" INTEGER REFERENCES "dim_ubicacion"("ubicacion_id"),
  "tipo_movimiento_id" SMALLINT NOT NULL REFERENCES "dim_movimiento"("id"),
  "cantidad" INTEGER NOT NULL
);

-- Tipos de movimiento predefinidos
INSERT INTO "dim_movimiento" (tipo_movimiento, descripcion_movimiento)
VALUES
  ('ENTRADA_INI', 'Entrada por Inventario Inicial'),
  ('SALIDA_VTA', 'Salida por Venta'),
  ('ENTRADA_COMPRA', 'Entrada por Compra a Proveedor'),
  ('AJUSTE_INV_POS', 'Ajuste de Inventario Positivo'),
  ('AJUSTE_INV_NEG', 'Ajuste de Inventario Negativo')
ON CONFLICT (tipo_movimiento) DO NOTHING;
