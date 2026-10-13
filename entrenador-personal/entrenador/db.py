"""Capa de datos SQLite: esquema, catálogo, sesiones, récords, logros y aprendizaje."""
import json
import sqlite3
import uuid
from datetime import date, datetime, timedelta

from . import catalogo, lecciones, metricas

SCHEMA = """
CREATE TABLE IF NOT EXISTS user_profile (
    id TEXT PRIMARY KEY, name TEXT, birth_date TEXT, sex TEXT, height_cm REAL,
    experience_level TEXT, primary_focus TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS muscle_group (id TEXT PRIMARY KEY, name TEXT, parent TEXT);
CREATE TABLE IF NOT EXISTS equipment (id TEXT PRIMARY KEY, name TEXT, category TEXT);
CREATE TABLE IF NOT EXISTS exercise (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT, block TEXT,
    difficulty INTEGER, type TEXT, measure TEXT DEFAULT 'reps', unilateral INTEGER DEFAULT 0,
    description TEXT, notes TEXT, technique TEXT, video_url TEXT, custom INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS exercise_muscle (
    exercise_id TEXT, muscle_id TEXT, role TEXT, PRIMARY KEY (exercise_id, muscle_id)
);
CREATE TABLE IF NOT EXISTS exercise_equipment (
    exercise_id TEXT, equipment_id TEXT, PRIMARY KEY (exercise_id, equipment_id)
);
CREATE TABLE IF NOT EXISTS progression_link (
    from_id TEXT, to_id TEXT, PRIMARY KEY (from_id, to_id)
);
CREATE TABLE IF NOT EXISTS routine (
    id TEXT PRIMARY KEY, name TEXT, method TEXT, goal TEXT, days_per_week INTEGER,
    estimated_duration_min INTEGER, notes TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS routine_day (
    id TEXT PRIMARY KEY, routine_id TEXT REFERENCES routine(id) ON DELETE CASCADE,
    day_label TEXT, ord INTEGER, focus TEXT
);
CREATE TABLE IF NOT EXISTS routine_exercise (
    id TEXT PRIMARY KEY, day_id TEXT REFERENCES routine_day(id) ON DELETE CASCADE,
    exercise_id TEXT, ord INTEGER, planned_sets INTEGER, planned_reps_min INTEGER,
    planned_reps_max INTEGER, planned_rest_seconds INTEGER, intensity_type TEXT,
    intensity_value REAL, tempo TEXT, notes TEXT
);
CREATE TABLE IF NOT EXISTS session (
    id TEXT PRIMARY KEY, date TEXT, routine_id TEXT, routine_day_id TEXT,
    started_at TEXT, ended_at TEXT, duration_min INTEGER, bodyweight_kg REAL,
    sleep_hours REAL, energy_level INTEGER, mood INTEGER, notes TEXT,
    tonnage_kg REAL DEFAULT 0, avg_rir REAL
);
CREATE TABLE IF NOT EXISTS session_exercise (
    id TEXT PRIMARY KEY, session_id TEXT REFERENCES session(id) ON DELETE CASCADE,
    exercise_id TEXT, ord INTEGER, tonnage_kg REAL, estimated_1rm_kg REAL
);
CREATE TABLE IF NOT EXISTS set_log (
    id TEXT PRIMARY KEY,
    session_exercise_id TEXT REFERENCES session_exercise(id) ON DELETE CASCADE,
    set_number INTEGER, reps INTEGER, seconds INTEGER, weight_kg REAL, rir INTEGER,
    tempo TEXT, rest_after_seconds INTEGER, is_warmup INTEGER DEFAULT 0,
    is_failure INTEGER DEFAULT 0, is_pr INTEGER DEFAULT 0, notes TEXT
);
CREATE TABLE IF NOT EXISTS schedule_day (
    date TEXT PRIMARY KEY, routine_day_id TEXT, status TEXT, session_id TEXT
);
CREATE TABLE IF NOT EXISTS body_measurement (
    id TEXT PRIMARY KEY, date TEXT, weight_kg REAL, body_fat_pct REAL,
    muscle_mass_kg REAL, measurements TEXT, notes TEXT
);
CREATE TABLE IF NOT EXISTS progress_photo (
    id TEXT PRIMARY KEY, date TEXT, file_path TEXT, pose TEXT, weight_kg REAL,
    notes TEXT, tags TEXT
);
CREATE TABLE IF NOT EXISTS personal_record (
    id TEXT PRIMARY KEY, exercise_id TEXT, type TEXT, value REAL, unit TEXT,
    date_achieved TEXT, previous_value REAL, session_id TEXT
);
CREATE TABLE IF NOT EXISTS goal (
    id TEXT PRIMARY KEY, title TEXT, type TEXT, target_exercise_id TEXT,
    deadline TEXT, notes TEXT, created_at TEXT, done INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS goal_milestone (
    id TEXT PRIMARY KEY, goal_id TEXT REFERENCES goal(id) ON DELETE CASCADE,
    label TEXT, done INTEGER DEFAULT 0, ord INTEGER
);
CREATE TABLE IF NOT EXISTS achievement (
    id TEXT PRIMARY KEY, name TEXT, description TEXT, icon TEXT, unlocked_at TEXT
);
CREATE TABLE IF NOT EXISTS learning_progress (
    item_id TEXT PRIMARY KEY, kind TEXT, status TEXT, quiz_score REAL, updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_session_date ON session(date);
CREATE INDEX IF NOT EXISTS idx_se_session ON session_exercise(session_id);
CREATE INDEX IF NOT EXISTS idx_set_se ON set_log(session_exercise_id);
"""

DEFAULT_SETTINGS = {
    "units": "metric",
    "default_rest_seconds": "90",
    "week_starts_on": "monday",
    "theme": "light",
    "auto_backup_days": "7",
    "export_format_default": "json",
    "target_days_per_week": "3",
    "last_backup": "",
}

# Estados de aprendizaje de un ejercicio (árbol de habilidades).
LEARN_STATES = ["pendiente", "aprendiendo", "dominado"]

ACHIEVEMENTS = [
    ("ach_primera_sesion", "Primer paso", "Registraste tu primera sesión.", "🏁"),
    ("ach_10_sesiones", "Constancia", "10 sesiones registradas.", "📅"),
    ("ach_50_sesiones", "Hábito de hierro", "50 sesiones registradas.", "🏋"),
    ("ach_racha_7", "Racha de 7 días", "Mantuviste una racha de 7 días.", "🔥"),
    ("ach_racha_30", "Racha de 30 días", "Mantuviste una racha de 30 días.", "🔥"),
    ("ach_100_dominadas_mes", "100 dominadas en un mes", "Sumaste 100 repeticiones de dominadas en 30 días.", "💪"),
    ("ach_1000_flexiones", "1000 flexiones", "Sumaste 1000 repeticiones de flexiones en total.", "💪"),
    ("ach_first_muscleup", "Primer muscle up", "Registraste tu primer muscle up.", "🚀"),
    ("ach_primer_pino", "Primer pino", "Aguantaste un pino libre.", "🤸"),
    ("ach_front_lever", "Front lever", "Aguantaste un front lever completo.", "🦅"),
    ("ach_primer_pr", "Primer récord", "Lograste tu primer récord personal.", "🏆"),
    ("ach_10_prs", "Coleccionista de récords", "10 récords personales.", "🏆"),
    ("ach_tonelaje_10t", "10 toneladas", "Moviste 10 000 kg en una semana.", "⚖"),
    ("ach_medidas", "Me mido", "Registraste tus medidas corporales.", "📏"),
    ("ach_5_lecciones", "Estudiante", "Completaste 5 lecciones.", "📘"),
    ("ach_todas_lecciones", "Teoría al día", "Completaste todas las lecciones.", "🎓"),
    ("ach_quiz_perfecto", "Quiz perfecto", "Acertaste todas las preguntas de un quiz.", "✅"),
    ("ach_5_dominados", "Técnica sólida", "Marcaste 5 ejercicios como dominados.", "⭐"),
]


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def now_iso():
    return datetime.now().replace(microsecond=0).isoformat()


class Database:
    def __init__(self, path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self._seed()

    def close(self):
        self.conn.close()

    # ───────────────────────── utilidades ─────────────────────────
    def q(self, sql, params=()):
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def q1(self, sql, params=()):
        r = self.conn.execute(sql, params).fetchone()
        return dict(r) if r else None

    def x(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    # ───────────────────────── semilla ─────────────────────────
    def _seed(self):
        c = self.conn
        for k, v in DEFAULT_SETTINGS.items():
            c.execute("INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)", (k, v))
        c.executemany("INSERT OR REPLACE INTO muscle_group VALUES (?, ?, ?)", catalogo.MUSCLE_GROUPS)
        c.executemany("INSERT OR REPLACE INTO equipment VALUES (?, ?, ?)", catalogo.EQUIPMENT)
        for e in catalogo.EXERCISES:
            self._upsert_exercise(e, custom=False, commit=False)
        valid = catalogo.exercise_ids()
        for e in catalogo.EXERCISES:
            for prev in e["progressions_to_reach"]:
                if prev in valid:
                    c.execute("INSERT OR IGNORE INTO progression_link VALUES (?, ?)", (prev, e["id"]))
            for nxt in e["progresses_to"]:
                if nxt in valid:
                    c.execute("INSERT OR IGNORE INTO progression_link VALUES (?, ?)", (e["id"], nxt))
        for aid, name, desc, icon in ACHIEVEMENTS:
            c.execute("INSERT OR IGNORE INTO achievement(id, name, description, icon) VALUES (?, ?, ?, ?)",
                      (aid, name, desc, icon))
            c.execute("UPDATE achievement SET name=?, description=?, icon=? WHERE id=?",
                      (name, desc, icon, aid))
        if not c.execute("SELECT 1 FROM user_profile").fetchone():
            c.execute("INSERT INTO user_profile(id, name, experience_level, primary_focus, created_at) "
                      "VALUES ('me', 'Atleta', 'principiante', ?, ?)",
                      (json.dumps(["calistenia", "hipertrofia"]), now_iso()))
        c.commit()
        if not c.execute("SELECT 1 FROM routine").fetchone():
            from .plantillas import seed_routines
            seed_routines(self)

    def _upsert_exercise(self, e, custom=False, commit=True):
        c = self.conn
        c.execute(
            "INSERT INTO exercise(id, name, category, block, difficulty, type, measure, unilateral, "
            "description, notes, technique, video_url, custom) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET name=excluded.name, category=excluded.category, "
            "block=excluded.block, difficulty=excluded.difficulty, type=excluded.type, "
            "measure=excluded.measure, unilateral=excluded.unilateral, "
            "description=excluded.description, technique=excluded.technique",
            (e["id"], e["name"], e["category"], e["block"], e["difficulty"], e["type"],
             e.get("measure", "reps"), int(bool(e.get("unilateral"))), e.get("description", ""),
             e.get("notes", ""), json.dumps(e.get("technique", {}), ensure_ascii=False),
             e.get("video_url"), int(custom)))
        c.execute("DELETE FROM exercise_muscle WHERE exercise_id=?", (e["id"],))
        for m in e.get("primary_muscles", []):
            c.execute("INSERT OR REPLACE INTO exercise_muscle VALUES (?, ?, 'primario')", (e["id"], m))
        for m in e.get("secondary_muscles", []):
            c.execute("INSERT OR IGNORE INTO exercise_muscle VALUES (?, ?, 'secundario')", (e["id"], m))
        c.execute("DELETE FROM exercise_equipment WHERE exercise_id=?", (e["id"],))
        for eq in e.get("equipment", []):
            c.execute("INSERT OR IGNORE INTO exercise_equipment VALUES (?, ?)", (e["id"], eq))
        if commit:
            c.commit()

    # ───────────────────────── ajustes / perfil ─────────────────────────
    def get_setting(self, key, default=None):
        r = self.q1("SELECT value FROM settings WHERE key=?", (key,))
        return r["value"] if r else default

    def set_setting(self, key, value):
        self.x("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, str(value)))

    def settings(self):
        return {r["key"]: r["value"] for r in self.q("SELECT * FROM settings")}

    def profile(self):
        p = self.q1("SELECT * FROM user_profile LIMIT 1") or {}
        if p.get("primary_focus"):
            try:
                p["primary_focus"] = json.loads(p["primary_focus"])
            except ValueError:
                p["primary_focus"] = [p["primary_focus"]]
        return p

    def save_profile(self, **kw):
        if "primary_focus" in kw and isinstance(kw["primary_focus"], list):
            kw["primary_focus"] = json.dumps(kw["primary_focus"])
        cols = ", ".join(f"{k}=?" for k in kw)
        self.x(f"UPDATE user_profile SET {cols} WHERE id='me'", tuple(kw.values()))

    # ───────────────────────── ejercicios ─────────────────────────
    def muscle_names(self):
        return {r["id"]: r["name"] for r in self.q("SELECT * FROM muscle_group")}

    def equipment_names(self):
        return {r["id"]: r["name"] for r in self.q("SELECT * FROM equipment")}

    def exercises(self, block=None, category=None, search=None, max_difficulty=None):
        sql, p = "SELECT * FROM exercise WHERE 1=1", []
        if block:
            sql += " AND block=?"
            p.append(block)
        if category:
            sql += " AND category=?"
            p.append(category)
        if max_difficulty:
            sql += " AND difficulty<=?"
            p.append(max_difficulty)
        if search:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            p += [f"%{search}%", f"%{search}%"]
        sql += " ORDER BY block, difficulty, name"
        return self.q(sql, p)

    def exercise(self, ex_id):
        e = self.q1("SELECT * FROM exercise WHERE id=?", (ex_id,))
        if not e:
            return None
        e["technique"] = json.loads(e["technique"] or "{}")
        ms = self.q("SELECT muscle_id, role FROM exercise_muscle WHERE exercise_id=?", (ex_id,))
        e["primary_muscles"] = [m["muscle_id"] for m in ms if m["role"] == "primario"]
        e["secondary_muscles"] = [m["muscle_id"] for m in ms if m["role"] == "secundario"]
        e["equipment"] = [r["equipment_id"] for r in
                          self.q("SELECT equipment_id FROM exercise_equipment WHERE exercise_id=?", (ex_id,))]
        e["progressions_to_reach"] = [r["from_id"] for r in
                                      self.q("SELECT from_id FROM progression_link WHERE to_id=?", (ex_id,))]
        e["progresses_to"] = [r["to_id"] for r in
                              self.q("SELECT to_id FROM progression_link WHERE from_id=?", (ex_id,))]
        return e

    def exercise_name(self, ex_id):
        r = self.q1("SELECT name FROM exercise WHERE id=?", (ex_id,))
        return r["name"] if r else ex_id

    def add_custom_exercise(self, data):
        data = dict(data)
        data.setdefault("id", new_id("ex"))
        data.setdefault("technique", {"pasos": [], "errores": [], "claves": [], "respiracion": "",
                                      "criterio_avance": "", "seguridad": ""})
        self._upsert_exercise(data, custom=True)
        for prev in data.get("progressions_to_reach", []):
            self.x("INSERT OR IGNORE INTO progression_link VALUES (?, ?)", (prev, data["id"]))
        for nxt in data.get("progresses_to", []):
            self.x("INSERT OR IGNORE INTO progression_link VALUES (?, ?)", (data["id"], nxt))
        return data["id"]

    def progression_chain(self, ex_id, depth=6):
        """Devuelve (anteriores, siguientes) recorriendo la cadena por niveles."""
        def walk(start, col_from, col_to):
            seen, frontier, levels = {start}, [start], []
            for _ in range(depth):
                nxt = []
                for f in frontier:
                    for r in self.q(f"SELECT {col_to} AS t FROM progression_link WHERE {col_from}=?", (f,)):
                        if r["t"] not in seen:
                            seen.add(r["t"])
                            nxt.append(r["t"])
                if not nxt:
                    break
                levels.append(nxt)
                frontier = nxt
            return levels
        return walk(ex_id, "to_id", "from_id"), walk(ex_id, "from_id", "to_id")

    # ───────────────────────── rutinas ─────────────────────────
    def routines(self):
        return self.q("SELECT * FROM routine ORDER BY created_at")

    def routine_days(self, routine_id):
        return self.q("SELECT * FROM routine_day WHERE routine_id=? ORDER BY ord", (routine_id,))

    def routine_exercises(self, day_id):
        return self.q("SELECT re.*, e.name, e.measure, e.category FROM routine_exercise re "
                      "JOIN exercise e ON e.id = re.exercise_id WHERE day_id=? ORDER BY ord", (day_id,))

    def add_routine(self, name, method="full_body", goal="hipertrofia", days_per_week=3,
                    estimated_duration_min=60, notes="", rid=None):
        rid = rid or new_id("rt")
        self.x("INSERT INTO routine VALUES (?,?,?,?,?,?,?,?)",
               (rid, name, method, goal, days_per_week, estimated_duration_min, notes, now_iso()))
        return rid

    def update_routine(self, rid, **kw):
        cols = ", ".join(f"{k}=?" for k in kw)
        self.x(f"UPDATE routine SET {cols} WHERE id=?", (*kw.values(), rid))

    def delete_routine(self, rid):
        self.x("DELETE FROM routine WHERE id=?", (rid,))

    def add_routine_day(self, routine_id, label, focus=None, did=None):
        did = did or new_id("rd")
        n = self.q1("SELECT COUNT(*) n FROM routine_day WHERE routine_id=?", (routine_id,))["n"]
        self.x("INSERT INTO routine_day VALUES (?,?,?,?,?)",
               (did, routine_id, label, n + 1, json.dumps(focus or [], ensure_ascii=False)))
        return did

    def delete_routine_day(self, did):
        self.x("DELETE FROM routine_day WHERE id=?", (did,))

    def add_routine_exercise(self, day_id, exercise_id, sets=4, reps_min=8, reps_max=12, rest=90,
                             intensity_type="rir", intensity_value=2, tempo="", notes=""):
        rid = new_id("re")
        n = self.q1("SELECT COUNT(*) n FROM routine_exercise WHERE day_id=?", (day_id,))["n"]
        self.x("INSERT INTO routine_exercise VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
               (rid, day_id, exercise_id, n + 1, sets, reps_min, reps_max, rest,
                intensity_type, intensity_value, tempo, notes))
        return rid

    def delete_routine_exercise(self, reid):
        self.x("DELETE FROM routine_exercise WHERE id=?", (reid,))

    def move_routine_exercise(self, reid, delta):
        row = self.q1("SELECT * FROM routine_exercise WHERE id=?", (reid,))
        other = self.q1("SELECT * FROM routine_exercise WHERE day_id=? AND ord=?",
                        (row["day_id"], row["ord"] + delta))
        if other:
            self.x("UPDATE routine_exercise SET ord=? WHERE id=?", (other["ord"], reid))
            self.x("UPDATE routine_exercise SET ord=? WHERE id=?", (row["ord"], other["id"]))

    # ───────────────────────── calendario ─────────────────────────
    def schedule_week(self, start):
        days = []
        for i in range(7):
            d = (start + timedelta(days=i)).isoformat()
            row = self.q1("SELECT * FROM schedule_day WHERE date=?", (d,)) or {"date": d, "status": None}
            done = self.q1("SELECT id FROM session WHERE date=? LIMIT 1", (d,))
            if done:
                row["status"] = "completada"
                row["session_id"] = done["id"]
            days.append(row)
        return days

    def set_schedule(self, d, routine_day_id, status):
        self.x("INSERT OR REPLACE INTO schedule_day(date, routine_day_id, status) VALUES (?,?,?)",
               (d, routine_day_id, status))

    def clear_schedule(self, d):
        self.x("DELETE FROM schedule_day WHERE date=?", (d,))

    def routine_day_label(self, did):
        r = self.q1("SELECT rd.day_label, r.name FROM routine_day rd JOIN routine r ON r.id=rd.routine_id "
                    "WHERE rd.id=?", (did,))
        return f"{r['name']} · {r['day_label']}" if r else ""

    # ───────────────────────── sesiones ─────────────────────────
    def save_session(self, data):
        """Guarda una sesión completa y devuelve (session_id, nuevos_prs, nuevos_logros).

        data = {date, routine_id, routine_day_id, started_at, ended_at, bodyweight_kg,
                sleep_hours, energy_level, mood, notes,
                exercises: [{exercise_id, sets: [{reps, seconds, weight_kg, rir, tempo,
                             rest_after_seconds, is_warmup, is_failure, notes}]}]}
        """
        sid = data.get("id") or new_id("s")
        all_sets = []
        c = self.conn
        dur = data.get("duration_min")
        if dur is None and data.get("started_at") and data.get("ended_at"):
            try:
                dur = int((datetime.fromisoformat(data["ended_at"]) -
                           datetime.fromisoformat(data["started_at"])).total_seconds() // 60)
            except ValueError:
                dur = None
        c.execute("INSERT INTO session(id, date, routine_id, routine_day_id, started_at, ended_at, "
                  "duration_min, bodyweight_kg, sleep_hours, energy_level, mood, notes) "
                  "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                  (sid, data["date"], data.get("routine_id"), data.get("routine_day_id"),
                   data.get("started_at"), data.get("ended_at"), dur, data.get("bodyweight_kg"),
                   data.get("sleep_hours"), data.get("energy_level"), data.get("mood"),
                   data.get("notes")))
        new_prs = []
        for i, ex in enumerate(data.get("exercises", []), start=1):
            seid = new_id("se")
            sets = ex.get("sets", [])
            ton = metricas.tonnage(sets)
            e1 = metricas.best_e1rm(sets)
            c.execute("INSERT INTO session_exercise VALUES (?,?,?,?,?,?)",
                      (seid, sid, ex["exercise_id"], i, ton, e1))
            prs = self._detect_prs(ex["exercise_id"], sets, e1, sid, data["date"])
            new_prs += prs
            pr_types = {p["type"] for p in prs}
            for n, s in enumerate(sets, start=1):
                is_pr = self._set_is_pr(s, pr_types, sets)
                c.execute("INSERT INTO set_log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (new_id("set"), seid, n, s.get("reps"), s.get("seconds"),
                           s.get("weight_kg") or 0, s.get("rir"), s.get("tempo"),
                           s.get("rest_after_seconds"), int(bool(s.get("is_warmup"))),
                           int(bool(s.get("is_failure"))), int(is_pr), s.get("notes")))
            all_sets += sets
        c.execute("UPDATE session SET tonnage_kg=?, avg_rir=? WHERE id=?",
                  (metricas.tonnage(all_sets), metricas.avg_rir(all_sets), sid))
        c.execute("UPDATE schedule_day SET status='completada', session_id=? WHERE date=?",
                  (sid, data["date"]))
        c.commit()
        new_achievements = self.check_achievements()
        return sid, new_prs, new_achievements

    @staticmethod
    def _set_is_pr(s, pr_types, sets):
        if s.get("is_warmup") or not pr_types:
            return False
        ws = metricas.working_sets(sets)
        if "max_weight" in pr_types and (s.get("weight_kg") or 0) == max((x.get("weight_kg") or 0) for x in ws):
            return True
        if "max_reps" in pr_types and (s.get("weight_kg") or 0) == 0 and \
                (s.get("reps") or 0) == max((x.get("reps") or 0) for x in ws):
            return True
        if "max_hold" in pr_types and (s.get("seconds") or 0) == max((x.get("seconds") or 0) for x in ws):
            return True
        return False

    def best_record(self, ex_id, rtype):
        r = self.q1("SELECT MAX(value) v FROM personal_record WHERE exercise_id=? AND type=?", (ex_id, rtype))
        return r["v"] if r else None

    def _detect_prs(self, ex_id, sets, e1rm, sid, d):
        ws = metricas.working_sets(sets)
        if not ws:
            return []
        candidates = []
        bw_reps = [s.get("reps") or 0 for s in ws if (s.get("weight_kg") or 0) == 0]
        if bw_reps and max(bw_reps) > 0:
            candidates.append(("max_reps", max(bw_reps), "reps"))
        weights = [s.get("weight_kg") or 0 for s in ws if (s.get("reps") or 0) > 0]
        if weights and max(weights) > 0:
            candidates.append(("max_weight", max(weights), "kg"))
        holds = [s.get("seconds") or 0 for s in ws]
        if holds and max(holds) > 0:
            candidates.append(("max_hold", max(holds), "segundos"))
        if e1rm:
            candidates.append(("estimated_1rm", e1rm, "kg"))
        out = []
        for rtype, value, unit in candidates:
            prev = self.best_record(ex_id, rtype)
            if prev is None or value > prev:
                rec = {"id": new_id("pr"), "exercise_id": ex_id, "type": rtype, "value": value,
                       "unit": unit, "date_achieved": d, "previous_value": prev, "session_id": sid}
                self.conn.execute("INSERT INTO personal_record VALUES (?,?,?,?,?,?,?,?)",
                                  tuple(rec.values()))
                out.append(rec)
        return out

    def sessions(self, limit=None):
        sql = "SELECT * FROM session ORDER BY date DESC, started_at DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        return self.q(sql)

    def session_detail(self, sid):
        s = self.q1("SELECT * FROM session WHERE id=?", (sid,))
        if not s:
            return None
        s["exercises"] = self.q("SELECT se.*, e.name, e.measure FROM session_exercise se "
                                "JOIN exercise e ON e.id=se.exercise_id WHERE session_id=? ORDER BY ord", (sid,))
        for ex in s["exercises"]:
            ex["sets"] = self.q("SELECT * FROM set_log WHERE session_exercise_id=? ORDER BY set_number", (ex["id"],))
        return s

    def delete_session(self, sid):
        self.x("DELETE FROM personal_record WHERE session_id=?", (sid,))
        self.x("DELETE FROM session WHERE id=?", (sid,))
        self.x("UPDATE schedule_day SET status='planificada', session_id=NULL WHERE session_id=?", (sid,))

    def last_performance(self, ex_id):
        """Series de la última vez que se hizo el ejercicio (para sugerir progresión)."""
        se = self.q1("SELECT se.id, s.date FROM session_exercise se JOIN session s ON s.id=se.session_id "
                     "WHERE se.exercise_id=? ORDER BY s.date DESC, s.started_at DESC LIMIT 1", (ex_id,))
        if not se:
            return None
        se["sets"] = self.q("SELECT * FROM set_log WHERE session_exercise_id=? ORDER BY set_number", (se["id"],))
        return se

    def exercise_history(self, ex_id):
        """Por sesión: fecha, mejor e1RM, máx reps, máx segundos, máx peso, tonelaje."""
        rows = self.q(
            "SELECT s.date, se.estimated_1rm_kg e1rm, se.tonnage_kg ton, "
            "MAX(CASE WHEN sl.is_warmup=0 THEN sl.reps END) max_reps, "
            "MAX(CASE WHEN sl.is_warmup=0 THEN sl.seconds END) max_seconds, "
            "MAX(CASE WHEN sl.is_warmup=0 THEN sl.weight_kg END) max_weight, "
            "SUM(CASE WHEN sl.is_warmup=0 THEN 1 ELSE 0 END) n_sets "
            "FROM session_exercise se JOIN session s ON s.id=se.session_id "
            "LEFT JOIN set_log sl ON sl.session_exercise_id=se.id "
            "WHERE se.exercise_id=? GROUP BY se.id ORDER BY s.date", (ex_id,))
        return rows

    def trained_exercises(self):
        return self.q("SELECT DISTINCT e.id, e.name FROM session_exercise se JOIN exercise e "
                      "ON e.id=se.exercise_id ORDER BY e.name")

    # ───────────────────────── análisis ─────────────────────────
    def weekly_sets_by_muscle(self, week_start_date):
        start = week_start_date.isoformat()
        end = (week_start_date + timedelta(days=7)).isoformat()
        rows = self.q(
            "SELECT em.muscle_id, COUNT(*) n FROM set_log sl "
            "JOIN session_exercise se ON se.id=sl.session_exercise_id "
            "JOIN session s ON s.id=se.session_id "
            "JOIN exercise_muscle em ON em.exercise_id=se.exercise_id AND em.role='primario' "
            "WHERE sl.is_warmup=0 AND s.date>=? AND s.date<? GROUP BY em.muscle_id", (start, end))
        return {r["muscle_id"]: r["n"] for r in rows}

    def weekly_frequency_by_muscle(self, week_start_date):
        start = week_start_date.isoformat()
        end = (week_start_date + timedelta(days=7)).isoformat()
        rows = self.q(
            "SELECT em.muscle_id, COUNT(DISTINCT s.date) n FROM session_exercise se "
            "JOIN session s ON s.id=se.session_id "
            "JOIN exercise_muscle em ON em.exercise_id=se.exercise_id AND em.role='primario' "
            "WHERE s.date>=? AND s.date<? GROUP BY em.muscle_id", (start, end))
        return {r["muscle_id"]: r["n"] for r in rows}

    def weekly_tonnage(self, weeks=12, week_starts_on="monday"):
        today = date.today()
        ws = metricas.week_start(today, week_starts_on)
        out = []
        for i in range(weeks - 1, -1, -1):
            s = ws - timedelta(weeks=i)
            e = s + timedelta(days=7)
            r = self.q1("SELECT COALESCE(SUM(tonnage_kg),0) t, COUNT(*) n FROM session WHERE date>=? AND date<?",
                        (s.isoformat(), e.isoformat()))
            out.append({"week_start": s.isoformat(), "tonnage_kg": round(r["t"], 1), "sessions": r["n"]})
        return out

    def intensity_distribution(self, ex_id=None, days=28):
        """Series efectivas por zona de intensidad (% del mejor 1RM estimado)."""
        since = (date.today() - timedelta(days=days)).isoformat()
        sql = ("SELECT se.exercise_id, sl.weight_kg, sl.reps FROM set_log sl "
               "JOIN session_exercise se ON se.id=sl.session_exercise_id JOIN session s ON s.id=se.session_id "
               "WHERE sl.is_warmup=0 AND sl.weight_kg>0 AND s.date>=?")
        p = [since]
        if ex_id:
            sql += " AND se.exercise_id=?"
            p.append(ex_id)
        dist = {z[2]: 0 for z in metricas.ZONAS_INTENSIDAD}
        best = {}
        for r in self.q(sql, p):
            if r["exercise_id"] not in best:
                best[r["exercise_id"]] = self.best_record(r["exercise_id"], "estimated_1rm")
            one = best[r["exercise_id"]]
            if one:
                dist[metricas.intensity_zone(r["weight_kg"] * 100 / one)] += 1
        return dist

    def streaks(self):
        dates = [r["date"] for r in self.q("SELECT DISTINCT date FROM session")]
        return metricas.streaks(dates)

    def sessions_in_week(self, week_start_date):
        e = week_start_date + timedelta(days=7)
        return self.q1("SELECT COUNT(DISTINCT date) n FROM session WHERE date>=? AND date<?",
                       (week_start_date.isoformat(), e.isoformat()))["n"]

    def consecutive_hard_weeks(self, target, week_starts_on="monday"):
        ws = metricas.week_start(date.today(), week_starts_on)
        n = 0
        # La semana actual cuenta si ya alcanzó el objetivo.
        if self.sessions_in_week(ws) >= target:
            n += 1
        w = ws - timedelta(weeks=1)
        while self.sessions_in_week(w) >= target:
            n += 1
            w -= timedelta(weeks=1)
        return n

    def deload_advice(self):
        target = int(self.get_setting("target_days_per_week", "3") or 3)
        wso = self.get_setting("week_starts_on", "monday")
        ws = metricas.week_start(date.today(), wso)
        msgs = []
        hard = self.consecutive_hard_weeks(target, wso)
        if hard >= 6:
            msgs.append(f"Llevas {hard} semanas seguidas cumpliendo tu objetivo: "
                        "considera una semana de descarga (≈50 % de las series, RIR 3-4).")
        names = self.muscle_names()
        for m, n in self.weekly_sets_by_muscle(ws).items():
            if n > metricas.VOLUMEN_MAX:
                msgs.append(f"{names.get(m, m)}: {n} series esta semana (> 20). Vigila la recuperación.")
        recent = self.q("SELECT avg_rir FROM session WHERE avg_rir IS NOT NULL ORDER BY date DESC LIMIT 6")
        if len(recent) >= 6 and sum(r["avg_rir"] for r in recent) / len(recent) <= 0.75:
            msgs.append("Tu RIR medio de las últimas 6 sesiones está cerca del fallo: "
                        "aleja un poco el esfuerzo o programa una descarga.")
        return msgs

    def heatmap(self, weeks=26):
        since = (date.today() - timedelta(weeks=weeks)).isoformat()
        return {r["date"]: r["n"] for r in
                self.q("SELECT date, COUNT(*) n FROM session WHERE date>=? GROUP BY date", (since,))}

    # ───────────────────────── récords ─────────────────────────
    def personal_records(self, limit=None):
        sql = ("SELECT pr.*, e.name FROM personal_record pr JOIN exercise e ON e.id=pr.exercise_id "
               "ORDER BY pr.date_achieved DESC, pr.rowid DESC")
        if limit:
            sql += f" LIMIT {int(limit)}"
        return self.q(sql)

    def best_records(self):
        return self.q("SELECT pr.exercise_id, e.name, pr.type, MAX(pr.value) value, pr.unit, "
                      "MAX(pr.date_achieved) date_achieved FROM personal_record pr "
                      "JOIN exercise e ON e.id=pr.exercise_id GROUP BY pr.exercise_id, pr.type "
                      "ORDER BY e.name")

    # ───────────────────────── cuerpo ─────────────────────────
    def add_measurement(self, d, weight=None, fat=None, muscle=None, measurements=None, notes=""):
        mid = new_id("bm")
        self.x("INSERT INTO body_measurement VALUES (?,?,?,?,?,?,?)",
               (mid, d, weight, fat, muscle, json.dumps(measurements or {}, ensure_ascii=False), notes))
        return mid

    def measurements(self):
        rows = self.q("SELECT * FROM body_measurement ORDER BY date")
        for r in rows:
            r["measurements"] = json.loads(r["measurements"] or "{}")
        return rows

    def delete_measurement(self, mid):
        self.x("DELETE FROM body_measurement WHERE id=?", (mid,))

    def add_photo(self, d, file_path, pose="front", weight=None, notes="", tags=None):
        pid = new_id("ph")
        self.x("INSERT INTO progress_photo VALUES (?,?,?,?,?,?,?)",
               (pid, d, file_path, pose, weight, notes, json.dumps(tags or [], ensure_ascii=False)))
        return pid

    def photos(self):
        rows = self.q("SELECT * FROM progress_photo ORDER BY date DESC")
        for r in rows:
            r["tags"] = json.loads(r["tags"] or "[]")
        return rows

    def delete_photo(self, pid):
        self.x("DELETE FROM progress_photo WHERE id=?", (pid,))

    # ───────────────────────── objetivos ─────────────────────────
    def add_goal(self, title, gtype="habilidad", target_exercise_id=None, deadline=None,
                 milestones=None, notes=""):
        gid = new_id("g")
        self.x("INSERT INTO goal VALUES (?,?,?,?,?,?,?,0)",
               (gid, title, gtype, target_exercise_id, deadline, notes, now_iso()))
        for i, m in enumerate(milestones or [], start=1):
            self.x("INSERT INTO goal_milestone VALUES (?,?,?,0,?)", (new_id("gm"), gid, m, i))
        return gid

    def goals(self):
        gs = self.q("SELECT * FROM goal ORDER BY done, deadline")
        for g in gs:
            g["milestones"] = self.q("SELECT * FROM goal_milestone WHERE goal_id=? ORDER BY ord", (g["id"],))
            ms = g["milestones"]
            g["progress_pct"] = round(100 * sum(m["done"] for m in ms) / len(ms)) if ms else (100 if g["done"] else 0)
        return gs

    def toggle_milestone(self, mid):
        self.x("UPDATE goal_milestone SET done = 1 - done WHERE id=?", (mid,))

    def set_goal_done(self, gid, done=True):
        self.x("UPDATE goal SET done=? WHERE id=?", (int(done), gid))

    def delete_goal(self, gid):
        self.x("DELETE FROM goal WHERE id=?", (gid,))

    def chain_milestones(self, target_ex_id):
        """Propone hitos a partir de la cadena de progresión del ejercicio objetivo."""
        before, _ = self.progression_chain(target_ex_id, depth=4)
        labels = []
        for level in reversed(before):
            labels.append(" / ".join(self.exercise_name(x) for x in level[:2]))
        labels.append(self.exercise_name(target_ex_id))
        return labels

    # ───────────────────────── aprendizaje ─────────────────────────
    def learning_status(self, item_id):
        r = self.q1("SELECT * FROM learning_progress WHERE item_id=?", (item_id,))
        return r or {"item_id": item_id, "status": "pendiente", "quiz_score": None}

    def set_learning(self, item_id, kind, status=None, quiz_score=None):
        cur = self.learning_status(item_id)
        status = status or cur.get("status") or "pendiente"
        if quiz_score is None:
            quiz_score = cur.get("quiz_score")
        elif cur.get("quiz_score") is not None:
            quiz_score = max(quiz_score, cur["quiz_score"])
        self.x("INSERT OR REPLACE INTO learning_progress VALUES (?,?,?,?,?)",
               (item_id, kind, status, quiz_score, now_iso()))
        return self.check_achievements()

    def learning_summary(self):
        rows = self.q("SELECT * FROM learning_progress")
        lessons_done = sum(1 for r in rows if r["kind"] == "leccion" and r["status"] == "dominado")
        ex = {r["item_id"]: r["status"] for r in rows if r["kind"] == "ejercicio"}
        return {
            "lessons_done": lessons_done,
            "lessons_total": len(lecciones.LESSONS),
            "ex_mastered": sum(1 for s in ex.values() if s == "dominado"),
            "ex_learning": sum(1 for s in ex.values() if s == "aprendiendo"),
            "ex_total": self.q1("SELECT COUNT(*) n FROM exercise")["n"],
        }

    def next_skills(self, limit=8):
        """Ejercicios sugeridos para aprender: los siguientes de lo que ya dominas
        (o los de dificultad 1 si aún no has marcado nada)."""
        mastered = {r["item_id"] for r in self.q(
            "SELECT item_id FROM learning_progress WHERE kind='ejercicio' AND status='dominado'")}
        if not mastered:
            return self.q("SELECT * FROM exercise WHERE difficulty=1 ORDER BY block LIMIT ?", (limit,))
        cand = {}
        for m in mastered:
            for r in self.q("SELECT to_id FROM progression_link WHERE from_id=?", (m,)):
                if r["to_id"] in mastered:
                    continue
                prereq = [x["from_id"] for x in self.q("SELECT from_id FROM progression_link WHERE to_id=?",
                                                       (r["to_id"],))]
                cand[r["to_id"]] = sum(1 for p in prereq if p in mastered) / max(1, len(prereq))
        ids = sorted(cand, key=lambda k: -cand[k])[:limit]
        return [self.q1("SELECT * FROM exercise WHERE id=?", (i,)) for i in ids]

    # ───────────────────────── logros ─────────────────────────
    def achievements(self):
        return self.q("SELECT * FROM achievement ORDER BY unlocked_at IS NULL, unlocked_at DESC, name")

    def _reps_sum(self, ex_ids, since=None):
        if not ex_ids:
            return 0
        marks = ",".join("?" * len(ex_ids))
        sql = (f"SELECT COALESCE(SUM(sl.reps),0) n FROM set_log sl JOIN session_exercise se "
               f"ON se.id=sl.session_exercise_id JOIN session s ON s.id=se.session_id "
               f"WHERE se.exercise_id IN ({marks}) AND sl.is_warmup=0")
        p = list(ex_ids)
        if since:
            sql += " AND s.date>=?"
            p.append(since)
        return self.q1(sql, p)["n"]

    def _did(self, ex_id, min_seconds=0):
        r = self.q1("SELECT 1 FROM set_log sl JOIN session_exercise se ON se.id=sl.session_exercise_id "
                    "WHERE se.exercise_id=? AND sl.is_warmup=0 AND (COALESCE(sl.reps,0)>0 "
                    "OR COALESCE(sl.seconds,0)>?)", (ex_id, min_seconds))
        return bool(r)

    def check_achievements(self):
        n_sessions = self.q1("SELECT COUNT(*) n FROM session")["n"]
        _, best_streak = self.streaks()
        n_prs = self.q1("SELECT COUNT(*) n FROM personal_record")["n"]
        pull_ids = [r["id"] for r in self.q("SELECT id FROM exercise WHERE block='dominadas'")]
        push_ids = [r["id"] for r in self.q("SELECT id FROM exercise WHERE block='flexiones'")]
        since30 = (date.today() - timedelta(days=30)).isoformat()
        max_week_ton = max([w["tonnage_kg"] for w in self.weekly_tonnage(52)] or [0])
        ls = self.learning_summary()
        perfect = self.q1("SELECT 1 FROM learning_progress WHERE kind='leccion' AND quiz_score>=1")
        cond = {
            "ach_primera_sesion": n_sessions >= 1,
            "ach_10_sesiones": n_sessions >= 10,
            "ach_50_sesiones": n_sessions >= 50,
            "ach_racha_7": best_streak >= 7,
            "ach_racha_30": best_streak >= 30,
            "ach_100_dominadas_mes": self._reps_sum(pull_ids, since30) >= 100,
            "ach_1000_flexiones": self._reps_sum(push_ids) >= 1000,
            "ach_first_muscleup": self._did("ex_muscle_up") or self._did("ex_muscle_up_lento"),
            "ach_primer_pino": self._did("ex_pino", 1),
            "ach_front_lever": self._did("ex_front_lever", 1),
            "ach_primer_pr": n_prs >= 1,
            "ach_10_prs": n_prs >= 10,
            "ach_tonelaje_10t": max_week_ton >= 10000,
            "ach_medidas": bool(self.q1("SELECT 1 FROM body_measurement")),
            "ach_5_lecciones": ls["lessons_done"] >= 5,
            "ach_todas_lecciones": ls["lessons_done"] >= ls["lessons_total"],
            "ach_quiz_perfecto": bool(perfect),
            "ach_5_dominados": ls["ex_mastered"] >= 5,
        }
        unlocked = []
        for aid, ok in cond.items():
            if ok:
                cur = self.conn.execute("UPDATE achievement SET unlocked_at=? WHERE id=? AND unlocked_at IS NULL",
                                        (date.today().isoformat(), aid))
                if cur.rowcount:
                    unlocked.append(self.q1("SELECT * FROM achievement WHERE id=?", (aid,)))
        self.conn.commit()
        return unlocked
