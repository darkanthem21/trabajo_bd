
## USO DEL CODIGO

### Paso 1: Prerrequisitos

* **Python**
* **Git**
* **PostgreSQL**

### Paso 2: Obtener el Código

1.  **Clonar el repo**
    ```bash
    git clone https://github.com/darkanthem21/trabajo_bd.git
    cd trabajo_bd
    ```
### Paso 3: Configurar el Entorno Python

1.  **Crear Ambiente Virtual:** Dentro de la carpeta raíz del proyecto (`trabajo_bd/`).:
    ```bash
    python -m venv .venv
    ```
2.  **Activar Ambiente Virtual:**
    ```bash
    source venv/bin/activate
    ```
3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```



### Paso 4: Configurar la Base de Datos PostgreSQL

1.  **Conectarse a PostgreSQL como Superusuario:**
    ```bash
    sudo -u postgres psql
    ```
2.  **Crear el Rol (Usuario) para la Aplicación:** .
    ```sql
    CREATE USER user WITH PASSWORD 'pass';
    ```

3.  **Crear la Base de Datos:**
    ```sql
    CREATE DATABASE lubricentro_db;
    ```

4.  **Conectarse a la Nueva Base de Datos (aún como postgres) para los permisos al esquema:**
    ```sql
    \c lubricentro_db
    ```

    ```sql
    GRANT ALL ON SCHEMA public TO user;
    ```

6.  **Salir de `psql`:**
    ```sql
    \q
    ```

### Paso 6: Crear Estructura de Tablas (schema)

1.  **conectarse a la base de datos:**
    ```bash
    psql -U user -d lubricentro_db -h localhost
    ```

2.  **ejecutar el archivo para crear las tablas:**
    ```sql
    \i sql/crear_base_v2.sql
    ```

3.  **se pueden revisar las tablas con:**
    ```sql
    \dt
    ```

4.  **Salir:**
    ```sql
    \q
    ```
### Paso 7: Configurar Variables de Entorno
1.  **Crear archivo `.env`:** REVISAR (`.env_example`)

### Paso 8: Poblar la Base de Datos con Datos de Prueba
1.  **Revisar estar e la raiz del directorio y con el ambiente activado (ya me equivoque mucho) **.
2.  **Ejecuta el script de inserción:**
    ```bash
    python sql/inserts.py
    ```
