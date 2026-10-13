"""Sección de Aprendizaje: biblioteca de técnica, lecciones con quiz y ruta de habilidades."""
import tkinter as tk
from tkinter import messagebox, ttk

from . import lecciones
from .catalogo import BLOCKS
from .db import LEARN_STATES
from .ui_comun import (ACCENT, FONT, FONT_B, FONT_H1, FONT_H2, MUTED, PAD, ScrollFrame,
                       fill_tree, make_tree, stars)

STATE_LABEL = {"pendiente": "○ Pendiente", "aprendiendo": "◐ Aprendiendo", "dominado": "● Dominado"}
STATE_COLOR = {"pendiente": "#e5e7eb", "aprendiendo": "#fde68a", "dominado": "#86efac"}
TYPE_LABEL = {"dinamico": "Dinámico", "estatico": "Estático / isométrico", "isometrico": "Isométrico"}
PR_LABEL = {"max_reps": "Máx. repeticiones", "max_weight": "Máx. peso", "max_hold": "Máx. tiempo",
            "estimated_1rm": "1RM estimado"}


def wrap_label(master, text, font=FONT, fg=None, **pack):
    lbl = tk.Label(master, text=text, font=font, fg=fg or "#1f2937", bg="#ffffff",
                   justify="left", anchor="w", wraplength=560)
    lbl.pack(fill="x", anchor="w", **pack)
    # Ajusta el ancho de línea al redimensionar.
    lbl.bind("<Configure>", lambda e: lbl.configure(wraplength=max(200, e.width - 10)))
    return lbl


def section(master, title):
    tk.Label(master, text=title, font=FONT_H2, bg="#ffffff", fg="#111827", anchor="w").pack(
        fill="x", pady=(14, 4))


class AprendizajeTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=PAD)
        self.app = app
        self.db = app.db
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)
        self.library = TechniqueLibrary(self.nb, self)
        self.lessons = LessonsView(self.nb, self)
        self.path = SkillPath(self.nb, self)
        self.nb.add(self.library, text="  Biblioteca de técnica  ")
        self.nb.add(self.lessons, text="  Lecciones y quiz  ")
        self.nb.add(self.path, text="  Ruta de habilidades  ")
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refresh())

    def refresh(self):
        current = self.nb.nametowidget(self.nb.select())
        current.refresh()

    def open_exercise(self, ex_id):
        self.nb.select(self.library)
        self.library.show(ex_id, select=True)

    def announce(self, unlocked):
        if unlocked:
            self.app.announce_achievements(unlocked)


# ───────────────────────────── Biblioteca ─────────────────────────────
class TechniqueLibrary(ttk.Frame):
    def __init__(self, master, parent):
        super().__init__(master, padding=PAD)
        self.parent = parent
        self.db = parent.db
        self.current = None

        left = ttk.Frame(self)
        left.pack(side="left", fill="y")
        f = ttk.Frame(left)
        f.pack(fill="x", pady=(0, 6))
        self.q = tk.StringVar()
        ttk.Label(f, text="Buscar").grid(row=0, column=0, sticky="w")
        ttk.Entry(f, textvariable=self.q, width=28).grid(row=0, column=1, sticky="ew", padx=4)
        self.blocks = {"Todos los bloques": None, **{n: b for b, n in BLOCKS}}
        self.block = tk.StringVar(value="Todos los bloques")
        ttk.Label(f, text="Bloque").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Combobox(f, textvariable=self.block, values=list(self.blocks), state="readonly", width=26).grid(
            row=1, column=1, sticky="ew", padx=4, pady=2)
        self.state = tk.StringVar(value="Todos")
        ttk.Label(f, text="Estado").grid(row=2, column=0, sticky="w")
        ttk.Combobox(f, textvariable=self.state, values=["Todos", *LEARN_STATES], state="readonly",
                     width=26).grid(row=2, column=1, sticky="ew", padx=4)
        frame, self.tree = make_tree(left, [("name", "Ejercicio"), ("dif", "Dif."), ("st", "Estado")],
                                     heights=24, widths=[200, 80, 90])
        frame.pack(fill="both", expand=True)
        self.tree.tag_configure("dominado", background="#ecfdf3")
        self.tree.tag_configure("aprendiendo", background="#fffbeb")
        for v in (self.q, self.block, self.state):
            v.trace_add("write", lambda *a: self.refresh())
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.detail = ScrollFrame(self)
        self.detail.pack(side="left", fill="both", expand=True, padx=(PAD, 0))
        self.detail.inner.configure(padding=16)

    def refresh(self):
        rows = self.db.exercises(block=self.blocks.get(self.block.get()), search=self.q.get().strip() or None)
        out = []
        for r in rows:
            st = self.db.learning_status(r["id"])["status"]
            if self.state.get() != "Todos" and st != self.state.get():
                continue
            out.append((r["id"], [r["name"], stars(r["difficulty"]), STATE_LABEL[st]], st))
        self.tree.delete(*self.tree.get_children())
        for iid, vals, st in out:
            self.tree.insert("", "end", iid=iid, values=vals, tags=(st,))
        if self.current and self.tree.exists(self.current):
            self.tree.selection_set(self.current)
        elif self.current is None and out:
            self.show(out[0][0], select=True)

    def _on_select(self, _e):
        sel = self.tree.selection()
        if sel and sel[0] != self.current:
            self.show(sel[0])

    def show(self, ex_id, select=False):
        e = self.db.exercise(ex_id)
        if not e:
            return
        self.current = ex_id
        if select:
            if not self.tree.exists(ex_id):
                self.q.set("")
                self.block.set("Todos los bloques")
                self.state.set("Todos")
            if self.tree.exists(ex_id):
                self.tree.selection_set(ex_id)
                self.tree.see(ex_id)
        names = self.db.muscle_names()
        eq = self.db.equipment_names()
        t = e["technique"]
        d = self.detail
        d.clear()
        box = d.inner
        bnames = dict(BLOCKS)

        tk.Label(box, text=e["name"], font=FONT_H1, bg="#ffffff", anchor="w").pack(fill="x")
        meta = (f"{stars(e['difficulty'])}   ·   {bnames.get(e['block'], e['block'])}   ·   "
                f"{TYPE_LABEL.get(e['type'], e['type'])}   ·   se mide en {e['measure']}"
                + ("   ·   unilateral" if e["unilateral"] else ""))
        wrap_label(box, meta, fg=MUTED)

        # Estado de aprendizaje
        st_frame = tk.Frame(box, bg="#ffffff")
        st_frame.pack(fill="x", pady=(10, 0))
        tk.Label(st_frame, text="Mi estado:", font=FONT_B, bg="#ffffff").pack(side="left")
        cur = self.db.learning_status(ex_id)["status"]
        self.st_var = tk.StringVar(value=cur)
        for s in LEARN_STATES:
            ttk.Radiobutton(st_frame, text=STATE_LABEL[s], value=s, variable=self.st_var,
                            command=lambda: self._set_state(ex_id)).pack(side="left", padx=6)

        wrap_label(box, e["description"], pady=(10, 0))

        section(box, "Músculos y material")
        wrap_label(box, "Principales: " + (", ".join(names.get(m, m) for m in e["primary_muscles"]) or "—"))
        if e["secondary_muscles"]:
            wrap_label(box, "Secundarios: " + ", ".join(names.get(m, m) for m in e["secondary_muscles"]), fg=MUTED)
        wrap_label(box, "Material: " + (", ".join(eq.get(x, x) for x in e["equipment"]) or "—"), fg=MUTED)

        if t.get("pasos"):
            section(box, "Cómo hacerlo, paso a paso")
            for i, p in enumerate(t["pasos"], start=1):
                wrap_label(box, f"{i}.  {p}", pady=1)
        if t.get("claves"):
            section(box, "Claves técnicas")
            for c in t["claves"]:
                wrap_label(box, f"✓  {c}", fg="#166534", pady=1)
        if t.get("errores"):
            section(box, "Errores comunes")
            for c in t["errores"]:
                wrap_label(box, f"✗  {c}", fg="#991b1b", pady=1)
        if t.get("respiracion"):
            section(box, "Respiración")
            wrap_label(box, t["respiracion"])
        if t.get("seguridad"):
            section(box, "Seguridad")
            wrap_label(box, "⚠  " + t["seguridad"], fg="#92400e")
        if t.get("criterio_avance"):
            section(box, "¿Cuándo avanzar?")
            wrap_label(box, t["criterio_avance"])

        # Cadena de progresión
        before, after = self.db.progression_chain(ex_id, depth=4)
        section(box, "Cadena de progresión")
        chain = tk.Frame(box, bg="#ffffff")
        chain.pack(fill="x")
        col = 0
        for level in reversed(before):
            self._chain_column(chain, level, col)
            col += 1
            tk.Label(chain, text="→", bg="#ffffff", font=FONT_H2).grid(row=0, column=col)
            col += 1
        self._chain_column(chain, [ex_id], col, current=True)
        col += 1
        for level in after:
            tk.Label(chain, text="→", bg="#ffffff", font=FONT_H2).grid(row=0, column=col)
            col += 1
            self._chain_column(chain, level, col)
            col += 1
        if not before and not after:
            wrap_label(box, "Ejercicio independiente (sin cadena definida).", fg=MUTED)

        # Historial personal
        section(box, "Tu registro")
        last = self.db.last_performance(ex_id)
        if last:
            sets = ", ".join(
                (f"{s['reps'] or 0}" if e["measure"] == "reps" else f"{s['seconds'] or 0}s")
                + (f"×{s['weight_kg']:g}kg" if s["weight_kg"] else "")
                for s in last["sets"] if not s["is_warmup"])
            wrap_label(box, f"Última vez ({last['date']}): {sets}")
        else:
            wrap_label(box, "Aún no lo has registrado en una sesión.", fg=MUTED)
        for r in self.db.best_records():
            if r["exercise_id"] == ex_id:
                wrap_label(box, f"🏆 {PR_LABEL.get(r['type'], r['type'])}: {r['value']:g} {r['unit']} "
                                f"({r['date_achieved']})", fg="#92400e")

        btns = tk.Frame(box, bg="#ffffff")
        btns.pack(fill="x", pady=(16, 4))
        ttk.Button(btns, text="Crear objetivo con esta cadena",
                   command=lambda: self._goal_from(ex_id)).pack(side="left")
        ttk.Button(btns, text="Ver progreso",
                   command=lambda: self.parent.app.show_progress(ex_id)).pack(side="left", padx=6)

    def _chain_column(self, master, ids, col, current=False):
        f = tk.Frame(master, bg="#ffffff")
        f.grid(row=0, column=col, sticky="n", padx=2, pady=2)
        for x in ids:
            ex = self.db.q1("SELECT name, difficulty FROM exercise WHERE id=?", (x,))
            st = self.db.learning_status(x)["status"]
            b = tk.Button(f, text=f"{ex['name']}\n{stars(ex['difficulty'])}", wraplength=130,
                          bg=ACCENT if current else STATE_COLOR[st], fg="#ffffff" if current else "#111827",
                          relief="flat", font=("Segoe UI", 9, "bold" if current else "normal"),
                          padx=6, pady=4, cursor="hand2", command=lambda i=x: self.show(i, select=True))
            b.pack(fill="x", pady=2)

    def _set_state(self, ex_id):
        unlocked = self.db.set_learning(ex_id, "ejercicio", self.st_var.get())
        st = self.st_var.get()
        if self.tree.exists(ex_id):
            vals = list(self.tree.item(ex_id, "values"))
            vals[2] = STATE_LABEL[st]
            self.tree.item(ex_id, values=vals, tags=(st,))
        self.parent.announce(unlocked)

    def _goal_from(self, ex_id):
        ms = self.db.chain_milestones(ex_id)
        name = self.db.exercise_name(ex_id)
        self.db.add_goal(f"Conseguir: {name}", "habilidad", ex_id, None, ms,
                         "Creado desde la biblioteca de técnica.")
        messagebox.showinfo("Objetivo creado",
                            f"Se creó el objetivo «{name}» con {len(ms)} hitos de la cadena de progresión.\n"
                            "Puedes verlo en la pestaña Objetivos.", parent=self)


# ───────────────────────────── Lecciones ─────────────────────────────
class LessonsView(ttk.Frame):
    def __init__(self, master, parent):
        super().__init__(master, padding=PAD)
        self.parent = parent
        self.db = parent.db
        self.current = None
        left = ttk.Frame(self)
        left.pack(side="left", fill="y")
        self.summary = ttk.Label(left, text="", font=FONT_B)
        self.summary.pack(anchor="w", pady=(0, 4))
        self.pbar = ttk.Progressbar(left, maximum=len(lecciones.LESSONS), length=280)
        self.pbar.pack(fill="x", pady=(0, 8))
        frame, self.tree = make_tree(left, [("t", "Lección"), ("c", "Tema"), ("s", "Estado")],
                                     heights=24, widths=[250, 100, 110])
        frame.pack(fill="both", expand=True)
        self.tree.tag_configure("dominado", background="#ecfdf3")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.detail = ScrollFrame(self)
        self.detail.pack(side="left", fill="both", expand=True, padx=(PAD, 0))
        self.detail.inner.configure(padding=16)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        done = 0
        for l in lecciones.LESSONS:
            st = self.db.learning_status(l["id"])
            ok = st["status"] == "dominado"
            done += ok
            score = st.get("quiz_score")
            label = "✓ Hecha" if ok else ("Leída" if st["status"] == "aprendiendo" else "Nueva")
            if score is not None:
                label += f" · {round(score * 100)}%"
            self.tree.insert("", "end", iid=l["id"], values=[l["titulo"], l["categoria"], label],
                             tags=("dominado",) if ok else ())
        self.summary.configure(text=f"Lecciones completadas: {done} / {len(lecciones.LESSONS)}")
        self.pbar.configure(value=done)
        target = self.current or lecciones.LESSONS[0]["id"]
        self.tree.selection_set(target)
        self.tree.see(target)

    def _on_select(self, _e):
        sel = self.tree.selection()
        if sel and sel[0] != self.current:
            self.show(sel[0])

    def show(self, lid):
        l = next(x for x in lecciones.LESSONS if x["id"] == lid)
        self.current = lid
        if self.db.learning_status(lid)["status"] == "pendiente":
            self.db.set_learning(lid, "leccion", "aprendiendo")
        d = self.detail
        d.clear()
        box = d.inner
        tk.Label(box, text=l["titulo"], font=FONT_H1, bg="#ffffff", anchor="w").pack(fill="x")
        wrap_label(box, f"{l['categoria']}  ·  Fuente: {l['fuente']}", fg=MUTED)
        wrap_label(box, l["resumen"], font=("Segoe UI", 11, "italic"), pady=(10, 4))
        section(box, "Puntos clave")
        for p in l["puntos"]:
            wrap_label(box, "•  " + p, pady=2)

        section(box, "Comprueba lo aprendido")
        self.answers = []
        self.feedback = []
        for qi, (preg, ops, _ok, _expl) in enumerate(l["quiz"]):
            wrap_label(box, f"{qi + 1}. {preg}", font=FONT_B, pady=(8, 2))
            var = tk.IntVar(value=-1)
            self.answers.append(var)
            for oi, op in enumerate(ops):
                ttk.Radiobutton(box, text=op, value=oi, variable=var).pack(anchor="w", padx=16)
            fb = wrap_label(box, "", fg=MUTED)
            self.feedback.append(fb)
        bar = tk.Frame(box, bg="#ffffff")
        bar.pack(fill="x", pady=12)
        ttk.Button(bar, text="Comprobar respuestas", style="Accent.TButton",
                   command=lambda: self._check(l)).pack(side="left")
        ttk.Button(bar, text="Marcar como completada",
                   command=lambda: self._complete(l["id"])).pack(side="left", padx=6)
        self.result_lbl = wrap_label(box, "", font=FONT_B)

    def _check(self, l):
        correct = 0
        for var, fb, (_p, ops, ok, expl) in zip(self.answers, self.feedback, l["quiz"]):
            if var.get() == ok:
                correct += 1
                fb.configure(text=f"✓ Correcto. {expl}", fg="#166534")
            else:
                fb.configure(text=f"✗ La respuesta es «{ops[ok]}». {expl}", fg="#991b1b")
        score = correct / len(l["quiz"])
        status = "dominado" if score >= 0.5 else None
        unlocked = self.db.set_learning(l["id"], "leccion", status, score)
        self.result_lbl.configure(
            text=f"Resultado: {correct}/{len(l['quiz'])}" +
                 ("  —  ¡lección completada!" if status else "  —  repasa los puntos clave e inténtalo de nuevo."))
        self._update_row(l["id"])
        self.parent.announce(unlocked)

    def _complete(self, lid):
        unlocked = self.db.set_learning(lid, "leccion", "dominado")
        self._update_row(lid)
        self.parent.announce(unlocked)

    def _update_row(self, lid):
        cur = self.current
        self.refresh()
        self.current = cur


# ───────────────────────────── Ruta de habilidades ─────────────────────────────
class SkillPath(ttk.Frame):
    def __init__(self, master, parent):
        super().__init__(master, padding=PAD)
        self.parent = parent
        self.db = parent.db
        top = ttk.Frame(self)
        top.pack(fill="x")
        self.stats = ttk.Label(top, text="", font=FONT_B)
        self.stats.pack(side="left")
        ttk.Label(top, text="   Gris: pendiente · Amarillo: aprendiendo · Verde: dominado. "
                            "Haz clic en un ejercicio para ver su técnica.", foreground=MUTED).pack(side="left")
        self.sugg = ttk.LabelFrame(self, text="Siguientes ejercicios recomendados para aprender", padding=6)
        self.sugg.pack(fill="x", pady=6)
        self.grid_area = ScrollFrame(self)
        self.grid_area.pack(fill="both", expand=True)

    def refresh(self):
        s = self.db.learning_summary()
        self.stats.configure(text=f"Dominados: {s['ex_mastered']}  ·  Aprendiendo: {s['ex_learning']}  ·  "
                                  f"Total: {s['ex_total']}")
        for w in self.sugg.winfo_children():
            w.destroy()
        for e in self.db.next_skills():
            ttk.Button(self.sugg, text=f"{e['name']} {stars(e['difficulty'])}",
                       command=lambda i=e["id"]: self.parent.open_exercise(i)).pack(side="left", padx=2)

        self.grid_area.clear()
        box = self.grid_area.inner
        box.configure(padding=8)
        hdr = tk.Frame(box, bg="#ffffff")
        hdr.pack(fill="x")
        tk.Label(hdr, text="Bloque", width=16, anchor="w", font=FONT_B, bg="#ffffff").grid(row=0, column=0)
        for d in range(1, 6):
            tk.Label(hdr, text=stars(d), width=22, font=FONT_B, bg="#ffffff").grid(row=0, column=d)
        for bid, bname in BLOCKS:
            exs = self.db.exercises(block=bid)
            if not exs:
                continue
            row = tk.Frame(box, bg="#ffffff")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=bname, width=16, anchor="nw", font=FONT_B, bg="#ffffff").grid(
                row=0, column=0, sticky="nw")
            for d in range(1, 6):
                cell = tk.Frame(row, bg="#ffffff", width=170)
                cell.grid(row=0, column=d, sticky="n", padx=2)
                for e in [x for x in exs if x["difficulty"] == d]:
                    st = self.db.learning_status(e["id"])["status"]
                    tk.Button(cell, text=e["name"], wraplength=150, width=20, bg=STATE_COLOR[st],
                              relief="flat", font=("Segoe UI", 8), cursor="hand2",
                              command=lambda i=e["id"]: self.parent.open_exercise(i)).pack(pady=1)
