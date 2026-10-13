"""Componentes reutilizables de la interfaz (tkinter / ttk)."""
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

PAD = 8
FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_H1 = ("Segoe UI", 16, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
MUTED = "#6b7280"
ACCENT = "#2f6fdb"


def stars(n):
    return "💪" * int(n or 0)


def to_float(s):
    s = str(s or "").strip().replace(",", ".")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def to_int(s):
    f = to_float(s)
    return int(round(f)) if f is not None else None


def open_path(path):
    """Abre un archivo o carpeta con la aplicación del sistema."""
    path = str(path)
    if os.name == "nt":
        os.startfile(path)  # noqa: S606 - abrir archivo local del usuario
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class ScrollFrame(ttk.Frame):
    """Frame con scroll vertical; añade widgets a `self.inner`."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.canvas = tk.Canvas(self, highlightthickness=0, background="#f6f7f9")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas, style="Card.TFrame")
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        self.inner.bind("<Enter>", lambda e: self._bind_wheel(True))
        self.inner.bind("<Leave>", lambda e: self._bind_wheel(False))

    def _bind_wheel(self, on):
        if on:
            self.canvas.bind_all("<MouseWheel>", self._on_wheel)
            self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-2, "units"))
            self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(2, "units"))
        else:
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def _on_wheel(self, e):
        self.canvas.yview_scroll(int(-e.delta / 120) or (-1 if e.delta > 0 else 1), "units")

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self.canvas.yview_moveto(0)


def make_tree(master, columns, heights=10, widths=None, anchors=None):
    """Treeview con scrollbar. columns: [(id, título)]."""
    frame = ttk.Frame(master)
    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings", height=heights,
                        selectmode="browse")
    for i, (cid, title) in enumerate(columns):
        tree.heading(cid, text=title)
        tree.column(cid, width=(widths[i] if widths else 110),
                    anchor=(anchors[i] if anchors else "w"), stretch=True)
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return frame, tree


def fill_tree(tree, rows):
    """rows: [(iid, [valores])]."""
    tree.delete(*tree.get_children())
    for iid, vals in rows:
        tree.insert("", "end", iid=iid, values=["" if v is None else v for v in vals])


class FormDialog(tk.Toplevel):
    """Diálogo modal genérico.

    fields: [(clave, etiqueta, tipo, opciones/valor_inicial)]
      tipo: 'text' | 'int' | 'float' | 'combo' | 'multiline' | 'check'
    Resultado en self.result (dict) o None si se cancela.
    """

    def __init__(self, master, title, fields, initial=None, width=420):
        super().__init__(master)
        self.title(title)
        self.transient(master)
        self.resizable(True, False)
        self.result = None
        initial = initial or {}
        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        self.vars = {}
        self.widgets = {}
        for r, (key, label, kind, opts) in enumerate(fields):
            ttk.Label(body, text=label).grid(row=r, column=0, sticky="nw", pady=3, padx=(0, 8))
            val = initial.get(key, "" if kind != "check" else False)
            if kind == "combo":
                var = tk.StringVar(value=val if val is not None else "")
                w = ttk.Combobox(body, textvariable=var, values=opts, state="readonly")
            elif kind == "multiline":
                var = None
                w = tk.Text(body, height=4, width=40, wrap="word", font=FONT)
                w.insert("1.0", val or "")
            elif kind == "check":
                var = tk.BooleanVar(value=bool(val))
                w = ttk.Checkbutton(body, variable=var)
            else:
                var = tk.StringVar(value="" if val is None else str(val))
                w = ttk.Entry(body, textvariable=var)
            w.grid(row=r, column=1, sticky="ew", pady=3)
            self.vars[key] = (var, kind)
            self.widgets[key] = w
        btns = ttk.Frame(self, padding=(12, 0, 12, 12))
        btns.pack(fill="x")
        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(btns, text="Guardar", style="Accent.TButton", command=self._ok).pack(side="right", padx=6)
        self.bind("<Return>", lambda e: self._ok() if not isinstance(e.widget, tk.Text) else None)
        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        self.geometry(f"{max(width, self.winfo_reqwidth())}x{self.winfo_reqheight()}")
        self.grab_set()
        first = next(iter(self.widgets.values()), None)
        if first is not None:
            first.focus_set()
        self.wait_window()

    def _ok(self):
        out = {}
        for key, (var, kind) in self.vars.items():
            if kind == "multiline":
                out[key] = self.widgets[key].get("1.0", "end").strip()
            elif kind == "int":
                out[key] = to_int(var.get())
            elif kind == "float":
                out[key] = to_float(var.get())
            elif kind == "check":
                out[key] = bool(var.get())
            else:
                out[key] = var.get().strip()
        self.result = out
        self.destroy()


class ExercisePicker(tk.Toplevel):
    """Selector de ejercicio con búsqueda y filtro por bloque."""

    def __init__(self, master, db, title="Elegir ejercicio"):
        super().__init__(master)
        from .catalogo import BLOCKS
        self.db = db
        self.title(title)
        self.transient(master)
        self.geometry("560x480")
        self.result = None
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Buscar:").pack(side="left")
        self.q = tk.StringVar()
        e = ttk.Entry(top, textvariable=self.q)
        e.pack(side="left", fill="x", expand=True, padx=6)
        self.blocks = {"Todos": None, **{name: bid for bid, name in BLOCKS}}
        self.block = tk.StringVar(value="Todos")
        ttk.Combobox(top, textvariable=self.block, values=list(self.blocks), state="readonly",
                     width=18).pack(side="left")
        frame, self.tree = make_tree(self, [("name", "Ejercicio"), ("block", "Bloque"), ("dif", "Dificultad")],
                                     heights=16, widths=[260, 120, 110])
        frame.pack(fill="both", expand=True, padx=8)
        btns = ttk.Frame(self, padding=8)
        btns.pack(fill="x")
        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(btns, text="Elegir", style="Accent.TButton", command=self._ok).pack(side="right", padx=6)
        self.q.trace_add("write", lambda *a: self._load())
        self.block.trace_add("write", lambda *a: self._load())
        self.tree.bind("<Double-1>", lambda e: self._ok())
        self._load()
        self.grab_set()
        e.focus_set()
        self.wait_window()

    def _load(self):
        from .catalogo import BLOCKS
        bnames = dict(BLOCKS)
        rows = self.db.exercises(block=self.blocks.get(self.block.get()), search=self.q.get().strip() or None)
        fill_tree(self.tree, [(r["id"], [r["name"], bnames.get(r["block"], r["block"]), stars(r["difficulty"])])
                              for r in rows])

    def _ok(self):
        sel = self.tree.selection()
        if sel:
            self.result = sel[0]
            self.destroy()
