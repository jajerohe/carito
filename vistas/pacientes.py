from datetime import date

import pandas as pd
import psycopg
import streamlit as st

import repositorio as repo
from formulario import GENEROS, TIPOS_DOCUMENTO
from utilidades import calcular_edad, formato_fecha, nombre_completo


def _formulario_paciente(paciente, clave):
    p = paciente or {}
    with st.form(clave):
        c1, c2, c3 = st.columns([1, 2, 2])
        tipo = c1.selectbox(
            "Tipo doc.", TIPOS_DOCUMENTO,
            index=TIPOS_DOCUMENTO.index(p["tipo_documento"])
            if p.get("tipo_documento") in TIPOS_DOCUMENTO else 0,
        )
        documento = c2.text_input("Documento de identidad *", p.get("documento", ""))
        nacimiento = c3.date_input(
            "Fecha de nacimiento", value=p.get("fecha_nacimiento"),
            min_value=date(1920, 1, 1), max_value=date.today(),
            format="DD/MM/YYYY",
        )

        c1, c2 = st.columns(2)
        apellidos = c1.text_input("Apellidos *", p.get("apellidos", ""))
        nombres = c2.text_input("Nombres *", p.get("nombres", ""))

        c1, c2, c3 = st.columns(3)
        genero = c1.selectbox(
            "Género", GENEROS,
            index=GENEROS.index(p["genero"]) if p.get("genero") in GENEROS else None,
            placeholder="Seleccione…",
        )
        telefono = c2.text_input("Teléfono fijo", p.get("telefono_fijo") or "")
        celular = c3.text_input("Celular", p.get("celular") or "")

        c1, c2 = st.columns(2)
        direccion = c1.text_input("Dirección de residencia", p.get("direccion") or "")
        correo = c2.text_input("Correo electrónico", p.get("correo") or "")

        c1, c2 = st.columns(2)
        acudiente = c1.text_input(
            "Acudiente / representante legal (menores de edad)",
            p.get("acudiente") or "",
        )
        doc_acudiente = c2.text_input(
            "Documento del acudiente", p.get("documento_acudiente") or "",
        )

        enviar = st.form_submit_button("Guardar paciente", type="primary")

    if not enviar:
        return None

    datos = {
        "tipo_documento": tipo,
        "documento": documento.strip(),
        "apellidos": apellidos.strip().upper(),
        "nombres": nombres.strip().upper(),
        "fecha_nacimiento": nacimiento,
        "genero": genero,
        "telefono_fijo": telefono.strip(),
        "celular": celular.strip(),
        "direccion": direccion.strip(),
        "correo": correo.strip(),
        "acudiente": acudiente.strip().upper(),
        "documento_acudiente": doc_acudiente.strip(),
    }
    faltantes = [n for n, k in (("documento", "documento"), ("apellidos", "apellidos"),
                                ("nombres", "nombres")) if not datos[k]]
    if faltantes:
        st.error("Complete los campos obligatorios: " + ", ".join(faltantes))
        return None
    return datos


def _guardar(datos, usuario, paciente_id=None):
    try:
        return repo.guardar_paciente(datos, usuario, paciente_id)
    except psycopg.errors.UniqueViolation:
        st.error(f"Ya existe un paciente con el documento {datos['documento']}.")
        return None


def pagina_pacientes(usuario):
    st.header("Pacientes")

    with st.expander("➕ Registrar paciente nuevo"):
        datos = _formulario_paciente(None, "nuevo_paciente")
        if datos:
            nuevo_id = _guardar(datos, usuario)
            if nuevo_id:
                st.session_state["paciente_id"] = nuevo_id
                st.session_state.pop("historia_id", None)
                st.success("Paciente registrado.")
                st.rerun()

    texto = st.text_input("Buscar por nombre, apellido o documento",
                          placeholder="Ej: PÉREZ o 1023456789")
    resultados = repo.buscar_pacientes(texto)

    if not resultados:
        st.info("No se encontraron pacientes.")
    else:
        tabla = pd.DataFrame([{
            "Documento": f"{r['tipo_documento']} {r['documento']}",
            "Apellidos": r["apellidos"],
            "Nombres": r["nombres"],
            "Edad": calcular_edad(r["fecha_nacimiento"]),
            "Celular": r["celular"],
            "Historias": r["historias"],
        } for r in resultados])
        evento = st.dataframe(
            tabla, hide_index=True, use_container_width=True,
            on_select="rerun", selection_mode="single-row",
        )
        filas = evento.selection.rows
        if filas:
            elegido = resultados[filas[0]]["id"]
            if st.session_state.get("paciente_id") != elegido:
                st.session_state["paciente_id"] = elegido
                st.session_state.pop("historia_id", None)
                st.rerun()

    paciente_id = st.session_state.get("paciente_id")
    if paciente_id:
        _detalle_paciente(paciente_id, usuario)


def _detalle_paciente(paciente_id, usuario):
    paciente = repo.obtener_paciente(paciente_id)
    if not paciente:
        st.session_state.pop("paciente_id", None)
        return

    st.subheader(nombre_completo(paciente))

    with st.expander("✏️ Editar datos del paciente"):
        datos = _formulario_paciente(paciente, f"editar_paciente_{paciente_id}")
        if datos and _guardar(datos, usuario, paciente_id):
            st.success("Datos actualizados.")
            st.rerun()

    st.markdown("**Historias clínicas**")
    historias = repo.historias_de_paciente(paciente_id)
    for h in historias:
        c1, c2, c3 = st.columns([2, 4, 1])
        c1.write(f"{formato_fecha(h['fecha_apertura'])} · {h['estado']}")
        c2.write(h["motivo_consulta"] or "")
        if c3.button("Abrir", key=f"abrir_{h['id']}"):
            st.session_state["historia_id"] = h["id"]
            st.session_state["ir_a"] = "Historia clínica"
            st.rerun()

    with st.form(f"nueva_historia_{paciente_id}"):
        st.markdown("**Abrir historia clínica nueva**")
        fecha = st.date_input("Fecha de apertura", value=date.today(),
                              format="DD/MM/YYYY")
        motivo = st.text_area("Motivo de la consulta")
        if st.form_submit_button("Crear historia", type="primary"):
            st.session_state["historia_id"] = repo.crear_historia(
                paciente_id, fecha, motivo.strip(), usuario,
            )
            st.session_state["ir_a"] = "Historia clínica"
            st.rerun()
