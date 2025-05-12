DROP TABLE IF EXISTS "hechos_stock";

DROP TABLE IF EXISTS "hechos_ventas";

DROP TABLE IF EXISTS "productos";

DROP TABLE IF EXISTS "cliente";

DROP TABLE IF EXISTS "ubicaciones";

DROP TABLE IF EXISTS "categorias";

DROP TABLE IF EXISTS "fabricantes";

DROP TABLE IF EXISTS "dim_tipo_movimiento";

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
    "cliente_id" INTEGER PRIMARY KEY, -- OJO: No es SERIAL
    "nombre_cliente" VARCHAR(255) NOT NULL
);

CREATE TABLE "dim_movimiento" (
    "id" SMALLSERIAL PRIMARY KEY, -- Puedes usar SMALLSERIAL si sabes que serán muy pocos tipos
    "tipo_movimiento" VARCHAR(20) UNIQUE NOT NULL, -- ej: 'ENTRADA_INI', 'SALIDA_VTA'
    "descripcion_movimiento" VARCHAR(255) -- ej: 'Entrada por Inventario Inicial', 'Salida por Venta'
);

-- Creación Tabla Productos (depende de fabricantes, categorias, ubicaciones)
CREATE TABLE "productos" (
    "producto_id" INTEGER PRIMARY KEY, -- OJO: No es SERIAL
    "nombre_articulo" VARCHAR(255) NOT NULL,
    "fabricante_fk" INTEGER NOT NULL REFERENCES "fabricantes" ("fabricante_id"), -- FK directa
    "categoria_fk" INTEGER NOT NULL REFERENCES "categorias" ("categoria_id"), -- FK directa
    "sku" VARCHAR(100) UNIQUE,
    "costo" NUMERIC(12, 2),
    "precio" NUMERIC(12, 2) NOT NULL,
    "stock_actual" INTEGER NOT NULL DEFAULT 0,
    "ubicacion_fk" INTEGER REFERENCES "ubicaciones" ("ubicacion_id") -- FK directa
);

-- Creación Tablas de Hechos
CREATE TABLE "hechos_ventas" (
    "venta_id" SERIAL PRIMARY KEY,
    "nro_boleta" INTEGER NOT NULL,
    "producto_fk" INTEGER NOT NULL REFERENCES "productos" ("producto_id"), -- FK directa
    "fecha" TIMESTAMP NOT NULL,
    "cliente_fk" INTEGER REFERENCES "cliente" ("cliente_id"), -- FK directa
    "cantidad" INTEGER NOT NULL,
    "costo_unitario" NUMERIC(12, 2) NOT NULL,
    "total_venta" NUMERIC(14, 2) NOT NULL
);

CREATE TABLE "hechos_stock" (
    "movimiento_id" SERIAL PRIMARY KEY,
    "producto_fk" INTEGER NOT NULL REFERENCES "productos" ("producto_id"), -- FK directa
    "fecha" TIMESTAMP NOT NULL,
    "ubicacion_fk" INTEGER REFERENCES "ubicaciones" ("ubicacion_id"), -- FK directa
    "tipo_movimiento_fk" INTEGER NOT NULL REFERENCES "dim_movimiento" ("id"), -- Nueva FK
    "cantidad" INTEGER NOT NULL
);

INSERT INTO
    "dim_movimiento" (tipo_movimiento, descripcion_movimiento)
VALUES
    ('ENTRADA_INI', 'Entrada por Inventario Inicial'),
    ('SALIDA_VTA', 'Salida por Venta'),
    (
        'ENTRADA_COMPRA',
        'Entrada por Compra a Proveedor'
    ),
    ('AJUSTE_INV_POS', 'Ajuste de Inventario Positivo'),
    ('AJUSTE_INV_NEG', 'Ajuste de Inventario Negativo') ON CONFLICT (id) DO NOTHING;
