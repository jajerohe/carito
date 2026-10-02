import streamlit as st

import repositorio as repo
import textos
from formulario import (
    CONSENTIMIENTO, SECCIONES_HISTORIA, SECCIONES_ORTODONCIA,
)
from utilidades import datos_clinica, nombre_completo
from vistas.campos import formulario_seccion

ESTADOS = ("ACTIVA", "FINALIZADA", "SUSPENDIDA")


def _pestanas_secciones(historia, secciones, usuario, notas=None):
    notas = notas or {}
    pestanas = st.tabs([s.titulo for s in secciones])
    for pestana, seccion in zip(pestanas, secciones):
        with pestana:
            valores = formulario_seccion(
                seccion, historia[seccion.clave], f"h{historia['id']}",
            )
            if seccion.clave in notas:
                st.caption(notas[seccion.clave])
            if valores is not None:
                repo.guardar_seccion(historia["id"], seccion.clave, valores, usuario)
                st.toast(f"{seccion.titulo}: guardado ✅")


def pagina_historia(historia, paciente, usuario):
    st.header("Historia clínica odontológica")

    with st.form(f"datos_historia_{historia['id']}"):
        c1, c2 = st.columns(2)
        fecha = c1.date_input("Fecha de apertura", value=historia["fecha_apertura"],
                              format="DD/MM/YYYY")
        estado = c2.selectbox("Estado", ESTADOS, index=ESTADOS.index(historia["estado"]))
        motivo = st.text_area("2. Motivo de la consulta", historia["motivo_consulta"] or "")
        if st.form_submit_button("Guardar datos generales", type="primary"):
            repo.actualizar_datos_historia(historia["id"], fecha, estado,
                                           motivo.strip(), usuario)
            st.toast("Datos generales guardados ✅")
            st.rerun()

    _pestanas_secciones(
        historia, SECCIONES_HISTORIA, usuario,
        notas={"anamnesis": textos.CERTIFICACION_ANAMNESIS
               + " (Se firma en el documento impreso.)"},
    )


def pagina_ortodoncia(historia, paciente, usuario):
    st.header("Anexo de ortodoncia")
    _pestanas_secciones(historia, SECCIONES_ORTODONCIA, usuario)


def pagina_consentimiento(historia, paciente, usuario):
    st.header("Consentimiento informado de ortodoncia")

    valores = dict(historia["consentimiento"] or {})
    # Valores sugeridos la primera vez
    valores.setdefault("firmante_nombre", nombre_completo(paciente))
    valores.setdefault("firmante_documento", paciente["documento"])
    if not valores.get("objetivos_generales"):
        diag = historia["diagnostico"] or {}
        objetivos = [diag.get(f"{a}_objetivos") for a in
                     ("facial", "esqueletico", "dental", "funcional")]
        valores["objetivos_generales"] = "\n".join(o for o in objetivos if o)

    nuevos = formulario_seccion(CONSENTIMIENTO, valores, f"h{historia['id']}")
    if nuevos is not None:
        repo.guardar_seccion(historia["id"], "consentimiento", nuevos, usuario)
        st.toast("Consentimiento guardado ✅")
        st.rerun()

    with st.expander("Ver texto completo del consentimiento", expanded=False):
        st.markdown(textos.texto_consentimiento(valores, datos_clinica()))
