import psycopg2
import pandas as pd
import src.config as config

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL usando psycopg2.
    Devuelve None si la conexión falla.
    """
    if not config.check_db_config():
        return None

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"error al conectar con psycopg2: {e}")
        return None
    except Exception as e:
        print(f"error al conectar con psycopg2: {e}")
        return None

def test_connection():
    """
    Intenta conectar a la base de datos usando get_db_connection y devuelve True/False.
    """
    conn = get_db_connection()
    if conn:
        try:
            conn.close()
            return True
        except Exception as e:
            print(f"Error al cerrar conexión de prueba (psycopg2): {e}")
            return False
    else:
        return False

def execute_query(sql_query: str, params: dict = None) -> pd.DataFrame | None:
    """
    ejecuta una consulta sql, devuelve un df con el resultado (si la consulta no esta bien devuelve un df vacio)
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
        with conn.cursor() as cursor:
            cursor.execute(sql_query, params)
            if cursor.description:
                column_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return pd.DataFrame(rows, columns=column_names)
            else:
                return pd.DataFrame()

    except psycopg2.Error as e:
        print(f"Error de Base de Datos (psycopg2) al ejecutar consulta SELECT: {e}\nSQL: {sql_query.strip()}\nParams: {params}")
        return None
    except Exception as e:
        print(f"Error Inesperado al ejecutar consulta SELECT: {e}\nSQL: {sql_query.strip()}\nParams: {params}")
        return None
    finally:
        if conn:
            conn.close()

def execute_mod_query(sql_query: str, params: tuple = None) -> tuple[bool, str]:
    """
    Ejecuta una consulta de modificación (INSERT, UPDATE, DELETE) en la base de datos.
    Devuelve una tupla: (True/False si fue exitoso, mensaje de éxito o error).
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return (False, "No se pudo conectar a la base de datos.")
        with conn.cursor() as cursor:
            cursor.execute(sql_query, params)
            conn.commit()
            msg = f"Consulta de modificación ejecutada. Filas afectadas: {cursor.rowcount}"
            print(f"INFO: {msg}")
            return (True, msg)

    except psycopg2.Error as e:
        error_msg = f"Error de Base de Datos: {e.pgerror}"
        print(f"{error_msg}\nSQL: {sql_query.strip()}\nParams: {params}")
        if conn:
            conn.rollback()
        return (False, error_msg) # Devuelve el mensaje de error de la BD
    except Exception as e:
        error_msg = f"Error Inesperado: {e}"
        print(f"{error_msg}\nSQL: {sql_query.strip()}\nParams: {params}")
        if conn:
            conn.rollback()
        return (False, error_msg)
    finally:
        if conn:
            conn.close()

def get_next_product_id() -> int:
    """
    Calcula el siguiente ID de producto disponible encontrando el máximo actual y sumando 1.
    """
    df = execute_query("SELECT MAX(producto_id) as max_id FROM productos;")
    if df is not None and not df.empty and df['max_id'][0] is not None:
        return int(df['max_id'][0]) + 1
    return 1
