import base64
import html
import mimetypes
import os
import re
import unicodedata

import streamlit as st

import repositorio as repo
from database import ErrorConexion
from envios import mostrar_envio_pendiente
from marca import DESCRIPCION_SISTEMA, NOMBRE_SISTEMA, TITULO_PESTANA, fijar_titulo_pestana
from pdf import PARTES, generar_pdf
from utilidades import FONDO_LOGIN, LOGO, calcular_edad, nombre_completo
from vistas.historia import pagina_consentimiento, pagina_historia, pagina_ortodoncia
from vistas.pacientes import pagina_pacientes
from vistas.seguimiento import pagina_evolucion, pagina_pagos
from usuarios import datos_sesion, mostrar_mi_cuenta, mostrar_modulo_usuarios

st.set_page_config(page_title=TITULO_PESTANA, page_icon="🦷",
                   layout="wide", initial_sidebar_state="expanded")
fijar_titulo_pestana()

# Estilo general con los colores de Carito y ajustes para celular.
st.markdown("""
<style>
h1, h2, h3 { color: #0B2A6F; }
/* Ventanas y fichas */
.hc-topbar{background:#fff;border:1px solid #E3E8F0;border-radius:14px;min-height:64px;padding:12px 18px;display:flex;
  align-items:center;justify-content:space-between;box-shadow:inset 0 4px 0 #5B4FE0;margin-bottom:12px}
.hc-top-title{color:#0B2A6F;font-size:18px;font-weight:700}
.hc-top-subtitle{color:#5A6785;font-size:11px;margin-top:2px}
.hc-dialog-header{margin:-6px 0 14px!important}
.hc-section-title{color:#0B2A6F;font-size:15px;font-weight:700;margin:2px 0 5px}
.hc-section-caption{color:#5A6785;font-size:12px;margin-bottom:8px}
.hc-dialog-section{margin-top:14px!important}
.hc-ficha{display:grid;gap:12px 22px;background:#F7F9FC;border:1px solid #E3E8F0;border-radius:14px;padding:14px 18px;margin:6px 0}
.hc-ficha-label{color:#5B4FE0;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px}
.hc-ficha-valor{color:#1B2540;font-size:14px;margin-top:3px;line-height:1.35;word-break:break-word;font-weight:500}
/* Título de tarjeta: pequeño, en mayúscula y espaciado */
.hc-card-titulo,[data-testid="stMain"] [data-testid="stHeading"] h3{color:#33415C!important;font-size:13px!important;font-weight:700!important;
  text-transform:uppercase;letter-spacing:.07em;margin:4px 0 10px!important;padding:0!important;line-height:1.4!important}
[data-testid="stMain"] [data-testid="stHeading"] h3 [data-testid="stHeaderActionElements"]{display:none!important}
.hc-card-cabeza{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:4px}
.hc-card-cabeza .hc-card-titulo{margin:0!important}
.hc-card-detalle{color:#5A6785;font-size:13px}
.hc-card-detalle b{color:#0B2A6F}

/* Botones ovalados con ícono y texto. El color sale de la key:
   btn_ok_, btn_info_, btn_warn_, btn_neutral_, btn_cancel_, btn_danger_. */
div[data-testid="stButton"] button,div[data-testid="stFormSubmitButton"] button,div[data-testid="stDownloadButton"] button,
div[data-testid="stPopover"] > div > button{
  border-radius:999px!important;min-height:40px!important;padding:0 18px!important;font-weight:600!important;
  border:1px solid #CBD5E1!important;background:#fff!important;color:#0B2A6F!important;box-shadow:none!important}
div[data-testid="stButton"] button p,div[data-testid="stFormSubmitButton"] button p,div[data-testid="stDownloadButton"] button p{font-weight:600!important}
div[data-testid="stButton"] button:hover,div[data-testid="stFormSubmitButton"] button:hover,div[data-testid="stDownloadButton"] button:hover{
  border-color:#5B4FE0!important;color:#5B4FE0!important;background:#F7F8FF!important}
div[data-testid] button[kind="primary"],div[data-testid] button[kind="primaryFormSubmit"]{background:#0B2A6F!important;border-color:#0B2A6F!important;color:#fff!important}
div[data-testid] button[kind="primary"]:hover,div[data-testid] button[kind="primaryFormSubmit"]:hover{background:#1F4FB8!important;border-color:#1F4FB8!important;color:#fff!important}
button:disabled{opacity:.45!important}
[class*="st-key-acciones_"]{flex-wrap:wrap!important}
[class*="st-key-acciones_"] button span[data-testid="stIconMaterial"]{font-size:18px!important}
/* Barras de herramientas de las páginas */
[class*="st-key-btn_ok_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button{background:#E9EFFD!important;border-color:#B9C8F2!important;color:#1F4FB8!important}
[class*="st-key-btn_ok_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button:hover{background:#DCE6FC!important;border-color:#1F4FB8!important}
[class*="st-key-btn_danger_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button{background:#fff!important;border-color:#F2B8B5!important;color:#C62828!important}
[class*="st-key-btn_danger_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button:hover{background:#FDECEC!important;border-color:#C62828!important;color:#C62828!important}
[class*="st-key-btn_warn_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button{background:#fff!important;border-color:#F3D19C!important;color:#B45309!important}
[class*="st-key-btn_warn_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button:hover{background:#FFF6E8!important;border-color:#B45309!important;color:#B45309!important}
/* En las ventanas, la acción principal va rellena */
[class*="st-key-acciones_dlg_"] [class*="st-key-btn_ok_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button,[class*="st-key-acciones_dlg_"] [class*="st-key-btn_info_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button,
[class*="st-key-acciones_dlg_"] [class*="st-key-btn_neutral_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button{background:#0B2A6F!important;border-color:#0B2A6F!important;color:#fff!important}
[class*="st-key-acciones_dlg_"] [class*="st-key-btn_ok_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button:hover,[class*="st-key-acciones_dlg_"] [class*="st-key-btn_info_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button:hover,
[class*="st-key-acciones_dlg_"] [class*="st-key-btn_neutral_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button:hover{background:#1F4FB8!important;border-color:#1F4FB8!important;color:#fff!important}
[class*="st-key-acciones_dlg_"] [class*="st-key-btn_danger_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button{background:#C62828!important;border-color:#C62828!important;color:#fff!important}
[class*="st-key-acciones_dlg_"] [class*="st-key-btn_warn_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button{background:#D97706!important;border-color:#D97706!important;color:#fff!important}
[class*="st-key-acciones_dlg_"] [class*="st-key-btn_danger_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button:hover{background:#A51F1F!important;color:#fff!important}
[class*="st-key-acciones_dlg_"] [class*="st-key-btn_warn_"] :is(div[data-testid="stButton"],div[data-testid="stFormSubmitButton"]) button:hover{background:#B45309!important;color:#fff!important}

/* Tarjetas: formularios, recuadros, desplegables y tablas */
[data-testid="stMain"] div[data-testid="stForm"],div[role="dialog"] div[data-testid="stForm"],
[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"]{
  background:#fff!important;border:1px solid #E3E8F0!important;border-radius:16px!important;padding:22px 24px!important}
[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stForm"]{padding:0!important;border:none!important}
[data-testid="stMain"] [data-testid="stExpander"] details{background:#fff!important;border:1px solid #E3E8F0!important;border-radius:16px!important}
[data-testid="stMain"] [data-testid="stExpander"] summary{padding:14px 22px!important}
[data-testid="stMain"] [data-testid="stExpander"] summary p{color:#33415C;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.07em}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}
[data-testid="stMetric"]{background:#fff;border:1px solid #E3E8F0;border-radius:16px;padding:14px 18px}
[data-testid="stMetricLabel"] p{color:#5A6785!important;font-size:12px!important;text-transform:uppercase;letter-spacing:.06em;font-weight:600!important}
[data-testid="stMetricValue"]{color:#0B2A6F!important}
[data-testid="stMain"] hr{border-color:#EEF1F6!important;margin:14px 0!important}
/* Pestañas */
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:6px;border-bottom:1px solid #E3E8F0}
[data-testid="stTabs"] button[data-baseweb="tab"]{border-radius:999px 999px 0 0;padding:8px 14px}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p{color:#0B2A6F;font-weight:700}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:#5B4FE0!important}

/* Campos: fondo suave y bordes redondeados */
[data-testid="stTextInputRootElement"],[data-testid="stTextAreaRootElement"],[data-testid="stNumberInputContainer"],
[data-testid="stDateInputField"],[data-testid="stSelectbox"]>div>div,[data-testid="stMultiSelect"]>div>div{
  background:#F7F8FB!important;border:1px solid #DCE2EC!important;border-radius:10px!important}
[data-testid="stTextInputRootElement"]:focus-within,[data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stNumberInputContainer"]:focus-within,[data-testid="stDateInputField"]:focus-within,
[data-testid="stSelectbox"]>div>div:focus-within,[data-testid="stMultiSelect"]>div>div:focus-within{
  border-color:#5B4FE0!important;box-shadow:0 0 0 3px rgba(91,79,224,.12)!important}
[data-testid="stWidgetLabel"] p{color:#33415C!important;font-weight:500!important}
/* Los bloques que solo traen estilos o scripts no deben ocupar espacio */
[data-testid="stMainBlockContainer"] div[data-testid="stElementContainer"]:has(style),
[data-testid="stMainBlockContainer"] div[data-testid="stElementContainer"]:has(script) { display: none; }
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
    "Pacientes": ":material/person_search:", "Historia clínica": ":material/assignment:",
    "Anexo de ortodoncia": ":material/dentistry:", "Presupuesto y pagos": ":material/payments:",
    "Consentimiento": ":material/draw:", "Evolución": ":material/event_note:",
    "Imprimir": ":material/print:",
    "Usuarios": ":material/group:", "Mi cuenta": ":material/key:", "Administración": ":material/admin_panel_settings:",
}
PAGINAS_ADMINISTRACION = ["Usuarios", "Mi cuenta"]


# ============================================================
# Inicio de sesión
# ============================================================

MANCHA_LOGIN = base64.b64encode(
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480">'
    b'<path fill="#E6EDFA" d="M190 20c120-25 230 15 270 85 30 55 110 60 125 150 15 90-50 165-150 185'
    b'-90 18-150-25-235-10C110 445 30 420 12 330 0 265 45 230 35 165 25 95 90 40 190 20z"/></svg>'
).decode()

ESTILO_LOGIN = """
<style>
/* Pantalla de acceso: logo arriba y tarjeta centrada sobre una mancha suave */
[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #F7F9FD !important; }
.block-container, [data-testid="stMainBlockContainer"] { padding: 0 1rem !important; max-width: 100% !important; }
/* Los bloques que solo traen estilos no deben ocupar espacio */
div[data-testid="stElementContainer"]:has(style) { display: none; }
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] { gap: 0; }

/* Logo, tarjeta y pie centrados, con los mismos espacios en todos los sistemas */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    min-height: 100vh; justify-content: center; padding: 32px 0;
}
.login-logo { text-align: center; padding: 0; line-height: 0; }
.login-logo img { width: 150px; max-width: 50%; height: auto; }
.st-key-login_zona {
    max-width: 600px; margin: 0 auto; padding: 110px 0 96px;
    background: url("data:image/svg+xml;base64,MANCHA") center / 100% auto no-repeat;
}
.st-key-login_tarjeta {
    width: 100%; max-width: 385px; margin: 0 auto; background: #FFFFFF; border-radius: 6px;
    box-shadow: 0 4px 18px rgba(11, 42, 111, 0.07); padding: 0 45px 35px; overflow: visible;
}
.login-icono {
    width: 86px; height: 86px; margin: -43px auto 22px; border-radius: 50%;
    background: linear-gradient(160deg, #1F6FE0 0%, #5B4FE0 55%, #8E3FD1 100%);
    box-shadow: 0 6px 16px rgba(47, 91, 216, 0.28);
    display: flex; align-items: center; justify-content: center;
}
.login-titulo { text-align: center; color: #0B2A6F; font-size: 1.3rem; font-weight: 700;
                line-height: 1.3; margin: 0 0 26px; }
.st-key-login_tarjeta [data-testid="stForm"] { border: none; padding: 0; }
.st-key-login_tarjeta [data-testid="stForm"] [data-testid="stVerticalBlock"] { gap: 14px; }
.st-key-login_tarjeta [data-testid="stTextInputRootElement"] {
    background: #FFFFFF !important; border: 1px solid #C9D3E6 !important; border-radius: 3px !important;
}
.st-key-login_tarjeta [data-testid="stTextInput"] input {
    background: #FFFFFF !important; min-height: 40px; padding-left: 18px; font-size: 0.9rem;
}
.st-key-login_tarjeta [data-testid="stTextInputRootElement"]:focus-within {
    border-color: #5B4FE0 !important; box-shadow: 0 0 0 1px #5B4FE0 !important;
}
.st-key-login_tarjeta div[data-testid="stFormSubmitButton"] button {
    border-radius: 3px !important; min-height: 36px !important; font-weight: 700 !important; margin-top: 2px;
}
.st-key-login_tarjeta [data-testid="stAlert"] { margin-top: 12px; }
.st-key-login_tarjeta div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(90deg, #1F6FE0 0%, #5B4FE0 55%, #8E3FD1 100%) !important;
    border: none !important; color: #fff !important; padding: 0 18px !important;
}
.st-key-login_tarjeta [data-baseweb="base-input"] { background: #FFFFFF !important; }
.login-pie { text-align: center; color: #7A86A3; font-size: 0.78rem; line-height: 1.5; padding: 0; }
.login-pie b { color: #0B2A6F; }
@media (max-width: 640px) {
    .st-key-login_zona { padding: 90px 0 64px; background-size: 140% auto; }
    .st-key-login_tarjeta { padding: 0 24px 28px; }
}
</style>
""".replace("MANCHA", MANCHA_LOGIN)


@st.cache_data
def _imagen_en_base64(ruta, _modificado):
    tipo = mimetypes.guess_type(ruta)[0] or "image/jpeg"
    with open(ruta, "rb") as f:
        return f"data:{tipo};base64,{base64.b64encode(f.read()).decode()}"


def _estilo_fondo_login():
    """Si hay una foto fondo_login.*, se pone de fondo del acceso con una capa clara encima."""
    if not FONDO_LOGIN:
        return ""
    imagen = _imagen_en_base64(FONDO_LOGIN, os.path.getmtime(FONDO_LOGIN))
    return f"""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background:
        linear-gradient(160deg, rgba(247, 249, 253, 0.86) 0%, rgba(240, 244, 252, 0.82) 100%),
        url("{imagen}") center / cover no-repeat fixed !important;
}}
</style>
"""


def pantalla_login():
    from auth import iniciar_sesion

    st.markdown(ESTILO_LOGIN + _estilo_fondo_login(), unsafe_allow_html=True)
    if os.path.exists(LOGO):
        st.markdown(f'<div class="login-logo"><img src="{_imagen_en_base64(LOGO, os.path.getmtime(LOGO))}" '
                    f'alt="{html.escape(NOMBRE_SISTEMA)}"></div>', unsafe_allow_html=True)

    with st.container(key="login_zona"):
        with st.container(key="login_tarjeta"):
            st.markdown(
                '<div class="login-icono"><svg viewBox="0 0 24 24" width="38" height="38" fill="none" '
                'stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                '<rect x="4.5" y="10.5" width="15" height="10" rx="2" fill="rgba(255,255,255,.18)"/>'
                '<path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>'
                '<circle cx="12" cy="15.5" r="1.4" fill="#FFFFFF" stroke="none"/></svg></div>'
                f'<div class="login-titulo">Inicia sesión y accede a<br>{html.escape(NOMBRE_SISTEMA)}</div>',
                unsafe_allow_html=True,
            )
            with st.form("login", border=False):
                email = st.text_input("Correo", placeholder="Correo electrónico",
                                      label_visibility="collapsed")
                password = st.text_input("Contraseña", type="password", placeholder="Contraseña",
                                         label_visibility="collapsed")
                entrar = st.form_submit_button("Ingresar", type="primary", use_container_width=True)
            if entrar:
                if not email.strip() or not password:
                    st.warning("⚠️ Debe ingresar el correo electrónico y la contraseña.")
                else:
                    try:
                        st.session_state["usuario"] = iniciar_sesion(email.strip(), password)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    st.markdown(
        f'<div class="login-pie"><b>{html.escape(NOMBRE_SISTEMA)}</b> · {html.escape(DESCRIPCION_SISTEMA)}<br>'
        'Powered by <b>JAJEROHE Systems</b></div>',
        unsafe_allow_html=True,
    )


def usuario_actual():
    # DEV_SIN_LOGIN permite probar la app localmente sin iniciar sesión.
    if os.environ.get("DEV_SIN_LOGIN"):
        return os.environ.get("DEV_USUARIO", "desarrollo@local")
    return st.session_state.get("usuario")


# ============================================================
# Páginas
# ============================================================

def pagina_imprimir(historia, paciente, usuario):
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


ALTO_BARRA = 76


def paciente_e_historia():
    """Paciente e historia abiertos (los que están en la sesión)."""
    paciente = historia = None
    if st.session_state.get("paciente_id"):
        paciente = repo.obtener_paciente(st.session_state["paciente_id"])
    if paciente and st.session_state.get("historia_id"):
        historia = repo.obtener_historia(st.session_state["historia_id"])
        if historia and historia["paciente_id"] != paciente["id"]:
            historia = None
    return paciente, historia


# Íconos (trazos) del recuadro de la barra superior, uno por página.
_TRAZOS = {
    "pacientes": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
                 '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "historia": '<rect x="8" y="2" width="8" height="4" rx="1"/>'
                '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 12h6M9 16h4"/>',
    "anexo": '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01M15 9h.01"/>',
    "pagos": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
    "firma": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "evolucion": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M8 14h.01M12 14h.01M16 14h.01"/>',
    "imprimir": '<path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>'
                '<rect x="6" y="14" width="12" height="8"/>',
    "llave": '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6M15.5 7.5l3 3L22 7l-3-3"/>',
}
# Título, ícono y descripción de cada página en la barra superior.
ENCABEZADOS = {
    "Pacientes": ("Pacientes", "pacientes", "Busque, registre y administre los pacientes"),
    "Historia clínica": ("Historia clínica odontológica", "historia", None),
    "Anexo de ortodoncia": ("Anexo de ortodoncia", "anexo", None),
    "Presupuesto y pagos": ("Presupuesto y pagos", "pagos", None),
    "Consentimiento": ("Consentimiento informado de ortodoncia", "firma", None),
    "Evolución": ("Evolución del tratamiento", "evolucion", None),
    "Imprimir": ("Imprimir historia clínica", "imprimir", None),
    "Usuarios": ("Administración de Usuarios", "pacientes", "Usuarios, perfiles y acceso al sistema"),
    "Mi cuenta": ("Mi cuenta", "llave", "Sus datos y su contraseña"),
}


def _icono(trazo, tamano=20, color="currentColor"):
    return (f'<svg viewBox="0 0 24 24" width="{tamano}" height="{tamano}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{_TRAZOS[trazo]}</svg>')


def texto_paciente(paciente, historia):
    """Paciente e historia abiertos (se muestran bajo el título de la página)."""
    if not paciente:
        return None
    texto = f"{nombre_completo(paciente)} · {paciente['tipo_documento']} {paciente['documento']}"
    edad = calcular_edad(paciente["fecha_nacimiento"])
    if edad is not None:
        texto += f" · {edad} años"
    if historia:
        texto += f" · Historia #{historia['id']} ({historia['estado'].lower()})"
    return texto


def barra_superior(usuario, menu_colapsado, sesion, pagina, paciente, historia):
    """Marco de la aplicación: menú lateral oscuro de arriba abajo con la marca,
    barra superior blanca con el título de la página y el contenido en tarjetas."""
    ancho = 72 if menu_colapsado else 264
    st.markdown(f"""
<style>
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{{background:#F4F6FA!important}}
/* Marca, arriba del menú lateral */
.hc-marca{{position:fixed;top:0;left:0;width:{ancho}px;height:{ALTO_BARRA}px;z-index:1000004;background:#0B2A6F;
  display:flex;align-items:center;justify-content:center;padding:0 16px;box-sizing:border-box;border-bottom:1px solid rgba(255,255,255,.08)}}
.hc-marca-logo{{background:#fff;border-radius:12px;width:100%;height:46px;display:flex;align-items:center;justify-content:center}}
.hc-marca-logo img{{height:28px;width:auto}}
.hc-marca-letra{{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#fff;
  font-weight:800;font-size:20px;background:linear-gradient(160deg,#1F6FE0,#5B4FE0 55%,#8E3FD1)}}
/* Barra superior blanca */
.hc-barra{{position:fixed;top:0;left:{ancho}px;right:0;height:{ALTO_BARRA}px;z-index:1000003;display:flex;align-items:center;gap:14px;
  background:#fff;border-bottom:1px solid #E3E8F0;padding:0 28px;box-sizing:border-box}}
.hc-barra-icono{{width:46px;height:46px;flex:0 0 46px;border-radius:12px;background:#EEF2FC;color:#1F4FB8;display:flex;
  align-items:center;justify-content:center}}
.hc-barra-titulo{{min-width:0}}
.hc-barra-titulo b{{display:block;color:#0B2A6F;font-size:19px;font-weight:700;line-height:1.25;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}}
.hc-barra-titulo span{{display:block;color:#5A6785;font-size:12px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.hc-barra-acciones{{margin-left:auto;display:flex;align-items:center;gap:10px;flex:0 0 auto}}
.hc-usuario,.hc-salir{{display:inline-flex;align-items:center;gap:7px;height:40px;padding:0 16px;border-radius:999px;
  border:1px solid #CBD5E1;background:#fff;color:#0B2A6F!important;font-size:13px;font-weight:600;text-decoration:none!important;white-space:nowrap}}
.hc-usuario small{{color:#5A6785;font-weight:500;font-size:12px}}
.hc-salir{{background:#0B2A6F;border-color:#0B2A6F;color:#fff!important}}
.hc-salir:hover{{background:#1F4FB8;border-color:#1F4FB8}}
/* Menú lateral oscuro */
section[data-testid="stSidebar"],section[data-testid="stSidebar"][aria-expanded]{{position:fixed!important;top:{ALTO_BARRA}px!important;left:0!important;
  height:calc(100vh - {ALTO_BARRA}px)!important;width:{ancho}px!important;min-width:{ancho}px!important;max-width:{ancho}px!important;
  transform:none!important;visibility:visible!important;z-index:1000002!important;background:#0B2A6F!important;border-right:none!important;
  box-shadow:none!important}}
section[data-testid="stSidebar"]>div{{padding:.75rem .9rem 3.2rem!important;background:#0B2A6F!important}}
[data-testid="stSidebarHeader"],[data-testid="stSidebarCollapseButton"],[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarResizeHandle"]{{display:none!important}}
[data-testid="stSidebarUserContent"]{{padding:0!important}}
[data-testid="stSidebarUserContent"] div[data-testid="stElementContainer"]:has(style){{display:none}}
header[data-testid="stHeader"]{{display:none!important}}
[data-testid="stMain"]{{margin-left:{ancho}px!important;width:calc(100% - {ancho}px)!important;max-width:calc(100% - {ancho}px)!important}}
.block-container{{padding:{ALTO_BARRA + 24}px 28px 2.5rem!important;max-width:100%!important}}
@media(max-width:900px){{.block-container{{padding-left:.75rem!important;padding-right:.75rem!important}}}}
.st-key-menu_toggle{{display:flex;justify-content:{'center' if menu_colapsado else 'flex-end'}}}
.st-key-menu_toggle div[data-testid="stButton"] button{{width:34px!important;height:30px!important;min-height:30px!important;padding:0!important;
  border:1px solid rgba(255,255,255,.25)!important;border-radius:8px!important;background:transparent!important;color:#DCE5F5!important}}
.st-key-menu_toggle div[data-testid="stButton"] button:hover{{background:rgba(255,255,255,.08)!important}}
/* Opciones del menú (en el panel flotante van sobre fondo blanco) */
[class*="st-key-hc_menu"]{{gap:4px!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button{{justify-content:flex-start!important;min-height:42px!important;padding:9px 14px!important;
  border:none!important;border-radius:10px!important;background:transparent!important;color:#2b3a5c!important;box-shadow:none!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button:hover{{background:#e6edfa!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button[kind="primary"]{{color:#fff!important;
  background:linear-gradient(90deg,#1F6FE0 0%,#5B4FE0 55%,#8E3FD1 100%)!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button>div{{justify-content:flex-start!important;width:100%!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button p{{font-size:14px!important;font-weight:600!important;text-align:left!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button span[data-testid="stIconMaterial"]{{font-size:19px!important}}
section[data-testid="stSidebar"] [class*="st-key-hc_menu"] div[data-testid="stButton"]>button{{color:#DCE5F5!important}}
section[data-testid="stSidebar"] [class*="st-key-hc_menu"] div[data-testid="stButton"]>button:hover{{background:rgba(255,255,255,.08)!important;color:#fff!important}}
section[data-testid="stSidebar"] [class*="st-key-hc_menu"] div[data-testid="stButton"]>button[kind="primary"]{{color:#fff!important}}
.hc-menu-seccion{{color:rgba(220,229,245,.55);font-size:11px;font-weight:700;text-transform:uppercase;margin:18px 14px 6px;letter-spacing:.08em}}
.hc-pie{{position:fixed;left:0;bottom:0;width:{ancho}px;z-index:1000003;padding:14px 22px;box-sizing:border-box;color:#C9D6F2;font-size:12px;
  display:{'none' if menu_colapsado else 'flex'};align-items:center;gap:9px;background:#0B2A6F}}
.hc-pie i{{width:8px;height:8px;border-radius:50%;background:#34D399;flex:0 0 8px;box-shadow:0 0 0 3px rgba(52,211,153,.18)}}
/* Franja contraída: un ícono por grupo que abre su panel a la derecha */
[class*="st-key-grupo_"]{{display:flex;justify-content:center;margin-top:6px}}
[class*="st-key-grupo_"] [data-testid="stPopover"],[class*="st-key-grupo_"] [data-testid="stPopover"]>div{{width:46px!important}}
[class*="st-key-grupo_"] button{{width:46px!important;height:44px!important;min-height:44px!important;padding:0!important;
  border:none!important;border-radius:10px!important;background:transparent!important;color:#DCE5F5!important;box-shadow:none!important}}
[class*="st-key-grupo_"] button:hover{{background:rgba(255,255,255,.08)!important}}
[class*="st-key-grupo_"] div button[kind="primary"]{{background:linear-gradient(90deg,#1F6FE0,#5B4FE0)!important;color:#fff!important}}
[class*="st-key-grupo_"] button span[data-testid="stIconMaterial"]{{font-size:23px!important;margin:0!important}}
[class*="st-key-grupo_"] button div[aria-hidden="true"]{{display:none!important}}
[data-testid="stPopoverBody"]:has(.hc-panel-titulo){{margin-left:58px!important;margin-top:-48px!important;
  min-width:250px;border:1px solid #E3E8F0;border-radius:14px!important;box-shadow:4px 6px 18px rgba(11,42,111,.16)!important}}
.hc-panel-titulo{{color:#0B2A6F;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:2px 2px 8px;
  margin-bottom:4px;border-bottom:1px solid #e3e9f5}}
@media(max-width:900px){{.hc-usuario{{display:none}}.hc-barra{{padding:0 14px}}}}
@media(max-width:640px){{.hc-barra-icono,.hc-salir span{{display:none}}.hc-barra-titulo b{{font-size:16px}}}}
</style>
""", unsafe_allow_html=True)
    if menu_colapsado:
        # Al elegir una opción del panel, se cierra el panel.
        st.html("""
<script>
(() => {
    if (window.hcPanelMenu) return;
    window.hcPanelMenu = true;
    document.addEventListener("click", (e) => {
        if (!e.target.closest('[data-testid="stPopoverBody"] [class*="st-key-hc_menu"] button')) return;
        setTimeout(() => {
            const abierto = document.querySelector('[class*="st-key-grupo_"] button[aria-expanded="true"]');
            if (abierto) abierto.click();
        }, 120);
    }, true);
})();
</script>
""", unsafe_allow_javascript=True)

    if menu_colapsado:
        marca = f'<div class="hc-marca-letra">{html.escape(NOMBRE_SISTEMA[:1])}</div>'
    elif os.path.exists(LOGO):
        marca = (f'<div class="hc-marca-logo"><img src="{_imagen_en_base64(LOGO, os.path.getmtime(LOGO))}" '
                 f'alt="{html.escape(NOMBRE_SISTEMA)}"></div>')
    else:
        marca = f'<div class="hc-marca-logo"><b>{html.escape(NOMBRE_SISTEMA)}</b></div>'

    titulo, trazo, descripcion = ENCABEZADOS.get(pagina, (pagina, "historia", None))
    if pagina in PAGINAS_HISTORIA:
        descripcion = texto_paciente(paciente, historia) or descripcion
    if sesion:
        quien = (f"{html.escape(sesion['nombre'] or sesion['usuario'])}"
                 f"<small>· {html.escape(sesion['perfil'])}</small>")
    else:
        quien = html.escape(usuario)
    st.markdown(f"""
<div class="hc-marca">{marca}</div>
<div class="hc-barra">
  <div class="hc-barra-icono">{_icono(trazo, 22)}</div>
  <div class="hc-barra-titulo"><b>{html.escape(titulo)}</b>{f'<span>{html.escape(descripcion)}</span>' if descripcion else ''}</div>
  <div class="hc-barra-acciones">
    <div class="hc-usuario">{_icono("pacientes", 16)}{quien}</div>
    <a class="hc-salir" href="?logout=1" target="_self" title="Cerrar sesión"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H9"/></svg><span>Salir</span></a>
  </div>
</div>
<div class="hc-pie"><i></i>Base de datos conectada</div>
""", unsafe_allow_html=True)


def paginas_administracion(es_administrador):
    return PAGINAS_ADMINISTRACION if es_administrador else ["Mi cuenta"]


def pagina_actual(historia, es_administrador):
    """Página a mostrar: Pacientes, las secciones de la historia abierta o Administración."""
    opciones = (["Pacientes"] + (list(PAGINAS_HISTORIA) if historia else [])
                + paginas_administracion(es_administrador))
    if "ir_a" in st.session_state:
        st.session_state["pagina"] = st.session_state.pop("ir_a")
    if st.session_state.get("pagina") not in opciones:
        st.session_state["pagina"] = "Pacientes"
    return st.session_state["pagina"]


def _clave(texto):
    """'Evolución' -> 'evolucion' (clave de widget sin tildes ni espacios)."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


def menu_lateral(pagina, historia, menu_colapsado, es_administrador):
    """Menú lateral: completo, o franja de íconos por grupo con panel flotante."""
    with st.sidebar:
        with st.container(key="menu_toggle"):
            if st.button("", key="btn_menu_toggle",
                         icon=(":material/keyboard_double_arrow_right:" if menu_colapsado
                               else ":material/keyboard_double_arrow_left:"),
                         help="Expandir menú" if menu_colapsado else "Contraer menú"):
                st.session_state["menu_colapsado"] = not menu_colapsado
                st.rerun()

        def opciones_menu(clave_menu, opciones):
            with st.container(key=clave_menu):
                for opcion in opciones:
                    if st.button(opcion, icon=ICONOS[opcion], key=f"menu_{_clave(opcion)}",
                                 type="primary" if pagina == opcion else "secondary", width="stretch"):
                        st.session_state["pagina"] = opcion
                        st.rerun()

        grupos = [("pacientes", "Pacientes", ICONOS["Pacientes"], "hc_menu_pacientes", ["Pacientes"])]
        if historia:
            grupos.append(("historia", "Historia clínica", ICONOS["Historia clínica"], "hc_menu_historia",
                           list(PAGINAS_HISTORIA)))
        grupos.append(("admin", "Administración", ICONOS["Administración"], "hc_menu_admin",
                       paginas_administracion(es_administrador)))
        for clave, titulo, icono, clave_menu, opciones in grupos:
            if menu_colapsado:
                with st.popover("", icon=icono, help=titulo, key=f"grupo_{clave}",
                                type="primary" if pagina in opciones else "secondary"):
                    st.markdown(f'<div class="hc-panel-titulo">{titulo}</div>', unsafe_allow_html=True)
                    opciones_menu(clave_menu, opciones)
            else:
                st.markdown(f'<div class="hc-menu-seccion">{titulo}</div>', unsafe_allow_html=True)
                opciones_menu(clave_menu, opciones)


def main():
    # El botón de cerrar sesión de la barra superior es un enlace a ?logout=1.
    if st.query_params.get("logout"):
        from auth import cerrar_sesion

        cerrar_sesion()
        st.session_state.clear()
        st.query_params.clear()

    usuario = usuario_actual()
    if not usuario:
        pantalla_login()
        return

    # Si el usuario fue desactivado o eliminado, la sesión se cierra.
    sesion = None if os.environ.get("DEV_SIN_LOGIN") else datos_sesion(usuario)
    if not os.environ.get("DEV_SIN_LOGIN") and sesion is None:
        st.session_state.clear()
        st.rerun()
    es_administrador = os.environ.get("DEV_SIN_LOGIN") is not None or sesion["perfil"] == "Administrador"

    menu_colapsado = st.session_state.get("menu_colapsado", False)
    paciente, historia = paciente_e_historia()
    pagina = pagina_actual(historia, es_administrador)
    barra_superior(usuario, menu_colapsado, sesion, pagina, paciente, historia)
    menu_lateral(pagina, historia, menu_colapsado, es_administrador)
    # Vista previa del correo pendiente (por ejemplo, el de bienvenida) y resultado del envío.
    mostrar_envio_pendiente()
    if pagina in PAGINAS_ADMINISTRACION:
        if pagina == "Usuarios":
            mostrar_modulo_usuarios(usuario)
        else:
            mostrar_mi_cuenta(usuario)
        return
    # Al volver a Pacientes la tabla llega sin marca; no es que se haya quitado.
    if pagina != "Pacientes":
        st.session_state.pop("pacientes_habia_seleccion", None)

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
