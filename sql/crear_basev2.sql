DROP TABLE IF EXISTS "hechos_stock";
DROP TABLE IF EXISTS "hechos_ventas";
DROP TABLE IF EXISTS "productos";
DROP TABLE IF EXISTS "cliente";
DROP TABLE IF EXISTS "ubicaciones";
DROP TABLE IF EXISTS "categorias";
DROP TABLE IF EXISTS "fabricantes";
DROP TABLE IF EXISTS "dim_movimiento";

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
  "id" SMALLSERIAL PRIMARY KEY,                  -- Llave primaria es 'id'
  "tipo_movimiento" VARCHAR(20) UNIQUE NOT NULL, -- Columna con código es 'tipo_movimiento'
  "descripcion_movimiento" VARCHAR(255)
);

CREATE TABLE "productos" (
  "producto_id" INTEGER PRIMARY KEY, -- OJO: No es SERIAL
  "nombre_articulo" VARCHAR(255) NOT NULL,
  "fabricante_fk" INTEGER NOT NULL REFERENCES "fabricantes"("fabricante_id"),
  "categoria_fk" INTEGER NOT NULL REFERENCES "categorias"("categoria_id"),
  "sku" VARCHAR(100) UNIQUE,
  "costo" NUMERIC(12, 2),             -- Se mantienen NUMERIC, pero insertaremos enteros
  "precio" NUMERIC(12, 2) NOT NULL,   -- Se mantienen NUMERIC, pero insertaremos enteros
  "stock_actual" INTEGER NOT NULL DEFAULT 0,
  "ubicacion_fk" INTEGER REFERENCES "ubicaciones"("ubicacion_id")
);

CREATE TABLE "hechos_ventas" (
  "venta_id" SERIAL PRIMARY KEY,
  "nro_boleta" INTEGER NOT NULL,
  "producto_fk" INTEGER NOT NULL REFERENCES "productos"("producto_id"),
  "fecha" TIMESTAMP NOT NULL,
  "cliente_fk" INTEGER REFERENCES "cliente"("cliente_id"),
  "cantidad" INTEGER NOT NULL,
  "costo_unitario" NUMERIC(12, 2) NOT NULL, -- Se mantienen NUMERIC
  "total_venta" NUMERIC(14, 2) NOT NULL     -- Se mantienen NUMERIC
);

CREATE TABLE "hechos_stock" (
  "movimiento_id" SERIAL PRIMARY KEY,
  "producto_fk" INTEGER NOT NULL REFERENCES "productos"("producto_id"),
  "fecha" TIMESTAMP NOT NULL,
  "ubicacion_fk" INTEGER REFERENCES "ubicaciones"("ubicacion_id"),
  "tipo_movimiento_fk" SMALLINT NOT NULL REFERENCES "dim_movimiento"("id"), -- FK a 'id' de dim_movimiento
  "cantidad" INTEGER NOT NULL
);

INSERT INTO
  "dim_movimiento" (tipo_movimiento, descripcion_movimiento)
VALUES
  ('ENTRADA_INI', 'Entrada por Inventario Inicial'),
  ('SALIDA_VTA', 'Salida por Venta'),
  ('ENTRADA_COMPRA', 'Entrada por Compra a Proveedor'),
  ('AJUSTE_INV_POS', 'Ajuste de Inventario Positivo'),
  ('AJUSTE_INV_NEG', 'Ajuste de Inventario Negativo')
ON CONFLICT (tipo_movimiento) DO NOTHING; -- Conflicto sobre el código UNIQUE, no sobre el ID serial


\echo "Script crear_base_v2 (con RUT y nombres corregidos) ejecutado."
