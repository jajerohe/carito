"""Acceso a datos: pacientes, historias, evoluciones y pagos."""

from decimal import Decimal

from psycopg.types.json import Jsonb

from database import conexion
from formulario import TODAS_LAS_SECCIONES

COLUMNAS_PACIENTE = (
    "tipo_documento", "documento", "apellidos", "nombres", "fecha_nacimiento",
    "genero", "telefono_fijo", "celular", "direccion", "correo",
    "acudiente", "documento_acudiente",
)
SECCIONES_JSON = {s.clave for s in TODAS_LAS_SECCIONES}


# ============================================================
# Pacientes
# ============================================================

def buscar_pacientes(texto="", limite=50):
    patron = f"%{texto.strip().lower()}%"
    with conexion() as conn:
        return conn.execute(
            """
            SELECT p.*,
                   (SELECT count(*) FROM historias h WHERE h.paciente_id = p.id)
                       AS historias
            FROM pacientes p
            WHERE lower(p.documento) LIKE %s
               OR lower(p.apellidos || ' ' || p.nombres) LIKE %s
               OR lower(p.nombres || ' ' || p.apellidos) LIKE %s
            ORDER BY p.apellidos, p.nombres
            LIMIT %s
            """,
            (patron, patron, patron, limite),
        ).fetchall()


def obtener_paciente(paciente_id):
    with conexion() as conn:
        return conn.execute(
            "SELECT * FROM pacientes WHERE id = %s", (paciente_id,)
        ).fetchone()


def guardar_paciente(datos, usuario, paciente_id=None):
    """Crea o actualiza un paciente y devuelve su id."""
    valores = [datos.get(c) for c in COLUMNAS_PACIENTE]
    with conexion() as conn:
        if paciente_id is None:
            columnas = ", ".join(COLUMNAS_PACIENTE)
            marcas = ", ".join(["%s"] * len(COLUMNAS_PACIENTE))
            fila = conn.execute(
                f"""
                INSERT INTO pacientes ({columnas}, creado_por, actualizado_por)
                VALUES ({marcas}, %s, %s)
                RETURNING id
                """,
                (*valores, usuario, usuario),
            ).fetchone()
            return fila["id"]

        asignaciones = ", ".join(f"{c} = %s" for c in COLUMNAS_PACIENTE)
        conn.execute(
            f"""
            UPDATE pacientes
            SET {asignaciones}, actualizado_en = now(), actualizado_por = %s
            WHERE id = %s
            """,
            (*valores, usuario, paciente_id),
        )
        return paciente_id


# ============================================================
# Historias clínicas
# ============================================================

def historias_de_paciente(paciente_id):
    with conexion() as conn:
        return conn.execute(
            """
            SELECT id, fecha_apertura, estado, motivo_consulta
            FROM historias
            WHERE paciente_id = %s
            ORDER BY fecha_apertura DESC, id DESC
            """,
            (paciente_id,),
        ).fetchall()


def obtener_historia(historia_id):
    with conexion() as conn:
        return conn.execute(
            "SELECT * FROM historias WHERE id = %s", (historia_id,)
        ).fetchone()


def crear_historia(paciente_id, fecha_apertura, motivo_consulta, usuario):
    with conexion() as conn:
        fila = conn.execute(
            """
            INSERT INTO historias
                (paciente_id, fecha_apertura, motivo_consulta,
                 creado_por, actualizado_por)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (paciente_id, fecha_apertura, motivo_consulta, usuario, usuario),
        ).fetchone()
        return fila["id"]


def actualizar_datos_historia(historia_id, fecha_apertura, estado,
                              motivo_consulta, usuario):
    with conexion() as conn:
        conn.execute(
            """
            UPDATE historias
            SET fecha_apertura = %s, estado = %s, motivo_consulta = %s,
                actualizado_en = now(), actualizado_por = %s
            WHERE id = %s
            """,
            (fecha_apertura, estado, motivo_consulta, usuario, historia_id),
        )


def guardar_seccion(historia_id, seccion, valores, usuario):
    """Guarda una sección JSONB del formato (anamnesis, oclusion, ...)."""
    if seccion not in SECCIONES_JSON:
        raise ValueError(f"Sección desconocida: {seccion}")
    with conexion() as conn:
        conn.execute(
            f"""
            UPDATE historias
            SET {seccion} = %s, actualizado_en = now(), actualizado_por = %s
            WHERE id = %s
            """,
            (Jsonb(valores), usuario, historia_id),
        )


# ============================================================
# Evolución del tratamiento
# ============================================================

def evoluciones(historia_id):
    with conexion() as conn:
        return conn.execute(
            """
            SELECT * FROM evoluciones
            WHERE historia_id = %s
            ORDER BY fecha, id
            """,
            (historia_id,),
        ).fetchall()


def agregar_evolucion(historia_id, fecha, procedimiento, es_control,
                      ortodoncista, usuario):
    with conexion() as conn:
        conn.execute(
            """
            INSERT INTO evoluciones
                (historia_id, fecha, procedimiento, es_control,
                 ortodoncista, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (historia_id, fecha, procedimiento, es_control, ortodoncista, usuario),
        )


def eliminar_evolucion(evolucion_id):
    with conexion() as conn:
        conn.execute("DELETE FROM evoluciones WHERE id = %s", (evolucion_id,))


# ============================================================
# Pagos
# ============================================================

def pagos(historia_id):
    with conexion() as conn:
        return conn.execute(
            """
            SELECT * FROM pagos
            WHERE historia_id = %s
            ORDER BY fecha, id
            """,
            (historia_id,),
        ).fetchall()


def agregar_pago(historia_id, fecha, valor, concepto, medio_pago,
                 observaciones, usuario):
    with conexion() as conn:
        conn.execute(
            """
            INSERT INTO pagos
                (historia_id, fecha, valor, concepto, medio_pago,
                 observaciones, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (historia_id, fecha, Decimal(str(valor)), concepto, medio_pago,
             observaciones, usuario),
        )


def eliminar_pago(pago_id):
    with conexion() as conn:
        conn.execute("DELETE FROM pagos WHERE id = %s", (pago_id,))


def estado_de_cuenta(historia):
    """Resumen financiero de una historia: costo, pagado y saldo."""
    presupuesto = historia.get("presupuesto") or {}
    costo = Decimal(str(presupuesto.get("costo_total") or 0))
    lista = pagos(historia["id"])
    pagado = sum((p["valor"] for p in lista), Decimal("0"))
    return {
        "costo_total": costo,
        "pagado": pagado,
        "saldo": costo - pagado,
        "pagos": lista,
    }
