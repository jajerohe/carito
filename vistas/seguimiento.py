from datetime import date

import pandas as pd
import streamlit as st

import repositorio as repo
from formulario import CONCEPTOS_PAGO, MEDIOS_PAGO, PRESUPUESTO
from utilidades import datos_clinica, formato_fecha, formato_pesos
from vistas.campos import formulario_seccion


def _eliminar(registros, etiqueta, funcion, clave):
    """Selector + confirmación para borrar un registro."""
    if not registros:
        return
    with st.popover(f"🗑️ Eliminar {etiqueta}"):
        elegido = st.selectbox(
            "Registro", registros, key=f"sel_{clave}",
            format_func=lambda r: f"{formato_fecha(r['fecha'])} · "
                                  f"{r.get('procedimiento') or r.get('concepto')}"
                                  + (f" · {formato_pesos(r['valor'])}" if 'valor' in r else ""),
        )
        if st.button("Confirmar eliminación", type="primary", key=f"btn_{clave}"):
            funcion(elegido["id"])
            st.rerun()


# ============================================================
# Evolución del tratamiento
# ============================================================

def pagina_evolucion(historia, paciente, usuario):
    st.header("Evolución del tratamiento")
    lista = repo.evoluciones(historia["id"])

    presupuesto = historia["presupuesto"] or {}
    proyectados = presupuesto.get("controles_proyectados")
    realizados = sum(1 for e in lista if e["es_control"])
    c1, c2 = st.columns(2)
    c1.metric("Controles realizados", realizados)
    c2.metric("Controles proyectados", int(proyectados) if proyectados else "—")

    with st.form(f"evolucion_{historia['id']}", clear_on_submit=True):
        c1, c2 = st.columns([1, 3])
        fecha = c1.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")
        es_control = c1.checkbox("Cuenta como control", value=True)
        procedimiento = c2.text_area("Procedimiento realizado")
        ortodoncista = st.text_input("Ortodoncista", datos_clinica()["ortodoncista"])
        if st.form_submit_button("Registrar evolución", type="primary"):
            if not procedimiento.strip():
                st.error("Describa el procedimiento.")
            else:
                repo.agregar_evolucion(historia["id"], fecha, procedimiento.strip(),
                                       es_control, ortodoncista.strip(), usuario)
                st.rerun()

    if lista:
        st.dataframe(pd.DataFrame([{
            "Fecha": formato_fecha(e["fecha"]),
            "Procedimiento": e["procedimiento"],
            "Control": "Sí" if e["es_control"] else "No",
            "Ortodoncista": e["ortodoncista"],
        } for e in lista]), hide_index=True, use_container_width=True)
        _eliminar(lista, "evolución", repo.eliminar_evolucion, f"evo_{historia['id']}")
    else:
        st.info("Aún no hay evoluciones registradas.")


# ============================================================
# Presupuesto y pagos
# ============================================================

def pagina_pagos(historia, paciente, usuario):
    st.header("Presupuesto y pagos")

    cuenta = repo.estado_de_cuenta(historia)
    c1, c2, c3 = st.columns(3)
    c1.metric("Costo total", formato_pesos(cuenta["costo_total"]))
    c2.metric("Pagado", formato_pesos(cuenta["pagado"]))
    c3.metric("Saldo pendiente", formato_pesos(cuenta["saldo"]))

    with st.expander("Presupuesto del tratamiento", expanded=not cuenta["costo_total"]):
        valores = formulario_seccion(PRESUPUESTO, historia["presupuesto"],
                                     f"h{historia['id']}")
        if valores is not None:
            repo.guardar_seccion(historia["id"], "presupuesto", valores, usuario)
            st.toast("Presupuesto guardado ✅")
            st.rerun()

    st.subheader("Registrar pago")
    with st.form(f"pago_{historia['id']}", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        fecha = c1.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")
        valor = c2.number_input("Valor ($)", min_value=0, step=10000)
        concepto = c3.selectbox("Concepto", CONCEPTOS_PAGO)
        medio = c4.selectbox("Medio de pago", MEDIOS_PAGO)
        observaciones = st.text_input("Observaciones")
        if st.form_submit_button("Registrar pago", type="primary"):
            if valor <= 0:
                st.error("El valor debe ser mayor que cero.")
            else:
                repo.agregar_pago(historia["id"], fecha, valor, concepto, medio,
                                  observaciones.strip(), usuario)
                st.rerun()

    if cuenta["pagos"]:
        st.dataframe(pd.DataFrame([{
            "Fecha": formato_fecha(p["fecha"]),
            "Concepto": p["concepto"],
            "Valor": formato_pesos(p["valor"]),
            "Medio": p["medio_pago"],
            "Observaciones": p["observaciones"],
        } for p in cuenta["pagos"]]), hide_index=True, use_container_width=True)
        _eliminar(cuenta["pagos"], "pago", repo.eliminar_pago, f"pago_{historia['id']}")
    else:
        st.info("Aún no hay pagos registrados.")
