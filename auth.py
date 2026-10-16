"""Inicio de sesión contra la tabla public.usuarios de la propia base de datos.

La contraseña se guarda cifrada con bcrypt (pgcrypto: crypt + gen_salt('bf')),
igual que en Ponycash. Las contraseñas que venían de Supabase Auth también son
bcrypt, así que se copian tal cual y cada usuario conserva la suya.

Crear un usuario (SQL Editor):
    INSERT INTO public.usuarios (email, nombre, clave)
    VALUES ('correo@dominio.com', 'Nombre', crypt('Contraseña', gen_salt('bf')));
"""

from database import ErrorConexion, conexion


def iniciar_sesion(email: str, password: str) -> str:
    """Devuelve el correo del usuario si el correo y la contraseña son válidos."""
    try:
        with conexion() as conn:
            fila = conn.execute(
                """SELECT email, activo FROM public.usuarios
                   WHERE lower(email) = lower(%s) AND clave = crypt(%s, clave)""",
                (email.strip(), password),
            ).fetchone()
            if fila and fila["activo"]:
                conn.execute("UPDATE public.usuarios SET ultimo_ingreso = now() WHERE email = %s",
                             (fila["email"],))
    except ErrorConexion:
        raise
    except Exception as e:
        raise Exception(f"No fue posible iniciar sesión: {e}") from e

    if not fila:
        raise Exception("❌ Correo o contraseña incorrectos.")
    if not fila["activo"]:
        raise Exception("❌ El usuario está inactivo. Comuníquese con el administrador.")
    return fila["email"]


def cerrar_sesion():
    """La sesión vive solo en st.session_state; no hay nada que cerrar en el servidor."""
