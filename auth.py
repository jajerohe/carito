import unicodedata

import streamlit as st
from supabase import Client, create_client


def _limpiar_secreto(nombre):
    """
    Lee [supabase].<nombre> quitando espacios, saltos de línea, comillas y
    caracteres invisibles que se cuelan al copiar y pegar. La URL y la clave
    solo pueden tener caracteres ASCII; si queda otro, se avisa con claridad.
    """
    valor = str(st.secrets["supabase"][nombre])
    valor = "".join(
        c for c in valor
        if not c.isspace() and unicodedata.category(c) not in ("Cf", "Cc")
    ).strip("\"'“”‘’")
    if not valor.isascii():
        raise ValueError(
            f"El valor de [supabase] {nombre} en los Secrets tiene caracteres "
            "no válidos. Bórrelo y vuelva a copiarlo directamente desde "
            "Supabase (Project Settings → API Keys)."
        )
    return valor


@st.cache_resource
def obtener_cliente_supabase() -> Client:
    return create_client(_limpiar_secreto("url"), _limpiar_secreto("key"))


def iniciar_sesion(email: str, password: str):
    try:
        cliente = obtener_cliente_supabase()
    except ValueError as e:
        raise Exception(str(e))

    try:
        return cliente.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as e:
        raise Exception(f"No fue posible iniciar sesión: {e}")


def cerrar_sesion():
    try:
        obtener_cliente_supabase().auth.sign_out()
    except Exception:
        pass
