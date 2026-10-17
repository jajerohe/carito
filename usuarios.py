"""
Administración de usuarios (solo Administrador) y página Mi cuenta (cualquier
usuario), con el mismo manejo de Podex y Ponycash.

Cada usuario vive en public.usuarios: correo (con el que inicia sesión),
usuario, nombre, perfil, estado y la contraseña cifrada con bcrypt (pgcrypto).
"""

import re
from html import escape

import pandas as pd
import psycopg
import streamlit as st

from correo import APP_URL_DEFECTO, configuracion_correo, construir_correo_bienvenida
from database import conexion
from marca import NOMBRE_SISTEMA

PERFILES = {
    "Administrador": "Acceso completo, incluida la administración de usuarios.",
    "Usuario": "Acceso a pacientes e historias clínicas.",
}
LONGITUD_MINIMA_CONTRASENA = 8
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_USUARIO = re.compile(r"^[A-Z0-9_.-]{3,30}$")


# ============================================================
# CONSULTAS
# ============================================================
@st.cache_data(ttl=60, show_spinner=False)
def obtener_usuarios():
    with conexion() as conn:
        filas = conn.execute(
            "SELECT usuario, nombre, email, perfil, activo FROM public.usuarios ORDER BY usuario"
        ).fetchall()
    return pd.DataFrame(filas, columns=["usuario", "nombre", "email", "perfil", "activo"])


@st.cache_data(ttl=60, show_spinner=False)
def datos_sesion(email):
    """Usuario, nombre y perfil del correo que inició sesión (None si ya no existe o está inactivo)."""
    with conexion() as conn:
        return conn.execute(
            "SELECT usuario, nombre, perfil FROM public.usuarios WHERE email = %s AND activo",
            (email,),
        ).fetchone()


def ejecutar(sql, parametros):
    """Ejecuta una escritura en su propia transacción. Devuelve las filas afectadas."""
    with conexion() as conn:
        return conn.execute(sql, parametros).rowcount


# ============================================================
# VALIDACIONES
# ============================================================
def validar_contrasena(contrasena, confirmacion):
    if len(contrasena or "") < LONGITUD_MINIMA_CONTRASENA:
        return f"La contraseña debe tener al menos {LONGITUD_MINIMA_CONTRASENA} caracteres."
    if contrasena != confirmacion:
        return "La contraseña y su confirmación no coinciden."
    return None


def validar_datos(nombre, correo, perfil):
    if not nombre:
        return "Debe ingresar el nombre."
    if not PATRON_CORREO.match(correo or ""):
        return "Debe ingresar un correo electrónico válido."
    if perfil not in PERFILES:
        return "Debe seleccionar el perfil."
    return None


# ============================================================
# PIEZAS DE LAS VENTANAS
# ============================================================
def encabezado_ventana(titulo):
    """Encabezado de las ventanas con el mismo estilo del encabezado de página."""
    st.markdown(
        f'''<div class="hc-topbar hc-dialog-header"><div>
        <div class="hc-top-title">{titulo}</div>
        <div class="hc-top-subtitle">{escape(NOMBRE_SISTEMA)} · Historia Clínica de Ortodoncia y Ortopedia Maxilar</div>
        </div></div>''',
        unsafe_allow_html=True,
    )


def ficha(campos, columnas=3):
    """Tarjeta con datos en cuadrícula (etiqueta pequeña + valor)."""
    celdas = "".join(
        f'<div><div class="hc-ficha-label">{etiqueta}</div>'
        f'<div class="hc-ficha-valor">{"—" if valor is None or valor == "" else escape(str(valor))}</div></div>'
        for etiqueta, valor in campos
    )
    st.markdown(
        f'<div class="hc-ficha" style="grid-template-columns:repeat({columnas},minmax(0,1fr))">{celdas}</div>',
        unsafe_allow_html=True,
    )


def seccion(titulo, descripcion=None):
    """Subtítulo de sección dentro de una ventana."""
    html = f'<div class="hc-section-title hc-dialog-section">{titulo}</div>'
    if descripcion:
        html += f'<div class="hc-section-caption">{descripcion}</div>'
    st.markdown(html, unsafe_allow_html=True)


def notificar(mensaje, tipo="success"):
    """Guarda un mensaje para mostrarlo después del st.rerun() y descarta los
    datos en caché para que la tabla refleje el cambio."""
    st.cache_data.clear()
    st.session_state["mensaje_usuarios"] = (tipo, mensaje)
    st.rerun()


# ============================================================
# VENTANAS
# ============================================================
@st.dialog(" ", width="large")
def ventana_crear_usuario():
    encabezado_ventana("Nuevo Usuario")

    with st.form("form_crear_usuario"):
        c1, c2 = st.columns(2)
        with c1:
            usuario = st.text_input("Usuario", max_chars=30, placeholder="Ej: JPEREZ",
                                    help="Letras, números, punto, guion o guion bajo. Se guarda en MAYÚSCULAS.")
        with c2:
            nombre = st.text_input("Nombre completo")
        c3, c4 = st.columns(2)
        with c3:
            correo = st.text_input("Correo electrónico", placeholder="usuario@dominio.com",
                                   help="Con este correo inicia sesión.")
        with c4:
            perfil = st.selectbox("Perfil", list(PERFILES), index=1, format_func=lambda p: p,
                                  help=" · ".join(f"{p}: {d}" for p, d in PERFILES.items()))
        c5, c6 = st.columns(2)
        with c5:
            contrasena = st.text_input("Contraseña temporal", type="password")
        with c6:
            confirmacion = st.text_input("Confirmar contraseña", type="password")

        correo_configurado = configuracion_correo() is not None
        enviar_bienvenida = st.checkbox(
            "Preparar el correo de bienvenida (vista previa antes de enviar)",
            value=correo_configurado,
            disabled=not correo_configurado,
            help=(
                "Al crear el usuario se muestra el correo (dirección de acceso, usuario, perfil, "
                "contraseña temporal y procedimiento de ingreso) y allí decide si lo envía."
                if correo_configurado else
                "Configure la sección [email] en los secretos de la aplicación para habilitar el envío."
            ),
        )
        with st.container(key="acciones_dlg_crear", horizontal=True, horizontal_alignment="right", gap="small"):
            crear = st.form_submit_button("Crear usuario", icon=":material/person_add:", key="btn_ok_crear", help="Crear usuario")

    if not crear:
        return

    usuario = (usuario or "").strip().upper()
    nombre = (nombre or "").strip()
    correo = (correo or "").strip().lower()

    if not PATRON_USUARIO.match(usuario):
        st.error("❌ El usuario debe tener entre 3 y 30 caracteres: letras, números, punto, guion o guion bajo.")
        return
    error = validar_datos(nombre, correo, perfil) or validar_contrasena(contrasena, confirmacion)
    if error:
        st.error(f"❌ {error}")
        return

    try:
        ejecutar(
            """INSERT INTO public.usuarios (usuario, nombre, email, clave, perfil)
               VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')), %s)""",
            (usuario, nombre, correo, contrasena, perfil),
        )
    except psycopg.errors.UniqueViolation:
        st.error(f"❌ Ya existe un usuario con el código {usuario} o con el correo {correo}.")
        return
    except Exception as e:
        st.error(f"❌ No fue posible crear el usuario: {e}")
        return

    if not enviar_bienvenida:
        notificar(f"✅ Usuario {usuario} creado correctamente.")

    # El usuario ya quedó creado; el correo se revisa en la vista previa
    # (envios.py) y se envía desde allí. Un fallo al prepararlo solo avisa.
    try:
        from envios import programar_envio  # aquí para evitar la importación circular

        config = configuracion_correo() or {}
        asunto, texto, html = construir_correo_bienvenida(
            nombre=nombre, usuario=usuario, correo=correo, perfil=perfil, contrasena=contrasena,
            app_url=config.get("app_url") or APP_URL_DEFECTO, descripcion_perfil=PERFILES[perfil],
        )
        programar_envio("Correo de bienvenida", asunto, texto, html, para=[correo],
                        aviso_ok=f"Correo de bienvenida de {usuario} enviado")
    except Exception as e:
        notificar(f"✅ Usuario {usuario} creado correctamente, pero no fue posible preparar "
                  f"el correo de bienvenida a {correo}: {e}", tipo="warning")

    notificar(f"✅ Usuario {usuario} creado correctamente. Revise el correo de bienvenida antes de enviarlo.")


@st.dialog(" ", width="large")
def ventana_editar_usuario(fila, email_actual):
    encabezado_ventana("Editar Usuario")
    es_mismo_usuario = fila["email"] == email_actual

    ficha([("Usuario", fila["usuario"]), ("Perfil", fila["perfil"]),
           ("Estado", "Activo" if fila["activo"] else "Inactivo")])

    with st.form(f"form_editar_{fila['usuario']}"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre completo", value=fila["nombre"] or "")
        with c2:
            correo = st.text_input("Correo electrónico", value=fila["email"] or "",
                                   help="Con este correo inicia sesión.")
        perfil = st.selectbox("Perfil", list(PERFILES), index=list(PERFILES).index(fila["perfil"]),
                              disabled=es_mismo_usuario,
                              help="No puede cambiar su propio perfil." if es_mismo_usuario else None)
        with st.container(key="acciones_dlg_editar", horizontal=True, horizontal_alignment="right", gap="small"):
            guardar = st.form_submit_button("Guardar cambios", icon=":material/save:", key="btn_info_editar", help="Guardar cambios")

    if not guardar:
        return

    nombre = (nombre or "").strip()
    correo = (correo or "").strip().lower()
    if es_mismo_usuario:
        perfil = fila["perfil"]
    error = validar_datos(nombre, correo, perfil)
    if error:
        st.error(f"❌ {error}")
        return

    try:
        ejecutar(
            """UPDATE public.usuarios SET nombre = %s, email = %s, perfil = %s, actualizado = now()
               WHERE usuario = %s""",
            (nombre, correo, perfil, fila["usuario"]),
        )
    except psycopg.errors.UniqueViolation:
        st.error(f"❌ Ya existe otro usuario con el correo {correo}.")
        return
    except Exception as e:
        st.error(f"❌ No fue posible guardar los cambios: {e}")
        return

    if es_mismo_usuario:
        st.session_state["usuario"] = correo
    notificar(f"✅ Usuario {fila['usuario']} actualizado correctamente.")


@st.dialog(" ", width="large")
def ventana_contrasena(fila):
    encabezado_ventana("Cambiar Contraseña")
    ficha([("Usuario", fila["usuario"]), ("Nombre", fila["nombre"]), ("Correo", fila["email"])])

    with st.form(f"form_contrasena_{fila['usuario']}"):
        c1, c2 = st.columns(2)
        with c1:
            contrasena = st.text_input("Nueva contraseña", type="password")
        with c2:
            confirmacion = st.text_input("Confirmar contraseña", type="password")
        with st.container(key="acciones_dlg_clave", horizontal=True, horizontal_alignment="right", gap="small"):
            cambiar = st.form_submit_button("Cambiar contraseña", icon=":material/key:", key="btn_neutral_clave",
                                            help="Cambiar contraseña")

    if not cambiar:
        return
    error = validar_contrasena(contrasena, confirmacion)
    if error:
        st.error(f"❌ {error}")
        return
    try:
        ejecutar(
            "UPDATE public.usuarios SET clave = crypt(%s, gen_salt('bf')), actualizado = now() WHERE usuario = %s",
            (contrasena, fila["usuario"]),
        )
    except Exception as e:
        st.error(f"❌ No fue posible cambiar la contraseña: {e}")
        return
    notificar(f"✅ Contraseña de {fila['usuario']} actualizada correctamente.")


@st.dialog(" ", width="large")
def ventana_estado(fila):
    encabezado_ventana("Cambiar Estado del Usuario")
    activar = not fila["activo"]
    accion = "activar" if activar else "desactivar"

    ficha([("Usuario", fila["usuario"]), ("Nombre", fila["nombre"]), ("Correo", fila["email"])])
    seccion(f"¿Está seguro que desea {accion} este usuario?",
            None if activar else "Un usuario desactivado no puede iniciar sesión. Sus datos se conservan.")

    with st.form(f"form_estado_{fila['usuario']}"):
        with st.container(key="acciones_dlg_estado", horizontal=True, horizontal_alignment="right", gap="small"):
            cancelar = st.form_submit_button("Cancelar", icon=":material/close:", key="btn_cancel_estado", help="Cancelar")
            confirmar = st.form_submit_button(accion.capitalize(), icon=":material/check:", key="btn_warn_estado",
                                              help=f"Sí, {accion}")
    if cancelar:
        st.rerun()
    if not confirmar:
        return
    try:
        ejecutar("UPDATE public.usuarios SET activo = %s, actualizado = now() WHERE usuario = %s",
                 (activar, fila["usuario"]))
    except Exception as e:
        st.error(f"❌ No fue posible {accion} el usuario: {e}")
        return
    notificar(f"✅ Usuario {fila['usuario']} {'activado' if activar else 'desactivado'} correctamente.")


@st.dialog(" ", width="large")
def ventana_eliminar(fila):
    encabezado_ventana("Eliminar Usuario")
    ficha([("Usuario", fila["usuario"]), ("Nombre", fila["nombre"]), ("Correo", fila["email"])])
    seccion("¿Está seguro que desea eliminar este usuario?",
            "Se elimina el usuario y su acceso al sistema. Los pacientes e historias que registró se "
            "conservan. Esta acción no se puede deshacer.")

    with st.form(f"form_eliminar_{fila['usuario']}"):
        with st.container(key="acciones_dlg_eliminar", horizontal=True, horizontal_alignment="right", gap="small"):
            cancelar = st.form_submit_button("Cancelar", icon=":material/close:", key="btn_cancel_eliminar", help="Cancelar")
            confirmar = st.form_submit_button("Eliminar", icon=":material/delete:", key="btn_danger_eliminar",
                                              help="Sí, eliminar")
    if cancelar:
        st.rerun()
    if not confirmar:
        return
    try:
        ejecutar("DELETE FROM public.usuarios WHERE usuario = %s", (fila["usuario"],))
    except Exception as e:
        st.error(f"❌ No fue posible eliminar el usuario: {e}")
        return
    notificar(f"✅ Usuario {fila['usuario']} eliminado correctamente.")


# ============================================================
# PÁGINA DE USUARIOS (solo Administrador)
# ============================================================
def mostrar_modulo_usuarios(email_actual):
    mensaje = st.session_state.pop("mensaje_usuarios", None)
    if mensaje:
        tipo, texto = mensaje
        (st.warning if tipo == "warning" else st.success)(texto)

    try:
        usuarios = obtener_usuarios()
    except Exception as e:
        st.error("❌ No fue posible consultar los usuarios.")
        st.exception(e)
        return

    c_busca, c_acciones = st.columns([1, 1.9], vertical_alignment="center")
    with c_busca:
        texto = st.text_input("Buscar usuario", label_visibility="collapsed",
                              placeholder="🔎  Buscar usuario por usuario, nombre, correo o perfil…")
    if texto:
        buscado = texto.lower()
        usuarios = usuarios[usuarios.apply(
            lambda f: buscado in " ".join(str(f[c]) for c in ("usuario", "nombre", "perfil", "email")).lower(),
            axis=1,
        )]
    usuarios = usuarios.reset_index(drop=True)

    # Fila seleccionada en la cuadrícula (se dibuja más abajo).
    seleccion = st.session_state.get("tabla_usuarios")
    filas = seleccion.selection.rows if seleccion else []
    fila = usuarios.iloc[filas[0]] if filas and filas[0] < len(usuarios) else None
    es_mismo_usuario = fila is not None and fila["email"] == email_actual
    activo = bool(fila["activo"]) if fila is not None else None

    with c_acciones:
        with st.container(key="acciones_usuarios", horizontal=True, horizontal_alignment="right", gap="small"):
            if st.button("Nuevo usuario", icon=":material/person_add:", key="btn_ok_usr_nuevo", help="Nuevo usuario"):
                ventana_crear_usuario()
            if st.button("Editar", icon=":material/edit:", key="btn_info_usr_editar", disabled=fila is None,
                         help="Editar usuario"):
                ventana_editar_usuario(fila, email_actual)
            if st.button("Contraseña", icon=":material/key:", key="btn_neutral_usr_clave", disabled=fila is None,
                         help="Cambiar contraseña"):
                ventana_contrasena(fila)
            if st.button("Activar" if activo is False else "Desactivar", icon=":material/person_off:" if activo is not False else ":material/person_check:",
                         key="btn_warn_usr_estado", disabled=fila is None or es_mismo_usuario,
                         help="Activar usuario" if activo is False else "Desactivar usuario"):
                ventana_estado(fila)
            if st.button("Eliminar", icon=":material/delete:", key="btn_danger_usr_eliminar",
                         disabled=fila is None or es_mismo_usuario, help="Eliminar usuario"):
                ventana_eliminar(fila)

    with st.container(border=True):
        detalle = (f"<b>Seleccionado:</b> {escape(fila['usuario'])} · {escape(fila['nombre'] or '')}"
                   if fila is not None else "☝️ Seleccione un usuario en la tabla")
        st.markdown(f'<div class="hc-card-cabeza"><div class="hc-card-titulo">Usuarios del sistema</div>'
                    f'<div class="hc-card-detalle">{detalle}</div></div>', unsafe_allow_html=True)
        _tabla_usuarios(usuarios)


def _tabla_usuarios(usuarios):
    if usuarios.empty:
        st.info("ℹ️ No existen usuarios que coincidan con el criterio de búsqueda.")
        return

    tabla = pd.DataFrame({
        "USUARIO": usuarios["usuario"],
        "NOMBRE": usuarios["nombre"].fillna("—"),
        "PERFIL": usuarios["perfil"],
        "CORREO": usuarios["email"],
        "ESTADO": usuarios["activo"].map(lambda v: "🟢 Activo" if v else "🔴 Inactivo"),
    })
    st.dataframe(
        tabla, key="tabla_usuarios", on_select="rerun", selection_mode="single-row",
        hide_index=True, width="stretch", height=min(38 + 35 * len(tabla), 640),
        column_config={
            "USUARIO": st.column_config.TextColumn("USUARIO", width="small"),
            "NOMBRE": st.column_config.TextColumn("NOMBRE", width="medium"),
            "PERFIL": st.column_config.TextColumn("PERFIL", width="small"),
            "CORREO": st.column_config.TextColumn("CORREO", width="medium"),
            "ESTADO": st.column_config.TextColumn("ESTADO", width="small"),
        },
    )


# ============================================================
# MI CUENTA (cualquier usuario)
# ============================================================
def mostrar_mi_cuenta(email_actual):
    if "mensaje_mi_cuenta" in st.session_state:
        st.success(st.session_state.pop("mensaje_mi_cuenta"))

    with st.container(border=True):
        st.markdown(
            '<div class="hc-card-titulo">Cambiar mi contraseña</div>'
            f'<div class="hc-section-caption">Mínimo {LONGITUD_MINIMA_CONTRASENA} caracteres.</div>',
            unsafe_allow_html=True,
        )
        with st.form("form_mi_clave", clear_on_submit=True):
            actual = st.text_input("Contraseña actual", type="password")
            c1, c2 = st.columns(2)
            with c1:
                nueva = st.text_input("Nueva contraseña", type="password")
            with c2:
                confirmacion = st.text_input("Confirmar nueva contraseña", type="password")
            with st.container(key="acciones_dlg_mi_clave", horizontal=True, horizontal_alignment="right", gap="small"):
                cambiar = st.form_submit_button("Cambiar contraseña", icon=":material/key:", key="btn_ok_mi_clave",
                                                help="Cambiar contraseña")
    if not cambiar:
        return
    error = validar_contrasena(nueva, confirmacion)
    if error:
        st.error(f"❌ {error}")
        return
    try:
        cambiada = ejecutar(
            """UPDATE public.usuarios SET clave = crypt(%s, gen_salt('bf')), actualizado = now()
               WHERE email = %s AND clave = crypt(%s, clave)""",
            (nueva, email_actual, actual),
        ) == 1
    except Exception as e:
        st.error(f"❌ No fue posible cambiar la contraseña: {e}")
        return
    if not cambiada:
        st.error("❌ La contraseña actual no es correcta.")
        return
    st.session_state["mensaje_mi_cuenta"] = "✅ Su contraseña fue cambiada correctamente."
    st.rerun()
