"""
Prueba de punta a punta contra una base de datos Postgres de prueba.

    DATABASE_URL=postgresql://usuario@host:puerto/base pytest

La base debe tener aplicado sql/schema.sql. NO usar la base de producción:
la prueba crea y borra registros.
"""

import os
import sys
from datetime import date
from decimal import Decimal

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"), reason="Requiere DATABASE_URL"
)


@pytest.fixture
def paciente_id():
    import repositorio as repo
    from database import conexion

    pid = repo.guardar_paciente({
        "tipo_documento": "CC", "documento": "TEST-123",
        "apellidos": "PÉREZ GÓMEZ", "nombres": "ANA MARÍA",
        "fecha_nacimiento": date(2010, 5, 20), "genero": "Femenino",
        "celular": "3001234567",
    }, "prueba@local")
    yield pid
    with conexion() as conn:
        conn.execute("DELETE FROM historias WHERE paciente_id = %s", (pid,))
        conn.execute("DELETE FROM pacientes WHERE id = %s", (pid,))


def test_flujo_completo(paciente_id):
    import repositorio as repo
    from formulario import TODAS_LAS_SECCIONES
    from pdf import generar_pdf

    assert repo.buscar_pacientes("pérez")[0]["id"] == paciente_id
    assert repo.buscar_pacientes("TEST-123")[0]["id"] == paciente_id

    hid = repo.crear_historia(paciente_id, date(2026, 10, 1), "Dientes torcidos", "prueba@local")
    repo.guardar_seccion(hid, "anamnesis", {"diabetes": "No", "personal_alergias": "Sí",
                                            "medicamentos": "Ninguno"}, "prueba@local")
    repo.guardar_seccion(hid, "oclusion", {"overjet": 4.5, "molar_derecha": "Clase II",
                                           "malposiciones": ["Rotaciones"]}, "prueba@local")
    repo.guardar_seccion(hid, "presupuesto", {"costo_total": 5000000,
                                              "controles_proyectados": 24}, "prueba@local")
    repo.guardar_seccion(hid, "consentimiento", {"incluye_ortoquirurgico": "Sí",
                                                 "fecha": "2026-10-01"}, "prueba@local")
    with pytest.raises(ValueError):
        repo.guardar_seccion(hid, "pacientes; DROP TABLE x", {}, "prueba@local")

    repo.agregar_evolucion(hid, date(2026, 10, 1), "Instalación de brackets", True,
                           "Dra. Prueba", "prueba@local")
    repo.agregar_pago(hid, date(2026, 10, 1), 1500000, "Cuota inicial", "Efectivo", "",
                      "prueba@local")
    repo.agregar_pago(hid, date(2026, 10, 15), 200000, "Control", "Transferencia", "",
                      "prueba@local")

    historia = repo.obtener_historia(hid)
    assert historia["oclusion"]["malposiciones"] == ["Rotaciones"]

    cuenta = repo.estado_de_cuenta(historia)
    assert cuenta["pagado"] == Decimal("1700000")
    assert cuenta["saldo"] == Decimal("3300000")

    paciente = repo.obtener_paciente(paciente_id)
    contenido = generar_pdf(paciente, historia, repo.evoluciones(hid), cuenta)
    assert contenido.startswith(b"%PDF")
    assert len(TODAS_LAS_SECCIONES) == 11
