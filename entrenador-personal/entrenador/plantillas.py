"""Rutinas de ejemplo que se crean en el primer arranque."""


def _day(db, rid, label, focus, items):
    did = db.add_routine_day(rid, label, focus)
    for it in items:
        ex, sets, rmin, rmax, rest = it[:5]
        rir = it[5] if len(it) > 5 else 2
        notes = it[6] if len(it) > 6 else ""
        db.add_routine_exercise(did, ex, sets, rmin, rmax, rest, "rir", rir, "", notes)


def seed_routines(db):
    # Nivel 0 (pre-principiante) — Guía de Calistenia: versiones fáciles de cada bloque.
    rid = db.add_routine("Nivel 0 · Pre-principiante", "full_body", "habilidad", 3, 45,
                         "Versiones más sencillas de cada bloque. Haz al menos 1,5 meses antes de "
                         "pasar a los básicos completos.", rid="rt_nivel0")
    _day(db, rid, "Día único", ["empuje", "tiron", "pierna", "core"], [
        ("ex_flexiones_inclinadas", 4, 8, 15, 90),
        ("ex_australian_pullups", 4, 6, 12, 90),
        ("ex_fondos_banco", 4, 6, 12, 90),
        ("ex_sentadilla_asistida", 4, 10, 15, 90),
        ("ex_dead_hang", 3, 15, 30, 90, 2, "Segundos colgado."),
        ("ex_plancha_abdominal", 3, 20, 40, 60, 2, "Segundos."),
    ])

    # Full body 6×4 — fórmula de la guía: espalda-bíceps, pecho-tríceps, pierna, abs, 2 hombro-tríceps.
    rid = db.add_routine("Full Body Principiante (6×4)", "full_body", "hipertrofia", 3, 60,
                         "6 ejercicios a 4 series. Progresa cuando completes 4×15 limpias.",
                         rid="rt_fullbody_principiante")
    _day(db, rid, "Día A", ["empuje", "tiron", "pierna", "core"], [
        ("ex_dominadas_pronas", 4, 5, 8, 120, 2, "Si aún no salen: negativas."),
        ("ex_flexiones", 4, 8, 15, 90, 2, "Progresar a declinadas cuando 4×15 limpias."),
        ("ex_sentadilla", 4, 12, 20, 90),
        ("ex_plancha_abdominal", 4, 30, 45, 60, 2, "Segundos."),
        ("ex_pike_push_ups", 4, 6, 10, 90),
        ("ex_fondos", 4, 6, 12, 90),
    ])
    _day(db, rid, "Día B", ["empuje", "tiron", "pierna", "core"], [
        ("ex_dominadas_supinas", 4, 5, 8, 120),
        ("ex_flexiones_diamante", 4, 8, 12, 90),
        ("ex_zancadas", 4, 10, 12, 90),
        ("ex_knee_raises_barra", 4, 8, 12, 60),
        ("ex_flexiones_declinadas", 4, 8, 12, 90),
        ("ex_pino_pared", 4, 15, 30, 90, 2, "Segundos."),
    ])

    # Frecuencia 2 (Martínez): torso/pierna, tensión mecánica al inicio de semana, estrés metabólico después.
    rid = db.add_routine("Frecuencia 2 · Torso / Pierna", "grupos", "hipertrofia", 4, 70,
                         "Lunes-martes: tensión mecánica (6-10 reps). Jueves-viernes: estrés metabólico "
                         "(12-20 reps). Ajusta los rangos cada 2 semanas (ver lección Frecuencia 2).",
                         rid="rt_frecuencia2")
    _day(db, rid, "Torso A · tensión", ["empuje", "tiron"], [
        ("ex_press_banca", 4, 6, 8, 150, 2),
        ("ex_dominadas_pronas", 4, 6, 8, 150, 2, "Con lastre si superas 10 reps."),
        ("ex_press_militar", 3, 6, 8, 120, 2),
        ("ex_remo_barra", 3, 6, 8, 120, 2),
        ("ex_fondos", 3, 6, 10, 120, 2, "Lastrados si es posible."),
    ])
    _day(db, rid, "Pierna A · tensión", ["pierna", "core"], [
        ("ex_sentadilla_barra", 4, 6, 8, 180, 2),
        ("ex_peso_muerto_rumano", 3, 6, 8, 150, 2),
        ("ex_bulgarian_squat", 3, 8, 10, 120, 2),
        ("ex_levantamiento_gemelos", 4, 8, 12, 90, 1),
        ("ex_leg_raises_barra", 3, 8, 12, 90, 2),
    ])
    _day(db, rid, "Torso B · metabólico", ["empuje", "tiron"], [
        ("ex_flexiones", 4, 15, 25, 60, 1),
        ("ex_australian_pullups", 4, 12, 20, 60, 1),
        ("ex_elevaciones_laterales", 4, 15, 20, 45, 1),
        ("ex_curl_biceps", 3, 12, 15, 45, 1),
        ("ex_extension_triceps", 3, 12, 15, 45, 1),
    ])
    _day(db, rid, "Pierna B · metabólico", ["pierna", "core"], [
        ("ex_sentadilla", 4, 20, 30, 60, 1),
        ("ex_hip_thrust", 4, 12, 15, 75, 1),
        ("ex_curl_femoral_pc", 3, 12, 15, 60, 1),
        ("ex_zancadas", 3, 15, 20, 60, 1),
        ("ex_plancha_lateral", 3, 30, 45, 45, 2, "Segundos por lado."),
    ])

    # Por objetivos: muscle up (progresión de la guía).
    rid = db.add_routine("Objetivo · Muscle up", "objetivos", "habilidad", 3, 60,
                         "Lunes, miércoles y viernes. Requisito: 10 dominadas explosivas y fondos en barra. "
                         "Al conseguirlo, no más de 2-3 muscle ups al día.", rid="rt_obj_muscleup")
    _day(db, rid, "Sesión objetivo", ["tiron", "empuje"], [
        ("ex_dominadas_explosivas", 4, 3, 6, 150, 1),
        ("ex_fondos_barra", 4, 6, 10, 120, 2),
        ("ex_muscle_up_salto", 4, 3, 5, 120, 2, "Aprende la transición."),
        ("ex_muscle_up_pierna", 3, 3, 5, 120, 2),
        ("ex_dominadas_pronas", 3, 6, 10, 120, 2),
        ("ex_leg_raises_barra", 3, 8, 12, 90, 2),
    ])
