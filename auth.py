import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def obtener_cliente_supabase() -> Client:
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])


def iniciar_sesion(email: str, password: str):
    try:
        return obtener_cliente_supabase().auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as e:
        raise Exception(f"No fue posible iniciar sesión: {e}")


def cerrar_sesion():
    try:
        obtener_cliente_supabase().auth.sign_out()
    except Exception:
        pass
