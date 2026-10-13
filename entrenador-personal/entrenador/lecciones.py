"""Lecciones de la sección de Aprendizaje (teoría + mini-quiz).

Resúmenes propios de las ideas principales de los libros:
- Guía Completa de Calistenia y Street Workout (calentamiento, métodos,
  diseño de rutinas, progresiones, lesiones, manos).
- B. Schoenfeld, Ciencia y desarrollo de la hipertrofia muscular.
- W. Martínez, La ciencia de la hipertrofia (tensión mecánica / estrés
  metabólico, frecuencia 2, periodización por rangos).
- Peña Fernández et al., Levantamiento de pesas (tonelaje, IMR, zonas).
- N. Sosa Chavez, Cuerpos de calistenia (submodalidades).

Cada lección: id, titulo, categoria, fuente, resumen, puntos (lista),
quiz (lista de (pregunta, [opciones], índice_correcto, explicación)).
"""

LESSONS = [
    {
        "id": "lec_calentamiento",
        "titulo": "Calentamiento y estiramientos",
        "categoria": "Fundamentos",
        "fuente": "Guía Completa de Calistenia y Street Workout",
        "resumen": "Un calentamiento de ~15 minutos en tres partes, antes de cada sesión, "
                   "mejora el rendimiento y previene lesiones.",
        "puntos": [
            "1) Movilidad articular: 10 movimientos (5 por lado) de muñecas, codos, hombros, "
            "escápulas, cuello, cintura, cadera, rodillas y tobillos.",
            "2) Estiramientos cortos: 2 × 6 s de hombros, trapecios, bíceps, dorsal, isquios y abductores.",
            "3) Ejercicios fáciles: 5 repeticiones de 3 ejercicios sencillos (ej. flexiones con "
            "rodillas, fondos cortos, australian chin ups). Incluye al menos uno de empuje y uno de tirón.",
            "Después de entrenar: repite los estiramientos pero largos (2 × 15 s o más).",
            "Regla del libro: nunca entrenar sin haber calentado.",
        ],
        "quiz": [
            ("¿Cuánto dura aproximadamente el calentamiento recomendado?",
             ["5 minutos", "15 minutos", "40 minutos"], 1,
             "La guía propone unos 15 minutos divididos en tres partes."),
            ("¿Qué tipo de estiramiento va DESPUÉS de entrenar?",
             ["Cortos de 6 s", "Largos de 15 s o más", "Ninguno"], 1,
             "Antes: cortos (6 s). Después: largos (15 s o más)."),
        ],
    },
    {
        "id": "lec_progresiones",
        "titulo": "Cadenas de progresión y dificultad (💪)",
        "categoria": "Fundamentos",
        "fuente": "Guía Completa de Calistenia y Street Workout",
        "resumen": "Cada ejercicio tiene una dificultad de 1 a 5 💪, ejercicios previos "
                   "('progresiones para conseguirlo') y siguientes ('sirve de progresión para').",
        "puntos": [
            "Empieza por los ejercicios más fáciles de cada bloque y mejóralos hasta dominarlos.",
            "Ejemplo de criterio: 4 series de 20 flexiones antes de pasar a variantes más difíciles.",
            "En cada sesión intenta superar las repeticiones (o segundos) de la vez anterior y anótalo.",
            "Rangos orientativos: bajas 1-8, medias 8-20, altas >20 repeticiones. "
            "A mayor dificultad del ejercicio, menos repeticiones.",
            "En la Biblioteca de técnica puedes navegar la cadena completa: pulsa un ejercicio "
            "previo o siguiente para ver su técnica.",
        ],
        "quiz": [
            ("Según la guía, ¿qué es razonable antes de pasar de flexiones a variantes difíciles?",
             ["1 serie de 5", "4 series de 20", "Hacerlas al fallo cada día"], 1,
             "El ejemplo de la guía es 4×20 flexiones."),
            ("Las repeticiones 'medias' están entre…",
             ["1 y 8", "8 y 20", "20 y 50"], 1, "Bajas 1-8, medias 8-20, altas más de 20."),
        ],
    },
    {
        "id": "lec_tension_estres",
        "titulo": "Tensión mecánica vs. estrés metabólico",
        "categoria": "Hipertrofia",
        "fuente": "W. Martínez · B. Schoenfeld",
        "resumen": "Dos caminos principales hacia la hipertrofia: cargas altas con pocas "
                   "repeticiones (tensión mecánica) y cargas moderadas con muchas (estrés metabólico).",
        "puntos": [
            "Tensión mecánica: cerca del 1RM, pocas repeticiones (≈3-8). Más fuerza y crecimiento.",
            "Estrés metabólico: cargas bajas-moderadas, muchas repeticiones (≈12-30), "
            "descansos cortos, sensación de 'bombeo'.",
            "Cuanto más cerca del RM, más tensión mecánica; cuanto más lejos, más estrés metabólico.",
            "El 1RM puro (100 %) no es lo más interesante para crecer; 3-5 repeticiones ya dan "
            "adaptación neural, fuerza e hipertrofia.",
            "Lo práctico es combinar ambos durante la semana (ver lección Frecuencia 2).",
        ],
        "quiz": [
            ("Un trabajo de 25 repeticiones con descanso corto busca sobre todo…",
             ["Tensión mecánica", "Estrés metabólico", "Fuerza máxima"], 1,
             "Muchas repeticiones con carga moderada → estrés metabólico."),
            ("¿Es necesario entrenar al 100 % del 1RM para ganar músculo?",
             ["Sí, siempre", "No; 3-5 reps ya generan hipertrofia"], 1,
             "Martínez destaca que el 1RM puro no es lo más interesante para la hipertrofia."),
        ],
    },
    {
        "id": "lec_volumen",
        "titulo": "Volumen semanal: 10-20 series por músculo",
        "categoria": "Hipertrofia",
        "fuente": "B. Schoenfeld",
        "resumen": "El volumen es uno de los motores principales del crecimiento muscular.",
        "puntos": [
            "Cuenta las series efectivas (sin calentamiento) por grupo muscular y semana.",
            "Rango orientativo: 10-20 series semanales por grupo muscular.",
            "Menos de 10: probablemente te quedas corto. Más de 20: vigila la recuperación.",
            "La app cuenta 1 serie para cada músculo PRIMARIO del ejercicio. Míralo en Inicio.",
            "Sube el volumen poco a poco (1-2 series por semana) y haz una descarga si te estancas.",
        ],
        "quiz": [
            ("¿Qué rango semanal de series por músculo usa la app como referencia?",
             ["3-5", "10-20", "30-40"], 1, "Rango de Schoenfeld: 10-20 series semanales."),
            ("¿Las series de calentamiento cuentan para el volumen?",
             ["Sí", "No"], 1, "Sólo cuentan las series efectivas."),
        ],
    },
    {
        "id": "lec_frecuencia2",
        "titulo": "Frecuencia 2 y periodización por rangos",
        "categoria": "Hipertrofia",
        "fuente": "W. Martínez, La ciencia de la hipertrofia",
        "resumen": "Entrenar cada grupo muscular 2 veces por semana es uno de los mejores "
                   "puntos de partida.",
        "puntos": [
            "Primera parte de la semana: tensión mecánica. Segunda parte: estrés metabólico.",
            "Ejemplo pectoral: lunes fuerza, jueves bombeo.",
            "Bloque de 8 semanas en tensión mecánica: S1-S2 10-12 reps → S3-S4 8-10 → "
            "S5-S6 6-8 → S7 4-6 → S8 3-5 (subiendo la carga).",
            "En paralelo, el día de estrés metabólico va de 12-15 hasta 25-30 repeticiones.",
            "Periodizar sólo cambiando el rango de repeticiones ya ayuda a romper estancamientos.",
        ],
        "quiz": [
            ("En frecuencia 2, ¿cuántas veces por semana se entrena cada músculo?",
             ["1", "2", "4"], 1, "Frecuencia 2 = dos estímulos semanales por grupo."),
            ("En el ejemplo de 8 semanas, ¿en qué rango terminas la semana 8 del día de fuerza?",
             ["10-12", "6-8", "3-5"], 2, "Se empieza en 10-12 y se termina en 3-5 repeticiones."),
        ],
    },
    {
        "id": "lec_rir",
        "titulo": "RIR: repeticiones en reserva",
        "categoria": "Intensidad",
        "fuente": "B. Schoenfeld · práctica habitual",
        "resumen": "RIR es cuántas repeticiones más podrías haber hecho con buena técnica.",
        "puntos": [
            "RIR 0 = fallo; RIR 2 = te sobraban 2 repeticiones.",
            "Para hipertrofia la mayoría de series rinden bien entre RIR 0 y 3.",
            "Ir siempre al fallo acumula fatiga, sobre todo en ejercicios multiarticulares pesados.",
            "Anota el RIR en cada serie: la app calcula tu RIR medio por sesión.",
            "Si tu RIR medio baja a 0-1 durante varias semanas seguidas, considera una descarga.",
        ],
        "quiz": [
            ("Si terminas una serie y podrías haber hecho 2 más, tu RIR es…",
             ["0", "2", "10"], 1, "RIR = repeticiones que quedaban en reserva."),
        ],
    },
    {
        "id": "lec_zonas",
        "titulo": "Zonas de intensidad, tonelaje e IMR",
        "categoria": "Intensidad",
        "fuente": "Peña Fernández et al., Levantamiento de pesas",
        "resumen": "Cómo cuantificar la carga de las pesas.",
        "puntos": [
            "Tonelaje = Σ (repeticiones × peso). Mide el trabajo total de la sesión o semana.",
            "Peso medio (PM) = tonelaje / repeticiones totales.",
            "IMR (intensidad media relativa) = PM × 100 / 1RM.",
            "Zonas (I. Román, 1996): hasta 60 % mínima · 61-70 % pequeña · 71-80 % media · "
            "81-90 % grande · más de 90 % submáxima y máxima.",
            "1RM estimado (Epley) = peso × (1 + reps / 30). La app lo calcula sola.",
        ],
        "quiz": [
            ("3 series de 10 con 50 kg suman un tonelaje de…",
             ["150 kg", "500 kg", "1500 kg"], 2, "3 × 10 × 50 = 1500 kg."),
            ("Trabajar al 85 % del 1RM está en la zona…",
             ["Media", "Grande", "Mínima"], 1, "81-90 % es la zona grande."),
        ],
    },
    {
        "id": "lec_metodos",
        "titulo": "Métodos de entrenamiento en calistenia",
        "categoria": "Planificación",
        "fuente": "Guía Completa de Calistenia y Street Workout",
        "resumen": "Siete formas de organizar tus sesiones, con sus pros y contras.",
        "puntos": [
            "Vuelta al mundo: dominadas, fondos, flexiones y sentadillas en circuito al ~60 % casi a diario.",
            "Grupos musculares: un grupo (o dos) por día, o tirón/empuje. Muy bueno para el físico.",
            "Full body: 6 ejercicios × 4 series (espalda-bíceps, pecho-tríceps, pierna, abdominales "
            "y 2 de hombro-tríceps).",
            "Por objetivos: practica el truco elegido 3 veces por semana (front lever, bandera…).",
            "Lastrado: básicos con peso añadido. Mucha fuerza, pero empieza con muy poco lastre.",
            "Resistencia (Beast Mode): volúmenes de repeticiones muy altos; no para principiantes.",
            "Mixto: primero técnica/freestyle y después parte física.",
            "Consejo: no cambies de método antes de un mes.",
        ],
        "quiz": [
            ("¿Cuánto tiempo mínimo recomienda la guía antes de cambiar de método?",
             ["Una semana", "Un mes", "Un año"], 1, "No cambies de tipo de rutina antes de un mes."),
            ("¿Qué método es más eficaz para conseguir un truco concreto?",
             ["Vuelta al mundo", "Por objetivos", "Resistencia"], 1,
             "El entrenamiento por objetivos practica el truco al menos 3 veces por semana."),
        ],
    },
    {
        "id": "lec_diseno",
        "titulo": "Cómo diseñar tu rutina",
        "categoria": "Planificación",
        "fuente": "Guía Completa de Calistenia y Street Workout",
        "resumen": "Estructura sencilla que funciona.",
        "puntos": [
            "Entrena entre 3 y 6 veces por semana, nunca menos de 3.",
            "Sesión: calentamiento → (técnica/freestyle si es mixto) → parte principal de 45 min a 2 h.",
            "Descansos de 45 s a 2 min 30 s según cansancio y dificultad.",
            "Fórmula de partida: 6 ejercicios × 4 series con repeticiones exigentes.",
            "Elige ejercicios según tu nivel; empieza por los fáciles y progresa por la cadena.",
            "Semana de descarga cada pocos meses, tras varias semanas duras.",
        ],
        "quiz": [
            ("¿Cuántos ejercicios y series propone la guía como base?",
             ["3 × 2", "6 × 4", "10 × 10"], 1, "6 ejercicios a 4 series cada uno."),
        ],
    },
    {
        "id": "lec_lesiones",
        "titulo": "Prevenir dolores y lesiones",
        "categoria": "Salud",
        "fuente": "Guía Completa de Calistenia y Street Workout",
        "resumen": "Los tendones y ligamentos se adaptan más despacio que los músculos.",
        "puntos": [
            "Trabaja la movilidad y flexibilidad tanto como la fuerza (muñecas y bíceps para planchas, "
            "hombros para muscle up, escápulas para front lever).",
            "Regla del mes y medio: haz al menos 1,5 meses de progresiones fáciles antes de pasar "
            "a las difíciles, y otro 1,5 antes del movimiento final.",
            "Muscle up: cuando lo consigas, no más de 2-3 al día durante un tiempo.",
            "Si te lesionas: cúrate del todo, sigue a tu médico/fisio y vuelve a empezar desde las "
            "progresiones fáciles, dejando el ego de lado.",
            "Busca información ANTES de lesionarte, no después.",
        ],
        "quiz": [
            ("¿Qué se adapta más despacio al entrenamiento?",
             ["Los músculos", "Tendones y ligamentos"], 1,
             "Por eso hay que progresar con paciencia aunque haya fuerza suficiente."),
            ("Recién conseguido el muscle up, ¿cuántos al día como máximo sugiere la guía?",
             ["2-3", "10-15", "Los que salgan"], 0, "No más de 2-3 al día al principio."),
        ],
    },
    {
        "id": "lec_manos",
        "titulo": "Cuidado de las manos y callos",
        "categoria": "Salud",
        "fuente": "Guía Completa de Calistenia y Street Workout",
        "resumen": "Callos duros pero planos evitan que la piel se arranque en la barra.",
        "puntos": [
            "Si un callo sobresale como una 'bola', recorta sólo la piel muerta.",
            "Crema hidratante por la noche.",
            "Antes de entrenar, lima los callos para dejarlos lisos.",
            "Si la mano está muy irritada, para: forzar te impedirá entrenar al día siguiente.",
        ],
        "quiz": [
            ("¿Qué tipo de callo es el ideal?",
             ["Grueso y sobresaliente", "Duro pero plano", "Ninguno"], 1,
             "Duro para que la piel no se pliegue, pero plano para que no se enganche."),
        ],
    },
    {
        "id": "lec_submodalidades",
        "titulo": "Submodalidades y cultura de la calistenia",
        "categoria": "Cultura",
        "fuente": "N. Sosa Chavez, Cuerpos de calistenia · Guía Completa",
        "resumen": "La calistenia no es sólo estética: es comunidad, territorio y aprendizaje.",
        "puntos": [
            "Básicos: flexiones, fondos y dominadas con tu propio peso; el punto de partida infravalorado.",
            "Lastre: básicos con peso extra; más hipertrofia y fuerza absoluta.",
            "Tensión o estáticos: pino, planchas, levers. 'Mantener una posición es fruto de mucho "
            "entrenamiento, coordinación y técnica.'",
            "Dinámicos: combos en barras con giros, saltos y cambios de barra.",
            "Freestyle: pasadas de ~1 minuto combinando todo con fluidez y originalidad.",
            "Reto clásico de la comunidad: ¿10 dominadas explosivas limpias, 10 fondos y tu primer muscle up?",
            "Graba tus progresos: el registro audiovisual forma parte de la práctica.",
        ],
        "quiz": [
            ("¿Qué submodalidad incluye pino, planchas y levers?",
             ["Lastre", "Tensión o estáticos", "Freestyle"], 1,
             "Las posiciones mantenidas forman la submodalidad de tensión."),
        ],
    },
    {
        "id": "lec_descarga",
        "titulo": "Descarga (deload) y recuperación",
        "categoria": "Planificación",
        "fuente": "Guía Completa · W. Martínez",
        "resumen": "Bajar la carga a propósito para volver más fuerte.",
        "puntos": [
            "Tras varias semanas entrenando muchos días y duro, haz una semana de descarga.",
            "En la descarga reduce el volumen (≈40-50 % de las series) y aleja el fallo (RIR 3-4).",
            "Señales: estancamiento, RIR medio muy bajo varias semanas, más de 20 series por músculo, "
            "dolores articulares, mal sueño.",
            "La app te sugiere descarga si encadenas 6 semanas duras o superas 20 series en un músculo.",
            "Registra sueño, energía y ánimo en cada sesión para detectar la fatiga a tiempo.",
        ],
        "quiz": [
            ("¿Qué se reduce principalmente en una semana de descarga?",
             ["El volumen", "El calentamiento", "Las horas de sueño"], 0,
             "Se reducen series y esfuerzo para disipar fatiga."),
        ],
    },
]


def lesson_ids():
    return {l["id"] for l in LESSONS}
