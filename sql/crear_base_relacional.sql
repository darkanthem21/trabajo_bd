DROP TABLE IF EXISTS "DetallesVenta";
DROP TABLE IF EXISTS "Ventas";
DROP TABLE IF EXISTS "MovimientosInventario";
DROP TABLE IF EXISTS "Productos";
DROP TABLE IF EXISTS "Clientes";
DROP TABLE IF EXISTS "Categorias";
DROP TABLE IF EXISTS "Fabricantes";
DROP TABLE IF EXISTS "Ubicaciones";

-- Tablas de Dimensiones / Catálogos
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
  "categoria_id" INT REFERENCES "Categorias"("categoria_id"),
  "fabricante_id" INT REFERENCES "Fabricantes"("fabricante_id"),
  "ubicacion_id" INT REFERENCES "Ubicaciones"("ubicacion_id")
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
  "tipo" VARCHAR(50) NOT NULL, -- Ej: 'compra_proveedor', 'venta_cliente', 'ajuste_positivo', 'ajuste_negativo'
  "cantidad" INT NOT NULL,
  "producto_id" INT NOT NULL REFERENCES "Productos"("producto_id"),
  "ubicacion_id" INT REFERENCES "Ubicaciones"("ubicacion_id")
);
-- Agregar campo para soft delete en productos
ALTER TABLE "Productos" ADD COLUMN "eliminado" BOOLEAN DEFAULT FALSE;
ALTER TABLE "Productos" ADD COLUMN "fecha_eliminacion" TIMESTAMP NULL;

-- Crear índice para mejorar rendimiento en consultas de productos activos
CREATE INDEX idx_productos_eliminado ON "Productos"("eliminado") WHERE eliminado = FALSE;

\echo "Script crear_base_relacional.sql ejecutado con éxito."
