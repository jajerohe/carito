import os
from datetime import date

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
# Se usa logo.png si existe; si no, logo.jpg. Para cambiar el logo basta con
# subir un archivo con uno de esos nombres a la raíz del repositorio.
LOGO = next(
    (os.path.join(DIRECTORIO, n) for n in ("logo.png", "logo.jpg")
     if os.path.exists(os.path.join(DIRECTORIO, n))),
    os.path.join(DIRECTORIO, "logo.png"),
)

CLINICA_POR_DEFECTO = {
    "nombre": "Carolina Rodríguez H. - Ortodoncia & Ortopedia Maxilar",
    "ortodoncista": "Leidy Carolina Rodríguez Hernández",
    "cargo": "Ortodoncista",
}


def datos_clinica():
    """Datos del consultorio: sección [clinica] de secrets.toml o valores por defecto."""
    datos = dict(CLINICA_POR_DEFECTO)
    try:
        import streamlit as st

        datos.update(st.secrets.get("clinica", {}))
    except Exception:
        pass
    return datos


def a_fecha(valor):
    """Convierte str ISO / date / None en date o None."""
    if not valor:
        return None
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def calcular_edad(fecha_nacimiento, referencia=None):
    nacimiento = a_fecha(fecha_nacimiento)
    if not nacimiento:
        return None
    hoy = referencia or date.today()
    return hoy.year - nacimiento.year - (
        (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day)
    )


def formato_fecha(valor):
    fecha = a_fecha(valor)
    return fecha.strftime("%d/%m/%Y") if fecha else ""


def formato_pesos(valor):
    if valor in (None, ""):
        return ""
    return "$ " + f"{float(valor):,.0f}".replace(",", ".")


def nombre_completo(paciente):
    return f"{paciente['nombres']} {paciente['apellidos']}".strip()
