"""Pestañas Inicio, Progreso, Cuerpo, Objetivos y Ajustes."""
import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import exportar, graficos, metricas, rutas
from .catalogo import BLOCKS
from .ui_comun import (FONT, FONT_B, FONT_H1, FONT_H2, MUTED, PAD, ExercisePicker, FormDialog,
                       ScrollFrame, fill_tree, make_tree, open_path, stars, to_float)

DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MEASURE_KEYS = ["cuello", "pecho", "cintura", "cadera", "biceps_der", "biceps_izq",
                "muslo_der", "muslo_izq", "pantorrilla_der", "pantorrilla_izq"]


def card(master, title, value, sub=""):
    f = tk.Frame(master, bg="#ffffff", highlightbackground="#e5e7eb", highlightthickness=1, padx=14, pady=10)
    tk.Label(f, text=title, bg="#ffffff", fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
    tk.Label(f, text=value, bg="#ffffff", fg="#111827", font=("Segoe UI", 20, "bold")).pack(anchor="w")
    if sub:
        tk.Label(f, text=sub, bg="#ffffff", fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
    return f


# ───────────────────────────── INICIO ─────────────────────────────
class InicioTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.db = app.db
        self.sf = ScrollFrame(self)
        self.sf.pack(fill="both", expand=True)

    def refresh(self):
        self.sf.clear()
        box = self.sf.inner
        box.configure(padding=16)
        p = self.db.profile()
        wso = self.db.get_setting("week_starts_on", "monday")
        target = int(self.db.get_setting("target_days_per_week", "3") or 3)
        today = date.today()
        ws = metricas.week_start(today, wso)
        cur, best = self.db.streaks()
        n_week = self.db.sessions_in_week(ws)
        total = self.db.q1("SELECT COUNT(*) n FROM session")["n"]
        ls = self.db.learning_summary()

        tk.Label(box, text=f"Hola, {p.get('name') or 'atleta'} 👋", font=FONT_H1, bg="#ffffff").pack(anchor="w")
        planned = self.db.q1("SELECT * FROM schedule_day WHERE date=?", (today.isoformat(),))
        done_today = self.db.q1("SELECT 1 FROM session WHERE date=?", (today.isoformat(),))
        if done_today:
            msg = "✅ Hoy ya entrenaste. ¡Buen trabajo! Descansa y come bien."
        elif planned and planned["status"] == "planificada":
            msg = f"📌 Hoy toca: {self.db.routine_day_label(planned['routine_day_id'])}. Ve a «Entrenar» y carga el plan."
        elif planned and planned["status"] == "descanso":
            msg = "😴 Hoy es día de descanso."
        else:
            msg = "Planifica tu semana abajo o registra una sesión libre en «Entrenar»."
        tk.Label(box, text=msg, font=FONT, bg="#ffffff", fg=MUTED).pack(anchor="w", pady=(2, 10))

        cards = tk.Frame(box, bg="#ffffff")
        cards.pack(fill="x")
        for i, (t, v, s) in enumerate([
            ("Racha actual", f"{cur} días", "se mantiene con ≤ 2 días de descanso seguidos"),
            ("Racha más larga", f"{best} días", ""),
            ("Esta semana", f"{n_week}/{target}", f"cumplimiento {metricas.weekly_compliance(n_week, target)} %"),
            ("Sesiones totales", str(total), ""),
            ("Aprendizaje", f"{ls['lessons_done']}/{ls['lessons_total']}", f"{ls['ex_mastered']} ejercicios dominados"),
        ]):
            card(cards, t, v, s).grid(row=0, column=i, padx=(0, 10), sticky="nsew")

        for m in self.db.deload_advice():
            tk.Label(box, text="⚠ " + m, bg="#fff7ed", fg="#9a3412", font=FONT, anchor="w", justify="left",
                     wraplength=900, padx=8, pady=4).pack(fill="x", pady=(8, 0))

        # Planificador semanal
        tk.Label(box, text="Mi semana", font=FONT_H2, bg="#ffffff").pack(anchor="w", pady=(16, 4))
        week = tk.Frame(box, bg="#ffffff")
        week.pack(fill="x")
        colors = {"completada": "#dcfce7", "planificada": "#dbeafe", "descanso": "#f3f4f6", "saltada": "#fee2e2"}
        for i, d in enumerate(self.db.schedule_week(ws)):
            dd = date.fromisoformat(d["date"])
            st = d.get("status")
            if st == "planificada" and dd < today:
                st = "saltada"
            f = tk.Frame(week, bg=colors.get(st, "#ffffff"), highlightbackground="#2f6fdb" if dd == today
                         else "#e5e7eb", highlightthickness=2 if dd == today else 1, padx=8, pady=6, width=150)
            f.grid(row=0, column=i, padx=3, sticky="nsew")
            week.columnconfigure(i, weight=1)
            tk.Label(f, text=f"{DAY_NAMES[dd.weekday()]} {dd.day}", font=FONT_B, bg=f["bg"]).pack(anchor="w")
            label = {"completada": "✓ Completada", "planificada": "Planificada", "descanso": "Descanso",
                     "saltada": "✗ Saltada"}.get(st, "—")
            tk.Label(f, text=label, bg=f["bg"], fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
            if d.get("routine_day_id"):
                tk.Label(f, text=self.db.routine_day_label(d["routine_day_id"]), bg=f["bg"], wraplength=130,
                         justify="left", font=("Segoe UI", 8)).pack(anchor="w")
            if st != "completada":
                ttk.Button(f, text="Planificar", command=lambda x=d["date"]: self.plan_day(x)).pack(anchor="w", pady=2)

        # Volumen semanal
        names = self.db.muscle_names()
        vol = self.db.weekly_sets_by_muscle(ws)
        freq = self.db.weekly_frequency_by_muscle(ws)
        rows = [(names[r["id"]], vol[r["id"]]) for r in self.db.q("SELECT id FROM muscle_group ORDER BY rowid")
                if vol.get(r["id"])]
        tk.Label(box, text="Volumen de esta semana", font=FONT_H2, bg="#ffffff").pack(anchor="w", pady=(16, 4))
        cv = tk.Canvas(box, height=max(120, 26 * len(rows) + 40), width=900, highlightthickness=0)
        cv.pack(fill="x")
        cv.bind("<Configure>", lambda e, c=cv, r=rows: graficos.volume_bars(c, r))
        if freq:
            low = [names[m] for m, n in freq.items() if n < 2]
            txt = "Frecuencia: " + ", ".join(f"{names[m]} ×{n}" for m, n in freq.items())
            if low:
                txt += f"   ·   Para frecuencia 2 (Martínez), entrena otra vez: {', '.join(low)}"
            tk.Label(box, text=txt, bg="#ffffff", fg=MUTED, wraplength=900, justify="left").pack(anchor="w")

        # PRs y logros
        cols = tk.Frame(box, bg="#ffffff")
        cols.pack(fill="x", pady=(16, 0))
        prf = tk.Frame(cols, bg="#ffffff")
        prf.pack(side="left", fill="both", expand=True)
        tk.Label(prf, text="Récords recientes", font=FONT_H2, bg="#ffffff").pack(anchor="w")
        labels = {"max_reps": "reps", "max_weight": "peso", "max_hold": "tiempo", "estimated_1rm": "1RM est."}
        prs = self.db.personal_records(limit=6)
        for pr in prs:
            tk.Label(prf, text=f"🏆 {pr['date_achieved']}  {pr['name']}: {labels.get(pr['type'])} "
                               f"{pr['value']:g} {pr['unit']}", bg="#ffffff", font=FONT).pack(anchor="w")
        if not prs:
            tk.Label(prf, text="Aún no hay récords.", bg="#ffffff", fg=MUTED).pack(anchor="w")
        af = tk.Frame(cols, bg="#ffffff")
        af.pack(side="left", fill="both", expand=True)
        ach = self.db.achievements()
        got = [a for a in ach if a["unlocked_at"]]
        tk.Label(af, text=f"Logros ({len(got)}/{len(ach)})", font=FONT_H2, bg="#ffffff").pack(anchor="w")
        for a in got[:6]:
            tk.Label(af, text=f"{a['icon']} {a['name']}  ({a['unlocked_at']})", bg="#ffffff").pack(anchor="w")
        nxt = [a for a in ach if not a["unlocked_at"]][:3]
        for a in nxt:
            tk.Label(af, text=f"🔒 {a['name']}: {a['description']}", bg="#ffffff", fg=MUTED).pack(anchor="w")

        # Siguiente paso de aprendizaje
        sk = self.db.next_skills(limit=4)
        if sk:
            tk.Label(box, text="Para aprender a continuación", font=FONT_H2, bg="#ffffff").pack(anchor="w", pady=(16, 4))
            f = tk.Frame(box, bg="#ffffff")
            f.pack(anchor="w")
            for e in sk:
                ttk.Button(f, text=f"{e['name']} {stars(e['difficulty'])}",
                           command=lambda i=e["id"]: self.app.open_technique(i)).pack(side="left", padx=(0, 4))

    def plan_day(self, d):
        options = {"Descanso": ("descanso", None), "(Quitar plan)": (None, None)}
        for r in self.db.routines():
            for dd in self.db.routine_days(r["id"]):
                options[f"{r['name']} · {dd['day_label']}"] = ("planificada", dd["id"])
        res = FormDialog(self, f"Planificar {d}", [("opt", "Sesión", "combo", list(options))],
                         {"opt": "Descanso"}).result
        if res and res["opt"]:
            st, did = options[res["opt"]]
            if st is None:
                self.db.clear_schedule(d)
            else:
                self.db.set_schedule(d, did, st)
            self.app.refresh_all()


# ───────────────────────────── PROGRESO ─────────────────────────────
class ProgresoTab(ttk.Frame):
    METRICS = {"1RM estimado (kg)": "e1rm", "Máx. repeticiones": "max_reps", "Máx. tiempo (s)": "max_seconds",
               "Máx. peso (kg)": "max_weight", "Tonelaje (kg)": "ton", "Series efectivas": "n_sets"}

    def __init__(self, master, app):
        super().__init__(master, padding=PAD)
        self.app = app
        self.db = app.db
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="Ejercicio:").pack(side="left")
        self.ex_var = tk.StringVar()
        self.ex_combo = ttk.Combobox(top, textvariable=self.ex_var, state="readonly", width=34)
        self.ex_combo.pack(side="left", padx=4)
        ttk.Label(top, text="Métrica:").pack(side="left", padx=(10, 0))
        self.m_var = tk.StringVar(value="Máx. repeticiones")
        ttk.Combobox(top, textvariable=self.m_var, values=list(self.METRICS), state="readonly",
                     width=20).pack(side="left", padx=4)
        self.stats = ttk.Label(top, text="", foreground=MUTED)
        self.stats.pack(side="left", padx=10)
        self.ex_var.trace_add("write", lambda *a: self.draw_exercise())
        self.m_var.trace_add("write", lambda *a: self.draw_exercise())

        grid = ttk.Frame(self)
        grid.pack(fill="both", expand=True, pady=6)
        grid.columnconfigure((0, 1), weight=1)
        grid.rowconfigure((0, 1), weight=1)
        self.c_ex = tk.Canvas(grid, height=230, width=520, highlightthickness=0)
        self.c_ton = tk.Canvas(grid, height=230, width=520, highlightthickness=0)
        self.c_heat = tk.Canvas(grid, height=190, width=520, highlightthickness=0)
        self.c_body = tk.Canvas(grid, height=190, width=520, highlightthickness=0)
        for i, c in enumerate((self.c_ex, self.c_ton, self.c_heat, self.c_body)):
            c.grid(row=i // 2, column=i % 2, sticky="nsew", padx=4, pady=4)
            c.bind("<Configure>", lambda e: self.after_idle(self.draw_all))
        self.c_zone = tk.Canvas(self, height=170, width=520, highlightthickness=0)
        self.c_zone.pack(fill="x", padx=4)
        self.ex_ids = {}

    def refresh(self):
        self.ex_ids = {e["name"]: e["id"] for e in self.db.trained_exercises()}
        self.ex_combo.configure(values=list(self.ex_ids))
        if self.ex_var.get() not in self.ex_ids and self.ex_ids:
            self.ex_var.set(next(iter(self.ex_ids)))
        self.draw_all()

    def select(self, ex_id):
        name = self.db.exercise_name(ex_id)
        self.refresh()
        if name in self.ex_ids:
            self.ex_var.set(name)
            e = self.db.exercise(ex_id)
            self.m_var.set("Máx. tiempo (s)" if e["measure"] == "segundos" else
                           ("1RM estimado (kg)" if e["category"] == "pesas" else "Máx. repeticiones"))

    def draw_all(self):
        self.draw_exercise()
        wso = self.db.get_setting("week_starts_on", "monday")
        wt = self.db.weekly_tonnage(12, wso)
        graficos.bar_chart(self.c_ton, [w["week_start"][5:] for w in wt], [w["tonnage_kg"] for w in wt],
                           "Tonelaje semanal (kg)")
        graficos.heatmap(self.c_heat, self.db.heatmap(26))
        ms = [m for m in self.db.measurements() if m["weight_kg"]]
        graficos.line_chart(self.c_body, [m["date"] for m in ms], [m["weight_kg"] for m in ms],
                            "Peso corporal (kg)", "kg", color="#7c3aed")
        dist = self.db.intensity_distribution(days=28)
        graficos.bar_chart(self.c_zone, list(dist), list(dist.values()),
                           "Series por zona de intensidad (% 1RM, últimas 4 semanas)",
                           colors=["#93c5fd", "#60a5fa", "#3b82f6", "#1d4ed8", "#1e3a8a"])

    def draw_exercise(self):
        ex_id = self.ex_ids.get(self.ex_var.get())
        if not ex_id:
            graficos.line_chart(self.c_ex, [], [], "Progreso por ejercicio")
            self.stats.configure(text="Registra sesiones para ver tu progreso.")
            return
        key = self.METRICS[self.m_var.get()]
        hist = self.db.exercise_history(ex_id)
        graficos.line_chart(self.c_ex, [h["date"] for h in hist], [h[key] for h in hist],
                            f"{self.ex_var.get()} · {self.m_var.get()}")
        last = self.db.last_performance(ex_id)
        one = self.db.best_record(ex_id, "estimated_1rm")
        txt = f"Sesiones: {len(hist)}"
        if one:
            txt += f" · Mejor 1RM est.: {one:g} kg"
            imr = metricas.imr(last["sets"], one) if last else None
            if imr:
                txt += f" · IMR última: {imr:g}% ({metricas.intensity_zone(imr)})"
        self.stats.configure(text=txt)


# ───────────────────────────── CUERPO ─────────────────────────────
class CuerpoTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=PAD)
        self.app = app
        self.db = app.db
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        med = ttk.Frame(nb, padding=6)
        nb.add(med, text="  Peso y medidas  ")
        b = ttk.Frame(med)
        b.pack(fill="x")
        ttk.Button(b, text="+ Nueva medición", style="Accent.TButton", command=self.add_measure).pack(side="left")
        ttk.Button(b, text="Eliminar", command=self.del_measure).pack(side="left", padx=4)
        cols = [("d", "Fecha"), ("w", "Peso"), ("f", "% grasa"), ("m", "Masa musc.")] + \
               [(k, k.replace("_", " ")) for k in MEASURE_KEYS] + [("n", "Notas")]
        frame, self.m_tree = make_tree(med, cols, heights=10, widths=[90, 60, 60, 70] + [70] * len(MEASURE_KEYS) + [150])
        frame.pack(fill="both", expand=True, pady=6)
        cf = ttk.Frame(med)
        cf.pack(fill="x")
        ttk.Label(cf, text="Gráfico:").pack(side="left")
        self.chart_key = tk.StringVar(value="weight_kg")
        ttk.Combobox(cf, textvariable=self.chart_key, state="readonly", width=18,
                     values=["weight_kg", "body_fat_pct", "muscle_mass_kg", *MEASURE_KEYS]).pack(side="left", padx=4)
        self.chart_key.trace_add("write", lambda *a: self.draw())
        self.canvas = tk.Canvas(med, height=220, width=800, highlightthickness=0)
        self.canvas.pack(fill="x", pady=6)
        self.canvas.bind("<Configure>", lambda e: self.draw())

        ph = ttk.Frame(nb, padding=6)
        nb.add(ph, text="  Fotos de progreso  ")
        b = ttk.Frame(ph)
        b.pack(fill="x")
        ttk.Button(b, text="+ Añadir foto", style="Accent.TButton", command=self.add_photo).pack(side="left")
        ttk.Button(b, text="Abrir", command=self.open_photo).pack(side="left", padx=4)
        ttk.Button(b, text="Comparar 2 seleccionadas", command=self.compare).pack(side="left")
        ttk.Button(b, text="Eliminar", command=self.del_photo).pack(side="left", padx=4)
        ttk.Button(b, text="Abrir carpeta", command=lambda: open_path(rutas.photos_dir())).pack(side="left")
        frame, self.p_tree = make_tree(ph, [("d", "Fecha"), ("p", "Pose"), ("w", "Peso"), ("n", "Notas"),
                                            ("f", "Archivo")], heights=18, widths=[90, 70, 60, 250, 300])
        self.p_tree.configure(selectmode="extended")
        frame.pack(fill="both", expand=True, pady=6)
        self.p_tree.bind("<Double-1>", lambda e: self.open_photo())

    def refresh(self):
        rows = []
        for m in reversed(self.db.measurements()):
            rows.append((m["id"], [m["date"], m["weight_kg"], m["body_fat_pct"], m["muscle_mass_kg"]] +
                         [m["measurements"].get(k) for k in MEASURE_KEYS] + [m["notes"]]))
        fill_tree(self.m_tree, rows)
        fill_tree(self.p_tree, [(p["id"], [p["date"], p["pose"], p["weight_kg"], p["notes"], p["file_path"]])
                                for p in self.db.photos()])
        self.draw()

    def draw(self):
        k = self.chart_key.get()
        ms = self.db.measurements()
        pts = [(m["date"], m.get(k) if k in m else m["measurements"].get(k)) for m in ms]
        pts = [(d, v) for d, v in pts if v is not None]
        graficos.line_chart(self.canvas, [d for d, _ in pts], [v for _, v in pts], k.replace("_", " "),
                            color="#7c3aed")

    def add_measure(self):
        fields = [("date", "Fecha (AAAA-MM-DD)", "text", None), ("weight_kg", "Peso (kg)", "float", None),
                  ("body_fat_pct", "% grasa", "float", None), ("muscle_mass_kg", "Masa muscular (kg)", "float", None)]
        fields += [(k, k.replace("_", " ").capitalize() + " (cm)", "float", None) for k in MEASURE_KEYS]
        fields += [("notes", "Notas", "text", None)]
        r = FormDialog(self, "Nueva medición", fields, {"date": date.today().isoformat()}).result
        if not r:
            return
        meas = {k: r[k] for k in MEASURE_KEYS if r.get(k) is not None}
        self.db.add_measurement(r["date"] or date.today().isoformat(), r["weight_kg"], r["body_fat_pct"],
                                r["muscle_mass_kg"], meas, r["notes"])
        self.app.announce_achievements(self.db.check_achievements())
        self.refresh()

    def del_measure(self):
        sel = self.m_tree.selection()
        if sel and messagebox.askyesno("Eliminar", "¿Eliminar esta medición?", parent=self):
            self.db.delete_measurement(sel[0])
            self.refresh()

    def add_photo(self):
        f = filedialog.askopenfilename(parent=self, title="Elegir foto",
                                       filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif *.webp"), ("Todos", "*.*")])
        if not f:
            return
        last = self.db.q1("SELECT weight_kg FROM body_measurement WHERE weight_kg IS NOT NULL ORDER BY date DESC LIMIT 1")
        r = FormDialog(self, "Foto de progreso", [
            ("date", "Fecha", "text", None), ("pose", "Pose", "combo", ["front", "side", "back", "flex"]),
            ("weight_kg", "Peso (kg)", "float", None), ("notes", "Notas", "text", None),
            ("tags", "Etiquetas (comas)", "text", None)],
            {"date": date.today().isoformat(), "pose": "front", "weight_kg": last["weight_kg"] if last else ""}).result
        if not r:
            return
        dest = exportar.copy_photo(f, rutas.photos_dir(), r["date"], r["pose"])
        rel = str(Path("media/photos") / dest.name)
        self.db.add_photo(r["date"], rel, r["pose"], r["weight_kg"], r["notes"],
                          [t.strip() for t in (r["tags"] or "").split(",") if t.strip()])
        self.refresh()

    def _abs(self, pid):
        p = self.db.q1("SELECT file_path FROM progress_photo WHERE id=?", (pid,))
        return rutas.data_dir() / p["file_path"]

    def open_photo(self):
        sel = self.p_tree.selection()
        if sel:
            open_path(self._abs(sel[0]))

    def del_photo(self):
        sel = self.p_tree.selection()
        if sel and messagebox.askyesno("Eliminar", "¿Quitar la foto del registro? (el archivo se conserva)", parent=self):
            for s in sel:
                self.db.delete_photo(s)
            self.refresh()

    def compare(self):
        sel = self.p_tree.selection()
        if len(sel) != 2:
            messagebox.showinfo("Comparar", "Selecciona exactamente 2 fotos (Ctrl + clic).", parent=self)
            return
        try:
            from PIL import Image, ImageTk
        except ImportError:
            for s in sel:
                open_path(self._abs(s))
            return
        win = tk.Toplevel(self)
        win.title("Comparador de fotos")
        win.imgs = []
        for i, s in enumerate(sorted(sel, key=lambda x: self.p_tree.item(x, "values")[0])):
            img = Image.open(self._abs(s))
            img.thumbnail((480, 640))
            tkimg = ImageTk.PhotoImage(img)
            win.imgs.append(tkimg)
            f = ttk.Frame(win, padding=6)
            f.grid(row=0, column=i)
            vals = self.p_tree.item(s, "values")
            ttk.Label(f, text=f"{vals[0]} · {vals[1]} · {vals[2]} kg", font=FONT_B).pack()
            tk.Label(f, image=tkimg).pack()


# ───────────────────────────── OBJETIVOS ─────────────────────────────
class ObjetivosTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=PAD)
        self.app = app
        self.db = app.db
        left = ttk.Frame(self)
        left.pack(side="left", fill="both", expand=True)
        b = ttk.Frame(left)
        b.pack(fill="x")
        ttk.Button(b, text="+ Nuevo objetivo", style="Accent.TButton", command=self.new_goal).pack(side="left")
        ttk.Button(b, text="Marcar logrado", command=self.done_goal).pack(side="left", padx=4)
        ttk.Button(b, text="Eliminar", command=self.del_goal).pack(side="left")
        self.sf = ScrollFrame(left)
        self.sf.pack(fill="both", expand=True, pady=6)
        right = ttk.LabelFrame(self, text="Logros", padding=6)
        right.pack(side="left", fill="y", padx=(PAD, 0))
        frame, self.a_tree = make_tree(right, [("i", ""), ("n", "Logro"), ("d", "Fecha")], heights=24,
                                       widths=[30, 220, 90])
        frame.pack(fill="both", expand=True)
        self.a_tree.tag_configure("locked", foreground="#9ca3af")
        self.selected = None

    def refresh(self):
        self.sf.clear()
        self._vars = []  # evita que tkinter libere las variables de las casillas
        box = self.sf.inner
        box.configure(padding=10)
        goals = self.db.goals()
        if not goals:
            tk.Label(box, text="Sin objetivos. Crea uno o usa «Crear objetivo con esta cadena» en Aprendizaje.",
                     bg="#ffffff", fg=MUTED).pack(anchor="w")
        for g in goals:
            f = tk.Frame(box, bg="#ffffff", highlightthickness=2 if g["id"] == self.selected else 1,
                         highlightbackground="#2f6fdb" if g["id"] == self.selected else "#e5e7eb", padx=10, pady=8)
            f.pack(fill="x", pady=4)
            f.bind("<Button-1>", lambda e, gid=g["id"]: self._select(gid))
            title = ("✅ " if g["done"] else "") + g["title"]
            tk.Label(f, text=title, font=FONT_H2, bg="#ffffff").pack(anchor="w")
            meta = f"{g['type']}"
            if g["target_exercise_id"]:
                meta += f" · {self.db.exercise_name(g['target_exercise_id'])}"
            if g["deadline"]:
                meta += f" · fecha límite {g['deadline']}"
            tk.Label(f, text=meta, bg="#ffffff", fg=MUTED).pack(anchor="w")
            pb = ttk.Progressbar(f, maximum=100, value=g["progress_pct"], length=400)
            pb.pack(anchor="w", pady=4)
            tk.Label(f, text=f"{g['progress_pct']} %", bg="#ffffff", font=FONT_B).pack(anchor="w")
            for m in g["milestones"]:
                v = tk.BooleanVar(value=bool(m["done"]))
                self._vars.append(v)
                ttk.Checkbutton(f, text=m["label"], variable=v,
                                command=lambda mid=m["id"]: self._toggle(mid)).pack(anchor="w")
            if g["target_exercise_id"]:
                ttk.Button(f, text="Ver técnica del objetivo",
                           command=lambda x=g["target_exercise_id"]: self.app.open_technique(x)).pack(anchor="w", pady=2)
            for w in f.winfo_children():
                if isinstance(w, tk.Label):
                    w.bind("<Button-1>", lambda e, gid=g["id"]: self._select(gid))
        rows = []
        for a in self.db.achievements():
            rows.append((a["id"], [a["icon"] if a["unlocked_at"] else "🔒", a["name"], a["unlocked_at"] or "—"]))
        self.a_tree.delete(*self.a_tree.get_children())
        for iid, vals in rows:
            self.a_tree.insert("", "end", iid=iid, values=vals, tags=() if vals[2] != "—" else ("locked",))

    def _select(self, gid):
        self.selected = gid
        self.refresh()

    def _toggle(self, mid):
        self.db.toggle_milestone(mid)
        self.refresh()

    def new_goal(self):
        r = FormDialog(self, "Nuevo objetivo", [
            ("title", "Título", "text", None),
            ("type", "Tipo", "combo", ["habilidad", "fuerza", "hipertrofia", "resistencia", "composicion"]),
            ("pick", "Elegir ejercicio objetivo", "check", None),
            ("deadline", "Fecha límite (AAAA-MM-DD)", "text", None),
            ("milestones", "Hitos (uno por línea; vacío = usar la cadena de progresión)", "multiline", None),
            ("notes", "Notas", "text", None)], {"type": "habilidad", "pick": True}).result
        if not r or not r["title"]:
            return
        ex_id = None
        if r["pick"]:
            p = ExercisePicker(self, self.db, "Ejercicio objetivo")
            ex_id = p.result
        ms = [x.strip() for x in r["milestones"].splitlines() if x.strip()]
        if not ms and ex_id:
            ms = self.db.chain_milestones(ex_id)
        self.db.add_goal(r["title"], r["type"], ex_id, r["deadline"] or None, ms, r["notes"])
        self.refresh()

    def done_goal(self):
        if self.selected:
            self.db.set_goal_done(self.selected, True)
            self.refresh()
        else:
            messagebox.showinfo("Objetivos", "Haz clic en un objetivo para seleccionarlo.", parent=self)

    def del_goal(self):
        if self.selected and messagebox.askyesno("Eliminar", "¿Eliminar el objetivo seleccionado?", parent=self):
            self.db.delete_goal(self.selected)
            self.selected = None
            self.refresh()


# ───────────────────────────── AJUSTES ─────────────────────────────
class AjustesTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=PAD)
        self.app = app
        self.db = app.db
        prof = ttk.LabelFrame(self, text="Perfil", padding=10)
        prof.pack(fill="x")
        self.pvars = {}
        pf = [("name", "Nombre"), ("birth_date", "Nacimiento (AAAA-MM-DD)"), ("sex", "Sexo (M/F/otro)"),
              ("height_cm", "Altura (cm)"), ("experience_level", "Nivel"), ("primary_focus", "Enfoque (comas)")]
        for i, (k, lbl) in enumerate(pf):
            ttk.Label(prof, text=lbl).grid(row=i // 3, column=(i % 3) * 2, sticky="w", padx=(0, 4), pady=3)
            v = tk.StringVar()
            if k == "experience_level":
                w = ttk.Combobox(prof, textvariable=v, values=["principiante", "intermedio", "avanzado"],
                                 state="readonly", width=18)
            else:
                w = ttk.Entry(prof, textvariable=v, width=22)
            w.grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="w", padx=(0, 16), pady=3)
            self.pvars[k] = v

        st = ttk.LabelFrame(self, text="Ajustes", padding=10)
        st.pack(fill="x", pady=PAD)
        self.svars = {}
        sf = [("default_rest_seconds", "Descanso por defecto (s)", None),
              ("target_days_per_week", "Objetivo de días/semana", None),
              ("week_starts_on", "La semana empieza", ["monday", "sunday"]),
              ("auto_backup_days", "Copia automática cada (días)", None),
              ("units", "Unidades", ["metric"])]
        for i, (k, lbl, opts) in enumerate(sf):
            ttk.Label(st, text=lbl).grid(row=i // 3, column=(i % 3) * 2, sticky="w", padx=(0, 4), pady=3)
            v = tk.StringVar()
            w = ttk.Combobox(st, textvariable=v, values=opts, state="readonly", width=12) if opts else \
                ttk.Entry(st, textvariable=v, width=12)
            w.grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="w", padx=(0, 16), pady=3)
            self.svars[k] = v
        ttk.Button(self, text="Guardar perfil y ajustes", style="Accent.TButton", command=self.save).pack(anchor="w")

        data = ttk.LabelFrame(self, text="Datos, exportación y respaldo", padding=10)
        data.pack(fill="x", pady=PAD)
        for txt, cmd in (("Exportar JSON completo", self.exp_json), ("Exportar CSV (por tabla)", self.exp_csv),
                         ("Importar / restaurar JSON", self.imp_json), ("Copia de seguridad ahora", self.backup),
                         ("Abrir carpeta de datos", lambda: open_path(rutas.data_dir()))):
            ttk.Button(data, text=txt, command=cmd).pack(side="left", padx=(0, 6))
        self.data_lbl = ttk.Label(self, text="", foreground=MUTED)
        self.data_lbl.pack(anchor="w")

        ex = ttk.LabelFrame(self, text="Ejercicio personalizado", padding=10)
        ex.pack(fill="x", pady=PAD)
        ttk.Label(ex, text="Añade ejercicios propios a la biblioteca (con su técnica y cadena de progresión).",
                  foreground=MUTED).pack(side="left")
        ttk.Button(ex, text="+ Crear ejercicio", command=self.custom_ex).pack(side="left", padx=8)

    def refresh(self):
        p = self.db.profile()
        for k, v in self.pvars.items():
            val = p.get(k)
            v.set(", ".join(val) if isinstance(val, list) else ("" if val is None else str(val)))
        s = self.db.settings()
        for k, v in self.svars.items():
            v.set(s.get(k, ""))
        self.data_lbl.configure(text=f"Datos en: {rutas.data_dir()}   ·   Última copia: {s.get('last_backup') or 'nunca'}")

    def save(self):
        p = {k: v.get().strip() for k, v in self.pvars.items()}
        p["height_cm"] = to_float(p["height_cm"])
        p["primary_focus"] = [x.strip() for x in p["primary_focus"].split(",") if x.strip()]
        self.db.save_profile(**p)
        for k, v in self.svars.items():
            self.db.set_setting(k, v.get().strip())
        messagebox.showinfo("Ajustes", "Guardado.", parent=self)
        self.app.refresh_all()

    def exp_json(self):
        f = filedialog.asksaveasfilename(parent=self, defaultextension=".json", initialdir=rutas.exports_dir(),
                                         initialfile=f"entrenador_{date.today()}.json",
                                         filetypes=[("JSON", "*.json")])
        if f:
            exportar.export_json(self.db, f)
            messagebox.showinfo("Exportar", f"Exportado a:\n{f}", parent=self)

    def exp_csv(self):
        d = filedialog.askdirectory(parent=self, initialdir=rutas.exports_dir(), title="Carpeta para los CSV")
        if d:
            out = exportar.export_csv(self.db, Path(d) / f"csv_{date.today()}")
            messagebox.showinfo("Exportar", f"CSV guardados en:\n{out}", parent=self)

    def imp_json(self):
        f = filedialog.askopenfilename(parent=self, filetypes=[("JSON", "*.json")], initialdir=rutas.exports_dir())
        if not f:
            return
        if not messagebox.askyesno("Restaurar", "Esto REEMPLAZA todos tus datos actuales por los del archivo.\n"
                                                "Se hará antes una copia de seguridad. ¿Continuar?", parent=self):
            return
        exportar.backup(self.db, rutas.backups_dir(), force=True)
        try:
            exportar.import_json(self.db, f)
        except (ValueError, KeyError) as e:
            messagebox.showerror("Restaurar", str(e), parent=self)
            return
        messagebox.showinfo("Restaurar", "Datos restaurados.", parent=self)
        self.app.refresh_all()

    def backup(self):
        dest = exportar.backup(self.db, rutas.backups_dir(), force=True)
        messagebox.showinfo("Copia de seguridad", f"Copia creada:\n{dest}", parent=self)
        self.refresh()

    def custom_ex(self):
        blocks = {n: b for b, n in BLOCKS}
        muscles = {v: k for k, v in self.db.muscle_names().items()}
        r = FormDialog(self, "Nuevo ejercicio", [
            ("name", "Nombre", "text", None), ("category", "Categoría", "combo", ["calistenia", "pesas"]),
            ("block", "Bloque", "combo", list(blocks)), ("difficulty", "Dificultad 1-5", "int", None),
            ("type", "Tipo", "combo", ["dinamico", "estatico"]), ("measure", "Se mide en", "combo", ["reps", "segundos"]),
            ("primary", "Músculo principal", "combo", list(muscles)),
            ("secondary", "Músculo secundario", "combo", ["", *muscles]),
            ("description", "Descripción", "multiline", None),
            ("pasos", "Pasos de técnica (uno por línea)", "multiline", None),
            ("errores", "Errores comunes (uno por línea)", "multiline", None),
            ("claves", "Claves (una por línea)", "multiline", None)],
            {"category": "calistenia", "block": "Flexiones", "difficulty": 2, "type": "dinamico", "measure": "reps"},
            width=520).result
        if not r or not r["name"] or not r["primary"]:
            return
        lines = lambda s: [x.strip() for x in (s or "").splitlines() if x.strip()]  # noqa: E731
        prev = ExercisePicker(self, self.db, "Ejercicio previo en la cadena (opcional, Cancelar para omitir)").result
        ex_id = self.db.add_custom_exercise({
            "name": r["name"], "category": r["category"], "block": blocks[r["block"]],
            "difficulty": max(1, min(5, r["difficulty"] or 1)), "type": r["type"], "measure": r["measure"],
            "primary_muscles": [muscles[r["primary"]]],
            "secondary_muscles": [muscles[r["secondary"]]] if r["secondary"] else [],
            "equipment": [], "description": r["description"],
            "progressions_to_reach": [prev] if prev else [], "progresses_to": [],
            "technique": {"pasos": lines(r["pasos"]), "errores": lines(r["errores"]), "claves": lines(r["claves"]),
                          "respiracion": "", "criterio_avance": "", "seguridad": ""},
        })
        self.app.open_technique(ex_id)
