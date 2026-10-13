"""Fórmulas de carga y progreso (funciones puras, sin base de datos).

Fuentes:
- Tonelaje, peso medio, IMR y zonas de intensidad: Peña Fernández et al.,
  "Levantamiento de pesas" (zonas de Iván Román, 1996).
- Volumen semanal por grupo muscular (10-20 series): Schoenfeld.
- Frecuencia 2 y periodización por rangos de repeticiones: W. Martínez.
- 1RM estimado: fórmula de Epley.
"""
from datetime import date, timedelta


def epley_1rm(weight_kg, reps):
    """1RM estimado (Epley). Sólo fiable entre 1 y 12 repeticiones."""
    if not weight_kg or not reps or weight_kg <= 0 or reps <= 0:
        return None
    if reps == 1:
        return round(float(weight_kg), 1)
    if reps > 12:
        return None
    return round(weight_kg * (1 + reps / 30.0), 1)


def working_sets(sets):
    """Series efectivas: excluye calentamiento."""
    return [s for s in sets if not s.get("is_warmup")]


def tonnage(sets):
    """Σ reps × peso de las series efectivas (kg)."""
    return round(sum((s.get("reps") or 0) * (s.get("weight_kg") or 0)
                     for s in working_sets(sets)), 1)


def best_e1rm(sets):
    vals = [epley_1rm(s.get("weight_kg"), s.get("reps")) for s in working_sets(sets)]
    vals = [v for v in vals if v]
    return max(vals) if vals else None


def peso_medio(sets):
    """Peso medio levantado = tonelaje / repeticiones totales."""
    ws = [s for s in working_sets(sets) if (s.get("weight_kg") or 0) > 0]
    reps = sum(s.get("reps") or 0 for s in ws)
    if not reps:
        return None
    return round(tonnage(ws) / reps, 1)


def imr(sets, one_rm):
    """Intensidad media relativa (%) = peso medio × 100 / 1RM."""
    pm = peso_medio(sets)
    if not pm or not one_rm:
        return None
    return round(pm * 100.0 / one_rm, 1)


# Zonas de intensidad (Iván Román, 1996) en % del 1RM.
ZONAS_INTENSIDAD = [
    (0, 60, "Mínima", "Técnica, calentamiento, resistencia"),
    (60, 70, "Pequeña", "Resistencia muscular / estrés metabólico"),
    (70, 80, "Media", "Hipertrofia"),
    (80, 90, "Grande", "Fuerza-hipertrofia (tensión mecánica)"),
    (90, 1000, "Submáxima y máxima", "Fuerza máxima"),
]


def intensity_zone(pct):
    if pct is None:
        return None
    for lo, hi, name, _ in ZONAS_INTENSIDAD:
        if lo <= pct < hi:
            return name
    return ZONAS_INTENSIDAD[-1][2]


def zona_por_reps(reps):
    """Orientación de Martínez: 1-6 fuerza, 6-15 hipertrofia, >15 resistencia."""
    if not reps:
        return None
    if reps <= 6:
        return "fuerza"
    if reps <= 15:
        return "hipertrofia"
    return "resistencia"


def avg_rir(sets):
    vals = [s["rir"] for s in working_sets(sets) if s.get("rir") is not None]
    return round(sum(vals) / len(vals), 1) if vals else None


def density(work_seconds, total_seconds):
    if not total_seconds:
        return None
    return round(work_seconds / total_seconds, 2)


VOLUMEN_MIN, VOLUMEN_MAX = 10, 20


def estado_volumen(series):
    """Compara series semanales de un músculo con el rango 10-20."""
    if series < VOLUMEN_MIN:
        return "bajo"
    if series > VOLUMEN_MAX:
        return "alto"
    return "óptimo"


def week_start(d, week_starts_on="monday"):
    if isinstance(d, str):
        d = date.fromisoformat(d[:10])
    offset = d.weekday() if week_starts_on == "monday" else (d.weekday() + 1) % 7
    return d - timedelta(days=offset)


def streaks(session_dates, today=None, max_gap_days=3):
    """Rachas de entrenamiento.

    Una racha sigue viva mientras entre dos sesiones no haya más de
    `max_gap_days` días (permite 1-2 días de descanso, como recomiendan los
    libros: entrenar 3-6 veces por semana). Devuelve (actual, máxima) en días
    transcurridos desde el inicio de la racha.
    """
    today = today or date.today()
    days = sorted({date.fromisoformat(str(d)[:10]) for d in session_dates})
    if not days:
        return 0, 0
    best = cur = 1
    start = days[0]
    for prev, d in zip(days, days[1:]):
        if (d - prev).days <= max_gap_days:
            cur = (d - start).days + 1
        else:
            start = d
            cur = 1
        best = max(best, cur)
    current = cur if (today - days[-1]).days <= max_gap_days else 0
    return current, best


def weekly_compliance(sessions_this_week, target_days):
    if not target_days:
        return 0
    return min(100, round(sessions_this_week * 100 / target_days))
