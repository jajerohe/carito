"""Textos legales del formato (copiados del documento original)."""

from utilidades import a_fecha, formato_fecha

CERTIFICACION_ANAMNESIS = (
    'Certifico que los datos anteriormente consignados en la historia '
    'clínica fueron suministrados por mí y que todos los espacios fueron '
    'diligenciados antes de mi firma.'
)

MANIFIESTO_PLAN = (
    'Manifiesto que se me ha explicado el diagnóstico, el plan de '
    'tratamiento ideal y las opciones alternativas del mismo, al igual que '
    'sus riesgos, limitaciones, ventajas, desventajas y eventuales '
    'variaciones, derivadas del cambio de las circunstancias con base en '
    'las cuales se estructuró el plan de tratamiento inicial. De igual '
    'forma, se me ha explicado el presupuesto como consta en este documento '
    'y se me ha permitido realizar las preguntas pertinentes y éstas han '
    'sido respondidas amplia y satisfactoriamente. He elegido y aceptado el '
    'plan de tratamiento descrito anteriormente. Conozco que si he iniciado '
    'mi tratamiento de ortodoncia previamente con otro especialista, los '
    'objetivos planteados inicialmente pueden haber sido modificados '
    'parcial o totalmente de acuerdo a la reevaluación de mi caso, los '
    'cuales decidí aceptar de manera libre y voluntaria. Me ha sido '
    'informado además que en este último caso, los riesgos aumentan en '
    'función del tiempo de mi tratamiento ortodóncico previo. Tengo '
    'claridad que mi plan de tratamiento puede requerir antes, durante o '
    'después, de interconsultas y manejo con otros especialistas y me '
    'comprometo a realizarlos de acuerdo a las indicaciones de mi '
    'ortodoncista. Declaro que todos los espacios en blanco en ésta y en '
    'las páginas anteriores han sido diligenciados antes de mi firma.'
)

INTRO_RIESGOS = (
    'Además, se me han indicado sus consecuencias, ventajas, riesgos y '
    'posibles complicaciones que pueden presentarse. Me han señalado como '
    'riesgos y/o cambios comunes y frecuentes, los siguientes:'
)

RIESGOS = (
    '1. Caries dental: Que se puede presentar por malos hábitos en la higiene oral, no seguir las recomendaciones dadas por el especialista tratante en el manejo de todos los elementos de higiene oral que deben ser utilizados durante el tratamiento, desde el inicio hasta la terminación.',
    '2. Gingivitis y enfermedad periodontal: La gingivitis es una inflamación de la encía en donde puede haber sangrado y aumento en el tamaño de la encía, que se produce por no realizar una adecuada higiene con los elementos que se recomiendan. Cuando el aumento en el tamaño de la encía se convierte en un proceso crónico, se deben recurrir a procedimientos quirúrgicos para su corrección. La enfermedad periodontal corresponde a una alteración en las estructuras de soporte dental, debe ser tratada por un periodoncista y en algunos casos puede causar la suspensión del tratamiento.',
    '3. Manchas en los dientes: Pueden estar asociadas a caries o a descalcificación de los dientes, que pueden presentarse por mala higiene oral. Es importante informar al profesional sobre cualquier anomalía que se presente durante el tratamiento.',
    '4. Reabsorción radicular: En algunos casos la longitud de las raíces de los dientes puede sufrir una remodelación sobre todo en el ápice radicular (punta de la raíz) que se considera un proceso producido por el movimiento dentario. En algunos casos puede convertirse en un proceso más severo y reducir notablemente el tamaño de la raíz de los dientes. Es indispensable no dejar de asistir a las citas programadas y realizarse exámenes radiográficos que solicite el especialista tratante.',
    '5. Pacientes con enfermedad periodontal: El tratamiento ortodóncico no está contraindicado en pacientes que hayan sufrido enfermedad periodontal, siempre y cuando estén controlados por el periodoncista y su enfermedad no esté activa. Estos pacientes deben ser valorados periódicamente y se le solicitarán ayudas diagnósticas como radiografías, para evaluar el progreso del tratamiento y controlar los tejidos de soporte de los dientes involucrados. En estos casos, el tratamiento podrá suspenderse si existe recomendación del periodoncista o en caso donde el ortodoncista tratante lo considere pertinente.',
    '6. Problemas de la articulación temporomandibular: Estos problemas pueden causar dolor de cabeza, de oído o de la misma articulación; o se pueden generar ruidos al abrir o cerrar la boca. En algunos casos, estos ruidos no desaparecen tras el tratamiento de ortodoncia e incluso, podrían acentuarse.',
    '7. Fractura de restauraciones: Es posible que un diente con restauraciones existentes (calzas- resinas, amalgamas – coronas, pilares de prótesis, etc.), o con antecedente de trauma (golpes), pueden tener afección del paquete vasculonervioso (pulpa, nervio). En algunas ocasiones, esto puede agravarse con los movimientos ortodóncicos y debe realizarse tratamiento de endodoncia (tratamiento de conductos). Además, esto puede manifestarse con un cambio de color en la corona del diente, por necrosis (muerte) pulpar.',
    '8. Dientes previamente traumatizados: Es posible que los dientes traumatizados tengan zonas de anquilosis que impidan el movimiento dental. En estos casos, esto se considera una limitante del tratamiento.',
    '9. Recidivas de posición: Durante el transcurso de la vida, la oclusión (mordida) y la posición de los dientes puede variar debido a factores como: cambios en el crecimiento, respirar por la boca, tocar instrumentos y otros hábitos orales nocivos, que pueden alterar los resultados finales del tratamiento. Por esta razón, los controles de retención son indispensables una vez retirada la aparatología. Sin embargo, estos factores no pueden ser controlados por el ortodoncista. Incluso pacientes que nunca han tenido ortodoncia presentan variaciones en la posición dental con el paso de los años. La necesidad de realizar un retratamiento de ortodoncia será determinada una vez se presenten dichos cambios y en este momento se establecerá el nuevo costo del tratamiento, dependiendo de cada caso.',
    '10. Daños en los tejidos blandos: Las encías, mejillas, labios y otros tejidos orales y periorales, pueden verse afectados por la aparatología. Estas alteraciones pueden presentarse en forma de irritación, laceración, molestias, etc. En caso de que esto se presente, debe comunicarlo de forma inmediata o acudir a consulta a manera de urgencia.',
    '11. Tratamiento multidisciplinario: En ocasiones se requiere de un equipo multidisciplinario para tratar algunas condiciones que surgen a lo largo del tratamiento o que se han diagnosticado desde el principio. Es fundamental la asistencia a interconsultas médicas o con otras especialidades para que el tratamiento sea satisfactorio. En caso de no asistir, la ortodoncista tratante no puede hacerse responsable si los resultados no son los deseados. En algunas ocasiones, el tratamiento de ortodoncia debe ser interrumpido hasta que el paciente asista a dichas interconsultas. En todos los casos, la contrarremisión del especialista deberá presentarse por escrito.',
    '12. Deglución o aspiración de brackets y tubos antes, durante y después de la consulta: Además, en el momento de la atención es posible que esto suceda con otros materiales u objetos necesarios para el control en el tratamiento de ortodoncia. También pueden presentarse injurias a los tejidos corporales con los instrumentos. Los aparatos removibles o fijos que se hayan descementado, también podrían ser deglutidos. En caso de que se presenten inconvenientes con la aparatología, se debe informar de inmediato para disminuir este riesgo.',
    '13. Sensibilidad dental: Es una sensación dolorosa en los dientes después de ingerir alimentos o bebidas calientes o frías. En ocasiones, el contacto directo con el aire, podría generarla.',
    '14. Lesiones en deportistas: Los pacientes que practican algún deporte que involucre el contacto, podrían presentar con más frecuencia lesiones a los tejidos, ocasionadas por la aparatología, al recibir golpes durante la práctica deportiva.',
    '15. Daños al esmalte dental: Durante el tratamiento de ortodoncia podrá ser necesario reposicionar los brackets y/o tubos. Esto requerirá del uso de fresas para retirar posibles restos de material adherido a la superficie dental. De igual manera puede suceder al retirar la aparatología al final del tratamiento. Esto podría generar algún tipo de lesión (infracción), lesión o desgastes en el esmalte dental. Así como la posible aparición de líneas de fisura o fracturas.',
    '16. Cambios anormales por el crecimiento: La cantidad de cambios en el crecimiento posteriores al tratamiento, no pueden ser previstos o predecibles por el ortodoncista. Estos cambios pueden afectar los resultados y estabilidad postratamiento.',
    '17. Demora en el tratamiento por poca colaboración: La inasistencia a los controles programados, así como la continua descementación (caída) de la aparatología, retrasa el tratamiento de ortodoncia. Es importante el compromiso y colaboración del paciente en estos aspectos, así como en el uso de aditamentos adicionales requeridos.',
    '18. Espacios remanentes: Por diversas circunstancias, podrían presentarse espacios cerrados de forma incompleta o reapertura de los mismos posterior al tratamiento de ortodoncia. En caso de que por diversas circunstancias haya imposibilidad de cerrar un espacio, pueden requerirse tratamientos restauradores complementarios que serán informados en el momento en que se requieran y NO están incluidos en el costo del tratamiento. Las formas atípicas o irregulares de los dientes puede imposibilitar el cierre completo e ideal de los espacios, en estos casos también puede ser necesario el tratamiento restaurador y/o estético.',
    '19. Tiempo de tratamiento: La respuesta de los tejidos que soportan el diente (hueso, ligamento periodontal) es individual y puede variar entre pacientes e incluso en algunos movimientos dentro del mismo paciente. Esto podría aumentar el tiempo estimado del tratamiento de manera impredecible.',
    '20. Existen además otros riesgos como: movilidad dental, trauma oclusal, recesión gingival, pérdida ósea, pérdida de la papila interdental y cambios en el perfil facial y en la posición de los labios, principalmente en tratamientos con extracciones dentales; los cuales me han sido explicados de forma suficiente y he entendido el concepto de cada uno.',
    '21. Cambios en el perfil facial: Cuando el tratamiento ortodóncico implica la necesidad de extracciones dentales, el cambio en la inclinación de los dientes, productos del cierre de estos espacios, puede generar a su vez cambios en la posición de los labios con la consecuente alteración del perfil labial y facial.',
    '22. DOLOR: El dolor al momento de la colocación de la aparatología y en los días posteriores a cada control, es frecuente. La intensidad varía según el umbral del dolor de cada paciente, es individual y no es predecible. Estas molestias deben ir disminuyendo a medida que pasan los días. Si por el contrario, el dolor aumenta progresivamente y no es soportable, se debe informar de inmediato. Los analgésicos conocidos como AINES (ibuprofeno, naproxeno, etc.) en su forma genérica o comercial, retrasan el movimiento dental ortodóncico.',
)

PARRAFO_ORTOQUIRURGICO = (
    'Entiendo la información respecto a que mi plan de tratamiento ideal '
    'incluye una fase de ortodoncia prequirúrgica, cirugía ortognática y '
    'ortodoncia posquirúrgica y hago constar que por voluntad propia, he '
    'decidido NO ACEPTAR el tratamiento orto-quirúrgico y que se me ha '
    'explicado amplia y suficientemente, que esto implica que el '
    'tratamiento que se va a realizar será una compensación ortodóncica, '
    'que no será ideal y que no se podrán lograr todos los resultados '
    'faciales, dentales y estéticos, puesto que no se realizarán '
    'modificaciones de posición o tamaño de las bases óseas. Entiendo '
    'además, que esto aumenta los riesgos en la condición periodontal.'
)

COMPROMISOS = (
    'Además, tengo claro que los daños en los aparatos ocasionados por el uso incorrecto de elementos auxiliares, incumplimiento de citas o ingesta de alimentos duros, pegajosos o crujientes, conllevan a mayor tiempo de tratamiento y los resultados posiblemente no serán los inicialmente programados. Acepto pagar los cargos adicionales por pérdida de brackets, tubos y demás aparatos requeridos para mi tratamiento. Sé que en ocasiones la ingesta continua de alimentos indebidos puede generar paulatinas alteraciones en el material con el cual se adhieren los brackets y que por tanto, en ocasiones estos pueden caerse incluso comiendo alimentos blandos o al realizar higiene oral.',
    'Se me ha indicado que debo tener una higiene oral perfecta que incluya el uso de cepillo dental, cepillo interproximal, seda dental y enhebradores. Entiendo además que el tratamiento requiere de total continuidad. Si se presenta un período de ausencia mayor a tres (3) controles sin justa causa, registradas en la historia clínica, el compromiso profesional del caso quedará suspendido. Si después de esto, se decide dar continuidad al tratamiento, se generarán cobros de controles adicionales. Otra forma de terminación anticipada del tratamiento es el NO PAGO DE LOS CONTROLES, que debe ser mensual.',
    'Me comprometo a los siguientes autocuidados: No ingerir productos pegajosos, tostados, duros o crujientes (Ejemplo: tostadas, manzanas, peras, zanahoria, maíz, chicles, melcochas, bocadillos, manimotos, hielo, maíz pira y todos aquellos similares en consistencia); no introducir objetos como lápices y lapiceros; cumplir las citas para llevar a cabo mi tratamiento; cumplir con las instrucciones de higiene oral y el uso adecuado de cepillos, seda dental, enjuagues, cepillo interproximal y enhebradores (me han explicado su forma de uso); cumplir con las remisiones de interconsulta médica y de otras especialidades odontológicas; colaborar con el uso de aparatología o aditamentos adicionales removibles, extraorales o elásticos, que requieran mi colaboración; pagar el costo de reparación o pérdida de aparatos usados en el tratamiento por descuido de los mismos y a cancelar de manera oportuna los valores acordados y derivados del mismo acuerdo, que constan en el PRESUPUESTO anexo en la historia clínica; cumplir con las ayudas diagnósticas solicitadas periódicamente por el especialista.',
    'Por medio de la presente, certifico que se me ha informado sobre la naturaleza, beneficios, posibles riesgos del tratamiento y así mismo se me han resuelto todas las dudas e interrogantes que he formulado, motivo por el cual decido dar este consentimiento y autorización para la realización del tratamiento, teniendo en cuenta los riesgos y reacciones idiopáticas (no se conoce su causa) o resultados desfavorables inmediatos o tardíos de imposible o difícil previsión. Acepto la advertencia en lo referente a que el tratamiento compromete una actividad de medios, pero no de resultados.',
    'Certifico que he leído y entendido el contenido de esta forma y estoy informado de los riesgos y limitaciones de la ortodoncia y estoy de acuerdo con el plan de tratamiento. Además entiendo la importancia del período de retención al final del tratamiento.',
)

DECLARACION_FINAL = (
    'Comprendo las implicaciones del presente consentimiento, me encuentro '
    'en capacidad de expresarlo y dejo constancia que los espacios en '
    'blanco de este documento han sido diligenciados antes de mi firma y en '
    'mi presencia.'
)

# Párrafo de apertura del consentimiento. Se completa con
# .format(fecha=..., hora=..., firmante=..., ortodoncista=..., objetivos=...)
APERTURA_CONSENTIMIENTO = (
    'Este consentimiento informado es firmado el día {fecha}; Hora: {hora}.'
)

AUTORIZACION = (
    'Yo, {firmante}, identificado como aparece al pie de mi firma, en calidad '
    'de {calidad}, autorizo a {ortodoncista} y al equipo odontológico que '
    'disponga, a realizar el plan de tratamiento que considere pertinente, el '
    'cual me ha sido informado y explicado de manera amplia y suficiente, '
    'resolviendo todas las preguntas que he hecho al respecto. Se describen '
    'como objetivos generales del tratamiento: {objetivos} (Nota: Los '
    'objetivos puntuales y particulares a mi caso se describen en el plan de '
    'tratamiento anexo, el cual me ha sido explicado y con el que he estado '
    'de acuerdo. He realizado preguntas y me han sido resueltas mis '
    'inquietudes satisfactoriamente).'
)


def texto_consentimiento(valores, clinica):
    """Texto del consentimiento en Markdown, con los datos ya completados."""
    fecha = formato_fecha(a_fecha(valores.get("fecha"))) or "(por diligenciar)"
    partes = [
        APERTURA_CONSENTIMIENTO.format(
            fecha=fecha, hora=valores.get("hora") or "(por diligenciar)"),
        AUTORIZACION.format(
            firmante=valores.get("firmante_nombre") or "(por diligenciar)",
            calidad=(valores.get("calidad") or "paciente y/o representante legal").lower(),
            ortodoncista=clinica["ortodoncista"],
            objetivos=valores.get("objetivos_generales") or "(por diligenciar)",
        ),
        INTRO_RIESGOS,
        *RIESGOS,
        "Otros riesgos asociados particularmente a mi caso: "
        + (valores.get("otros_riesgos") or "Ninguno."),
    ]
    if valores.get("incluye_ortoquirurgico") == "Sí":
        partes.append(PARRAFO_ORTOQUIRURGICO)
    partes += list(COMPROMISOS)
    partes.append("Observaciones: " + (valores.get("observaciones") or "Ninguna."))
    partes.append(DECLARACION_FINAL)
    return "\n\n".join(partes)
