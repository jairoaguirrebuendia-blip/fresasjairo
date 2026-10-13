"""Catálogo base: grupos musculares, equipamiento y ejercicios con su técnica.

Los bloques, la dificultad (1-5 💪), los músculos y las cadenas de progresión
siguen la estructura de la "Guía Completa de Calistenia y Street Workout".
Los ejercicios con pesas se apoyan en Peña Fernández et al. ("Levantamiento
de pesas") y en los principios de Schoenfeld y Martínez. Los textos de técnica
están redactados para la app (no son copia literal de los libros).
"""

MUSCLE_GROUPS = [
    ("mg_pecho", "Pectoral", "mg_torso"),
    ("mg_espalda", "Espalda (dorsal)", "mg_torso"),
    ("mg_hombros", "Hombros", "mg_torso"),
    ("mg_trapecio", "Trapecio", "mg_torso"),
    ("mg_biceps", "Bíceps", "mg_brazos"),
    ("mg_triceps", "Tríceps", "mg_brazos"),
    ("mg_antebrazo", "Antebrazo / agarre", "mg_brazos"),
    ("mg_core", "Core (abs / oblicuos)", "mg_tronco"),
    ("mg_lumbar", "Lumbar", "mg_tronco"),
    ("mg_cuadriceps", "Cuádriceps", "mg_pierna"),
    ("mg_femoral", "Isquiosurales", "mg_pierna"),
    ("mg_gluteos", "Glúteos", "mg_pierna"),
    ("mg_gemelos", "Gemelos", "mg_pierna"),
]

EQUIPMENT = [
    ("eq_peso_corporal", "Peso corporal", "calistenia"),
    ("eq_barra_dominadas", "Barra de dominadas", "calistenia"),
    ("eq_paralelas", "Paralelas / fondos", "calistenia"),
    ("eq_anillas", "Anillas", "calistenia"),
    ("eq_espaldera", "Espaldera / barra vertical", "calistenia"),
    ("eq_pared", "Pared", "calistenia"),
    ("eq_barra_olimpica", "Barra olímpica", "pesas"),
    ("eq_mancuernas", "Mancuernas", "pesas"),
    ("eq_discos", "Discos", "pesas"),
    ("eq_kettlebell", "Kettlebell", "pesas"),
    ("eq_chaleco", "Chaleco lastrado", "lastre"),
    ("eq_banco", "Banco", "pesas"),
    ("eq_polea", "Polea", "pesas"),
]

BLOCKS = [
    ("flexiones", "Flexiones"), ("fondos", "Fondos"), ("dominadas", "Dominadas"),
    ("pierna", "Pierna"), ("core", "Core"), ("muscle_up", "Muscle up"),
    ("pino", "Pino"), ("planchas", "Planchas"), ("levers", "Flags y levers"),
    ("pesas_empuje", "Pesas · empuje"), ("pesas_tiron", "Pesas · tirón"),
    ("pesas_pierna", "Pesas · pierna"), ("halterofilia", "Halterofilia"),
]

RESPIRACION = {
    "dinamico": "Inhala en la bajada (fase excéntrica) y exhala al empujar o tirar. "
                "No contengas el aire durante toda la serie.",
    "estatico": "Respiraciones cortas y controladas por la nariz, sin soltar la "
                "tensión del abdomen ni de los glúteos.",
    "pesado": "Inhala profundo y bloquea el abdomen (bracing) antes de bajar; "
              "mantén la presión en el punto difícil y exhala al terminar la subida.",
}


def _criterio(medida, categoria):
    if medida == "segundos":
        return "Avanza cuando aguantes 4 series de 15-20 s con la posición limpia."
    if categoria == "pesas":
        return ("Doble progresión: cuando completes el máximo del rango de repeticiones "
                "en todas las series con RIR ≥ 1, sube la carga un 2,5-5 %.")
    return ("Avanza cuando hagas 4 series de 12-15 repeticiones limpias "
            "(la guía usa como ejemplo 4×20 flexiones antes de pasar a variantes).")


EXERCISES = []


def ej(id, nombre, cat, bloque, dif, tipo, prim, sec, equipo, antes, despues,
       desc, pasos, errores, claves, medida="reps", criterio=None,
       respiracion=None, seguridad=None, unilateral=False):
    resp_key = "pesado" if (cat == "pesas" and tipo == "dinamico") else tipo
    EXERCISES.append({
        "id": id, "name": nombre, "category": cat, "block": bloque,
        "difficulty": dif, "type": tipo, "measure": medida,
        "unilateral": unilateral,
        "primary_muscles": prim, "secondary_muscles": sec, "equipment": equipo,
        "progressions_to_reach": antes, "progresses_to": despues,
        "description": desc,
        "technique": {
            "pasos": pasos, "errores": errores, "claves": claves,
            "respiracion": respiracion or RESPIRACION.get(resp_key, RESPIRACION["dinamico"]),
            "criterio_avance": criterio or _criterio(medida, cat),
            "seguridad": seguridad or "",
        },
    })


PC = ["eq_peso_corporal"]
BAR = ["eq_barra_dominadas"]
PAR = ["eq_paralelas"]

# ───────────────────────────── FLEXIONES ─────────────────────────────
ej("ex_flexiones_inclinadas", "Flexiones inclinadas", "calistenia", "flexiones", 1, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros", "mg_core"], PC + ["eq_banco"], [], ["ex_flexiones"],
   "Manos sobre una superficie elevada y pies en el suelo. A más altura, más fácil: "
   "ideal para ajustar la dificultad.",
   ["Apoya las manos un poco más abiertas que los hombros sobre un banco, barra o mesa firme.",
    "Alinea talones, cadera y cabeza: el cuerpo es una tabla.",
    "Baja hasta que el pecho casi toque el apoyo, codos a ~45° del tronco.",
    "Empuja hasta estirar los brazos sin perder la línea del cuerpo."],
   ["Dejar caer la cadera (hiperextensión lumbar).", "Abrir los codos a 90° del cuerpo.",
    "Hacer medio recorrido."],
   ["Aprieta glúteos y abdomen.", "Empuja el suelo lejos de ti.", "Baja la altura del apoyo para progresar."])

ej("ex_flexiones_rodillas", "Flexiones con rodillas apoyadas", "calistenia", "flexiones", 1, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros"], PC, ["ex_flexiones_inclinadas"], ["ex_flexiones"],
   "Manos en el suelo y rodillas apoyadas. Espalda recta y rango completo.",
   ["Rodillas en el suelo (sobre una toalla) y manos bajo los hombros, algo más abiertas.",
    "Línea recta de rodillas a cabeza.", "Baja hasta que el pecho roce el suelo.",
    "Sube bloqueando codos."],
   ["Doblar la cadera (culo hacia arriba).", "Mirar al frente forzando el cuello."],
   ["Piensa en una plancha con rodillas.", "Controla 2 s la bajada."])

ej("ex_estatico_flexiones", "Estático de flexiones", "calistenia", "flexiones", 2, "estatico",
   ["mg_pecho", "mg_triceps", "mg_core"], ["mg_hombros"], PC,
   ["ex_flexiones_inclinadas", "ex_flexiones_rodillas"], ["ex_flexiones"],
   "Posición alta de flexión con brazos estirados; aguanta sin doblar la espalda.",
   ["Colócate en posición alta de flexión.", "Bloquea codos y empuja el suelo (escápulas separadas).",
    "Mantén la línea del cuerpo el máximo tiempo posible."],
   ["Hundir el pecho entre los hombros.", "Arquear la zona lumbar."],
   ["Glúteos apretados, costillas abajo."], medida="segundos")

ej("ex_flexiones", "Flexiones", "calistenia", "flexiones", 2, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros", "mg_core"], PC,
   ["ex_flexiones_inclinadas", "ex_flexiones_rodillas", "ex_estatico_flexiones"],
   ["ex_flexiones_diamante", "ex_flexiones_declinadas", "ex_flexiones_explosivas", "ex_flexiones_arqueras"],
   "Manos en el suelo, puntas de los pies apoyadas, tronco y piernas rectos. "
   "Ejercicio básico del empuje y base para pino y planchas.",
   ["Manos algo más abiertas que los hombros, dedos hacia delante.",
    "Pies juntos o a la anchura de cadera; cuerpo en línea recta.",
    "Baja controlando hasta que el pecho quede a 1-2 cm del suelo; codos a ~45°.",
    "Empuja hasta bloquear los codos y separa ligeramente las escápulas arriba."],
   ["Cadera caída o en pico.", "Codos abiertos en 'T' (estrés en el hombro).",
    "Cabeza adelantada buscando el suelo con la barbilla.", "Repeticiones cortas."],
   ["Tensión de cuerpo entero: glúteos + abdomen.", "Antebrazos verticales abajo.",
    "Calidad antes que cantidad."])

ej("ex_flexiones_diamante", "Flexiones diamante", "calistenia", "flexiones", 2, "dinamico",
   ["mg_triceps", "mg_pecho"], ["mg_hombros"], PC, ["ex_flexiones"], ["ex_flexiones_arqueras"],
   "Flexión con las manos juntas formando un diamante. Aumenta el trabajo de tríceps.",
   ["Junta pulgares e índices bajo el esternón.", "Cuerpo recto como en la flexión normal.",
    "Baja con los codos pegados al cuerpo hacia atrás.", "Empuja hasta bloquear."],
   ["Abrir los codos hacia fuera.", "Dejar caer la cadera para 'ganar' recorrido."],
   ["Codos rozando las costillas.", "Si molesta la muñeca, separa un poco las manos."])

ej("ex_flexiones_declinadas", "Flexiones declinadas", "calistenia", "flexiones", 3, "dinamico",
   ["mg_pecho", "mg_triceps", "mg_hombros"], ["mg_core"], PC + ["eq_banco"], ["ex_flexiones"],
   ["ex_pike_push_ups", "ex_flexiones_pino_asistidas"],
   "Manos en el suelo y pies elevados. Cuanto más altos los pies, más hombro. "
   "Preparatorio para pino y planchas.",
   ["Pies sobre un banco o escalón, manos en el suelo.", "Cuerpo recto, sin hundir la cadera.",
    "Baja hasta que la cabeza quede algo por delante de las manos.", "Empuja hasta bloquear."],
   ["Hiperextender la zona lumbar.", "Mirar al frente (sube el estrés cervical)."],
   ["Sube la altura de los pies poco a poco."])

ej("ex_pike_push_ups", "Pike push ups", "calistenia", "flexiones", 3, "dinamico",
   ["mg_hombros", "mg_triceps"], ["mg_pecho"], PC, ["ex_flexiones", "ex_flexiones_declinadas"],
   ["ex_flexiones_pino_asistidas"],
   "Manos y pies cerca con la cadera alta (V invertida). Preparatorio del trabajo de pino.",
   ["Desde flexión, camina con los pies hacia las manos hasta formar una V invertida.",
    "Baja la cabeza hacia un punto por delante de las manos (formando un triángulo).",
    "Empuja de vuelta extendiendo los brazos y llevando el peso sobre los hombros."],
   ["Bajar la cabeza justo entre las manos (los codos se abren).", "Doblar demasiado las rodillas."],
   ["Codos hacia atrás, no hacia los lados.", "Cuanto más vertical el tronco, más difícil."])

ej("ex_pseudo_push_ups", "Pseudo planche push ups", "calistenia", "flexiones", 3, "dinamico",
   ["mg_hombros", "mg_pecho", "mg_triceps"], ["mg_core", "mg_antebrazo"], PC,
   ["ex_flexiones_declinadas"], ["ex_planche_lean", "ex_tucked_planche"],
   "Flexión con las manos a la altura del ombligo y el cuerpo inclinado hacia delante. "
   "Introducción a las planchas.",
   ["Manos a la altura de la cintura con los dedos hacia fuera o atrás.",
    "Inclínate hasta que los hombros queden por delante de las manos.",
    "Baja manteniendo esa inclinación y sube sin perderla."],
   ["Volver a la posición de flexión normal al cansarse.", "Hundir las escápulas."],
   ["Protracción escapular (espalda alta 'redonda').", "Calienta bien muñecas y bíceps."],
   seguridad="Trabaja la flexibilidad de muñeca y bíceps desde las primeras progresiones de plancha.")

ej("ex_flexiones_arqueras", "Flexiones arqueras", "calistenia", "flexiones", 4, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros", "mg_core"], PC, ["ex_flexiones", "ex_flexiones_diamante"],
   ["ex_flexiones_un_brazo"],
   "Un brazo se flexiona mientras el otro queda completamente estirado hacia el lado.",
   ["Manos muy abiertas (el doble del ancho de hombros).", "Baja sobre un brazo, el otro queda recto.",
    "Gira las manos acompañando el movimiento.", "Sube y alterna el lado."],
   ["Doblar el brazo 'estirado'.", "Rotar la cadera."],
   ["Cuerpo en bloque.", "Paso intermedio hacia la flexión a una mano."], unilateral=True)

ej("ex_flexiones_explosivas", "Flexiones explosivas", "calistenia", "flexiones", 4, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros"], PC, ["ex_flexiones"], ["ex_flexiones_palmada"],
   "Al estirar los brazos con velocidad, las manos se despegan del suelo.",
   ["Baja controlado a la posición de flexión.", "Empuja lo más rápido posible hasta despegar las manos.",
    "Aterriza con los codos ligeramente flexionados y encadena la siguiente."],
   ["Aterrizar con codos bloqueados.", "Perder la línea del cuerpo al saltar."],
   ["Velocidad máxima en cada empuje.", "Domínalas antes de dar palmadas."])

ej("ex_flexiones_palmada", "Flexiones con palmada", "calistenia", "flexiones", 4, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros"], PC, ["ex_flexiones_explosivas"], ["ex_flexiones_superman"],
   "Flexión explosiva con una palmada en el aire en cada repetición.",
   ["Domina primero las flexiones explosivas.", "Empuja fuerte, da la palmada cerca del pecho.",
    "Vuelve a colocar las manos y amortigua."],
   ["Palmada sin altura suficiente (riesgo de caer de cara).", "Caer con los brazos rígidos."],
   ["Empieza sobre una superficie blanda."])

ej("ex_flexiones_un_brazo", "Flexiones a un brazo", "calistenia", "flexiones", 4, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_core", "mg_hombros"], PC, ["ex_flexiones_arqueras"], [],
   "Piernas abiertas para equilibrar y el brazo libre detrás del muslo. Lo difícil es el rango completo.",
   ["Abre las piernas más que los hombros.", "Mano de apoyo bajo el pecho, brazo libre a la espalda.",
    "Baja girando ligeramente el tronco hasta rozar el suelo.", "Sube sin torcer la cadera."],
   ["Rango corto.", "Rotación excesiva del tronco."],
   ["Empieza con la mano elevada (inclinadas a un brazo)."], unilateral=True)

ej("ex_flexiones_superman", "Flexiones Superman", "calistenia", "flexiones", 5, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_core"], PC, ["ex_flexiones_palmada"], [],
   "En cada repetición despegas manos y pies del suelo a la vez.",
   ["Empuja explosivo ayudándote de un pequeño balanceo de cadera.",
    "Despega manos y pies y estira el cuerpo en el aire.", "Aterriza a la vez con manos y pies."],
   ["Intentarlo sin dominar las flexiones con palmada."],
   ["Explosividad + tensión de core."])

# ───────────────────────────── FONDOS ─────────────────────────────
ej("ex_fondos_banco", "Fondos en banco", "calistenia", "fondos", 1, "dinamico",
   ["mg_triceps", "mg_pecho"], ["mg_hombros"], PC + ["eq_banco"], [], ["ex_estatico_fondos", "ex_fondos"],
   "De espaldas a un banco con las manos en el borde. Para quien aún no puede hacer fondos.",
   ["Manos en el borde del banco, dedos hacia delante.", "Piernas dobladas (más fácil) o estiradas.",
    "Baja hasta ~90° de codo con la espalda cerca del banco.", "Empuja hasta estirar."],
   ["Bajar demasiado (molestias en el hombro).", "Separar la espalda del banco."],
   ["Hombros abajo, lejos de las orejas."])

ej("ex_estatico_fondos", "Estático en fondos", "calistenia", "fondos", 1, "estatico",
   ["mg_triceps", "mg_pecho"], ["mg_trapecio", "mg_core"], PAR, ["ex_fondos_banco"], ["ex_fondos"],
   "En paralelas con los brazos estirados, aguanta. Da fuerza para fondos y para abdominales en paralelas.",
   ["Sube a las paralelas y bloquea los codos.", "Hombros hacia abajo (depresión escapular).",
    "Aguanta con el cuerpo quieto."],
   ["Hombros encogidos hacia las orejas."], ["Empuja las barras hacia el suelo."], medida="segundos")

ej("ex_fondos_negativos", "Fondos negativos con salto", "calistenia", "fondos", 1, "dinamico",
   ["mg_triceps", "mg_pecho"], ["mg_hombros"], PAR, ["ex_estatico_fondos"], ["ex_fondos"],
   "Saltas a la posición alta y bajas lentamente hasta tocar el suelo.",
   ["Salta a la posición alta de fondos.", "Baja en 3-5 s controlando.", "Apoya los pies y repite."],
   ["Dejarse caer en la parte baja."], ["La bajada lenta construye la fuerza."])

ej("ex_fondos", "Fondos en paralelas", "calistenia", "fondos", 2, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros", "mg_core"], PAR,
   ["ex_fondos_banco", "ex_estatico_fondos", "ex_fondos_negativos"],
   ["ex_fondos_barra", "ex_fondos_explosivos", "ex_korean_dips"],
   "Sostenido en paralelas, baja hasta que el codo forme al menos 90° y sube hasta bloquear.",
   ["Agarre firme, brazos estirados, hombros abajo.", "Inclina un poco el tronco hacia delante.",
    "Baja hasta 90° de codo o algo más.", "Empuja hasta bloquear sin balancear las piernas."],
   ["Encoger los hombros abajo del todo.", "Bajar sin control (dolor de clavícula/hombro).",
    "Medio recorrido."],
   ["Más inclinado = más pecho; más vertical = más tríceps."],
   seguridad="Si empiezas de cero, haz al menos mes y medio de versiones fáciles antes de los fondos completos.")

ej("ex_fondos_barra", "Fondos en barra", "calistenia", "fondos", 3, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros"], BAR, ["ex_fondos"], ["ex_muscle_up"],
   "Fondos con ambas manos en la misma barra; baja hasta que el pecho roce la barra. Clave para el muscle up.",
   ["Sobre la barra con los brazos estirados y las piernas algo adelantadas.",
    "Baja llevando el pecho hacia la barra.", "Empuja hasta bloquear."],
   ["No bajar lo suficiente.", "Patada con las piernas."], ["Es la fase final del muscle up."])

ej("ex_fondos_explosivos", "Fondos explosivos", "calistenia", "fondos", 3, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros"], PAR, ["ex_fondos"], [],
   "Al subir con fuerza las manos se despegan de las barras.",
   ["Baja controlado.", "Sube tan rápido que las manos se despeguen.", "Recoge y repite."],
   ["Ayudarse con las rodillas."], ["Mínimo movimiento de piernas."])

ej("ex_korean_dips", "Korean dips", "calistenia", "fondos", 3, "dinamico",
   ["mg_hombros", "mg_pecho", "mg_triceps"], [], BAR, ["ex_fondos", "ex_fondos_barra"], ["ex_back_lever"],
   "De espaldas a la barra con agarre prono, haz fondos aprovechando un poco el balanceo.",
   ["Colócate de espaldas a la barra, manos detrás de la cadera.", "Baja dejando que el cuerpo vaya hacia delante.",
    "Sube empujando y usando el balanceo para no atascarte."],
   ["Hacerlo sin movilidad de hombro."], ["Calienta y estira bien los hombros."],
   seguridad="Exige movilidad de hombro en extensión: progresa despacio.")

# ───────────────────────────── DOMINADAS ─────────────────────────────
ej("ex_dead_hang", "Dead hang (colgado)", "calistenia", "dominadas", 1, "estatico",
   ["mg_antebrazo", "mg_espalda"], ["mg_hombros"], BAR, [], ["ex_retracciones_escapulares", "ex_dominadas_pronas"],
   "Colgado de la barra con los brazos estirados. Fortalece el agarre y adapta los hombros.",
   ["Agarra la barra a la anchura de los hombros.", "Cuelga con los brazos estirados.",
    "Mantén el abdomen activo y las piernas juntas."],
   ["Soltar totalmente los hombros si duelen."], ["Agarre fuerte, respira tranquilo."], medida="segundos")

ej("ex_australian_pullups", "Australian pull ups (remo invertido)", "calistenia", "dominadas", 1, "dinamico",
   ["mg_espalda", "mg_biceps"], ["mg_core", "mg_antebrazo"], BAR, [], ["ex_dominada_prona_negativa", "ex_dominadas_pronas"],
   "Bajo una barra baja con el cuerpo recto, tira del pecho hacia la barra. Más horizontal = más difícil.",
   ["Barra a la altura de la cintura, agarre prono.", "Cuerpo recto, talones en el suelo.",
    "Tira llevando el pecho a la barra y juntando escápulas.", "Baja hasta estirar los brazos."],
   ["Cadera caída.", "Tirar sólo con los brazos sin juntar escápulas."],
   ["Pecho a la barra.", "Doblar las rodillas lo hace más fácil."])

ej("ex_australian_chinups", "Australian chin ups (supino)", "calistenia", "dominadas", 1, "dinamico",
   ["mg_biceps", "mg_espalda"], ["mg_core"], BAR, [], ["ex_dominadas_supinas"],
   "Como el australian pull up pero con agarre supino (palmas hacia ti).",
   ["Agarre supino a la anchura de hombros.", "Cuerpo recto.", "Pecho a la barra, baja controlado."],
   ["Cadera caída."], ["Prepara las dominadas supinas."])

ej("ex_retracciones_escapulares", "Retracciones escapulares", "calistenia", "dominadas", 2, "dinamico",
   ["mg_espalda", "mg_trapecio"], ["mg_antebrazo"], BAR, ["ex_dead_hang"],
   ["ex_dominadas_pronas", "ex_tucked_front_lever"],
   "Colgado con brazos rectos, sube el cuerpo sólo bajando y juntando las escápulas.",
   ["Desde dead hang con brazos estirados.", "Lleva los hombros lejos de las orejas sin doblar los codos.",
    "Aguanta 1 s y vuelve a soltar."],
   ["Doblar los codos."], ["Es el inicio de toda dominada estricta."])

ej("ex_dominada_prona_negativa", "Dominada prona negativa", "calistenia", "dominadas", 2, "dinamico",
   ["mg_espalda", "mg_biceps"], ["mg_antebrazo"], BAR, ["ex_australian_pullups"], ["ex_dominadas_pronas"],
   "Sube con un salto o apoyo y baja lo más lento posible.",
   ["Sube con un salto hasta tener la barbilla sobre la barra.", "Baja en 3-5 s.",
    "Estira por completo los brazos abajo."],
   ["Dejarse caer al final."], ["Cuenta en voz alta la bajada."])

ej("ex_dominadas_supinas", "Dominadas supinas (chin ups)", "calistenia", "dominadas", 3, "dinamico",
   ["mg_biceps", "mg_espalda"], ["mg_antebrazo", "mg_core"], BAR, ["ex_australian_chinups"],
   ["ex_dominadas_explosivas"],
   "Agarre supino, palmas hacia ti. Algo más fáciles que las pronas por la ayuda del bíceps.",
   ["Agarre supino a la anchura de hombros.", "Inicia con retracción escapular.",
    "Sube hasta pasar la barbilla.", "Baja hasta estirar completamente."],
   ["Balanceo (kipping).", "No estirar abajo."], ["Pecho hacia la barra."])

ej("ex_dominadas_pronas", "Dominadas pronas", "calistenia", "dominadas", 3, "dinamico",
   ["mg_espalda", "mg_biceps"], ["mg_antebrazo", "mg_core"], BAR,
   ["ex_australian_pullups", "ex_dominada_prona_negativa", "ex_retracciones_escapulares"],
   ["ex_dominadas_explosivas", "ex_dominadas_arqueras", "ex_muscle_up", "ex_tucked_front_lever"],
   "Agarre prono, barbilla sobre la barra y bajar hasta extensión completa.",
   ["Agarre prono algo más abierto que los hombros.", "Empieza bajando escápulas (sin doblar codos).",
    "Tira llevando los codos hacia las costillas hasta pasar la barbilla.",
    "Baja controlado hasta estirar los brazos."],
   ["Balancear las piernas.", "Estirar el cuello para 'pasar' la barbilla.",
    "Hacer medias repeticiones."],
   ["Piernas juntas y abdomen activo.", "Codos hacia los bolsillos."],
   seguridad="Si no haces aún 10 dominadas limpias, no empieces con muscle up.")

ej("ex_dominadas_neutras", "Dominadas agarre neutro", "calistenia", "dominadas", 3, "dinamico",
   ["mg_espalda", "mg_biceps"], ["mg_antebrazo"], BAR, ["ex_australian_pullups"], ["ex_dominada_un_brazo"],
   "Palmas enfrentadas. Agarre amable para codos y hombros.",
   ["Agarra las asas paralelas.", "Sube hasta pasar la barbilla.", "Baja completo."],
   ["Kipping."], ["Buena opción si molestan los codos."])

ej("ex_dominadas_explosivas", "Dominadas explosivas", "calistenia", "dominadas", 4, "dinamico",
   ["mg_espalda", "mg_biceps"], ["mg_core"], BAR, ["ex_dominadas_pronas"], ["ex_muscle_up"],
   "Tira tan rápido que el pecho llegue a la barra. Base del muscle up.",
   ["Desde colgado, tira con máxima velocidad.", "Intenta llevar el pecho (o el ombligo) a la barra.",
    "Baja controlado."],
   ["Usar balanceo exagerado."], ["La guía pide 10 explosivas limpias antes del muscle up."])

ej("ex_dominadas_arqueras", "Dominadas arqueras", "calistenia", "dominadas", 4, "dinamico",
   ["mg_espalda", "mg_biceps"], ["mg_core"], BAR, ["ex_dominadas_pronas"], ["ex_dominada_un_brazo"],
   "Agarre muy amplio; subes hacia una mano mientras el otro brazo queda estirado.",
   ["Agarre muy amplio.", "Sube hacia un lado, el otro brazo se estira.", "Baja y alterna."],
   ["Doblar el brazo de apoyo."], ["Paso hacia la dominada a una mano."], unilateral=True)

ej("ex_dominada_un_brazo", "Dominada a un brazo", "calistenia", "dominadas", 5, "dinamico",
   ["mg_espalda", "mg_biceps"], ["mg_antebrazo", "mg_core"], BAR,
   ["ex_dominadas_arqueras", "ex_dominadas_neutras"], [],
   "Dominada completa colgado de una sola mano.",
   ["Agarre neutro o supino con una mano.", "Retrae la escápula.", "Tira sin girar el cuerpo.",
    "Baja controlado."],
   ["Intentarla sin estáticos a un brazo previos."], ["Aprieta el puño libre y el abdomen."],
   unilateral=True, seguridad="Alta carga para codo y bíceps: progresión muy gradual.")

# ───────────────────────────── PIERNA ─────────────────────────────
ej("ex_sentadilla_asistida", "Sentadilla asistida", "calistenia", "pierna", 1, "dinamico",
   ["mg_cuadriceps", "mg_gluteos"], [], PC, [], ["ex_sentadilla"],
   "Sentadilla sujetándote a un apoyo para ayudarte.",
   ["Sujeta un poste o marco de puerta.", "Baja sentándote atrás.", "Sube ayudándote lo mínimo."],
   ["Rodillas hacia dentro."], ["Peso en todo el pie."])

ej("ex_sentadilla", "Sentadilla (peso corporal)", "calistenia", "pierna", 2, "dinamico",
   ["mg_cuadriceps", "mg_gluteos"], ["mg_femoral", "mg_core"], PC, ["ex_sentadilla_asistida"],
   ["ex_zancadas", "ex_bulgarian_squat", "ex_pistol_asistida", "ex_sentadilla_barra"],
   "Pies a la anchura de hombros, baja hasta al menos muslos paralelos y sube.",
   ["Pies a la anchura de hombros, puntas algo abiertas.", "Inicia moviendo cadera atrás y rodillas a la vez.",
    "Baja hasta muslos paralelos o más, talones en el suelo.", "Sube empujando el suelo."],
   ["Rodillas hacia dentro (valgo).", "Levantar los talones.", "Redondear la espalda."],
   ["Rodillas en la dirección de las puntas.", "Pecho orgulloso."])

ej("ex_zancadas", "Zancadas", "calistenia", "pierna", 2, "dinamico",
   ["mg_cuadriceps", "mg_gluteos"], ["mg_femoral"], PC, ["ex_sentadilla"], ["ex_bulgarian_squat"],
   "Paso largo y bajar la rodilla de atrás cerca del suelo.",
   ["Da un paso largo al frente.", "Baja hasta que ambas rodillas estén a ~90°.", "Empuja con la pierna delantera."],
   ["Rodilla delantera hacia dentro.", "Tronco muy inclinado."], ["Tronco erguido."], unilateral=True)

ej("ex_levantamiento_gemelos", "Elevaciones de gemelos", "calistenia", "pierna", 2, "dinamico",
   ["mg_gemelos"], [], PC, [], [],
   "Subir sobre las puntas de los pies; mejor en un escalón para más recorrido.",
   ["Puntas en un escalón, talones fuera.", "Baja el talón al máximo.", "Sube hasta la punta, pausa 1 s."],
   ["Rebotar."], ["Pausa arriba y abajo."])

ej("ex_curl_femoral_pc", "Curl femoral con peso corporal", "calistenia", "pierna", 2, "dinamico",
   ["mg_femoral"], ["mg_gluteos"], PC, [], [],
   "Tumbado boca arriba con talones sobre una superficie deslizante, acerca los talones a la cadera.",
   ["Tumbado, talones sobre toalla o deslizador.", "Eleva la cadera (puente).",
    "Recoge los talones hacia el glúteo sin bajar la cadera.", "Estira despacio."],
   ["Dejar caer la cadera."], ["Cadera alta todo el tiempo."])

ej("ex_bulgarian_squat", "Sentadilla búlgara", "calistenia", "pierna", 3, "dinamico",
   ["mg_cuadriceps", "mg_gluteos"], ["mg_femoral", "mg_core"], PC + ["eq_banco"], ["ex_zancadas"],
   ["ex_pistol_asistida"],
   "Pie trasero sobre un banco; bajas sobre la pierna delantera.",
   ["Empeine trasero sobre un banco.", "Pie delantero suficientemente adelantado.",
    "Baja vertical hasta casi tocar el suelo con la rodilla trasera.", "Sube con la pierna delantera."],
   ["Pie delantero demasiado cerca.", "Empujar con la pierna de atrás."],
   ["Más inclinado = más glúteo."], unilateral=True)

ej("ex_pistol_asistida", "Pistol squat asistida", "calistenia", "pierna", 4, "dinamico",
   ["mg_cuadriceps", "mg_gluteos"], ["mg_core"], PC, ["ex_sentadilla", "ex_bulgarian_squat"], ["ex_pistol_squat"],
   "Sentadilla a una pierna sujetándote a un apoyo.",
   ["Sujeta un poste.", "Estira una pierna al frente.", "Baja a una pierna hasta abajo.", "Sube usando el apoyo lo mínimo."],
   ["Talón despegado."], ["Brazos al frente para equilibrar."], unilateral=True)

ej("ex_pistol_squat", "Pistol squat", "calistenia", "pierna", 5, "dinamico",
   ["mg_cuadriceps", "mg_gluteos"], ["mg_core", "mg_femoral"], PC, ["ex_pistol_asistida"], [],
   "Sentadilla completa a una pierna con la otra estirada al frente.",
   ["De pie sobre una pierna, la otra estirada al frente.", "Baja controlando con el talón apoyado.",
    "Llega abajo sin rebotar.", "Sube manteniendo la pierna libre en el aire."],
   ["Rodilla hacia dentro.", "Caer abajo sin control."],
   ["Movilidad de tobillo: usa un disco bajo el talón si hace falta."], unilateral=True)

# ───────────────────────────── CORE ─────────────────────────────
ej("ex_plancha_abdominal", "Plancha abdominal", "calistenia", "core", 2, "estatico",
   ["mg_core"], ["mg_hombros", "mg_gluteos"], PC, [], ["ex_plancha_lateral", "ex_leg_raises_suelo"],
   "Apoyado en antebrazos y puntas de los pies con el cuerpo recto.",
   ["Antebrazos bajo los hombros.", "Cuerpo recto de talones a cabeza.",
    "Retroversión pélvica: mete el coxis y aprieta glúteos."],
   ["Cadera hundida o muy alta."], ["Costillas hacia la pelvis."], medida="segundos")

ej("ex_plancha_lateral", "Plancha lateral", "calistenia", "core", 2, "estatico",
   ["mg_core"], ["mg_hombros"], PC, ["ex_plancha_abdominal"], [],
   "Apoyado de lado sobre un antebrazo con el cuerpo recto. Oblicuos.",
   ["Codo bajo el hombro.", "Pies apilados.", "Sube la cadera hasta la línea recta."],
   ["Cadera caída."], ["Empuja el suelo con el antebrazo."], medida="segundos", unilateral=True)

ej("ex_leg_raises_suelo", "Elevaciones de piernas en suelo", "calistenia", "core", 2, "dinamico",
   ["mg_core"], [], PC, ["ex_plancha_abdominal"], ["ex_knee_raises_barra"],
   "Tumbado boca arriba, sube las piernas estiradas hasta la vertical y baja sin tocar el suelo.",
   ["Lumbar pegada al suelo.", "Sube piernas estiradas hasta la vertical.", "Baja lento sin tocar el suelo."],
   ["Arquear la zona lumbar."], ["Si se despega la lumbar, dobla las rodillas."])

ej("ex_crunches_lumbares", "Extensiones lumbares (superman)", "calistenia", "core", 2, "dinamico",
   ["mg_lumbar"], ["mg_gluteos"], PC, [], [],
   "Boca abajo, eleva pecho y piernas a la vez y baja controlado.",
   ["Boca abajo con los brazos al frente.", "Eleva pecho y piernas.", "Pausa 1 s y baja."],
   ["Tirar del cuello."], ["Mirada al suelo."])

ej("ex_knee_raises_barra", "Elevaciones de rodillas en barra", "calistenia", "core", 3, "dinamico",
   ["mg_core"], ["mg_antebrazo"], BAR, ["ex_leg_raises_suelo"], ["ex_leg_raises_barra"],
   "Colgado, lleva las rodillas al pecho sin balancearte.",
   ["Cuelga con escápulas activas.", "Sube las rodillas al pecho redondeando la pelvis.", "Baja sin balanceo."],
   ["Balancearse."], ["Piensa en enrollar la pelvis."])

ej("ex_estatico_l_sit", "L-sit en paralelas", "calistenia", "core", 3, "estatico",
   ["mg_core"], ["mg_triceps", "mg_cuadriceps"], PAR, ["ex_estatico_fondos", "ex_knee_raises_barra"], ["ex_leg_raises_barra"],
   "En paralelas con los brazos estirados, piernas rectas al frente formando una L.",
   ["Brazos bloqueados, hombros abajo.", "Sube las piernas rectas a la horizontal.", "Puntas estiradas, aguanta."],
   ["Piernas por debajo de la horizontal.", "Hombros encogidos."],
   ["Empieza con una pierna o rodillas recogidas (tuck)."], medida="segundos")

ej("ex_leg_raises_barra", "Elevaciones de piernas en barra", "calistenia", "core", 4, "dinamico",
   ["mg_core"], ["mg_antebrazo"], BAR, ["ex_knee_raises_barra"], ["ex_dragon_flag", "ex_tucked_front_lever"],
   "Colgado, sube las piernas estiradas hasta la barra o por encima de la cadera.",
   ["Cuelga con escápulas activas.", "Sube las piernas estiradas lo más alto posible.", "Baja controlado."],
   ["Usar inercia."], ["Pies a la barra = versión completa."])

ej("ex_dragon_flag", "Dragon flag", "calistenia", "levers", 3, "dinamico",
   ["mg_core", "mg_espalda"], ["mg_lumbar"], ["eq_banco"], ["ex_leg_raises_barra"], ["ex_front_lever"],
   "Boca arriba agarrado a un apoyo tras la cabeza; cuerpo recto apoyado sólo en la espalda alta.",
   ["Agarra un banco o barra baja detrás de la cabeza.", "Eleva el cuerpo recto apoyando sólo la espalda alta.",
    "Baja el bloque entero lentamente."],
   ["Doblar la cadera."], ["Empieza con una pierna recogida."])

# ───────────────────────────── MUSCLE UP ─────────────────────────────
ej("ex_muscle_up_salto", "Muscle up asistido con salto", "calistenia", "muscle_up", 2, "dinamico",
   ["mg_espalda", "mg_pecho", "mg_triceps"], ["mg_core"], BAR, ["ex_dominadas_pronas", "ex_fondos_barra"],
   ["ex_muscle_up_pierna", "ex_muscle_up"],
   "Usar un salto desde el suelo para aprender la transición por encima de la barra.",
   ["Barra a la altura del pecho.", "Salta y tira de la barra hacia la cadera.",
    "Gira las muñecas por encima y termina con un fondo en barra."],
   ["Saltar sin tirar."], ["Aprende la transición, no la fuerza."])

ej("ex_muscle_up_pierna", "Muscle up asistido con pierna", "calistenia", "muscle_up", 2, "dinamico",
   ["mg_espalda", "mg_pecho", "mg_triceps"], ["mg_core"], BAR, ["ex_muscle_up_salto"], ["ex_muscle_up"],
   "Una pierna sobre la barra ayuda a subir.",
   ["Engancha una rodilla en la barra.", "Tira y pasa el pecho sobre la barra.", "Termina con fondo en barra."],
   ["Hacer todo con la pierna."], ["Reduce la ayuda poco a poco."])

ej("ex_muscle_up", "Muscle up", "calistenia", "muscle_up", 4, "dinamico",
   ["mg_espalda", "mg_pecho", "mg_triceps"], ["mg_biceps", "mg_core", "mg_hombros"], BAR,
   ["ex_dominadas_explosivas", "ex_fondos_barra", "ex_muscle_up_pierna"], ["ex_muscle_up_lento"],
   "Dominada explosiva que termina con la cadera sobre la barra y un fondo en barra.",
   ["Agarre algo más cerrado que en la dominada, sin pulgar (falso agarre opcional).",
    "Pequeño balanceo atrás y tira explosivo hacia la cadera (no al pecho).",
    "Al llegar arriba, inclina el pecho sobre la barra y gira las muñecas.",
    "Termina con un fondo en barra hasta bloquear."],
   ["Subir un brazo antes que el otro (chicken wing).", "Tirar vertical hacia la barbilla.",
    "Repetirlo muchas veces el primer día."],
   ["Tira 'hacia atrás y alrededor' de la barra.", "Codos rápidos por encima."],
   seguridad="Cuando lo consigas, no hagas más de 2-3 al día durante semanas para que tendones y codos se adapten.")

ej("ex_muscle_up_lento", "Muscle up lento", "calistenia", "muscle_up", 4, "dinamico",
   ["mg_espalda", "mg_pecho", "mg_triceps"], ["mg_biceps", "mg_core"], BAR, ["ex_muscle_up"], [],
   "Muscle up sin impulso, controlando toda la transición.",
   ["Falso agarre.", "Tira lento hasta el pecho.", "Transición controlada.", "Fondo en barra."],
   ["Recurrir al balanceo."], ["Paso hacia el muscle up estricto."])

# ───────────────────────────── PINO ─────────────────────────────
ej("ex_pino_pared", "Pino asistido contra la pared", "calistenia", "pino", 2, "estatico",
   ["mg_hombros", "mg_triceps"], ["mg_core", "mg_trapecio"], PC + ["eq_pared"], ["ex_pike_push_ups"],
   ["ex_flexiones_pino_asistidas", "ex_pino"],
   "Parada de manos con los pies apoyados en la pared.",
   ["Manos a 10-20 cm de la pared, a la anchura de hombros.", "Sube con una patada controlada.",
    "Empuja el suelo y lleva los hombros a las orejas.", "Cuerpo recto, abdomen y glúteos apretados."],
   ["Banana (espalda muy arqueada).", "Hombros no extendidos."],
   ["Mira entre las manos.", "Prueba también con el pecho mirando a la pared."], medida="segundos")

ej("ex_flexiones_pino_asistidas", "Flexiones a pino asistidas", "calistenia", "pino", 3, "dinamico",
   ["mg_hombros", "mg_triceps"], ["mg_trapecio"], PC + ["eq_pared"],
   ["ex_pino_pared", "ex_pike_push_ups", "ex_flexiones_declinadas"], ["ex_flexiones_pino"],
   "Flexiones en pino con los pies apoyados en la pared.",
   ["Pino contra la pared.", "Baja la cabeza hacia delante de las manos (triángulo).", "Empuja hasta bloquear."],
   ["Abrir los codos hacia fuera.", "Golpear la cabeza en el suelo."], ["Usa un cojín bajo la cabeza."])

ej("ex_pino", "Pino (handstand libre)", "calistenia", "pino", 3, "estatico",
   ["mg_hombros", "mg_triceps"], ["mg_core", "mg_antebrazo"], PC, ["ex_pino_pared"], ["ex_flexiones_pino"],
   "Equilibrio sobre las manos sin apoyo. Requiere hombros fuertes, mucha práctica y técnica.",
   ["Dedos separados: el equilibrio se corrige con la presión de dedos y palma.",
    "Sube con patada suave hasta la vertical.", "Hombros extendidos, cuerpo recto.",
    "Aprende a salir rotando una mano (pirueta) por seguridad."],
   ["Patada demasiado fuerte.", "Mirar demasiado lejos.", "Arquear la espalda."],
   ["Más flexiones y lastre = mejor pino (consejo de la escuela de Jujuy).",
    "Practícalo a diario en series cortas."], medida="segundos")

ej("ex_flexiones_pino", "Flexiones a pino", "calistenia", "pino", 4, "dinamico",
   ["mg_hombros", "mg_triceps"], ["mg_trapecio", "mg_core"], PC, ["ex_pino", "ex_flexiones_pino_asistidas"], [],
   "Flexiones en pino libre.",
   ["Pino libre estable.", "Baja controlando el equilibrio.", "Empuja hasta bloquear."],
   ["Perder la vertical al bajar."], ["Dominar primero 5-8 asistidas limpias."])

# ───────────────────────────── PLANCHAS ─────────────────────────────
ej("ex_rana", "Rana (crow pose)", "calistenia", "planchas", 1, "estatico",
   ["mg_hombros", "mg_triceps"], ["mg_core", "mg_antebrazo"], PC, [], ["ex_planche_lean", "ex_tucked_planche"],
   "Rodillas apoyadas sobre los codos, inclinas el cuerpo hasta levantar los pies.",
   ["Manos en el suelo, rodillas sobre la parte externa de los codos.", "Inclínate adelante.",
    "Levanta los pies y equilibra."],
   ["Caer de cara por falta de control."], ["Pon un cojín delante."], medida="segundos")

ej("ex_planche_lean", "Planche lean", "calistenia", "planchas", 2, "estatico",
   ["mg_hombros", "mg_pecho"], ["mg_core", "mg_biceps"], PC, ["ex_pseudo_push_ups", "ex_rana"],
   ["ex_tucked_planche"],
   "En posición de flexión, inclínate hacia delante con brazos rectos hasta que los hombros superen las manos.",
   ["Posición de flexión, dedos hacia fuera.", "Inclínate adelante con brazos bloqueados.",
    "Protracción escapular y cadera en línea."],
   ["Doblar los codos.", "Hundir las escápulas."], ["Más inclinación = más difícil."], medida="segundos",
   seguridad="Calienta muñecas y bíceps: tendones necesitan más tiempo que los músculos.")

ej("ex_tucked_planche", "Tucked planche", "calistenia", "planchas", 2, "estatico",
   ["mg_hombros", "mg_pecho"], ["mg_core", "mg_triceps"], PC + PAR, ["ex_planche_lean"],
   ["ex_advanced_tucked_planche"],
   "Plancha con las rodillas recogidas al pecho y los brazos rectos.",
   ["Manos en el suelo o paralelas.", "Inclínate y despega los pies con las rodillas al pecho.",
    "Espalda redondeada, brazos bloqueados."],
   ["Apoyar las rodillas en los codos (eso es la rana).", "Codos doblados."],
   ["Empuja el suelo lejos."], medida="segundos")

ej("ex_advanced_tucked_planche", "Advanced tucked planche", "calistenia", "planchas", 3, "estatico",
   ["mg_hombros", "mg_pecho"], ["mg_core"], PC + PAR, ["ex_tucked_planche"], ["ex_straddle_planche"],
   "Como la tucked planche pero con la espalda plana y la cadera a la altura de los hombros.",
   ["Desde tucked, aplana la espalda.", "Cadera a la altura de los hombros.", "Rodillas recogidas bajo la cadera."],
   ["Cadera alta."], ["Inclina más los hombros adelante."], medida="segundos")

ej("ex_straddle_planche", "Straddle planche", "calistenia", "planchas", 4, "estatico",
   ["mg_hombros", "mg_pecho"], ["mg_core", "mg_lumbar"], PC + PAR, ["ex_advanced_tucked_planche"], ["ex_full_planche"],
   "Plancha con piernas abiertas, cuerpo paralelo al suelo.",
   ["Desde advanced tucked, estira las piernas abiertas.", "Cuerpo paralelo al suelo.", "Brazos bloqueados."],
   ["Cadera caída."], ["Glúteos apretados, puntas estiradas."], medida="segundos",
   seguridad="Al menos 1,5 meses de progresiones fáciles y otro 1,5 de avanzadas antes de intentarla.")

ej("ex_full_planche", "Full planche", "calistenia", "planchas", 5, "estatico",
   ["mg_hombros", "mg_pecho"], ["mg_core", "mg_lumbar"], PC + PAR, ["ex_straddle_planche"], [],
   "Plancha completa con piernas juntas, paralelo al suelo.",
   ["Desde straddle, junta las piernas.", "Mantén el cuerpo recto y paralelo."],
   ["Banana."], ["Objetivo de largo plazo."], medida="segundos")

# ───────────────────────────── FLAGS Y LEVERS ─────────────────────────────
ej("ex_skin_the_cat", "Skin the cat", "calistenia", "levers", 2, "dinamico",
   ["mg_espalda", "mg_hombros"], ["mg_core"], BAR + ["eq_anillas"], ["ex_knee_raises_barra"], ["ex_back_lever"],
   "Colgado, recoge las piernas, pásalas entre los brazos y gira hasta que los pies apunten al suelo.",
   ["Cuelga y recoge las rodillas.", "Pasa las piernas entre los brazos.", "Gira hasta donde permita el hombro.",
    "Vuelve por el mismo camino."],
   ["Forzar el rango de hombro."], ["Avanza el rango poco a poco."],
   seguridad="Movimiento de mucha movilidad de hombro: nunca lo fuerces.")

ej("ex_tucked_front_lever", "Tucked front lever", "calistenia", "levers", 2, "estatico",
   ["mg_espalda", "mg_core"], ["mg_biceps"], BAR, ["ex_dominadas_pronas", "ex_leg_raises_barra"],
   ["ex_front_lever_una_pierna"],
   "Agarre prono, rodillas al pecho, brazos estirados y espalda paralela al suelo.",
   ["Cuelga con brazos rectos.", "Retrae y deprime las escápulas.",
    "Lleva rodillas al pecho y la espalda a la horizontal.", "Empuja la barra hacia la cadera."],
   ["Doblar codos.", "Cadera por debajo de los hombros."], ["Piensa en 'brazos rectos empujando abajo'."],
   medida="segundos")

ej("ex_front_lever_una_pierna", "Front lever a una pierna", "calistenia", "levers", 3, "estatico",
   ["mg_espalda", "mg_core"], ["mg_biceps"], BAR, ["ex_tucked_front_lever"], ["ex_front_lever"],
   "Desde tucked front lever estira una pierna manteniéndote paralelo.",
   ["Tucked front lever.", "Estira una pierna sin bajar la cadera.", "Alterna la pierna en cada serie."],
   ["Bajar la cadera al estirar."], ["Paso intermedio: half lay."], medida="segundos")

ej("ex_front_lever", "Front lever", "calistenia", "levers", 4, "estatico",
   ["mg_espalda", "mg_core"], ["mg_biceps", "mg_lumbar"], BAR, ["ex_front_lever_una_pierna", "ex_dragon_flag"], [],
   "Agarre prono, cuerpo paralelo al suelo con ambas piernas estiradas.",
   ["Desde colgado, brazos rectos y escápulas abajo.", "Eleva el cuerpo recto hasta la horizontal.",
    "Glúteos y abdomen tensos, puntas estiradas."],
   ["Cadera caída.", "Codos doblados."], ["Empieza con straddle (piernas abiertas)."],
   medida="segundos",
   seguridad="Mínimo 1,5 meses de dominadas y tucked antes de progresiones avanzadas; trabaja movilidad escapular.")

ej("ex_back_lever", "Back lever", "calistenia", "levers", 4, "estatico",
   ["mg_hombros", "mg_pecho", "mg_lumbar"], ["mg_biceps", "mg_core"], BAR + ["eq_anillas"],
   ["ex_skin_the_cat", "ex_korean_dips"], [],
   "Agarre prono, pasas las piernas entre las manos y te quedas paralelo al suelo boca abajo.",
   ["Skin the cat hasta la posición invertida.", "Baja lento hasta la horizontal.", "Cuerpo recto, aguanta."],
   ["Bajar demasiado rápido.", "Doblar los codos."], ["Progresa: tuck → una pierna → completo."],
   medida="segundos", seguridad="Alta tensión en bíceps y hombro: progresión paciente.")

ej("ex_bandera_tucked", "Bandera en tucked", "calistenia", "levers", 2, "estatico",
   ["mg_espalda", "mg_hombros", "mg_core"], [], ["eq_espaldera"], ["ex_dominadas_pronas", "ex_pino_pared"],
   ["ex_bandera"],
   "En barra vertical: mano alta por encima de la cabeza, mano baja a la cintura, rodillas al pecho.",
   ["Mano superior tira, mano inferior empuja.", "Recoge las rodillas.", "Mantén el cuerpo lateral."],
   ["Brazo de abajo doblado."], ["Empuja fuerte con la mano baja."], medida="segundos")

ej("ex_bandera", "Bandera humana", "calistenia", "levers", 4, "estatico",
   ["mg_hombros", "mg_espalda", "mg_core"], [], ["eq_espaldera"], ["ex_bandera_tucked"], [],
   "Cuerpo paralelo al suelo sujeto a una barra vertical.",
   ["Agarre: mano alta tira, baja empuja.", "Sube las piernas juntas hasta la horizontal.", "Bloquea ambos brazos."],
   ["Cadera caída."], ["Pasa por bandera caída a 45°."], medida="segundos")

# ───────────────────────────── PESAS ─────────────────────────────
OLY = ["eq_barra_olimpica", "eq_discos"]

ej("ex_sentadilla_barra", "Sentadilla con barra", "pesas", "pesas_pierna", 3, "dinamico",
   ["mg_cuadriceps", "mg_gluteos"], ["mg_femoral", "mg_core", "mg_lumbar"], OLY, ["ex_sentadilla"],
   ["ex_sentadilla_frontal"],
   "Barra sobre los trapecios, bajar hasta ~90° o más con la espalda neutra.",
   ["Barra apoyada en el trapecio, agarre firme y codos abajo.",
    "Pies a la anchura de hombros, inhala y bloquea el abdomen.",
    "Baja con cadera y rodillas a la vez, rodillas siguiendo las puntas.",
    "Sube empujando el suelo y manteniendo el pecho arriba."],
   ["Redondear la espalda baja.", "Rodillas hacia dentro.", "Levantar talones.", "Subir la cadera antes que el pecho."],
   ["Peña Fernández: en las series, detente unos cm antes del rango máximo arriba para no relajar el músculo."],
   seguridad="Usa soportes de seguridad o un compañero en series pesadas.")

ej("ex_sentadilla_frontal", "Sentadilla frontal", "pesas", "pesas_pierna", 4, "dinamico",
   ["mg_cuadriceps", "mg_gluteos"], ["mg_core"], OLY, ["ex_sentadilla_barra"], ["ex_arranque", "ex_envion"],
   "Barra sobre los deltoides delanteros con codos altos. Tronco más vertical y más cuádriceps.",
   ["Barra sobre los hombros, codos altos.", "Baja con el tronco vertical.", "Sube sin bajar los codos."],
   ["Codos que caen.", "Inclinar el tronco."], ["Base para el clin y el envión."])

ej("ex_peso_muerto", "Peso muerto", "pesas", "pesas_tiron", 3, "dinamico",
   ["mg_femoral", "mg_gluteos", "mg_lumbar"], ["mg_espalda", "mg_antebrazo", "mg_trapecio"], OLY, [], [],
   "Levantar la barra desde el suelo hasta quedar erguido con la espalda neutra.",
   ["Pies a la anchura de cadera, barra sobre el medio pie.",
    "Agarre justo fuera de las piernas; espinillas a la barra.",
    "Pecho arriba, espalda neutra, inhala y bloquea.",
    "Empuja el suelo y lleva la barra pegada a las piernas hasta extender la cadera."],
   ["Espalda redondeada.", "Barra lejos del cuerpo.", "Tirón brusco desde el suelo.", "Hiperextender arriba."],
   ["'Empuja el suelo', no 'tira de la barra'."],
   seguridad="La barra lejos del centro de gravedad aumenta mucho la carga lumbar.")

ej("ex_peso_muerto_rumano", "Peso muerto rumano", "pesas", "pesas_tiron", 3, "dinamico",
   ["mg_femoral", "mg_gluteos"], ["mg_lumbar"], OLY + ["eq_mancuernas"], [], [],
   "Bisagra de cadera con rodillas semiflexionadas, bajando la barra pegada a las piernas.",
   ["De pie con la barra, rodillas algo flexionadas.", "Lleva la cadera atrás bajando la barra por los muslos.",
    "Baja hasta notar tensión en isquios sin redondear.", "Vuelve extendiendo la cadera."],
   ["Doblar mucho las rodillas (se convierte en sentadilla).", "Redondear la espalda."], ["Cadera atrás, no abajo."])

ej("ex_press_banca", "Press de banca", "pesas", "pesas_empuje", 3, "dinamico",
   ["mg_pecho", "mg_triceps"], ["mg_hombros"], OLY + ["eq_banco"], ["ex_flexiones"], [],
   "Tumbado en banco, bajar la barra al pecho y empujar hasta bloquear.",
   ["Ojos bajo la barra, pies firmes en el suelo.", "Retrae y deprime las escápulas (la calistenia ayuda aquí).",
    "Baja la barra a la parte baja del pecho, codos a ~45-70°.", "Empuja hacia arriba y algo atrás."],
   ["Rebotar en el pecho.", "Despegar los glúteos del banco.", "Codos abiertos a 90°."],
   ["Escápulas juntas todo el tiempo."], seguridad="Usa siempre un compañero o pines de seguridad.")

ej("ex_press_militar", "Press militar", "pesas", "pesas_empuje", 3, "dinamico",
   ["mg_hombros", "mg_triceps"], ["mg_core", "mg_trapecio"], OLY + ["eq_mancuernas"], ["ex_pike_push_ups"], [],
   "De pie, empujar la barra desde los hombros hasta encima de la cabeza.",
   ["Barra sobre los hombros, agarre algo más abierto que los hombros.", "Glúteos y abdomen tensos.",
    "Empuja vertical apartando la cabeza y métela bajo la barra al final."],
   ["Arquear la zona lumbar.", "Empujar la barra hacia delante."], ["Bíceps junto a las orejas al terminar."])

ej("ex_remo_barra", "Remo con barra", "pesas", "pesas_tiron", 3, "dinamico",
   ["mg_espalda", "mg_biceps"], ["mg_lumbar", "mg_trapecio"], OLY, ["ex_australian_pullups"], [],
   "Tronco inclinado, tirar de la barra hacia el abdomen.",
   ["Bisagra de cadera a ~45°, espalda neutra.", "Tira de la barra hacia el ombligo juntando escápulas.",
    "Baja controlado."],
   ["Usar impulso del tronco.", "Redondear la espalda."], ["Codos hacia atrás, no hacia fuera."])

ej("ex_remo_mancuerna", "Remo con mancuerna", "pesas", "pesas_tiron", 2, "dinamico",
   ["mg_espalda", "mg_biceps"], [], ["eq_mancuernas", "eq_banco"], [], [],
   "Apoyado en un banco, tirar de la mancuerna hacia la cadera.",
   ["Rodilla y mano en el banco.", "Tira llevando el codo hacia la cadera.", "Estira abajo."],
   ["Rotar el tronco."], ["Piensa en el codo, no en la mano."], unilateral=True)

ej("ex_hip_thrust", "Hip thrust", "pesas", "pesas_pierna", 2, "dinamico",
   ["mg_gluteos"], ["mg_femoral"], OLY + ["eq_banco"], [], [],
   "Espalda alta en un banco, barra sobre la cadera, extender la cadera.",
   ["Escápulas sobre el banco, barra en la cadera (con almohadilla).", "Pies a la anchura de cadera.",
    "Extiende la cadera hasta la horizontal, pausa 1 s."],
   ["Hiperextender la lumbar."], ["Barbilla al pecho, costillas abajo."])

ej("ex_curl_biceps", "Curl de bíceps", "pesas", "pesas_tiron", 1, "dinamico",
   ["mg_biceps"], ["mg_antebrazo"], ["eq_mancuernas", "eq_barra_olimpica"], [], [],
   "Flexión de codo con mancuernas o barra.",
   ["Codos pegados al cuerpo.", "Sube sin balancear.", "Baja en 2-3 s."], ["Balancear el tronco."],
   ["Controla la bajada."])

ej("ex_extension_triceps", "Extensión de tríceps en polea", "pesas", "pesas_empuje", 1, "dinamico",
   ["mg_triceps"], [], ["eq_polea"], [], [],
   "Extensión de codo en polea alta.",
   ["Codos fijos junto al cuerpo.", "Extiende hasta bloquear.", "Vuelve controlado."], ["Mover los codos."],
   ["Sólo se mueve el antebrazo."])

ej("ex_elevaciones_laterales", "Elevaciones laterales", "pesas", "pesas_empuje", 1, "dinamico",
   ["mg_hombros"], ["mg_trapecio"], ["eq_mancuernas"], [], [],
   "Elevar las mancuernas lateralmente hasta la altura de los hombros.",
   ["Ligera flexión de codo.", "Sube a los lados hasta la altura del hombro.", "Baja lento."],
   ["Encoger trapecios.", "Usar impulso."], ["Ideal para estrés metabólico (12-20 reps)."])

ej("ex_kettlebell_swing", "Swing con kettlebell", "pesas", "pesas_tiron", 2, "dinamico",
   ["mg_gluteos", "mg_femoral"], ["mg_lumbar", "mg_core"], ["eq_kettlebell"], [], [],
   "Balanceo explosivo con bisagra de cadera.",
   ["Bisagra de cadera con la pesa entre las piernas.", "Extiende la cadera explosivamente.",
    "La pesa sube por inercia hasta el pecho.", "Deja que baje y repite."],
   ["Hacer una sentadilla.", "Levantar con los brazos."], ["La potencia sale de la cadera."])

ej("ex_arranque", "Arranque (snatch)", "pesas", "halterofilia", 5, "dinamico",
   ["mg_cuadriceps", "mg_gluteos", "mg_femoral", "mg_espalda"], ["mg_hombros", "mg_trapecio", "mg_core"], OLY,
   ["ex_sentadilla_frontal", "ex_peso_muerto"], [],
   "Levantar la barra del suelo hasta encima de la cabeza en un solo movimiento, con agarre ancho.",
   ["Posición inicial: pies al ancho de cadera bajo la barra, agarre ancho, espalda neutra.",
    "1.ª fase del halón: despegue lento extendiendo piernas, barra pegada al cuerpo.",
    "2.ª fase del halón: extensión explosiva de cadera, rodillas y tobillos.",
    "Desliz: métete bajo la barra en cuclillas con brazos bloqueados.",
    "Ponte de pie estabilizando la barra arriba."],
   ["Despegue brusco desde el suelo.", "Extensión anticipada de la espalda.",
    "Cadera que sube demasiado pronto.", "Espalda flexionada.", "Barra por delante de la punta del pie."],
   ["Ritmo: lento al despegar, explosivo después.", "Barra cerca del cuerpo."],
   seguridad="Aprende con barra vacía o pica y supervisión de un entrenador.")

ej("ex_envion", "Envión (clean & jerk)", "pesas", "halterofilia", 5, "dinamico",
   ["mg_cuadriceps", "mg_gluteos", "mg_femoral", "mg_hombros"], ["mg_triceps", "mg_trapecio", "mg_core"], OLY,
   ["ex_sentadilla_frontal", "ex_peso_muerto"], [],
   "Dos tiempos: cargada (clin) al pecho y envión desde el pecho hasta encima de la cabeza.",
   ["Clin: halón con agarre al ancho de hombros y recibir la barra en los hombros en cuclillas.",
    "Ponte de pie y adopta la posición inicial del envión.",
    "Semiflexión-saque: flexión corta de rodillas y extensión explosiva.",
    "Desliz en tijera bajo la barra con brazos bloqueados.", "Junta los pies estabilizando."],
   ["Pies juntos o rodillas juntas en la posición inicial.", "Semiflexión profunda o lenta.",
    "Empujar con los brazos antes que con las piernas."],
   ["La fuerza del envión nace en las piernas."],
   seguridad="Aprende con barra vacía y supervisión de un entrenador.")


def exercise_ids():
    return {e["id"] for e in EXERCISES}
