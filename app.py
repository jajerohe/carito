import base64
import html
import mimetypes
import os
import re
import unicodedata

import streamlit as st

import repositorio as repo
from database import ErrorConexion
from marca import DESCRIPCION_SISTEMA, NOMBRE_SISTEMA, TITULO_PESTANA, fijar_titulo_pestana
from pdf import PARTES, generar_pdf
from utilidades import FONDO_LOGIN, LOGO, calcular_edad, nombre_completo
from vistas.historia import pagina_consentimiento, pagina_historia, pagina_ortodoncia
from vistas.pacientes import pagina_pacientes
from vistas.seguimiento import pagina_evolucion, pagina_pagos

st.set_page_config(page_title=TITULO_PESTANA, page_icon="🦷",
                   layout="wide", initial_sidebar_state="expanded")
fijar_titulo_pestana()

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
}


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
.login-logo img { width: 230px; max-width: 70%; height: auto; }
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
                        respuesta = iniciar_sesion(email.strip(), password)
                        st.session_state["usuario"] = respuesta.user.email
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    st.markdown(
        f'<div class="login-pie"><b>{html.escape(NOMBRE_SISTEMA)}</b> · {html.escape(DESCRIPCION_SISTEMA)}<br>'
        'Powered by <b>JAJEROHE Systems</b></div>',
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


ALTO_BARRA = 56


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


def barra_superior(usuario, menu_colapsado):
    """Barra fija a todo el ancho y estilos de la ventana (menú lateral fijo
    debajo de la barra, contraíble a una franja de íconos)."""
    ancho = 64 if menu_colapsado else 240
    st.markdown(f"""
<style>
.hc-barra{{position:fixed;top:0;left:0;right:0;height:{ALTO_BARRA}px;z-index:1000003;display:flex;align-items:center;
  background:linear-gradient(90deg,#0B2A6F 0%,#1F4FB8 50%,#5B4FE0 100%);box-shadow:inset 0 -3px 0 #8E3FD1,0 2px 8px rgba(11,42,111,.2)}}
.hc-barra-logo{{width:240px;height:100%;flex:0 0 240px;background:#fff;display:flex;align-items:center;justify-content:center;
  border-bottom:3px solid #8E3FD1;box-sizing:border-box}}
.hc-barra-logo img{{height:38px;width:auto}}
.hc-barra-nombre{{color:#fff;font-size:16px;font-weight:800;letter-spacing:.2px;padding-left:22px;white-space:nowrap}}
.hc-barra-nombre span{{display:block;color:#cfdcfa;font-size:10px;font-weight:600;margin-top:1px}}
.hc-barra-acciones{{margin-left:auto;display:flex;align-items:center;gap:12px;padding-right:18px}}
.hc-usuario{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);color:#fff;border-radius:20px;
  padding:7px 12px;font-size:11px;font-weight:700}}
.hc-salir{{width:34px;height:34px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
  background:rgba(255,255,255,.14);text-decoration:none!important}}
.hc-salir:hover{{background:rgba(255,255,255,.26)}}
section[data-testid="stSidebar"],section[data-testid="stSidebar"][aria-expanded]{{position:fixed!important;top:{ALTO_BARRA}px!important;left:0!important;
  height:calc(100vh - {ALTO_BARRA}px)!important;width:{ancho}px!important;min-width:{ancho}px!important;max-width:{ancho}px!important;
  transform:none!important;visibility:visible!important;z-index:1000002!important;background:#F3F6FC!important;border-right:1px solid #DCE5F5!important;
  box-shadow:none!important}}
section[data-testid="stSidebar"]>div{{padding:.5rem .55rem 1rem!important}}
[data-testid="stSidebarHeader"],[data-testid="stSidebarCollapseButton"],[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarResizeHandle"]{{display:none!important}}
[data-testid="stSidebarUserContent"]{{padding:0!important}}
[data-testid="stSidebarUserContent"] div[data-testid="stElementContainer"]:has(style){{display:none}}
header[data-testid="stHeader"]{{display:none!important}}
[data-testid="stMain"]{{margin-left:{ancho}px!important;width:calc(100% - {ancho}px)!important;max-width:calc(100% - {ancho}px)!important}}
.block-container{{padding-top:{ALTO_BARRA + 18}px!important}}
.st-key-menu_toggle{{display:flex;justify-content:{'center' if menu_colapsado else 'flex-end'}}}
.st-key-menu_toggle div[data-testid="stButton"]>button{{width:34px!important;height:30px!important;min-height:30px!important;padding:0!important;
  border:1px solid #cdd8ee!important;border-radius:5px!important;background:#fff!important;color:#0B2A6F!important}}
/* Opciones del menú */
[class*="st-key-hc_menu"]{{gap:3px!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button{{justify-content:flex-start!important;min-height:38px!important;padding:9px!important;
  border:none!important;border-radius:7px!important;background:transparent!important;color:#2b3a5c!important;box-shadow:none!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button:hover{{background:#e6edfa!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button[kind="primary"]{{color:#fff!important;
  background:linear-gradient(90deg,#1F6FE0 0%,#5B4FE0 55%,#8E3FD1 100%)!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button>div{{justify-content:flex-start!important;width:100%!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button p{{font-size:13px!important;font-weight:600!important;text-align:left!important}}
[class*="st-key-hc_menu"] div[data-testid="stButton"]>button span[data-testid="stIconMaterial"]{{font-size:19px!important}}
.hc-menu-seccion{{color:#7A86A3;font-size:10px;font-weight:800;text-transform:uppercase;margin:16px 9px 6px;letter-spacing:.6px}}
.hc-paciente{{color:#5A6785;font-size:13px;margin:-4px 0 10px}}
/* Franja contraída: un ícono por grupo que abre su panel a la derecha */
[class*="st-key-grupo_"]{{display:flex;justify-content:center;margin-top:6px}}
[class*="st-key-grupo_"] [data-testid="stPopover"],[class*="st-key-grupo_"] [data-testid="stPopover"]>div{{width:44px!important}}
[class*="st-key-grupo_"] button{{width:44px!important;height:42px!important;min-height:42px!important;padding:0!important;
  border:none!important;border-radius:7px!important;background:transparent!important;color:#2b3a5c!important;box-shadow:none!important}}
[class*="st-key-grupo_"] button:hover{{background:#e6edfa!important}}
[class*="st-key-grupo_"] button[kind="primary"]{{background:linear-gradient(90deg,#1F6FE0,#5B4FE0)!important;color:#fff!important}}
[class*="st-key-grupo_"] button span[data-testid="stIconMaterial"]{{font-size:23px!important;margin:0!important}}
[class*="st-key-grupo_"] button div[aria-hidden="true"]{{display:none!important}}
[data-testid="stPopoverBody"]:has(.hc-panel-titulo){{margin-left:51px!important;margin-top:-46px!important;
  min-width:250px;border:1px solid #DCE5F5;box-shadow:4px 6px 18px rgba(11,42,111,.16)!important}}
.hc-panel-titulo{{color:#0B2A6F;font-size:14px;font-weight:800;padding:2px 2px 8px;margin-bottom:4px;border-bottom:1px solid #e3e9f5}}
@media(max-width:900px){{.hc-barra-nombre span,.hc-usuario{{display:none}}}}
@media(max-width:640px){{.hc-barra-logo{{width:130px;flex-basis:130px}}.hc-barra-logo img{{height:26px}}.hc-barra-nombre{{display:none}}}}
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

    logo = (f'<img src="{_imagen_en_base64(LOGO, os.path.getmtime(LOGO))}" alt="{html.escape(NOMBRE_SISTEMA)}">'
            if os.path.exists(LOGO) else f"<b>{html.escape(NOMBRE_SISTEMA)}</b>")
    st.markdown(f"""
<div class="hc-barra">
  <div class="hc-barra-logo">{logo}</div>
  <div class="hc-barra-nombre">{html.escape(NOMBRE_SISTEMA)}<span>Historia Clínica de Ortodoncia y Ortopedia Maxilar</span></div>
  <div class="hc-barra-acciones">
    <div class="hc-usuario">👤 {html.escape(usuario)}</div>
    <a class="hc-salir" href="?logout=1" target="_self" title="Cerrar sesión" aria-label="Cerrar sesión"><svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h3a1 1 0 0 1 1 1v3M18 16v3a1 1 0 0 1-1 1h-3"/><path d="M5 4.5 11 3a1 1 0 0 1 1.2 1v16a1 1 0 0 1-1.2 1L5 19.5z" fill="#fff"/><path d="M14.5 12H22M19 9l3 3-3 3"/></svg></a>
  </div>
</div>
""", unsafe_allow_html=True)


def pagina_actual(historia):
    """Página a mostrar: Pacientes o, con una historia abierta, sus secciones."""
    opciones = ["Pacientes"] + (list(PAGINAS_HISTORIA) if historia else [])
    if "ir_a" in st.session_state:
        st.session_state["pagina"] = st.session_state.pop("ir_a")
    if st.session_state.get("pagina") not in opciones:
        st.session_state["pagina"] = "Pacientes"
    return st.session_state["pagina"]


def _clave(texto):
    """'Evolución' -> 'evolucion' (clave de widget sin tildes ni espacios)."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


def menu_lateral(pagina, historia, menu_colapsado):
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
        for clave, titulo, icono, clave_menu, opciones in grupos:
            if menu_colapsado:
                with st.popover("", icon=icono, help=titulo, key=f"grupo_{clave}",
                                type="primary" if pagina in opciones else "secondary"):
                    st.markdown(f'<div class="hc-panel-titulo">{titulo}</div>', unsafe_allow_html=True)
                    opciones_menu(clave_menu, opciones)
            else:
                st.markdown(f'<div class="hc-menu-seccion">{titulo}</div>', unsafe_allow_html=True)
                opciones_menu(clave_menu, opciones)


def encabezado_paciente(paciente, historia):
    """Paciente e historia abiertos, arriba del contenido."""
    if not paciente:
        return
    texto = f"**{nombre_completo(paciente)}** · {paciente['tipo_documento']} {paciente['documento']}"
    edad = calcular_edad(paciente["fecha_nacimiento"])
    if edad is not None:
        texto += f" · {edad} años"
    if historia:
        texto += f" · Historia #{historia['id']} ({historia['estado'].lower()})"
    st.caption(texto)


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

    menu_colapsado = st.session_state.get("menu_colapsado", False)
    barra_superior(usuario, menu_colapsado)
    paciente, historia = paciente_e_historia()
    pagina = pagina_actual(historia)
    menu_lateral(pagina, historia, menu_colapsado)
    encabezado_paciente(paciente, historia)

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
