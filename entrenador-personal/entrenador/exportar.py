"""Exportación (JSON completo / CSV por tabla), importación y copias de seguridad."""
import csv
import json
import shutil
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from . import APP_VERSION, EXPORT_VERSION, metricas

# Tablas que se respaldan/restauran tal cual en el JSON completo.
RAW_TABLES = [
    "user_profile", "settings", "exercise", "exercise_muscle", "exercise_equipment",
    "progression_link", "routine", "routine_day", "routine_exercise", "session",
    "session_exercise", "set_log", "schedule_day", "body_measurement", "progress_photo",
    "personal_record", "goal", "goal_milestone", "achievement", "learning_progress",
]


def export_json(db, path):
    cur, best = db.streaks()
    wso = db.get_setting("week_starts_on", "monday")
    ws = metricas.week_start(date.today(), wso)
    target = int(db.get_setting("target_days_per_week", "3") or 3)
    last = db.q1("SELECT MAX(date) d FROM session")["d"]
    data = {
        "export_version": EXPORT_VERSION,
        "exported_at": datetime.now().replace(microsecond=0).isoformat(),
        "app_version": APP_VERSION,
        "user_profile": db.profile(),
        "settings": db.settings(),
        "exercises": [db.exercise(e["id"]) for e in db.exercises()],
        "routines": [
            {**r, "days": [{**d, "exercises": db.routine_exercises(d["id"])} for d in db.routine_days(r["id"])]}
            for r in db.routines()
        ],
        "sessions": [db.session_detail(s["id"]) for s in db.sessions()],
        "body_measurements": db.measurements(),
        "progress_photos": db.photos(),
        "personal_records": db.personal_records(),
        "goals": db.goals(),
        "achievements": db.achievements(),
        "streaks": {
            "current_workout_streak_days": cur,
            "longest_workout_streak_days": best,
            "current_week_compliance_pct": metricas.weekly_compliance(db.sessions_in_week(ws), target),
            "last_workout_date": last,
        },
        # Copia exacta de las tablas para poder restaurar sin pérdidas.
        "_raw": {t: db.q(f"SELECT * FROM {t}") for t in RAW_TABLES},
    }
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def import_json(db, path):
    """Restaura un respaldo JSON completo (reemplaza los datos actuales)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw = data.get("_raw")
    if not raw:
        raise ValueError("El archivo no es un respaldo completo de esta app.")
    c = db.conn
    c.execute("PRAGMA foreign_keys = OFF")
    try:
        for t in RAW_TABLES:
            rows = raw.get(t)
            if rows is None:
                continue
            c.execute(f"DELETE FROM {t}")
            for r in rows:
                cols = ", ".join(r.keys())
                marks = ", ".join("?" * len(r))
                c.execute(f"INSERT OR REPLACE INTO {t} ({cols}) VALUES ({marks})", tuple(r.values()))
        c.commit()
    finally:
        c.execute("PRAGMA foreign_keys = ON")
    db._seed()  # asegura catálogo y logros actualizados
    return True


def _write_csv(path, rows, cols=None):
    cols = cols or (list(rows[0].keys()) if rows else [])
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
                        for k, v in r.items()})


def export_csv(db, folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    _write_csv(folder / "sessions.csv", db.q("SELECT * FROM session ORDER BY date"),
               ["id", "date", "routine_id", "routine_day_id", "started_at", "ended_at", "duration_min",
                "bodyweight_kg", "sleep_hours", "energy_level", "mood", "tonnage_kg", "avg_rir", "notes"])
    _write_csv(folder / "sets.csv", db.q(
        "SELECT s.date, e.name exercise, e.id exercise_id, sl.set_number, sl.reps, sl.seconds, sl.weight_kg, "
        "sl.rir, sl.tempo, sl.rest_after_seconds, sl.is_warmup, sl.is_failure, sl.is_pr, sl.notes, "
        "s.id session_id FROM set_log sl JOIN session_exercise se ON se.id=sl.session_exercise_id "
        "JOIN session s ON s.id=se.session_id JOIN exercise e ON e.id=se.exercise_id "
        "ORDER BY s.date, se.ord, sl.set_number"),
        ["date", "exercise", "exercise_id", "set_number", "reps", "seconds", "weight_kg", "rir", "tempo",
         "rest_after_seconds", "is_warmup", "is_failure", "is_pr", "notes", "session_id"])
    ms = db.measurements()
    keys = sorted({k for m in ms for k in m["measurements"]})
    flat = [{**{k: v for k, v in m.items() if k != "measurements"}, **m["measurements"]} for m in ms]
    _write_csv(folder / "body_measurements.csv", flat,
               ["id", "date", "weight_kg", "body_fat_pct", "muscle_mass_kg", *keys, "notes"])
    _write_csv(folder / "personal_records.csv", db.personal_records(),
               ["date_achieved", "name", "exercise_id", "type", "value", "unit", "previous_value", "session_id"])
    wso = db.get_setting("week_starts_on", "monday")
    names = db.muscle_names()
    rows = []
    first = db.q1("SELECT MIN(date) d FROM session")["d"]
    if first:
        w = metricas.week_start(first, wso)
        end = metricas.week_start(date.today(), wso)
        while w <= end:
            for m, n in db.weekly_sets_by_muscle(w).items():
                rows.append({"week_start": w.isoformat(), "muscle_id": m, "muscle": names.get(m, m),
                             "sets": n, "estado": metricas.estado_volumen(n)})
            w += timedelta(weeks=1)
    _write_csv(folder / "weekly_volume.csv", rows, ["week_start", "muscle_id", "muscle", "sets", "estado"])
    return folder


def backup(db, backups_dir, force=False):
    """Copia db.sqlite a backups/ si pasaron `auto_backup_days` desde la última."""
    days = int(db.get_setting("auto_backup_days", "7") or 7)
    last = db.get_setting("last_backup", "")
    if not force and last:
        try:
            if date.today() - date.fromisoformat(last) < timedelta(days=days):
                return None
        except ValueError:
            pass
    backups_dir = Path(backups_dir)
    backups_dir.mkdir(parents=True, exist_ok=True)
    dest = backups_dir / f"db_{datetime.now():%Y-%m-%d_%H%M%S}.sqlite"
    target = sqlite3.connect(str(dest))
    with target:
        db.conn.backup(target)
    target.close()
    db.set_setting("last_backup", date.today().isoformat())
    # Conserva las 10 copias más recientes.
    for old in sorted(backups_dir.glob("db_*.sqlite"))[:-10]:
        old.unlink(missing_ok=True)
    return dest


def copy_photo(src, photos_dir, d, pose):
    src = Path(src)
    dest = Path(photos_dir) / f"{d}_{pose}{src.suffix.lower()}"
    i = 1
    while dest.exists():
        dest = Path(photos_dir) / f"{d}_{pose}_{i}{src.suffix.lower()}"
        i += 1
    shutil.copy2(src, dest)
    return dest
