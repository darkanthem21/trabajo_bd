from src.database import test_connection, get_db_connection
from src.config import check_db_config

if __name__ == "__main__":
    if not check_db_config():
        print("error")
    else:
        print("configuraciones bien.")
        if test_connection():
            print("AAAAA")
        else:
            print("error.")
