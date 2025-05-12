import psycopg2
import src.config as config
def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL usando psycopg2.
    Devuelve None si la conexión falla.
    """
    conn = None
    if not all([config.DB_NAME, config.DB_USER, config.DB_PASS, config.DB_HOST, config.DB_PORT]):
         print("Error Crítico: Faltan variables de configuración de BD en config.py / .env")
         return None
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
        print(f"Error Crítico al conectar con psycopg2 (Operacional): {e}")
        return None
    except Exception as e:
        print(f"Error Crítico al conectar con psycopg2 (General): {e}")
        return None

def test_connection():
    """
    Intenta conectar a la base de datos usando get_db_connection y devuelve True/False.
    """
    print("\nIntentando probar la conexión a la base de datos...")
    conn = get_db_connection()
    if conn:
        try:
            conn.close()
            print("Prueba de conexión directa a la base de datos (psycopg2) exitosa.")
            return True
        except Exception as e:
            print(f"Error al cerrar conexión de prueba (psycopg2): {e}")
            return False
    else:
        print("Prueba de conexión directa a la base de datos (psycopg2) fallida.")
        return False

# --- Función de Ejecución de Consultas ---

def execute_query(sql_query: str, params: dict = None) -> tuple[list[tuple], list[str]] | None:
    """
    Ejecuta una consulta SQL (SELECT) usando psycopg2 y devuelve las filas y nombres de columnas.

    Args:
        sql_query (str): La consulta SQL a ejecutar (debe ser SELECT o devolver filas).
                         Puede contener placeholders estilo %(nombre_param)s.
        params (dict, optional): Un diccionario con los parámetros para la consulta.
                                 Ej: {'year': 2024, 'prod_id': 1}

    Returns:
        tuple[list[tuple], list[str]] | None: Una tupla conteniendo (lista_de_filas, lista_de_nombres_columnas)
                                             o None si ocurre un error.
                                             Devuelve ([], []) si la consulta no es SELECT o no devuelve filas.
                                             La lista_de_filas es una lista de tuplas.
    """
    conn = None
    print(f"\nEjecutando consulta con psycopg2:")
    print(f"SQL: {sql_query.strip()}")
    if params:
        print(f"Params: {params}")

    try:
        conn = get_db_connection()
        if not conn:
            print("Error en execute_query: No se pudo establecer conexión.")
            return None

        with conn.cursor() as cursor:
            cursor.execute(sql_query, params)

            if cursor.description:
                column_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                print(f"Consulta SELECT ejecutada. Filas obtenidas: {len(rows)}. Columnas: {column_names}")
                return rows, column_names
            else:
                try:
                    if cursor.rowcount != -1:
                        conn.commit()
                        print(f"Consulta (no SELECT o DML) ejecutada. Filas afectadas: {cursor.rowcount}. Commit realizado.")
                    else:
                        print("Consulta ejecutada (probablemente SELECT sin filas o comando DDL).")
                except psycopg2.Error as commit_error:
                     print(f"Error al hacer commit: {commit_error}")
                     conn.rollback()
                     return None
                return [], []

    except psycopg2.Error as e:
        print(f"Error de Base de Datos (psycopg2): {e}")
        if conn: conn.rollback()
        return None
    except Exception as e:
        print(f"Error Inesperado (no DB): {e}")
        if conn: conn.rollback()
        return None
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    print("\n--- Probando el módulo database.py (solo psycopg2) ---")
    try:
        import config
        config_ok = config.check_db_config()
    except ImportError:
        print("Error: No se pudo importar config. Asegúrate que src/__init__.py existe si es necesario.")
        config_ok = False
    except AttributeError:
         print("Error: La función check_db_config no existe en config.")
         config_ok = False

    if config_ok:
        if test_connection():
            print("\n--- Probando execute_query (listar tablas) ---")
            test_sql_tablas = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
            result_tablas = execute_query(test_sql_tablas)
            if result_tablas is not None:
                rows, cols = result_tablas
                print(f"Columnas: {cols}")
                if rows: print(f"Primeras 5 tablas: {[r[0] for r in rows[:5]]}")
                else: print("No se encontraron tablas.")

            print("\n--- Probando execute_query (buscar producto) ---")
            test_param_sql = "SELECT producto_id, nombre_articulo FROM productos WHERE producto_id = %(prod_id)s LIMIT 1;"
            prod_id_prueba = 1
            result_prod = execute_query(test_param_sql, params={'prod_id': prod_id_prueba})
            if result_prod is not None:
                rows, cols = result_prod
                print(f"Columnas: {cols}")
                if rows: print(f"Datos producto {prod_id_prueba}: {rows[0]}")
                else: print(f"No se encontró producto {prod_id_prueba}.")
    else:
        print("\nConfiguración de BD inválida. No se pueden ejecutar pruebas.")
