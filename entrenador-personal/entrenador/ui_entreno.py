"""Pestañas Entrenar, Rutinas e Historial."""
import json
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from . import metricas
from .ui_comun import (FONT, FONT_B, FONT_H1, FONT_H2, MUTED, PAD, ExercisePicker, FormDialog,
                       fill_tree, make_tree, stars, to_float, to_int)

METHODS = ["vuelta_al_mundo", "full_body", "grupos", "lastre", "resistencia", "fuerza", "objetivos", "mixto"]
GOALS = ["hipertrofia", "fuerza", "resistencia", "habilidad", "mixto"]


def fmt_set(s, measure):
    main = f"{s.get('seconds') or 0}s" if measure == "segundos" else f"{s.get('reps') or 0}"
    if s.get("weight_kg"):
        main += f" × {s['weight_kg']:g} kg"
    if s.get("rir") is not None:
        main += f" @RIR{s['rir']}"
    return main


# ───────────────────────────── ENTRENAR ─────────────────────────────
class EntrenarTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=PAD)
        self.app = app
        self.db = app.db
        self.items = []
        self.started_at = None
        self.timer_left = 0
        self.timer_job = None

        top = ttk.LabelFrame(self, text="Sesión", padding=6)
        top.pack(fill="x")
        ttk.Label(top, text="Rutina:").grid(row=0, column=0, sticky="w")
        self.day_var = tk.StringVar()
        self.day_combo = ttk.Combobox(top, textvariable=self.day_var, state="readonly", width=48)
        self.day_combo.grid(row=0, column=1, columnspan=3, sticky="ew", padx=4)
        ttk.Button(top, text="Cargar plan", command=self.load_plan).grid(row=0, column=4, padx=4)
        ttk.Button(top, text="Nueva sesión vacía", command=self.reset).grid(row=0, column=5, padx=4)
        self.vars = {}
        fields = [("date", "Fecha", 12), ("bodyweight_kg", "Peso corp. (kg)", 7),
                  ("sleep_hours", "Sueño (h)", 5), ("energy_level", "Energía 1-5", 4), ("mood", "Ánimo 1-5", 4)]
        row = ttk.Frame(top)
        row.grid(row=1, column=0, columnspan=8, sticky="w", pady=(6, 0))
        for k, lbl, w in fields:
            ttk.Label(row, text=lbl).pack(side="left", padx=(0, 3))
            v = tk.StringVar()
            ttk.Entry(row, textvariable=v, width=w).pack(side="left", padx=(0, 12))
            self.vars[k] = v
        self.clock = ttk.Label(top, text="", foreground=MUTED)
        self.clock.grid(row=0, column=6, padx=8)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=6)

        left = ttk.LabelFrame(body, text="Ejercicios de la sesión", padding=6)
        left.pack(side="left", fill="both", expand=False)
        frame, self.ex_tree = make_tree(left, [("n", "Ejercicio"), ("plan", "Plan"), ("done", "Hechas")],
                                        heights=16, widths=[190, 120, 60])
        frame.pack(fill="both", expand=True)
        b = ttk.Frame(left)
        b.pack(fill="x", pady=4)
        ttk.Button(b, text="+ Ejercicio", command=self.add_exercise).pack(side="left")
        ttk.Button(b, text="Quitar", command=self.remove_exercise).pack(side="left", padx=4)
        ttk.Button(b, text="Ver técnica", command=self.view_technique).pack(side="left")
        self.ex_tree.bind("<<TreeviewSelect>>", lambda e: self.show_current())

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=(PAD, 0))
        self.ex_title = ttk.Label(right, text="Elige o añade un ejercicio", font=FONT_H2)
        self.ex_title.pack(anchor="w")
        self.ex_info = ttk.Label(right, text="", foreground=MUTED, wraplength=620, justify="left")
        self.ex_info.pack(anchor="w", pady=(2, 6))

        entry = ttk.LabelFrame(right, text="Registrar serie", padding=6)
        entry.pack(fill="x")
        self.s_main_lbl = ttk.Label(entry, text="Reps")
        self.s_main_lbl.grid(row=0, column=0)
        ttk.Label(entry, text="Peso / lastre (kg)").grid(row=0, column=1)
        ttk.Label(entry, text="RIR").grid(row=0, column=2)
        ttk.Label(entry, text="Tempo").grid(row=0, column=3)
        self.s_main, self.s_kg, self.s_rir, self.s_tempo = (tk.StringVar() for _ in range(4))
        self.s_warm, self.s_fail = tk.BooleanVar(), tk.BooleanVar()
        for c, v, w in ((0, self.s_main, 8), (1, self.s_kg, 10), (2, self.s_rir, 5), (3, self.s_tempo, 9)):
            e = ttk.Entry(entry, textvariable=v, width=w)
            e.grid(row=1, column=c, padx=4)
            e.bind("<Return>", lambda ev: self.add_set())
        ttk.Checkbutton(entry, text="Calentamiento", variable=self.s_warm).grid(row=1, column=4, padx=4)
        ttk.Checkbutton(entry, text="Al fallo", variable=self.s_fail).grid(row=1, column=5, padx=4)
        ttk.Button(entry, text="Añadir serie ⏎", style="Accent.TButton", command=self.add_set).grid(
            row=1, column=6, padx=6)

        frame, self.set_tree = make_tree(right, [("n", "#"), ("v", "Serie"), ("w", "Tipo")],
                                         heights=8, widths=[40, 260, 120])
        frame.pack(fill="both", expand=True, pady=6)
        sb = ttk.Frame(right)
        sb.pack(fill="x")
        ttk.Button(sb, text="Borrar serie", command=self.delete_set).pack(side="left")
        ttk.Button(sb, text="Repetir última serie", command=self.repeat_set).pack(side="left", padx=4)

        timer = ttk.LabelFrame(right, text="Descanso", padding=6)
        timer.pack(fill="x", pady=6)
        self.timer_lbl = tk.Label(timer, text="00:00", font=("Consolas", 28, "bold"), fg="#111827")
        self.timer_lbl.pack(side="left", padx=8)
        ttk.Button(timer, text="▶ Iniciar", command=self.start_timer).pack(side="left")
        ttk.Button(timer, text="−15 s", command=lambda: self.bump_timer(-15)).pack(side="left", padx=2)
        ttk.Button(timer, text="+15 s", command=lambda: self.bump_timer(15)).pack(side="left", padx=2)
        ttk.Button(timer, text="■ Parar", command=self.stop_timer).pack(side="left", padx=2)
        self.auto_timer = tk.BooleanVar(value=True)
        ttk.Checkbutton(timer, text="Iniciar al añadir serie", variable=self.auto_timer).pack(side="left", padx=8)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x")
        ttk.Label(bottom, text="Notas:").pack(side="left")
        self.notes = tk.StringVar()
        ttk.Entry(bottom, textvariable=self.notes).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(bottom, text="💾 Guardar sesión", style="Accent.TButton", command=self.save).pack(side="right")
        self.reset()

    # ── estado ──
    def refresh(self):
        self.day_map = {"— Sesión libre —": None}
        for r in self.db.routines():
            for d in self.db.routine_days(r["id"]):
                self.day_map[f"{r['name']} · {d['day_label']}"] = (r["id"], d["id"])
        self.day_combo.configure(values=list(self.day_map))
        if self.day_var.get() not in self.day_map:
            planned = self.db.q1("SELECT routine_day_id FROM schedule_day WHERE date=? AND status='planificada'",
                                 (date.today().isoformat(),))
            label = next((k for k, v in self.day_map.items()
                          if planned and v and v[1] == planned["routine_day_id"]), "— Sesión libre —")
            self.day_var.set(label)

    def reset(self):
        self.items = []
        self.started_at = None
        self.vars["date"].set(date.today().isoformat())
        for k in ("bodyweight_kg", "sleep_hours", "energy_level", "mood"):
            self.vars[k].set("")
        last_bw = self.db.q1("SELECT weight_kg FROM body_measurement WHERE weight_kg IS NOT NULL "
                             "ORDER BY date DESC LIMIT 1")
        if last_bw:
            self.vars["bodyweight_kg"].set(f"{last_bw['weight_kg']:g}")
        self.notes.set("")
        self.render_exercises()
        self.show_current()

    def _start_clock(self):
        if not self.started_at:
            self.started_at = datetime.now().replace(microsecond=0)
            self.clock.configure(text=f"Inicio: {self.started_at:%H:%M}")

    def load_plan(self):
        sel = self.day_map.get(self.day_var.get())
        if self.items and not messagebox.askyesno("Cargar plan", "¿Reemplazar los ejercicios actuales?", parent=self):
            return
        self.items = []
        if sel:
            for re_ in self.db.routine_exercises(sel[1]):
                self.items.append({"exercise_id": re_["exercise_id"], "name": re_["name"],
                                   "measure": re_["measure"], "plan": re_, "sets": []})
        self._start_clock()
        self.render_exercises()
        if self.items:
            self.ex_tree.selection_set("0")

    def render_exercises(self):
        sel = self.ex_tree.selection()
        rows = []
        for i, it in enumerate(self.items):
            p = it.get("plan")
            plan = ""
            if p:
                unit = "s" if it["measure"] == "segundos" else ""
                plan = f"{p['planned_sets']}×{p['planned_reps_min']}-{p['planned_reps_max']}{unit}"
            done = len([s for s in it["sets"] if not s.get("is_warmup")])
            rows.append((str(i), [it["name"], plan, done]))
        fill_tree(self.ex_tree, rows)
        if sel and self.ex_tree.exists(sel[0]):
            self.ex_tree.selection_set(sel[0])

    def current(self):
        sel = self.ex_tree.selection()
        return self.items[int(sel[0])] if sel else None

    def show_current(self):
        it = self.current()
        if not it:
            self.ex_title.configure(text="Elige o añade un ejercicio")
            self.ex_info.configure(text="Carga el plan de una rutina o añade ejercicios con «+ Ejercicio».")
            fill_tree(self.set_tree, [])
            return
        e = self.db.exercise(it["exercise_id"])
        self.ex_title.configure(text=f"{e['name']}  {stars(e['difficulty'])}")
        is_sec = it["measure"] == "segundos"
        self.s_main_lbl.configure(text="Segundos" if is_sec else "Reps")
        info = []
        p = it.get("plan")
        if p:
            unit = "s" if is_sec else " reps"
            info.append(f"Plan: {p['planned_sets']} series de {p['planned_reps_min']}-{p['planned_reps_max']}{unit}, "
                        f"RIR {p['intensity_value']:g}, descanso {p['planned_rest_seconds']} s."
                        + (f" {p['notes']}" if p.get("notes") else ""))
        last = self.db.last_performance(it["exercise_id"])
        if last:
            ws = [s for s in last["sets"] if not s["is_warmup"]]
            info.append(f"Última vez ({last['date']}): " + ", ".join(fmt_set(s, it["measure"]) for s in ws))
            info.append(self._suggest(it, ws))
        else:
            info.append("Primera vez con este ejercicio: elige una carga con la que te queden 2-3 repeticiones "
                        "en reserva y revisa la técnica.")
        claves = e["technique"].get("claves") or []
        if claves:
            info.append("Clave: " + claves[0])
        self.ex_info.configure(text="\n".join(info))
        fill_tree(self.set_tree, [(str(i), [i + 1, fmt_set(s, it["measure"]),
                                            "calentamiento" if s.get("is_warmup") else
                                            ("fallo" if s.get("is_failure") else "efectiva")])
                                  for i, s in enumerate(it["sets"])])
        if last and not self.s_main.get():
            ws = [s for s in last["sets"] if not s["is_warmup"]]
            if ws:
                self.s_kg.set(f"{ws[0]['weight_kg']:g}" if ws[0]["weight_kg"] else "")

    def _suggest(self, it, ws):
        if not ws:
            return ""
        p = it.get("plan")
        key = "seconds" if it["measure"] == "segundos" else "reps"
        vals = [s[key] or 0 for s in ws]
        top = p["planned_reps_max"] if p else None
        if top and min(vals) >= top:
            if (ws[0]["weight_kg"] or 0) > 0:
                return f"➜ Completaste el rango: sube la carga un 2,5-5 % (≈ {ws[0]['weight_kg'] * 1.025:.1f} kg)."
            return "➜ Completaste el rango: añade lastre o pasa a la siguiente progresión (mira la técnica)."
        return f"➜ Objetivo de hoy: superar {max(vals)} {('s' if key == 'seconds' else 'reps')} en alguna serie."

    # ── acciones ──
    def add_exercise(self):
        p = ExercisePicker(self, self.db)
        if p.result:
            e = self.db.exercise(p.result)
            self.items.append({"exercise_id": e["id"], "name": e["name"], "measure": e["measure"],
                               "plan": None, "sets": []})
            self._start_clock()
            self.render_exercises()
            self.ex_tree.selection_set(str(len(self.items) - 1))

    def remove_exercise(self):
        sel = self.ex_tree.selection()
        if sel:
            del self.items[int(sel[0])]
            self.render_exercises()
            self.show_current()

    def view_technique(self):
        it = self.current()
        if it:
            self.app.open_technique(it["exercise_id"])

    def add_set(self):
        it = self.current()
        if not it:
            return
        main = to_int(self.s_main.get())
        if main is None:
            messagebox.showwarning("Serie", "Indica las repeticiones (o segundos).", parent=self)
            return
        s = {"weight_kg": to_float(self.s_kg.get()) or 0, "rir": to_int(self.s_rir.get()),
             "tempo": self.s_tempo.get().strip() or None, "is_warmup": self.s_warm.get(),
             "is_failure": self.s_fail.get()}
        if it["measure"] == "segundos":
            s["seconds"], s["reps"] = main, None
        else:
            s["reps"], s["seconds"] = main, None
        if s["is_failure"] and s["rir"] is None:
            s["rir"] = 0
        rest = (it["plan"] or {}).get("planned_rest_seconds") or int(self.db.get_setting("default_rest_seconds", "90"))
        s["rest_after_seconds"] = rest
        it["sets"].append(s)
        self._start_clock()
        self.s_warm.set(False)
        self.s_fail.set(False)
        self.render_exercises()
        self.show_current()
        if self.auto_timer.get() and not s["is_warmup"]:
            self.start_timer(rest)

    def repeat_set(self):
        it = self.current()
        if it and it["sets"]:
            s = it["sets"][-1]
            self.s_main.set(str(s.get("seconds") or s.get("reps") or ""))
            self.s_kg.set(f"{s['weight_kg']:g}" if s.get("weight_kg") else "")
            self.s_rir.set("" if s.get("rir") is None else str(s["rir"]))
            self.add_set()

    def delete_set(self):
        it = self.current()
        sel = self.set_tree.selection()
        if it and sel:
            del it["sets"][int(sel[0])]
            self.render_exercises()
            self.show_current()

    # ── temporizador ──
    def start_timer(self, seconds=None):
        it = self.current()
        if seconds is None:
            seconds = ((it or {}).get("plan") or {}).get("planned_rest_seconds") or \
                int(self.db.get_setting("default_rest_seconds", "90"))
        self.timer_left = int(seconds)
        self._tick()

    def bump_timer(self, d):
        self.timer_left = max(0, self.timer_left + d)
        self._draw_timer()

    def stop_timer(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_left = 0
        self._draw_timer()

    def _draw_timer(self):
        m, s = divmod(max(0, self.timer_left), 60)
        self.timer_lbl.configure(text=f"{m:02d}:{s:02d}", fg="#b91c1c" if 0 < self.timer_left <= 10 else "#111827")

    def _tick(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self._draw_timer()
        if self.timer_left <= 0:
            self.bell()
            self.timer_lbl.configure(text="¡A por la serie!", fg="#166534")
            return
        self.timer_left -= 1
        self.timer_job = self.after(1000, self._tick)

    # ── guardar ──
    def save(self):
        exercises = [{"exercise_id": it["exercise_id"], "sets": it["sets"]} for it in self.items if it["sets"]]
        if not exercises:
            messagebox.showwarning("Guardar", "Registra al menos una serie.", parent=self)
            return
        d = self.vars["date"].get().strip()
        try:
            date.fromisoformat(d)
        except ValueError:
            messagebox.showerror("Fecha", "Usa el formato AAAA-MM-DD.", parent=self)
            return
        sel = self.day_map.get(self.day_var.get())
        ended = datetime.now().replace(microsecond=0)
        started = self.started_at or ended
        data = {
            "date": d, "routine_id": sel[0] if sel else None, "routine_day_id": sel[1] if sel else None,
            "started_at": f"{d}T{started:%H:%M:%S}", "ended_at": f"{d}T{ended:%H:%M:%S}",
            "bodyweight_kg": to_float(self.vars["bodyweight_kg"].get()),
            "sleep_hours": to_float(self.vars["sleep_hours"].get()),
            "energy_level": to_int(self.vars["energy_level"].get()),
            "mood": to_int(self.vars["mood"].get()), "notes": self.notes.get().strip() or None,
            "exercises": exercises,
        }
        sid, prs, ach = self.db.save_session(data)
        s = self.db.session_detail(sid)
        n_sets = sum(len([x for x in e["sets"] if not x["is_warmup"]]) for e in s["exercises"])
        msg = [f"Duración: {s['duration_min'] or 0} min   ·   Series efectivas: {n_sets}",
               f"Tonelaje: {s['tonnage_kg']:g} kg   ·   RIR medio: {s['avg_rir'] if s['avg_rir'] is not None else '—'}"]
        if prs:
            msg.append("\n🏆 Récords personales:")
            labels = {"max_reps": "reps", "max_weight": "peso", "max_hold": "tiempo", "estimated_1rm": "1RM est."}
            for p in prs:
                msg.append(f"  • {self.db.exercise_name(p['exercise_id'])}: {labels[p['type']]} "
                           f"{p['value']:g} {p['unit']}" +
                           (f" (antes {p['previous_value']:g})" if p["previous_value"] is not None else ""))
        messagebox.showinfo("Sesión guardada", "\n".join(msg), parent=self)
        self.app.announce_achievements(ach)
        self.stop_timer()
        self.reset()
        self.app.refresh_all()


# ───────────────────────────── RUTINAS ─────────────────────────────
class RutinasTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=PAD)
        self.app = app
        self.db = app.db
        col1 = ttk.LabelFrame(self, text="Rutinas", padding=6)
        col1.pack(side="left", fill="y")
        frame, self.r_tree = make_tree(col1, [("n", "Nombre"), ("m", "Método"), ("d", "Días/sem")],
                                       heights=18, widths=[200, 90, 60])
        frame.pack(fill="both", expand=True)
        b = ttk.Frame(col1)
        b.pack(fill="x", pady=4)
        ttk.Button(b, text="Nueva", command=self.new_routine).pack(side="left")
        ttk.Button(b, text="Editar", command=self.edit_routine).pack(side="left", padx=3)
        ttk.Button(b, text="Eliminar", command=self.delete_routine).pack(side="left")
        self.r_notes = ttk.Label(col1, text="", wraplength=360, foreground=MUTED, justify="left")
        self.r_notes.pack(fill="x", pady=4)

        col2 = ttk.LabelFrame(self, text="Días", padding=6)
        col2.pack(side="left", fill="y", padx=PAD)
        frame, self.d_tree = make_tree(col2, [("n", "Día"), ("f", "Enfoque")], heights=18, widths=[150, 130])
        frame.pack(fill="both", expand=True)
        b = ttk.Frame(col2)
        b.pack(fill="x", pady=4)
        ttk.Button(b, text="+ Día", command=self.new_day).pack(side="left")
        ttk.Button(b, text="Eliminar día", command=self.delete_day).pack(side="left", padx=3)

        col3 = ttk.LabelFrame(self, text="Ejercicios del día", padding=6)
        col3.pack(side="left", fill="both", expand=True)
        frame, self.e_tree = make_tree(col3, [("o", "#"), ("n", "Ejercicio"), ("s", "Series"), ("r", "Reps/seg"),
                                              ("i", "RIR"), ("d", "Desc."), ("t", "Notas")],
                                       heights=18, widths=[30, 190, 55, 70, 45, 55, 200])
        frame.pack(fill="both", expand=True)
        b = ttk.Frame(col3)
        b.pack(fill="x", pady=4)
        ttk.Button(b, text="+ Ejercicio", command=self.add_ex).pack(side="left")
        ttk.Button(b, text="Editar", command=self.edit_ex).pack(side="left", padx=3)
        ttk.Button(b, text="Quitar", command=self.del_ex).pack(side="left")
        ttk.Button(b, text="▲", width=3, command=lambda: self.move_ex(-1)).pack(side="left", padx=3)
        ttk.Button(b, text="▼", width=3, command=lambda: self.move_ex(1)).pack(side="left")
        ttk.Button(b, text="Ver técnica", command=self.view_tech).pack(side="left", padx=3)
        self.vol_lbl = ttk.Label(col3, text="", foreground=MUTED, wraplength=600, justify="left")
        self.vol_lbl.pack(fill="x")

        self.r_tree.bind("<<TreeviewSelect>>", lambda e: self.load_days())
        self.d_tree.bind("<<TreeviewSelect>>", lambda e: self.load_exercises())
        self.e_tree.bind("<Double-1>", lambda e: self.edit_ex())

    def sel(self, tree):
        s = tree.selection()
        return s[0] if s else None

    def refresh(self):
        cur = self.sel(self.r_tree)
        fill_tree(self.r_tree, [(r["id"], [r["name"], r["method"], r["days_per_week"]]) for r in self.db.routines()])
        if cur and self.r_tree.exists(cur):
            self.r_tree.selection_set(cur)
        elif self.r_tree.get_children():
            self.r_tree.selection_set(self.r_tree.get_children()[0])
        self.load_days()

    def load_days(self):
        rid = self.sel(self.r_tree)
        cur = self.sel(self.d_tree)
        r = self.db.q1("SELECT * FROM routine WHERE id=?", (rid,)) if rid else None
        self.r_notes.configure(text=(f"Objetivo: {r['goal']} · ~{r['estimated_duration_min']} min\n{r['notes'] or ''}")
                               if r else "")
        days = self.db.routine_days(rid) if rid else []
        fill_tree(self.d_tree, [(d["id"], [d["day_label"], ", ".join(json.loads(d["focus"] or "[]"))]) for d in days])
        if cur and self.d_tree.exists(cur):
            self.d_tree.selection_set(cur)
        elif days:
            self.d_tree.selection_set(days[0]["id"])
        else:
            self.load_exercises()

    def load_exercises(self):
        did = self.sel(self.d_tree)
        cur = self.sel(self.e_tree)
        rows = self.db.routine_exercises(did) if did else []
        fill_tree(self.e_tree, [(r["id"], [r["ord"], r["name"], r["planned_sets"],
                                           f"{r['planned_reps_min']}-{r['planned_reps_max']}"
                                           + ("s" if r["measure"] == "segundos" else ""),
                                           r["intensity_value"], r["planned_rest_seconds"], r["notes"]])
                                for r in rows])
        if cur and self.e_tree.exists(cur):
            self.e_tree.selection_set(cur)
        # Series por músculo de toda la rutina (estimación semanal)
        rid = self.sel(self.r_tree)
        if rid:
            names = self.db.muscle_names()
            tot = {}
            for d in self.db.routine_days(rid):
                for re_ in self.db.routine_exercises(d["id"]):
                    for m in self.db.exercise(re_["exercise_id"])["primary_muscles"]:
                        tot[m] = tot.get(m, 0) + (re_["planned_sets"] or 0)
            r = self.db.q1("SELECT days_per_week FROM routine WHERE id=?", (rid,))
            ndays = len(self.db.routine_days(rid)) or 1
            factor = (r["days_per_week"] or ndays) / ndays
            txt = ", ".join(f"{names.get(m, m)} {v * factor:.0f}" for m, v in sorted(tot.items(), key=lambda x: -x[1]))
            self.vol_lbl.configure(text=f"Series semanales estimadas por músculo (objetivo 10-20): {txt}")

    def _routine_form(self, initial=None):
        return FormDialog(self, "Rutina", [
            ("name", "Nombre", "text", None), ("method", "Método", "combo", METHODS),
            ("goal", "Objetivo", "combo", GOALS), ("days_per_week", "Días por semana", "int", None),
            ("estimated_duration_min", "Duración (min)", "int", None), ("notes", "Notas", "multiline", None),
        ], initial or {"method": "full_body", "goal": "hipertrofia", "days_per_week": 3,
                       "estimated_duration_min": 60}).result

    def new_routine(self):
        r = self._routine_form()
        if r and r["name"]:
            rid = self.db.add_routine(r["name"], r["method"], r["goal"], r["days_per_week"] or 3,
                                      r["estimated_duration_min"] or 60, r["notes"])
            self.db.add_routine_day(rid, "Día A")
            self.refresh()
            self.r_tree.selection_set(rid)
            self.app.refresh_all()

    def edit_routine(self):
        rid = self.sel(self.r_tree)
        if not rid:
            return
        cur = self.db.q1("SELECT * FROM routine WHERE id=?", (rid,))
        r = self._routine_form(cur)
        if r and r["name"]:
            self.db.update_routine(rid, **r)
            self.refresh()

    def delete_routine(self):
        rid = self.sel(self.r_tree)
        if rid and messagebox.askyesno("Eliminar", "¿Eliminar la rutina y todos sus días?", parent=self):
            self.db.delete_routine(rid)
            self.refresh()
            self.app.refresh_all()

    def new_day(self):
        rid = self.sel(self.r_tree)
        if not rid:
            return
        r = FormDialog(self, "Día", [("label", "Nombre", "text", None),
                                     ("focus", "Enfoque (separado por comas)", "text", None)]).result
        if r and r["label"]:
            self.db.add_routine_day(rid, r["label"], [x.strip() for x in r["focus"].split(",") if x.strip()])
            self.load_days()

    def delete_day(self):
        did = self.sel(self.d_tree)
        if did and messagebox.askyesno("Eliminar", "¿Eliminar este día?", parent=self):
            self.db.delete_routine_day(did)
            self.load_days()

    def _ex_form(self, initial):
        return FormDialog(self, "Ejercicio planificado", [
            ("planned_sets", "Series", "int", None), ("planned_reps_min", "Reps/seg mín.", "int", None),
            ("planned_reps_max", "Reps/seg máx.", "int", None), ("intensity_value", "RIR objetivo", "float", None),
            ("planned_rest_seconds", "Descanso (s)", "int", None), ("tempo", "Tempo (ej. 2-0-2-0)", "text", None),
            ("notes", "Notas", "text", None),
        ], initial).result

    def add_ex(self):
        did = self.sel(self.d_tree)
        if not did:
            messagebox.showinfo("Rutinas", "Primero crea o elige un día.", parent=self)
            return
        p = ExercisePicker(self, self.db)
        if not p.result:
            return
        e = self.db.exercise(p.result)
        init = {"planned_sets": 4, "planned_reps_min": 15 if e["measure"] == "segundos" else 8,
                "planned_reps_max": 30 if e["measure"] == "segundos" else 12, "intensity_value": 2,
                "planned_rest_seconds": int(self.db.get_setting("default_rest_seconds", "90")), "tempo": "", "notes": ""}
        r = self._ex_form(init)
        if r:
            self.db.add_routine_exercise(did, p.result, r["planned_sets"] or 4, r["planned_reps_min"] or 8,
                                         r["planned_reps_max"] or 12, r["planned_rest_seconds"] or 90, "rir",
                                         r["intensity_value"] if r["intensity_value"] is not None else 2,
                                         r["tempo"], r["notes"])
            self.load_exercises()

    def edit_ex(self):
        reid = self.sel(self.e_tree)
        if not reid:
            return
        cur = self.db.q1("SELECT * FROM routine_exercise WHERE id=?", (reid,))
        r = self._ex_form(cur)
        if r:
            cols = ", ".join(f"{k}=?" for k in r)
            self.db.x(f"UPDATE routine_exercise SET {cols} WHERE id=?", (*r.values(), reid))
            self.load_exercises()

    def del_ex(self):
        reid = self.sel(self.e_tree)
        if reid:
            self.db.delete_routine_exercise(reid)
            self.load_exercises()

    def move_ex(self, d):
        reid = self.sel(self.e_tree)
        if reid:
            self.db.move_routine_exercise(reid, d)
            self.load_exercises()

    def view_tech(self):
        reid = self.sel(self.e_tree)
        if reid:
            r = self.db.q1("SELECT exercise_id FROM routine_exercise WHERE id=?", (reid,))
            self.app.open_technique(r["exercise_id"])


# ───────────────────────────── HISTORIAL ─────────────────────────────
class HistorialTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=PAD)
        self.app = app
        self.db = app.db
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        ses = ttk.Frame(nb, padding=6)
        nb.add(ses, text="  Sesiones  ")
        left = ttk.Frame(ses)
        left.pack(side="left", fill="both", expand=True)
        frame, self.tree = make_tree(left, [("d", "Fecha"), ("r", "Rutina"), ("m", "Min"), ("e", "Ejerc."),
                                            ("s", "Series"), ("t", "Tonelaje kg"), ("i", "RIR med.")],
                                     heights=22, widths=[90, 220, 50, 55, 55, 90, 60])
        frame.pack(fill="both", expand=True)
        b = ttk.Frame(left)
        b.pack(fill="x", pady=4)
        ttk.Button(b, text="Eliminar sesión", command=self.delete).pack(side="left")
        self.detail = tk.Text(ses, width=60, wrap="word", font=FONT, relief="flat", padx=10, pady=10)
        self.detail.pack(side="left", fill="both", expand=True, padx=(PAD, 0))
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.show())

        prs = ttk.Frame(nb, padding=6)
        nb.add(prs, text="  Récords personales  ")
        frame, self.pr_tree = make_tree(prs, [("d", "Fecha"), ("e", "Ejercicio"), ("t", "Tipo"), ("v", "Valor"),
                                              ("p", "Anterior")], heights=24, widths=[90, 240, 140, 100, 100])
        frame.pack(fill="both", expand=True)

    def refresh(self):
        rows = []
        for s in self.db.sessions():
            det = self.db.q1("SELECT COUNT(DISTINCT se.id) e, COUNT(sl.id) s FROM session_exercise se "
                             "LEFT JOIN set_log sl ON sl.session_exercise_id=se.id AND sl.is_warmup=0 "
                             "WHERE se.session_id=?", (s["id"],))
            rows.append((s["id"], [s["date"], self.db.routine_day_label(s["routine_day_id"]) or "Sesión libre",
                                   s["duration_min"], det["e"], det["s"], f"{s['tonnage_kg'] or 0:g}",
                                   s["avg_rir"]]))
        fill_tree(self.tree, rows)
        labels = {"max_reps": "Máx. reps", "max_weight": "Máx. peso", "max_hold": "Máx. tiempo",
                  "estimated_1rm": "1RM estimado"}
        fill_tree(self.pr_tree, [(p["id"], [p["date_achieved"], p["name"], labels.get(p["type"], p["type"]),
                                            f"{p['value']:g} {p['unit']}",
                                            "" if p["previous_value"] is None else f"{p['previous_value']:g}"])
                                 for p in self.db.personal_records()])
        self.show()

    def show(self):
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        sel = self.tree.selection()
        if not sel:
            self.detail.insert("end", "Selecciona una sesión para ver el detalle.")
            self.detail.configure(state="disabled")
            return
        s = self.db.session_detail(sel[0])
        t = self.detail
        t.tag_configure("h", font=FONT_H2)
        t.tag_configure("b", font=FONT_B)
        t.tag_configure("m", foreground=MUTED)
        t.tag_configure("pr", foreground="#92400e")
        t.insert("end", f"{s['date']}  ·  {self.db.routine_day_label(s['routine_day_id']) or 'Sesión libre'}\n", "h")
        meta = [f"Duración {s['duration_min'] or 0} min", f"Tonelaje {s['tonnage_kg'] or 0:g} kg"]
        for k, lbl in (("bodyweight_kg", "Peso"), ("sleep_hours", "Sueño"), ("energy_level", "Energía"),
                       ("mood", "Ánimo"), ("avg_rir", "RIR medio")):
            if s.get(k) is not None:
                meta.append(f"{lbl} {s[k]:g}")
        t.insert("end", " · ".join(meta) + "\n", "m")
        if s.get("notes"):
            t.insert("end", f"Notas: {s['notes']}\n", "m")
        for e in s["exercises"]:
            t.insert("end", f"\n{e['name']}\n", "b")
            for st in e["sets"]:
                kind = " (calentamiento)" if st["is_warmup"] else (" (fallo)" if st["is_failure"] else "")
                t.insert("end", f"   {st['set_number']}. {fmt_set(st, e['measure'])}{kind}")
                t.insert("end", "  🏆 PR\n" if st["is_pr"] else "\n", "pr")
            extra = []
            if e["tonnage_kg"]:
                extra.append(f"tonelaje {e['tonnage_kg']:g} kg")
            if e["estimated_1rm_kg"]:
                one = self.db.best_record(e["exercise_id"], "estimated_1rm")
                extra.append(f"1RM est. {e['estimated_1rm_kg']:g} kg")
                imr = metricas.imr(e["sets"], one)
                if imr:
                    extra.append(f"IMR {imr:g}% ({metricas.intensity_zone(imr)})")
            if extra:
                t.insert("end", "   " + " · ".join(extra) + "\n", "m")
        t.configure(state="disabled")

    def delete(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Eliminar", "¿Eliminar esta sesión y sus récords?", parent=self):
            self.db.delete_session(sel[0])
            self.app.refresh_all()
