WIP AAAAAAAAAAAAAAA
## CONSULTAR SI SE PUEDE USAR PANDAS PARA LOS DATOS, NO SE COMO GUARDAR BIEN LOS RESULTADOS SIN USAR DATAFRAMES
## IMPLEMENTADO (REVISAR Y PROPONER SUGERENCIAS, PERO FUNCIONA POR AHORA)

* **Base de Datos:** Esquema PostgreSQL definido en `sql/crear_basev2.sql`, incluyendo tablas para productos, clientes (con RUT generado aleatoriamente), ventas, stock y dimensiones auxiliares necesarias para el modelo estrella que buscamos plantear (fabricantes, categorías, ubicaciones, tipos de movimiento).
* **Población de Datos:** Script `sql/inserts.py` que genera datos de prueba ficticios (RUTs, precios en CLP como enteros, historial de stock coherente) y los inserta en la base de datos usando `psycopg2`.
* **Configuración:** Carga de credenciales de base de datos desde un archivo `.env` (revisar '.env_example') mediante `src/config.py`.
* **Acceso a Datos:** Módulo `src/database.py` para conectar a la base de datos y ejecutar consultas usando `psycopg2` . Devuelve resultados como datos crudos (formato filas-columnas).
* **Consultas Base:** Definición inicial de 3 consultas SQL parametrizadas por año en `src/queries.py`.

## Características Pendientes

* Definir las 3+ consultas SQL restantes para las 6 que pide el profe
* Implementar el módulo `src/plotting.py` con funciones para generar gráficos (barras, torta, etc.) Usando seaborn idealmente, pero en el requirements .txt esta matplotlib tambien.
* Implementar el módulo `src/analysis.py` con las funciones específicas para cada uno de los 6+ análisis (cada una debe tomar el año, ejecutar la query correspondiente, procesar datos y llamar a una función de plotting).
* Implementar el script principal `src/main.py` que:
    * Parsee el argumento de línea de comandos para el año.
    * La ejecución de todas las funciones de análisis.
    * Guarde los gráficos generados en la carpeta `output/`.
