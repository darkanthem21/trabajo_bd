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
  "nombre_cliente" VARCHAR(255) NOT NULL
);

CREATE TABLE "productos" (
  "producto_id" INTEGER PRIMARY KEY,
  "nombre_articulo" VARCHAR(255) NOT NULL,
  "fabricante_fk" INTEGER NOT NULL,
  "categoria_fk" INTEGER NOT NULL,
  "sku" VARCHAR(100) UNIQUE,
  "costo" NUMERIC(12,2),
  "precio" NUMERIC(12,2) NOT NULL,
  "stock_actual" INTEGER NOT NULL DEFAULT 0,
  "ubicacion_fk" INTEGER
);

CREATE TABLE "hechos_ventas" (
  "venta_id" SERIAL PRIMARY KEY,
  "nro_boleta" INTEGER NOT NULL,
  "producto_fk" INTEGER NOT NULL,
  "fecha" TIMESTAMP NOT NULL,
  "cliente_fk" INTEGER,
  "cantidad" INTEGER NOT NULL,
  "costo_unitario" NUMERIC(12,2) NOT NULL,
  "total_venta" NUMERIC(14,2) NOT NULL
);

CREATE TABLE "hechos_stock" (
  "movimiento_id" SERIAL PRIMARY KEY,
  "producto_fk" INTEGER NOT NULL,
  "fecha" TIMESTAMP NOT NULL,
  "ubicacion_fk" INTEGER,
  "tipo_movimiento" VARCHAR(50) NOT NULL,
  "cantidad" INTEGER NOT NULL
);

ALTER TABLE "productos" ADD FOREIGN KEY ("fabricante_fk") REFERENCES "fabricantes" ("fabricante_id");

ALTER TABLE "productos" ADD FOREIGN KEY ("categoria_fk") REFERENCES "categorias" ("categoria_id");

ALTER TABLE "productos" ADD FOREIGN KEY ("ubicacion_fk") REFERENCES "ubicaciones" ("ubicacion_id");

ALTER TABLE "hechos_ventas" ADD FOREIGN KEY ("producto_fk") REFERENCES "productos" ("producto_id");

ALTER TABLE "hechos_ventas" ADD FOREIGN KEY ("cliente_fk") REFERENCES "cliente" ("cliente_id");

ALTER TABLE "hechos_stock" ADD FOREIGN KEY ("producto_fk") REFERENCES "productos" ("producto_id");

ALTER TABLE "hechos_stock" ADD FOREIGN KEY ("ubicacion_fk") REFERENCES "ubicaciones" ("ubicacion_id");
