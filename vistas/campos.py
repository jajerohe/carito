"""Dibuja en Streamlit las secciones definidas en formulario.py."""

import re

import streamlit as st

from formulario import NORMAL_ANORMAL, SI_NO
from utilidades import a_fecha


def _indice(opciones, valor):
    return opciones.index(valor) if valor in opciones else None


def _radio(etiqueta, opciones, valor, clave):
    return st.radio(
        etiqueta, opciones, index=_indice(opciones, valor),
        horizontal=True, key=clave,
    )


def _campo(campo, valores, clave):
    """Dibuja un campo y devuelve {clave: valor} con lo ingresado."""
    v = valores.get(campo.clave)
    t = campo.tipo

    if t in ("sino", "opcion"):
        opciones = SI_NO if t == "sino" else campo.opciones
        return {campo.clave: _radio(campo.etiqueta, opciones, v, clave)}

    if t in ("sino_obs", "normal_obs"):
        opciones = SI_NO if t == "sino_obs" else NORMAL_ANORMAL
        izq, der = st.columns([1, 2])
        with izq:
            valor = _radio(campo.etiqueta, opciones, v, clave)
        with der:
            obs = st.text_input(
                "Observaciones", valores.get(campo.clave + "_obs", ""),
                key=clave + "_obs",
            )
        return {campo.clave: valor, campo.clave + "_obs": obs}

    if t == "multi":
        defecto = [x for x in (v or []) if x in campo.opciones]
        return {campo.clave: st.multiselect(
            campo.etiqueta, campo.opciones, default=defecto, key=clave,
            placeholder="Seleccione…",
        )}

    if t == "area":
        return {campo.clave: st.text_area(campo.etiqueta, v or "", key=clave)}

    if t == "numero":
        etiqueta = f"{campo.etiqueta} ({campo.unidad})" if campo.unidad else campo.etiqueta
        return {campo.clave: st.number_input(
            etiqueta, value=float(v) if v not in (None, "") else None,
            step=0.5, format="%.1f", key=clave,
        )}

    if t == "dinero":
        return {campo.clave: st.number_input(
            f"{campo.etiqueta} ($)", min_value=0,
            value=int(v) if v not in (None, "") else None,
            step=10000, key=clave,
        )}

    if t == "fecha":
        fecha = st.date_input(
            campo.etiqueta, value=a_fecha(v), format="DD/MM/YYYY", key=clave,
        )
        return {campo.clave: fecha.isoformat() if fecha else None}

    return {campo.clave: st.text_input(campo.etiqueta, v or "", key=clave)}


def formulario_seccion(seccion, valores, prefijo):
    """
    Dibuja una sección completa dentro de un st.form.
    Devuelve el diccionario de valores si se presionó Guardar, si no None.
    """
    valores = valores or {}
    resultado = {}

    with st.form(f"{prefijo}:{seccion.clave}"):
        for grupo in seccion.grupos:
            if len(seccion.grupos) > 1 or grupo.titulo != seccion.titulo:
                st.markdown(f"**{grupo.titulo}**")
            campos = list(grupo.campos)
            for inicio in range(0, len(campos), grupo.columnas):
                columnas = st.columns(grupo.columnas)
                for columna, campo in zip(columnas, campos[inicio:inicio + grupo.columnas]):
                    with columna:
                        resultado.update(_campo(
                            campo, valores,
                            f"{prefijo}:{seccion.clave}:{campo.clave}",
                        ))
            st.divider()

        nombre = re.sub(r"^\d+\.\s*", "", seccion.titulo).lower()
        guardar = st.form_submit_button(f"Guardar {nombre}", type="primary")

    return resultado if guardar else None
