import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from entrenador import catalogo, exportar, lecciones, metricas  # noqa: E402
from entrenador.db import Database  # noqa: E402


class MetricasTest(unittest.TestCase):
    def test_epley(self):
        self.assertEqual(metricas.epley_1rm(60, 8), 76.0)
        self.assertEqual(metricas.epley_1rm(100, 1), 100.0)
        self.assertIsNone(metricas.epley_1rm(0, 10))
        self.assertIsNone(metricas.epley_1rm(50, 20))

    def test_tonnage_excludes_warmup(self):
        sets = [{"reps": 10, "weight_kg": 20, "is_warmup": True},
                {"reps": 8, "weight_kg": 60}, {"reps": 8, "weight_kg": 60}]
        self.assertEqual(metricas.tonnage(sets), 960)
        self.assertEqual(metricas.peso_medio(sets), 60)
        self.assertEqual(metricas.imr(sets, 80), 75.0)

    def test_zonas(self):
        self.assertEqual(metricas.intensity_zone(55), "Mínima")
        self.assertEqual(metricas.intensity_zone(85), "Grande")
        self.assertEqual(metricas.intensity_zone(95), "Submáxima y máxima")
        self.assertEqual(metricas.zona_por_reps(5), "fuerza")
        self.assertEqual(metricas.zona_por_reps(12), "hipertrofia")

    def test_streaks(self):
        t = date(2025, 3, 20)
        ds = [t - timedelta(days=x) for x in (0, 2, 4, 6)]  # cada 2 días
        cur, best = metricas.streaks(ds, today=t)
        self.assertEqual(cur, 7)
        self.assertEqual(best, 7)
        cur, _ = metricas.streaks(ds, today=t + timedelta(days=10))
        self.assertEqual(cur, 0)

    def test_estado_volumen(self):
        self.assertEqual(metricas.estado_volumen(8), "bajo")
        self.assertEqual(metricas.estado_volumen(14), "óptimo")
        self.assertEqual(metricas.estado_volumen(22), "alto")


class CatalogoTest(unittest.TestCase):
    def test_ids_unicos_y_enlaces_validos(self):
        ids = [e["id"] for e in catalogo.EXERCISES]
        self.assertEqual(len(ids), len(set(ids)))
        valid = set(ids)
        muscles = {m[0] for m in catalogo.MUSCLE_GROUPS}
        equipment = {q[0] for q in catalogo.EQUIPMENT}
        blocks = {b[0] for b in catalogo.BLOCKS}
        for e in catalogo.EXERCISES:
            for x in e["progressions_to_reach"] + e["progresses_to"]:
                self.assertIn(x, valid, f"{e['id']} enlaza a {x}")
            for m in e["primary_muscles"] + e["secondary_muscles"]:
                self.assertIn(m, muscles, f"{e['id']} músculo {m}")
            for q in e["equipment"]:
                self.assertIn(q, equipment, f"{e['id']} equipo {q}")
            self.assertIn(e["block"], blocks)
            self.assertTrue(1 <= e["difficulty"] <= 5)
            self.assertTrue(e["technique"]["pasos"], e["id"])
            self.assertTrue(e["technique"]["errores"], e["id"])

    def test_quiz_bien_formado(self):
        self.assertEqual(len(lecciones.lesson_ids()), len(lecciones.LESSONS))
        for l in lecciones.LESSONS:
            for preg, ops, ok, expl in l["quiz"]:
                self.assertTrue(0 <= ok < len(ops), preg)


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "db.sqlite")

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def _session(self, d, ex="ex_sentadilla_barra", weight=60, reps=8, n=3):
        return self.db.save_session({
            "date": d, "started_at": f"{d}T18:00:00", "ended_at": f"{d}T19:07:00",
            "exercises": [{"exercise_id": ex, "sets": [
                {"reps": 10, "weight_kg": 20, "is_warmup": True},
                *[{"reps": reps, "weight_kg": weight, "rir": 2} for _ in range(n)]]}],
        })

    def test_semilla(self):
        self.assertEqual(len(self.db.exercises()), len(catalogo.EXERCISES))
        self.assertTrue(self.db.routines())
        for r in self.db.routines():
            for d in self.db.routine_days(r["id"]):
                self.assertTrue(self.db.routine_exercises(d["id"]))
        # Segunda apertura no duplica
        path = self.db.path
        self.db.close()
        self.db = Database(path)
        self.assertEqual(len(self.db.routines()), 4)

    def test_cadena(self):
        before, after = self.db.progression_chain("ex_flexiones")
        self.assertIn("ex_flexiones_inclinadas", before[0])
        self.assertIn("ex_flexiones_diamante", after[0])

    def test_sesion_metricas_y_prs(self):
        today = date.today().isoformat()
        sid, prs, ach = self._session(today)
        s = self.db.session_detail(sid)
        self.assertEqual(s["duration_min"], 67)
        self.assertEqual(s["tonnage_kg"], 1440)
        self.assertEqual(s["exercises"][0]["estimated_1rm_kg"], 76.0)
        types = {p["type"] for p in prs}
        self.assertEqual(types, {"max_weight", "estimated_1rm"})
        self.assertIn("ach_primera_sesion", {a["id"] for a in ach})
        self.assertIn("ach_primer_pr", {a["id"] for a in ach})
        # Una serie de calentamiento no marca PR
        self.assertFalse(s["exercises"][0]["sets"][0]["is_pr"])
        # Misma carga otra vez: sin PR
        _, prs2, _ = self._session(today)
        self.assertEqual(prs2, [])
        _, prs3, _ = self._session(today, weight=65)
        self.assertEqual({p["type"] for p in prs3}, {"max_weight", "estimated_1rm"})
        self.assertEqual(prs3[0]["previous_value"], 60)

    def test_volumen_semanal(self):
        today = date.today()
        self._session(today.isoformat(), ex="ex_flexiones", weight=0, reps=12, n=4)
        ws = metricas.week_start(today)
        vol = self.db.weekly_sets_by_muscle(ws)
        self.assertEqual(vol["mg_pecho"], 4)
        self.assertEqual(vol["mg_triceps"], 4)
        self.assertNotIn("mg_hombros", vol)  # secundario no cuenta

    def test_borrar_sesion_borra_prs(self):
        sid, prs, _ = self._session(date.today().isoformat())
        self.assertTrue(prs)
        self.db.delete_session(sid)
        self.assertEqual(self.db.personal_records(), [])

    def test_aprendizaje_y_logros(self):
        for l in lecciones.LESSONS[:5]:
            self.db.set_learning(l["id"], "leccion", "dominado", 0.5)
        ach = {a["id"] for a in self.db.achievements() if a["unlocked_at"]}
        self.assertIn("ach_5_lecciones", ach)
        self.db.set_learning(lecciones.LESSONS[0]["id"], "leccion", quiz_score=1.0)
        self.assertEqual(self.db.learning_status(lecciones.LESSONS[0]["id"])["quiz_score"], 1.0)
        # El mejor puntaje se conserva
        self.db.set_learning(lecciones.LESSONS[0]["id"], "leccion", quiz_score=0.0)
        self.assertEqual(self.db.learning_status(lecciones.LESSONS[0]["id"])["quiz_score"], 1.0)
        self.db.set_learning("ex_flexiones", "ejercicio", "dominado")
        sug = [e["id"] for e in self.db.next_skills()]
        self.assertIn("ex_flexiones_diamante", sug)

    def test_objetivo_hitos_desde_cadena(self):
        ms = self.db.chain_milestones("ex_muscle_up")
        self.assertEqual(ms[-1], "Muscle up")
        gid = self.db.add_goal("Primer muscle up", target_exercise_id="ex_muscle_up", milestones=ms)
        g = self.db.goals()[0]
        self.assertEqual(g["progress_pct"], 0)
        self.db.toggle_milestone(g["milestones"][0]["id"])
        self.assertGreater(self.db.goals()[0]["progress_pct"], 0)
        self.db.delete_goal(gid)

    def test_export_import(self):
        self._session(date.today().isoformat())
        self.db.add_measurement(date.today().isoformat(), 74.2, 15.5, None, {"cintura": 82})
        out = Path(self.tmp.name) / "exp"
        exportar.export_csv(self.db, out)
        for f in ("sessions.csv", "sets.csv", "body_measurements.csv", "personal_records.csv",
                  "weekly_volume.csv"):
            self.assertTrue((out / f).exists(), f)
        js = Path(self.tmp.name) / "full.json"
        exportar.export_json(self.db, js)
        data = json.loads(js.read_text(encoding="utf-8"))
        self.assertEqual(data["export_version"], "1.0")
        self.assertEqual(len(data["sessions"]), 1)
        # Restaurar en una base vacía
        db2 = Database(Path(self.tmp.name) / "db2.sqlite")
        exportar.import_json(db2, js)
        self.assertEqual(len(db2.sessions()), 1)
        self.assertEqual(len(db2.measurements()), 1)
        self.assertEqual(len(db2.routines()), 4)
        db2.close()
        b = exportar.backup(self.db, Path(self.tmp.name) / "bk", force=True)
        self.assertTrue(b.exists())
        self.assertIsNone(exportar.backup(self.db, Path(self.tmp.name) / "bk"))

    def test_descarga(self):
        self.db.set_setting("target_days_per_week", "1")
        ws = metricas.week_start(date.today())
        for i in range(6):
            self._session((ws - timedelta(weeks=i)).isoformat())
        msgs = self.db.deload_advice()
        self.assertTrue(any("descarga" in m for m in msgs))


if __name__ == "__main__":
    unittest.main()
