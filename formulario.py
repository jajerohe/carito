"""
Estructura del formato de historia clínica de ortodoncia.

Todas las secciones del documento se describen aquí como datos.
La interfaz (vistas/historia.py) y el PDF (pdf.py) se generan a
partir de estas definiciones, así que para agregar o cambiar una
pregunta basta con editar este archivo.

Tipos de campo:
    sino        Sí / No
    sino_obs    Sí / No + observaciones
    normal_obs  Normal / Anormal + observaciones
    opcion      una opción de una lista
    multi       varias opciones de una lista
    texto       texto corto
    area        texto largo
    numero      número (con unidad opcional)
    dinero      valor en pesos
    fecha       fecha
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Campo:
    clave: str
    etiqueta: str
    tipo: str = "texto"
    opciones: tuple = ()
    unidad: str = ""


@dataclass(frozen=True)
class Grupo:
    titulo: str
    campos: tuple
    columnas: int = 1


@dataclass(frozen=True)
class Seccion:
    clave: str          # columna JSONB en la tabla historias
    titulo: str
    grupos: tuple = field(default_factory=tuple)


SI_NO = ("Sí", "No")
NORMAL_ANORMAL = ("Normal", "Anormal")
CLASES = ("Clase I", "Clase II", "Clase III")


def _sino(*nombres):
    return tuple(Campo(_clave(n), n, "sino") for n in nombres)


def _clave(texto):
    import unicodedata

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = "".join(c if c.isalnum() else "_" for c in texto.lower())
    while "__" in texto:
        texto = texto.replace("__", "_")
    return texto.strip("_")


# ============================================================
# 3. ANAMNESIS
# ============================================================
ANAMNESIS = Seccion("anamnesis", "3. Anamnesis", (
    Grupo("Historia médica familiar", _sino(
        "Diabetes", "Cáncer", "Enf. cardiovascular", "Enf. hematológica",
        "Artritis", "Tuberculosis", "Alergias", "Enf. dermatológicas",
        "Anomalías congénitas", "Enf. mentales",
    ) + (Campo("familiar_otros", "Otros"),), columnas=3),

    Grupo("Historia médica personal", tuple(
        Campo("personal_" + c.clave, c.etiqueta, "sino") for c in _sino(
            "Traumas", "Cirugías", "Cardiopatías", "Hipertensión",
            "Cáncer", "Enfermedades hepáticas", "Alergias",
            "Enf. músculo-esqueléticas", "Enf. dermatológicas",
            "Enf. gastrointestinales", "Enf. transmisión sexual",
            "Convulsiones", "Enf. renales", "Enf. respiratorias",
            "Enf. hematológicas", "Enf. neurológicas", "Enf. endocrinas",
            "VIH/SIDA",
        )
    ) + (Campo("personal_otros", "Otros"),), columnas=3),

    Grupo("Estado médico actual", (
        Campo("medicamentos", "Medicamentos actuales", "area"),
        Campo("bajo_cuidado_medico", "¿Está bajo cuidado médico?", "sino"),
        Campo("medico_tratante", "Médico tratante"),
        Campo("interconsulta", "Interconsulta médica"),
        Campo("embarazo", "Embarazo"),
    )),

    Grupo("Historia odontológica personal", tuple(
        Campo("odonto_" + c.clave, c.etiqueta, "sino") for c in _sino(
            "Hemorragias", "Dolores", "Traumas", "Fracturas", "Infecciones",
            "Bloqueo articular", "Trismus", "Herpes labial", "Aftas (placas)",
        )
    ) + (Campo("odonto_otros", "Otros"),), columnas=3),
))

# ============================================================
# 4. EXAMEN ESTOMATOLÓGICO
# ============================================================
EXAMEN_INTRAORAL = Seccion("examen_intraoral", "4. Examen estomatológico", (
    Grupo("Examen intraoral", tuple(
        Campo(_clave(n), n, "normal_obs") for n in (
            "Labios", "Mucosas", "Piso de boca", "Lengua", "Paladares", "Dientes",
        )
    )),
))

# ============================================================
# 5. ESTADO PERIODONTAL
# ============================================================
PERIODONTAL = Seccion("periodontal", "5. Estado periodontal", (
    Grupo("Estado periodontal", tuple(
        Campo(_clave(n), n, "sino_obs") for n in (
            "Placa", "Cálculos", "Gingivitis", "Recesiones",
            "Lesión de furca", "Movilidad",
        )
    ) + (Campo("remision_periodoncia", "Remisión a periodoncia", "sino"),)),
))

# ============================================================
# ANEXO DE ORTODONCIA
# ============================================================
ANALISIS_FACIAL = Seccion("analisis_facial", "Análisis facial", (
    Grupo("Análisis facial", (
        Campo("tipo_facial", "Tipo facial", "opcion",
              ("Mesoprosopo", "Leptoprosopo", "Euriprosopo")),
        Campo("asimetria", "Asimetría", "opcion",
              ("Levognatismo", "Dextrognatismo", "No evidente clínicamente")),
        Campo("angulo_nasolabial", "Ángulo nasolabial", "opcion",
              ("Normal", "Aumentado", "Disminuido")),
        Campo("sellado_labial", "Sellado labial", "opcion",
              ("Normal", "Forzado", "Redundancia")),
        Campo("posicion_labial", "Posición labial", "opcion",
              ("Normal", "Retroquelia", "Proquelia")),
        Campo("perfil", "Perfil", "opcion", ("Recto", "Convexo", "Cóncavo")),
        Campo("tercios_faciales", "Tercios faciales", "opcion",
              ("Inferior aumentado", "Inferior disminuido", "Proporcionales")),
        Campo("sonrisa", "Sonrisa", "opcion", ("Normal", "Baja", "Gingival")),
        Campo("menton", "Mentón", "opcion", ("Normal", "Prominente", "Deficiente")),
        Campo("surco_mentolabial", "Surco mentolabial", "opcion",
              ("Normal", "Aumentado", "Disminuido")),
    ), columnas=2),
))

CEFALOMETRICO = Seccion("cefalometrico", "Análisis cefalométrico", (
    Grupo("Análisis cefalométrico (esquelético y dental)", (
        Campo("clase_esqueletica", "Clase esquelética", "opcion", CLASES),
        Campo("clase_esqueletica_por", "Clase esquelética por"),
        Campo("crecimiento", "Crecimiento", "opcion",
              ("Normodivergente", "Hiperdivergente", "Hipodivergente")),
        Campo("incisivos_superiores", "Incisivos superiores", "opcion",
              ("En la norma", "Proinclinados", "Retroinclinados")),
        Campo("incisivos_inferiores", "Incisivos inferiores", "opcion",
              ("En la norma", "Proinclinados", "Retroinclinados")),
    ), columnas=2),
    Grupo("Hallazgos radiográficos", (
        Campo("hallazgos_radiograficos",
              "Hallazgos radiográficos de relevancia clínica", "area"),
    )),
))

LADOS = ("Derecha", "Izquierda")

OCLUSION = Seccion("oclusion", "Análisis de oclusión", (
    Grupo("Arcos", (
        Campo("arco_superior", "Forma de arco superior", "opcion",
              ("Ovoide", "Cuadrado", "Triangular")),
        Campo("arco_inferior", "Forma de arco inferior", "opcion",
              ("Ovoide", "Cuadrado", "Triangular")),
        Campo("apinamiento_superior", "Apiñamiento superior", "numero", unidad="mm"),
        Campo("apinamiento_inferior", "Apiñamiento inferior", "numero", unidad="mm"),
        Campo("espaciamiento_superior", "Espaciamiento superior", "numero", unidad="mm"),
        Campo("espaciamiento_inferior", "Espaciamiento inferior", "numero", unidad="mm"),
        Campo("curva_spee", "Curva de Spee", "opcion",
              ("Normal", "Acentuada", "Disminuida")),
        Campo("plano_oclusal", "Plano oclusal", "opcion", ("Normal", "Canteado")),
    ), columnas=2),
    Grupo("Relaciones", (
        Campo("molar_derecha", "Relación molar derecha", "opcion", CLASES),
        Campo("molar_izquierda", "Relación molar izquierda", "opcion", CLASES),
        Campo("canina_derecha", "Relación canina derecha", "opcion", CLASES),
        Campo("canina_izquierda", "Relación canina izquierda", "opcion", CLASES),
        Campo("overjet", "Overjet", "numero", unidad="mm"),
        Campo("overbite", "Overbite", "numero", unidad="%"),
        Campo("linea_media", "Línea media", "opcion", ("Normal", "Desviada")),
        Campo("linea_media_detalle", "Desviación (superior / inferior)"),
        Campo("relacion_transversal", "Relación transversal", "opcion",
              ("Normal", "Cruzada", "Tijera")),
        Campo("relacion_transversal_localizacion", "Localización"),
    ), columnas=2),
    Grupo("Movimientos de lateralidad", (
        Campo("desoclusion_canina", "Desoclusión canina", "multi", LADOS),
        Campo("funcion_grupo", "Función en grupo", "multi", LADOS),
        Campo("contactos_balanza", "Contactos en balanza", "multi", LADOS),
    ), columnas=3),
    Grupo("Malposiciones dentarias", (
        Campo("malposiciones", "Malposiciones", "multi", (
            "Inclinaciones", "Rotaciones", "Gresiones",
            "Intrusiones", "Extrusiones", "Impactados/retenidos",
        )),
        Campo("malposiciones_detalle", "Detalle de malposiciones", "area"),
    )),
))

FUNCIONAL = Seccion("funcional", "Análisis funcional", (
    Grupo("Análisis funcional", (
        Campo("habitos", "Hábitos", "multi", (
            "Onicofagia", "Bruxismo", "Succión labial",
            "Succión digital", "Respiración oral",
        )),
        Campo("posicion_lingual", "Posición lingual", "opcion", (
            "Normal", "Interposición lingual anterior",
            "Interposición lingual lateral",
        )),
        Campo("atm", "ATM", "multi", (
            "Click", "Limitación en apertura",
            "Desviación mandibular", "Deflexión mandibular",
        )),
        Campo("atm_dolor", "Dolor ATM"),
        Campo("observaciones", "Observaciones", "area"),
        Campo("impresion_diagnostica", "Impresión diagnóstica", "area"),
    )),
))

DIAGNOSTICO = Seccion("diagnostico", "Resumen diagnóstico y objetivos", tuple(
    Grupo(area, (
        Campo(_clave(area) + "_diagnostico", "Diagnóstico", "area"),
        Campo(_clave(area) + "_objetivos", "Objetivos de tratamiento", "area"),
    ), columnas=2)
    for area in ("Facial", "Esquelético", "Dental", "Funcional")
))

PLAN_TRATAMIENTO = Seccion("plan_tratamiento", "Plan de tratamiento", (
    Grupo("Plan de tratamiento", (
        Campo("tipo", "Tipo de tratamiento", "multi", (
            "Ortopedia maxilar", "Ortodoncia interceptiva",
            "Ortodoncia correctiva", "Ortodoncia preprotésica",
        )),
        Campo("exodoncias_indicadas", "Exodoncias indicadas"),
        Campo("reevaluar_exodoncias", "Reevaluar exodoncias", "sino"),
        Campo("aparatologia_fija", "Aparatología fija", "area"),
        Campo("aparatologia_auxiliar", "Aparatología auxiliar", "area"),
        Campo("retencion", "Retención", "area"),
        Campo("precauciones", "Precauciones", "multi", (
            "Compromiso sistémico", "Disfunción de la ATM",
            "Reabsorción radicular", "Pérdida ósea",
        )),
        Campo("tiempo_observaciones",
              "Tiempo aproximado y observaciones del tratamiento", "area"),
    )),
))

PRESUPUESTO = Seccion("presupuesto", "Presupuesto", (
    Grupo("Costo del tratamiento", (
        Campo("costo_total", "Costo total del tratamiento", "dinero"),
        Campo("fecha", "Fecha", "fecha"),
        Campo("valor_ortodoncia", "Ortodoncia", "dinero"),
        Campo("valor_ortopedia", "Ortopedia", "dinero"),
        Campo("cuota_inicial", "Cuota inicial", "dinero"),
        Campo("controles_proyectados", "Número de controles proyectados", "numero"),
        Campo("valor_control", "Valor por control", "dinero"),
        Campo("valor_aparatos_adicionales", "Valor aparatos adicionales", "dinero"),
        Campo("valor_reparaciones", "Valor de reparaciones", "dinero"),
        Campo("valor_retenedores", "Valor de retenedores", "dinero"),
        Campo("otros", "Otros"),
    ), columnas=2),
))

CONSENTIMIENTO = Seccion("consentimiento", "Consentimiento informado", (
    Grupo("Datos del consentimiento", (
        Campo("fecha", "Fecha de firma", "fecha"),
        Campo("hora", "Hora"),
        Campo("firmante_nombre", "Nombre de quien firma"),
        Campo("firmante_documento", "Documento de quien firma"),
        Campo("calidad", "En calidad de", "opcion",
              ("Paciente", "Representante legal")),
    ), columnas=2),
    Grupo("Contenido", (
        Campo("objetivos_generales", "Objetivos generales del tratamiento", "area"),
        Campo("otros_riesgos", "Otros riesgos asociados particularmente al caso", "area"),
        Campo("incluye_ortoquirurgico",
              "¿Se incluye el párrafo de rechazo del tratamiento orto-quirúrgico?",
              "sino"),
        Campo("observaciones", "Observaciones", "area"),
    )),
))

SECCIONES_HISTORIA = (ANAMNESIS, EXAMEN_INTRAORAL, PERIODONTAL)
SECCIONES_ORTODONCIA = (
    ANALISIS_FACIAL, CEFALOMETRICO, OCLUSION, FUNCIONAL,
    DIAGNOSTICO, PLAN_TRATAMIENTO,
)
TODAS_LAS_SECCIONES = (
    SECCIONES_HISTORIA + SECCIONES_ORTODONCIA + (PRESUPUESTO, CONSENTIMIENTO)
)

GENEROS = ("Femenino", "Masculino", "Otro")
TIPOS_DOCUMENTO = ("CC", "TI", "RC", "CE", "PA", "PPT")
CONCEPTOS_PAGO = (
    "Cuota inicial", "Control", "Aparatos adicionales",
    "Reparación", "Retenedores", "Otro",
)
MEDIOS_PAGO = ("Efectivo", "Transferencia", "Tarjeta", "Otro")
