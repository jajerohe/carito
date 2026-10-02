import os
import unicodedata
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


class ErrorConexion(Exception):
    """No se pudo conectar a la base de datos; el mensaje explica qué revisar."""


# (texto del error de Postgres, explicación para el usuario)
DIAGNOSTICOS = (
    ("password authentication failed",
     "la contraseña de [database] password es incorrecta. Si no la recuerda, "
     "cámbiela en Supabase (Project Settings → Database → Reset database "
     "password) y actualícela en los Secrets."),
    ("tenant or user not found",
     "el usuario o el host no corresponden al proyecto. El usuario debe ser "
     "postgres.<código del proyecto> y el host debe copiarse exactamente "
     "desde Supabase → Connect → Session pooler (puede empezar por aws-0- o "
     "aws-1-)."),
    ("could not translate host name",
     "el host está mal escrito. Cópielo desde Supabase → Connect → Session pooler."),
    ("name or service not known",
     "el host está mal escrito. Cópielo desde Supabase → Connect → Session pooler."),
    ("network is unreachable",
     "está usando la conexión directa (db.xxx.supabase.co). Use el host del "
     "Session pooler (aws-...pooler.supabase.com)."),
    ("timeout",
     "el servidor no respondió. Verifique que el host sea el del Session "
     "pooler y que el proyecto de Supabase no esté pausado."),
    ("connection refused",
     "el servidor rechazó la conexión. Verifique el host y que el puerto sea 5432."),
)


def _limpio(valor):
    """Quita espacios en los extremos y caracteres invisibles pegados por error."""
    return "".join(
        c for c in str(valor) if unicodedata.category(c) not in ("Cf", "Cc")
    ).strip()


def _parametros_conexion():
    """Lee la conexión de DATABASE_URL (pruebas) o de st.secrets (app)."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return {"conninfo": url}

    import streamlit as st

    try:
        db = st.secrets["database"]
        return {
            "host": _limpio(db["host"]),
            "port": int(_limpio(db["port"])),
            "dbname": _limpio(db["database"]),
            "user": _limpio(db["user"]),
            "password": _limpio(db["password"]),
        }
    except (KeyError, ValueError) as e:
        raise ErrorConexion(
            "Faltan datos en la sección [database] de los Secrets o están mal "
            f"escritos (host, port, database, user, password). Detalle: {e}"
        ) from e


def _diagnosticar(error):
    texto = str(error).strip().splitlines()[0] if str(error).strip() else type(error).__name__
    for patron, explicacion in DIAGNOSTICOS:
        if patron in str(error).lower():
            return f"No se pudo conectar a la base de datos: {explicacion}\n\nDetalle técnico: {texto}"
    return f"No se pudo conectar a la base de datos.\n\nDetalle técnico: {texto}"


@contextmanager
def conexion():
    """Abre una conexión, hace commit al salir y rollback si hay error."""
    try:
        conn = psycopg.connect(**_parametros_conexion(), row_factory=dict_row,
                               connect_timeout=15)
    except psycopg.OperationalError as e:
        raise ErrorConexion(_diagnosticar(e)) from e

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
