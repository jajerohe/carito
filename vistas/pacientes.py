"""Página de pacientes con el mismo manejo de Usuarios (Podex y Ponycash):
búsqueda, fila seleccionada, botones circulares y ventanas para crear,
editar y eliminar. Debajo, las historias clínicas del paciente seleccionado."""

from datetime import date
from html import escape

import pandas as pd
import psycopg
import streamlit as st

import repositorio as repo
from formulario import GENEROS, TIPOS_DOCUMENTO
from usuarios import encabezado_ventana, ficha, seccion
from utilidades import calcular_edad, formato_fecha, nombre_completo


def _notificar(mensaje, tipo="success"):
    st.session_state["mensaje_pacientes"] = (tipo, mensaje)
    st.rerun()


def _seleccionar(paciente_id):
    if st.session_state.get("paciente_id") != paciente_id:
        st.session_state["paciente_id"] = paciente_id
        st.session_state.pop("historia_id", None)


def _ficha_paciente(p):
    ficha([("Documento", f"{p['tipo_documento']} {p['documento']}"), ("Paciente", nombre_completo(p)),
           ("Edad", calcular_edad(p["fecha_nacimiento"]))])


# ============================================================
# FORMULARIO
# ============================================================
def _formulario_paciente(paciente, clave, boton):
    """Formulario de datos del paciente. Devuelve los datos válidos al guardar."""
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

        with st.container(key=f"acciones_dlg_{clave}", horizontal=True, horizontal_alignment="right", gap="small"):
            enviar = st.form_submit_button(boton[2], icon=boton[0], key=boton[1])

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
        st.error("❌ Complete los campos obligatorios: " + ", ".join(faltantes) + ".")
        return None
    return datos


def _guardar(datos, usuario, paciente_id=None):
    try:
        return repo.guardar_paciente(datos, usuario, paciente_id)
    except psycopg.errors.UniqueViolation:
        st.error(f"❌ Ya existe un paciente con el documento {datos['documento']}.")
    except Exception as e:
        st.error(f"❌ No fue posible guardar el paciente: {e}")
    return None


# ============================================================
# VENTANAS
# ============================================================
@st.dialog(" ", width="large")
def ventana_crear_paciente(usuario):
    encabezado_ventana("Nuevo Paciente")
    datos = _formulario_paciente(None, "form_crear_paciente",
                                 (":material/person_add:", "btn_ok_crear_paciente", "Registrar paciente"))
    if datos:
        nuevo_id = _guardar(datos, usuario)
        if nuevo_id:
            _seleccionar(nuevo_id)
            _notificar(f"✅ Paciente {datos['apellidos']} {datos['nombres']} registrado correctamente.")


@st.dialog(" ", width="large")
def ventana_editar_paciente(paciente, usuario):
    encabezado_ventana("Editar Paciente")
    datos = _formulario_paciente(paciente, f"form_editar_paciente_{paciente['id']}",
                                 (":material/save:", "btn_info_editar_paciente", "Guardar cambios"))
    if datos and _guardar(datos, usuario, paciente["id"]):
        _notificar(f"✅ Paciente {datos['apellidos']} {datos['nombres']} actualizado correctamente.")


@st.dialog(" ", width="large")
def ventana_eliminar_paciente(paciente, historias):
    encabezado_ventana("Eliminar Paciente")
    _ficha_paciente(paciente)
    if historias:
        seccion("No es posible eliminar este paciente",
                f"Tiene {historias} historia(s) clínica(s) registrada(s). "
                "Las historias clínicas se conservan y no se pueden borrar desde aquí.")
        return

    seccion("¿Está seguro que desea eliminar este paciente?",
            "Se eliminan sus datos personales. Esta acción no se puede deshacer.")
    with st.form(f"form_eliminar_paciente_{paciente['id']}"):
        with st.container(key="acciones_dlg_eliminar_paciente", horizontal=True,
                          horizontal_alignment="right", gap="small"):
            cancelar = st.form_submit_button("Cancelar", icon=":material/close:", key="btn_cancel_eliminar_paciente",
                                             help="Cancelar")
            confirmar = st.form_submit_button("Eliminar", icon=":material/delete:", key="btn_danger_eliminar_paciente",
                                              help="Sí, eliminar")
    if cancelar:
        st.rerun()
    if not confirmar:
        return
    try:
        repo.eliminar_paciente(paciente["id"])
    except psycopg.errors.ForeignKeyViolation:
        st.error("❌ El paciente tiene historias clínicas; no es posible eliminarlo.")
        return
    except Exception as e:
        st.error(f"❌ No fue posible eliminar el paciente: {e}")
        return
    st.session_state.pop("paciente_id", None)
    st.session_state.pop("historia_id", None)
    _notificar(f"✅ Paciente {nombre_completo(paciente)} eliminado correctamente.")


@st.dialog(" ", width="large")
def ventana_nueva_historia(paciente, usuario):
    encabezado_ventana("Nueva Historia Clínica")
    _ficha_paciente(paciente)
    with st.form(f"form_nueva_historia_{paciente['id']}"):
        fecha = st.date_input("Fecha de apertura", value=date.today(), format="DD/MM/YYYY")
        motivo = st.text_area("Motivo de la consulta")
        with st.container(key="acciones_dlg_nueva_historia", horizontal=True,
                          horizontal_alignment="right", gap="small"):
            crear = st.form_submit_button("Crear historia", icon=":material/note_add:", key="btn_ok_nueva_historia",
                                          help="Crear historia clínica")
    if not crear:
        return
    try:
        historia_id = repo.crear_historia(paciente["id"], fecha, motivo.strip(), usuario)
    except Exception as e:
        st.error(f"❌ No fue posible crear la historia clínica: {e}")
        return
    st.session_state["historia_id"] = historia_id
    st.session_state["ir_a"] = "Historia clínica"
    st.rerun()


# ============================================================
# PÁGINA
# ============================================================
def pagina_pacientes(usuario):
    mensaje = st.session_state.pop("mensaje_pacientes", None)
    if mensaje:
        tipo, texto = mensaje
        (st.warning if tipo == "warning" else st.success)(texto)

    # Barra de búsqueda y acciones, como en el resto del sistema
    c_busca, c_acciones = st.columns([1, 1.3], vertical_alignment="center")
    with c_busca:
        texto = st.text_input("Buscar paciente", label_visibility="collapsed",
                              placeholder="🔎  Buscar paciente por nombre, apellido o documento…")
    try:
        resultados = repo.buscar_pacientes(texto)
    except Exception as e:
        st.error("❌ No fue posible consultar los pacientes.")
        st.exception(e)
        return

    # La fila elegida en la tabla manda; si no hay, se conserva el paciente
    # con el que se venía trabajando (por ejemplo, al volver de la historia).
    seleccion = st.session_state.get("tabla_pacientes")
    filas = seleccion.selection.rows if seleccion else []
    if filas and filas[0] < len(resultados):
        _seleccionar(resultados[filas[0]]["id"])
    elif st.session_state.get("pacientes_habia_seleccion"):
        # Se quitó la marca de la fila.
        st.session_state.pop("paciente_id", None)
        st.session_state.pop("historia_id", None)
    st.session_state["pacientes_habia_seleccion"] = bool(filas)

    paciente_id = st.session_state.get("paciente_id")
    fila = next((r for r in resultados if r["id"] == paciente_id), None)
    if fila is None and paciente_id:
        fila = repo.obtener_paciente(paciente_id)
        if fila is None:
            st.session_state.pop("paciente_id", None)
        else:
            fila = {**fila, "historias": len(repo.historias_de_paciente(paciente_id))}

    with c_acciones:
        with st.container(key="acciones_pacientes", horizontal=True, horizontal_alignment="right", gap="small"):
            if st.button("Nuevo paciente", icon=":material/person_add:", key="btn_ok_pac_nuevo", help="Nuevo paciente"):
                ventana_crear_paciente(usuario)
            if st.button("Editar", icon=":material/edit:", key="btn_info_pac_editar", disabled=fila is None,
                         help="Editar paciente"):
                ventana_editar_paciente(fila, usuario)
            if st.button("Nueva historia", icon=":material/note_add:", key="btn_neutral_pac_historia", disabled=fila is None,
                         help="Nueva historia clínica"):
                ventana_nueva_historia(fila, usuario)
            if st.button("Eliminar", icon=":material/delete:", key="btn_danger_pac_eliminar", disabled=fila is None,
                         help="Eliminar paciente"):
                ventana_eliminar_paciente(fila, fila["historias"])

    with st.container(border=True):
        _tabla_pacientes(resultados, fila)

    if fila is not None:
        with st.container(border=True):
            _historias_del_paciente(fila, usuario)


def _titulo_tarjeta(titulo, detalle=None):
    """Título de la tarjeta a la izquierda y, a la derecha, lo seleccionado."""
    st.markdown(
        f'<div class="hc-card-cabeza"><div class="hc-card-titulo">{titulo}</div>'
        + (f'<div class="hc-card-detalle">{detalle}</div>' if detalle else "") + "</div>",
        unsafe_allow_html=True,
    )


def _tabla_pacientes(resultados, fila):
    _titulo_tarjeta(
        "Pacientes registrados",
        f"<b>Seleccionado:</b> {escape(fila['tipo_documento'])} {escape(fila['documento'])} · "
        f"{escape(nombre_completo(fila))}" if fila is not None else "☝️ Seleccione un paciente en la tabla",
    )
    if not resultados:
        st.info("ℹ️ No existen pacientes que coincidan con el criterio de búsqueda.")
    else:
        tabla = pd.DataFrame([{
            "DOCUMENTO": f"{r['tipo_documento']} {r['documento']}",
            "APELLIDOS": r["apellidos"],
            "NOMBRES": r["nombres"],
            "EDAD": calcular_edad(r["fecha_nacimiento"]),
            "CELULAR": r["celular"] or "—",
            "HISTORIAS": r["historias"],
        } for r in resultados])
        tabla["EDAD"] = tabla["EDAD"].map(lambda e: "—" if pd.isna(e) else str(int(e)))
        st.dataframe(
            tabla, key="tabla_pacientes", on_select="rerun", selection_mode="single-row",
            hide_index=True, width="stretch", height=min(38 + 35 * len(tabla), 640),
        )


def _historias_del_paciente(paciente, usuario):
    historias = repo.historias_de_paciente(paciente["id"])
    if not historias:
        _titulo_tarjeta(f"Historias clínicas de {escape(nombre_completo(paciente))}")
        st.caption("Este paciente aún no tiene historias clínicas. Use el botón Nueva historia.")
        return

    seleccion = st.session_state.get(f"tabla_historias_{paciente['id']}")
    filas = seleccion.selection.rows if seleccion else []
    historia = historias[filas[0]] if filas and filas[0] < len(historias) else None

    c_titulo, c_acciones = st.columns([3, 1], vertical_alignment="center")
    with c_titulo:
        _titulo_tarjeta(
            f"Historias clínicas de {escape(nombre_completo(paciente))}",
            f"<b>Seleccionada:</b> {formato_fecha(historia['fecha_apertura'])} · {escape(historia['estado'])}"
            if historia is not None else "☝️ Seleccione una historia para abrirla",
        )
    with c_acciones:
        with st.container(key="acciones_historias", horizontal=True, horizontal_alignment="right", gap="small"):
            if st.button("Abrir historia", icon=":material/folder_open:", key="btn_ok_hist_abrir",
                         disabled=historia is None):
                st.session_state["historia_id"] = historia["id"]
                st.session_state["ir_a"] = "Historia clínica"
                st.rerun()

    tabla = pd.DataFrame([{
        "APERTURA": formato_fecha(h["fecha_apertura"]),
        "ESTADO": h["estado"],
        "MOTIVO DE CONSULTA": h["motivo_consulta"] or "—",
    } for h in historias])
    st.dataframe(
        tabla, key=f"tabla_historias_{paciente['id']}", on_select="rerun", selection_mode="single-row",
        hide_index=True, width="stretch", height=min(38 + 35 * len(tabla), 400),
    )
