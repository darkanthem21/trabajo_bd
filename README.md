
## USO DEL CODIGO

### Paso 1: Prerrequisitos

* **Python**
* **Git**
* **PostgreSQL**

### Paso 2: Obtener el Código

1.  **Clonar el repo**
    ```bash
    git clone <https://github.com/darkanthem21/trabajo_bd>
    cd trabajo_bd
    ```
### Paso 3: Configurar el Entorno Python

1.  **Crear Ambiente Virtual:** Dentro de la carpeta raíz del proyecto (`trabajo_bd/`), crea un ambiente virtual (recomendado `venv`):
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
    CREATE USER lubricentro_user WITH PASSWORD 'pass';
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
    GRANT ALL ON SCHEMA public TO lubricentro_user;
    ```

6.  **Salir de `psql`:**
    ```sql
    \q
    ```

### Paso 6: Crear Estructura de Tablas (schema)

Ahora que la base de datos y el usuario están configurados y el usuario es dueño, este usuario puede crear las tablas.

1.  **Conéctate a tu Base de Datos con el Usuario de la Aplicación:**
    ```bash
    psql -U lubricentro_user -d lubricentro_db -h localhost
    ```

2.  **Ejecuta el Script SQL de Creación de Tablas:**
    ```sql
    \i sql/crear_base_v2.sql
    ```

3.  **Verifica las Tablas:**
    ```sql
    \dt
    ```

4.  **Salir de `psql`:**
    ```sql
    \q
    ```
### Paso 7: Configurar Variables de Entorno
1.  **Crear archivo `.env`:** REVISAR (`.env_example`)

### Paso 8: Poblar la Base de Datos con Datos de Prueba
1.  **Asegúrate de estar en la carpeta raíz del proyecto** (`lubricentro_proyecto/`) en tu terminal y que tu **ambiente virtual (`.venv`) esté activado**.
2.  **Ejecuta el script de inserción Python:**
    ```bash
    python sql/inserts.py
    ```
