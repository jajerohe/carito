import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


def _parametros_conexion():
    """Lee la conexión de DATABASE_URL (pruebas) o de st.secrets (app)."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return {"conninfo": url}

    import streamlit as st

    db = st.secrets["database"]
    return {
        "host": db["host"],
        "port": db["port"],
        "dbname": db["database"],
        "user": db["user"],
        "password": db["password"],
    }


@contextmanager
def conexion():
    """Abre una conexión, hace commit al salir y rollback si hay error."""
    conn = psycopg.connect(**_parametros_conexion(), row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
