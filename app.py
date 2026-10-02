import os

import streamlit as st

import repositorio as repo
from database import ErrorConexion
from pdf import PARTES, generar_pdf
from utilidades import LOGO, calcular_edad, nombre_completo
from vistas.historia import pagina_consentimiento, pagina_historia, pagina_ortodoncia
from vistas.pacientes import pagina_pacientes
from vistas.seguimiento import pagina_evolucion, pagina_pagos

st.set_page_config(page_title="SICOR · Historia Clínica de Ortodoncia", page_icon="🦷",
                   layout="wide")

# Estilo general con los colores de SICOR y ajustes para celular.
st.markdown("""
<style>
h1, h2, h3 { color: #0B2A6F; }
button[kind="primary"], button[kind="primaryFormSubmit"] {
    background: linear-gradient(90deg, #1F6FE0 0%, #5B4FE0 55%, #8E3FD1 100%) !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(47, 91, 216, 0.25);
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
    filter: brightness(1.07);
}
section[data-testid="stSidebar"] { border-right: 1px solid #DCE5F5; }
@media (max-width: 640px) {
    .block-container { padding: 3.5rem 0.75rem 3rem !important; }
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; }
}
</style>
""", unsafe_allow_html=True)

PAGINAS_HISTORIA = {
    "Historia clínica": pagina_historia,
    "Anexo de ortodoncia": pagina_ortodoncia,
    "Presupuesto y pagos": pagina_pagos,
    "Consentimiento": pagina_consentimiento,
    "Evolución": pagina_evolucion,
    "Imprimir": None,
}
ICONOS = {
    "Pacientes": "🔍", "Historia clínica": "📋", "Anexo de ortodoncia": "🦷",
    "Presupuesto y pagos": "💲", "Consentimiento": "✍️", "Evolución": "📅",
    "Imprimir": "🖨️",
}


# ============================================================
# Inicio de sesión
# ============================================================

ESTILO_LOGIN = """
<style>
/* Pantalla de acceso en dos mitades: marca a la izquierda, acceso a la derecha */
header[data-testid="stHeader"] { display: none; }
/* Los bloques que solo traen estilos no deben ocupar espacio */
div[data-testid="stElementContainer"]:has(> div > style),
div[data-testid="stElementContainer"]:has(style) { display: none; }
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] { gap: 0; }
[data-testid="stForm"] [data-testid="stVerticalBlock"] { gap: 1rem; }
.block-container, [data-testid="stMainBlockContainer"] {
    padding: 0 !important; max-width: 100% !important;
}
div[data-testid="stHorizontalBlock"]:has(.login-marca) { gap: 0 !important; min-height: 100vh; }
div[data-testid="stColumn"]:has(.login-marca) {
    background:
        radial-gradient(circle at 15% 20%, rgba(25, 181, 216, 0.16), transparent 45%),
        radial-gradient(circle at 85% 85%, rgba(142, 63, 209, 0.14), transparent 45%),
        linear-gradient(160deg, #EAF2FD 0%, #E3ECFB 55%, #ECE6FA 100%);
    border-right: 1px solid #DCE5F5;
}
div[data-testid="stColumn"]:has(.login-marca),
div[data-testid="stColumn"]:has(.login-acceso) { min-height: 100vh; }
div[data-testid="stColumn"]:has(.login-marca) > div,
div[data-testid="stColumn"]:has(.login-acceso) > div {
    height: 100%; display: flex; flex-direction: column; justify-content: center;
}
div[data-testid="stColumn"]:has(.login-marca) > div { padding: 2rem 3.5rem; }
div[data-testid="stColumn"]:has(.login-acceso) > div { padding: 2rem 1.5rem; }
.login-acceso { text-align: center; }
.login-acceso h3 { color: #0B2A6F; font-weight: 700; font-size: 1.75rem !important;
                   margin: 0; padding: 0 0 0.3rem; }
.login-acceso p { color: #5A6785; font-size: 1.05rem; margin: 0 0 1.4rem; }
div[data-testid="stColumn"]:has(.login-acceso) [data-testid="stForm"] {
    background: #FFFFFF; border: 1px solid #E1E8F5; border-radius: 14px;
    box-shadow: 0 10px 30px rgba(11, 42, 111, 0.08); padding: 1.6rem 1.6rem 1.2rem;
}
.login-pie { text-align: center; color: #5A6785; font-size: 0.83rem;
             line-height: 1.5; margin-top: 1.8rem; }
.login-pie p { margin: 0 0 0.8rem; }
.login-pie b { color: #0B2A6F; }
.login-pie .firma { font-size: 0.78rem; letter-spacing: 0.02em; }
@media (max-width: 640px) {
    div[data-testid="stHorizontalBlock"]:has(.login-marca),
    div[data-testid="stColumn"]:has(.login-marca),
    div[data-testid="stColumn"]:has(.login-acceso) { min-height: auto; }
    div[data-testid="stColumn"]:has(.login-marca) > div { padding: 2.5rem 1.5rem 2rem; }
    div[data-testid="stColumn"]:has(.login-acceso) > div { padding: 2rem 1rem; }
}
</style>
"""


def pantalla_login():
    from auth import iniciar_sesion

    st.markdown(ESTILO_LOGIN, unsafe_allow_html=True)
    marca, acceso = st.columns(2)

    with marca:
        st.markdown('<div class="login-marca"></div>', unsafe_allow_html=True)
        if os.path.exists(LOGO):
            st.image(LOGO, use_container_width=True)

    with acceso:
        st.markdown(
            '<div class="login-acceso"><h3>Bienvenido de nuevo</h3>'
            '<p>Ingresa con tus credenciales para continuar</p></div>',
            unsafe_allow_html=True,
        )
        _, centro, _ = st.columns([0.12, 0.76, 0.12])
        with centro:
            with st.form("login"):
                email = st.text_input("Correo")
                password = st.text_input("Contraseña", type="password")
                entrar = st.form_submit_button("Ingresar", type="primary",
                                               use_container_width=True)
            if entrar:
                try:
                    respuesta = iniciar_sesion(email.strip(), password)
                    st.session_state["usuario"] = respuesta.user.email
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.markdown(
            '<div class="login-pie"><p><b>SICOR</b> · Sistema de Información Clínica '
            'para Pacientes de Ortodoncia y Ortopedia Maxilar<br>'
            'Acceso protegido mediante autenticación segura.</p>'
            '<p class="firma">Powered by <b>JAJEROHE Systems</b></p></div>',
            unsafe_allow_html=True,
        )


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

        st.divider()
        if st.button("Cerrar sesión"):
            from auth import cerrar_sesion

            cerrar_sesion()
            st.session_state.clear()
            st.rerun()

    return paciente, historia


def menu_superior(paciente, historia):
    """
    Menú en la parte superior de cada pantalla. En celular la barra lateral
    queda oculta, así que el menú y el paciente abierto deben verse aquí.
    """
    if paciente:
        texto = f"**{nombre_completo(paciente)}** · {paciente['documento']}"
        if historia:
            texto += f" · Historia #{historia['id']} ({historia['estado'].lower()})"
        st.caption(texto)

    opciones = ["Pacientes"] + (list(PAGINAS_HISTORIA) if historia else [])
    if "ir_a" in st.session_state:
        st.session_state["pagina"] = st.session_state.pop("ir_a")
    if st.session_state.get("pagina") not in opciones:
        st.session_state["pagina"] = st.session_state.get("ultima_pagina", "Pacientes")
        if st.session_state["pagina"] not in opciones:
            st.session_state["pagina"] = "Pacientes"

    pagina = st.pills("Menú", opciones, key="pagina", label_visibility="collapsed",
                      format_func=lambda o: f"{ICONOS[o]} {o}")
    # Al tocar la opción ya seleccionada, st.pills la deselecciona: se mantiene la anterior.
    pagina = pagina or st.session_state.get("ultima_pagina", "Pacientes")
    st.session_state["ultima_pagina"] = pagina
    return pagina


def main():
    usuario = usuario_actual()
    if not usuario:
        pantalla_login()
        return

    paciente, historia = barra_lateral(usuario)
    pagina = menu_superior(paciente, historia)

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
