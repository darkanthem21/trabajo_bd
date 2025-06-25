import psycopg2
import pandas as pd
import src.config as config

def get_db_connection(tipo="transaccional"):
    """
    Establece y devuelve una conexión a la base de datos solicitada (por defecto transaccional/operativa).
    Devuelve None si la conexión falla.
    """
    try:
        db_conf = config.get_db_config(tipo)
        conn = psycopg2.connect(
            dbname=db_conf['database'],
            user=db_conf['user'],
            password=db_conf['password'],
            host=db_conf['host'],
            port=db_conf['port']
        )
        return conn
    except Exception:
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
        except Exception:
            return False
    else:
        return False

def execute_query(sql_query: str, params: dict = None, tipo: str = "transaccional") -> pd.DataFrame | None:
    """
    Ejecuta una consulta SQL y devuelve un DataFrame con el resultado.
    Por defecto usa la base transaccional.
    """
    conn = None
    try:
        conn = get_db_connection(tipo)
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
    except Exception:
        return None
    finally:
        if conn:
            conn.close()

def execute_mod_query(sql_query: str, params: tuple = None, tipo: str = "transaccional") -> tuple[bool, str]:
    """
    Ejecuta una consulta de modificación (INSERT, UPDATE, DELETE) en la base de datos.
    Devuelve una tupla: (True/False si fue exitoso, mensaje de éxito o error).
    Por defecto usa la base transaccional.
    """
    conn = None
    try:
        conn = get_db_connection(tipo)
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
