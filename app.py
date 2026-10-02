import os

import streamlit as st

import repositorio as repo
from database import ErrorConexion
from pdf import PARTES, generar_pdf
from utilidades import LOGO, calcular_edad, nombre_completo
from vistas.historia import pagina_consentimiento, pagina_historia, pagina_ortodoncia
from vistas.pacientes import pagina_pacientes
from vistas.seguimiento import pagina_evolucion, pagina_pagos

st.set_page_config(page_title="Historia Clínica de Ortodoncia", page_icon="🦷",
                   layout="wide")

PAGINAS_HISTORIA = {
    "Historia clínica": pagina_historia,
    "Anexo de ortodoncia": pagina_ortodoncia,
    "Presupuesto y pagos": pagina_pagos,
    "Consentimiento": pagina_consentimiento,
    "Evolución": pagina_evolucion,
    "Imprimir": None,
}


# ============================================================
# Inicio de sesión
# ============================================================

def pantalla_login():
    from auth import iniciar_sesion

    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        if os.path.exists(LOGO):
            st.image(LOGO)
        with st.form("login"):
            email = st.text_input("Correo")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar", type="primary", use_container_width=True):
                try:
                    respuesta = iniciar_sesion(email.strip(), password)
                    st.session_state["usuario"] = respuesta.user.email
                    st.rerun()
                except Exception as e:
                    st.error(str(e))


def usuario_actual():
    # DEV_SIN_LOGIN permite probar la app localmente sin Supabase Auth.
    if os.environ.get("DEV_SIN_LOGIN"):
        return os.environ.get("DEV_USUARIO", "desarrollo@local")
    return st.session_state.get("usuario")


# ============================================================
# Páginas
# ============================================================

def pagina_imprimir(historia, paciente, usuario):
    st.header("Imprimir")
    partes = st.multiselect(
        "Secciones a incluir", list(PARTES), default=list(PARTES),
        format_func=PARTES.get,
    )
    if st.button("Generar PDF", type="primary", disabled=not partes):
        with st.spinner("Generando PDF…"):
            st.session_state["pdf"] = generar_pdf(
                paciente, historia, repo.evoluciones(historia["id"]),
                repo.estado_de_cuenta(historia), partes,
            )
    if st.session_state.get("pdf"):
        st.download_button(
            "⬇️ Descargar PDF", st.session_state["pdf"],
            file_name=f"HC_{paciente['documento']}_{historia['fecha_apertura']}.pdf",
            mime="application/pdf",
        )


def barra_lateral(usuario):
    with st.sidebar:
        if os.path.exists(LOGO):
            st.image(LOGO)
        st.caption(f"👤 {usuario}")

        paciente = historia = None
        if st.session_state.get("paciente_id"):
            paciente = repo.obtener_paciente(st.session_state["paciente_id"])
        if paciente and st.session_state.get("historia_id"):
            historia = repo.obtener_historia(st.session_state["historia_id"])
            if historia and historia["paciente_id"] != paciente["id"]:
                historia = None

        if paciente:
            edad = calcular_edad(paciente["fecha_nacimiento"])
            st.markdown(f"**{nombre_completo(paciente)}**  \n"
                        f"{paciente['tipo_documento']} {paciente['documento']}"
                        + (f" · {edad} años" if edad is not None else ""))
            if historia:
                st.caption(f"Historia #{historia['id']} · {historia['estado']}")

        opciones = ["Pacientes"] + (list(PAGINAS_HISTORIA) if historia else [])
        if "ir_a" in st.session_state:
            st.session_state["pagina"] = st.session_state.pop("ir_a")
        if st.session_state.get("pagina") not in opciones:
            st.session_state["pagina"] = "Pacientes"
        pagina = st.radio("Menú", opciones, key="pagina", label_visibility="collapsed")

        st.divider()
        if st.button("Cerrar sesión"):
            from auth import cerrar_sesion

            cerrar_sesion()
            st.session_state.clear()
            st.rerun()

    return pagina, paciente, historia


def main():
    usuario = usuario_actual()
    if not usuario:
        pantalla_login()
        return

    pagina, paciente, historia = barra_lateral(usuario)

    # El PDF generado pertenece a una historia; se descarta al cambiar.
    if st.session_state.get("pdf_historia") != st.session_state.get("historia_id"):
        st.session_state.pop("pdf", None)
        st.session_state["pdf_historia"] = st.session_state.get("historia_id")

    if pagina == "Pacientes":
        pagina_pacientes(usuario)
    elif pagina == "Imprimir":
        pagina_imprimir(historia, paciente, usuario)
    else:
        PAGINAS_HISTORIA[pagina](historia, paciente, usuario)


try:
    main()
except ErrorConexion as e:
    st.error(str(e), icon="🔌")
