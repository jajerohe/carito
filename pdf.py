"""Generación del PDF de la historia clínica con reportlab."""

import io
import os
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
    TableStyle,
)

import textos
from formulario import (
    CONSENTIMIENTO, PRESUPUESTO, SECCIONES_HISTORIA, SECCIONES_ORTODONCIA,
)
from utilidades import (
    LOGO, a_fecha, calcular_edad, datos_clinica, formato_fecha, formato_pesos,
    nombre_completo,
)

COLOR = colors.HexColor("#1E3A8A")
GRIS = colors.HexColor("#E8EEFA")
ANCHO = LETTER[0] - 3 * cm

_base = getSampleStyleSheet()
E = {
    "titulo": ParagraphStyle("titulo", parent=_base["Title"], fontSize=14,
                             textColor=COLOR, spaceAfter=6),
    "h2": ParagraphStyle("h2", parent=_base["Heading2"], fontSize=11,
                         textColor=COLOR, spaceBefore=8, spaceAfter=4),
    "h3": ParagraphStyle("h3", parent=_base["Heading3"], fontSize=9.5,
                         spaceBefore=4, spaceAfter=2),
    "normal": ParagraphStyle("normal", parent=_base["Normal"], fontSize=8.5,
                             leading=11),
    "legal": ParagraphStyle("legal", parent=_base["Normal"], fontSize=8,
                            leading=10.5, alignment=TA_JUSTIFY, spaceAfter=4),
    "celda": ParagraphStyle("celda", parent=_base["Normal"], fontSize=8,
                            leading=10),
    "etiqueta": ParagraphStyle("etiqueta", parent=_base["Normal"], fontSize=8,
                               leading=10, fontName="Helvetica-Bold"),
    "firma": ParagraphStyle("firma", parent=_base["Normal"], fontSize=8,
                            leading=10, alignment=TA_CENTER),
}


def _p(texto, estilo="celda"):
    texto = escape(str(texto if texto not in (None, "") else "")).replace("\n", "<br/>")
    return Paragraph(texto, E[estilo])


def texto_valor(campo, valores):
    """Valor de un campo listo para imprimir."""
    v = valores.get(campo.clave)
    t = campo.tipo
    if t in ("sino_obs", "normal_obs"):
        obs = valores.get(campo.clave + "_obs")
        return " — ".join(x for x in (v, obs) if x)
    if t == "multi":
        return ", ".join(v or [])
    if v in (None, ""):
        return ""
    if t == "numero":
        numero = f"{float(v):g}"
        return f"{numero} {campo.unidad}".strip()
    if t == "dinero":
        return formato_pesos(v)
    if t == "fecha":
        return formato_fecha(v)
    return str(v)


def _tabla(filas, anchos, encabezado=False, alturas=None):
    tabla = Table(filas, colWidths=anchos, rowHeights=alturas,
                  repeatRows=1 if encabezado else 0)
    estilo = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    if encabezado:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), GRIS))
    tabla.setStyle(TableStyle(estilo))
    return tabla


def _tabla_grupo(grupo, valores):
    """Pares etiqueta/valor; dos pares por fila cuando el grupo lo permite."""
    pares = [(_p(c.etiqueta, "etiqueta"), _p(texto_valor(c, valores)))
             for c in grupo.campos]
    if grupo.columnas >= 2:
        filas = []
        for i in range(0, len(pares), 2):
            fila = list(pares[i]) + (list(pares[i + 1]) if i + 1 < len(pares)
                                     else [_p(""), _p("")])
            filas.append(fila)
        ancho = ANCHO / 2
        return _tabla(filas, [ancho * 0.45, ancho * 0.55] * 2)
    return _tabla([list(p) for p in pares], [ANCHO * 0.3, ANCHO * 0.7])


def _seccion(seccion, valores, mostrar_titulo=True):
    elementos = [Paragraph(escape(seccion.titulo.upper()), E["h2"])] if mostrar_titulo else []
    for grupo in seccion.grupos:
        bloque = []
        if grupo.titulo.lower() != seccion.titulo.lower().split(". ")[-1]:
            bloque.append(Paragraph(escape(grupo.titulo), E["h3"]))
        bloque.append(_tabla_grupo(grupo, valores or {}))
        elementos.append(KeepTogether(bloque))
    return elementos


def _firmas(izquierda, derecha):
    linea = "_" * 45
    return Table(
        [[_p(linea, "firma"), _p(linea if derecha else "", "firma")],
         [_p(izquierda, "firma"), _p(derecha, "firma")]],
        colWidths=[ANCHO / 2] * 2,
        style=[("TOPPADDING", (0, 0), (-1, 0), 28)],
    )


def _firmas_paciente_ortodoncista(paciente, clinica):
    return [
        _firmas(
            f"{nombre_completo(paciente)}\n{paciente['tipo_documento']} {paciente['documento']}",
            "Firma del paciente o representante\nC.C.:",
        ),
        _firmas(f"{clinica['ortodoncista']}\n{clinica['cargo']}", ""),
    ]


def _identificacion(paciente, historia):
    edad = calcular_edad(paciente["fecha_nacimiento"])
    filas = [
        ["Apellidos", paciente["apellidos"], "Nombres", paciente["nombres"]],
        ["Documento", f"{paciente['tipo_documento']} {paciente['documento']}",
         "Fecha de nacimiento", formato_fecha(paciente["fecha_nacimiento"])],
        ["Edad", f"{edad} años" if edad is not None else "", "Género", paciente["genero"]],
        ["Teléfono fijo", paciente["telefono_fijo"], "Celular", paciente["celular"]],
        ["Dirección", paciente["direccion"], "Correo", paciente["correo"]],
    ]
    if paciente.get("acudiente"):
        filas.append(["Acudiente", paciente["acudiente"],
                      "Doc. acudiente", paciente["documento_acudiente"]])
    filas = [[_p(a, "etiqueta"), _p(b), _p(c, "etiqueta"), _p(d)] for a, b, c, d in filas]
    return _tabla(filas, [ANCHO * 0.17, ANCHO * 0.33, ANCHO * 0.2, ANCHO * 0.3])


def _parte_historia(paciente, historia, clinica):
    el = [
        Paragraph("HISTORIA CLÍNICA ODONTOLÓGICA", E["titulo"]),
        _p(f"Fecha de apertura: {formato_fecha(historia['fecha_apertura'])}", "normal"),
        Paragraph("1. IDENTIFICACIÓN", E["h2"]),
        _identificacion(paciente, historia),
        Paragraph("2. MOTIVO DE LA CONSULTA", E["h2"]),
        _tabla([[_p(historia["motivo_consulta"])]], [ANCHO]),
    ]
    for seccion in SECCIONES_HISTORIA:
        el += _seccion(seccion, historia[seccion.clave])
        if seccion.clave == "anamnesis":
            el.append(KeepTogether([
                Spacer(1, 4), _p(textos.CERTIFICACION_ANAMNESIS, "legal"),
                _firmas("Firma del paciente o representante", "")]))

    el += [PageBreak(), Paragraph("ANEXO DE ORTODONCIA", E["titulo"]),
           _p(f"Paciente: {nombre_completo(paciente)} · Identificación: "
              f"{paciente['documento']} · Edad: {calcular_edad(paciente['fecha_nacimiento']) or ''}",
              "normal")]
    for seccion in SECCIONES_ORTODONCIA:
        el += _seccion(seccion, historia[seccion.clave])
    el += _seccion(PRESUPUESTO, historia["presupuesto"])
    el.append(KeepTogether([Spacer(1, 6), _p(textos.MANIFIESTO_PLAN, "legal"),
                            *_firmas_paciente_ortodoncista(paciente, clinica)]))
    return el


def _parte_consentimiento(paciente, historia, clinica):
    valores = historia["consentimiento"] or {}
    el = [Paragraph("CONSENTIMIENTO INFORMADO DE ORTODONCIA", E["titulo"])]
    for parrafo in textos.texto_consentimiento(valores, clinica).split("\n\n"):
        el.append(_p(parrafo, "legal"))
    firmante = valores.get("firmante_nombre") or nombre_completo(paciente)
    documento = valores.get("firmante_documento") or paciente["documento"]
    el.append(KeepTogether([
        _firmas(f"{firmante}\nIdentificación: {documento}",
                "Firma del paciente y/o representante legal\nC.C.:"),
        _firmas(f"{clinica['ortodoncista']}\n{clinica['cargo']}", ""),
    ]))
    return el


def _parte_evolucion(paciente, evoluciones, filas_en_blanco=12):
    el = [
        Paragraph("EVOLUCIÓN DEL TRATAMIENTO", E["titulo"]),
        _p(f"NOMBRE: {nombre_completo(paciente)}    IDENTIFICACIÓN: "
           f"{paciente['documento']}", "normal"),
        Spacer(1, 6),
    ]
    filas = [[_p(t, "etiqueta") for t in ("FECHA", "PROCEDIMIENTO", "PACIENTE", "ORTODONCISTA")]]
    filas += [[_p(formato_fecha(e["fecha"])), _p(e["procedimiento"]), "", _p(e["ortodoncista"])]
              for e in evoluciones]
    filas += [["", "", "", ""] for _ in range(filas_en_blanco)]
    alturas = [None] * (1 + len(evoluciones)) + [22] * filas_en_blanco
    el.append(_tabla(filas, [ANCHO * 0.13, ANCHO * 0.52, ANCHO * 0.17, ANCHO * 0.18],
                     encabezado=True, alturas=alturas))
    return el


def _parte_cuenta(paciente, historia, cuenta):
    el = [
        Paragraph("ESTADO DE CUENTA", E["titulo"]),
        _p(f"Paciente: {nombre_completo(paciente)} · {paciente['documento']}", "normal"),
        Spacer(1, 6),
        _tabla([[_p(a, "etiqueta"), _p(b)] for a, b in (
            ("Costo total del tratamiento", formato_pesos(cuenta["costo_total"])),
            ("Total pagado", formato_pesos(cuenta["pagado"])),
            ("Saldo pendiente", formato_pesos(cuenta["saldo"])),
        )], [ANCHO * 0.4, ANCHO * 0.6]),
        Spacer(1, 8),
    ]
    filas = [[_p(t, "etiqueta") for t in ("FECHA", "CONCEPTO", "MEDIO", "VALOR", "OBSERVACIONES")]]
    filas += [[_p(formato_fecha(p["fecha"])), _p(p["concepto"]), _p(p["medio_pago"]),
               _p(formato_pesos(p["valor"])), _p(p["observaciones"])]
              for p in cuenta["pagos"]]
    el.append(_tabla(filas, [ANCHO * 0.13, ANCHO * 0.2, ANCHO * 0.15, ANCHO * 0.17,
                             ANCHO * 0.35], encabezado=True))
    return el


def _pie(canvas, doc):
    canvas.saveState()
    if os.path.exists(LOGO):
        imagen = ImageReader(LOGO)
        ancho_px, alto_px = imagen.getSize()
        # Cabe en 1,6 cm de alto y como máximo 9 cm de ancho, sin deformarse.
        escala = min(1.6 * cm / alto_px, 9 * cm / ancho_px)
        ancho, alto = ancho_px * escala, alto_px * escala
        canvas.drawImage(imagen, (LETTER[0] - ancho) / 2, LETTER[1] - alto - 0.6 * cm,
                         width=ancho, height=alto, mask="auto")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(LETTER[0] - 1.5 * cm, 1 * cm, f"PÁGINA {doc.page}")
    canvas.restoreState()


PARTES = {
    "historia": "Historia clínica y anexo de ortodoncia",
    "consentimiento": "Consentimiento informado",
    "evolucion": "Evolución del tratamiento",
    "cuenta": "Estado de cuenta",
}


def generar_pdf(paciente, historia, evoluciones, cuenta, partes=tuple(PARTES)):
    clinica = datos_clinica()
    bloques = []
    for parte in partes:
        if parte == "historia":
            bloques.append(_parte_historia(paciente, historia, clinica))
        elif parte == "consentimiento":
            bloques.append(_parte_consentimiento(paciente, historia, clinica))
        elif parte == "evolucion":
            bloques.append(_parte_evolucion(paciente, evoluciones))
        elif parte == "cuenta":
            bloques.append(_parte_cuenta(paciente, historia, cuenta))

    historia_pdf = []
    for i, bloque in enumerate(bloques):
        if i:
            historia_pdf.append(PageBreak())
        historia_pdf += bloque

    salida = io.BytesIO()
    doc = SimpleDocTemplate(
        salida, pagesize=LETTER, leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=2.8 * cm, bottomMargin=1.6 * cm,
        title=f"Historia clínica - {nombre_completo(paciente)}",
        author=clinica["ortodoncista"],
    )
    doc.build(historia_pdf, onFirstPage=_pie, onLaterPages=_pie)
    return salida.getvalue()
