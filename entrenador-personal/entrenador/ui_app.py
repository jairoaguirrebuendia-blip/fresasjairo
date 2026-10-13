"""Ventana principal."""
import tkinter as tk
from tkinter import messagebox, ttk

from . import APP_NAME, APP_VERSION, exportar, rutas
from .db import Database
from .ui_aprendizaje import AprendizajeTab
from .ui_comun import ACCENT
from .ui_entreno import EntrenarTab, HistorialTab, RutinasTab
from .ui_otros import AjustesTab, CuerpoTab, InicioTab, ObjetivosTab, ProgresoTab


def setup_style(root):
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    root.option_add("*Font", ("Segoe UI", 10))
    style.configure("Card.TFrame", background="#ffffff")
    style.configure("TNotebook.Tab", padding=(10, 6))
    style.configure("Accent.TButton", foreground="#ffffff", background=ACCENT)
    style.map("Accent.TButton", background=[("active", "#2559b3"), ("!disabled", ACCENT)],
              foreground=[("!disabled", "#ffffff")])
    style.configure("Treeview", rowheight=24)


class App(tk.Tk):
    def __init__(self, db_path=None):
        super().__init__()
        self.title(f"{APP_NAME} · Calistenia + Pesas")
        self.geometry("1280x820")
        self.minsize(1000, 640)
        setup_style(self)
        self.db = Database(db_path or rutas.db_path())
        try:
            exportar.backup(self.db, rutas.backups_dir())
        except OSError:
            pass

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)
        self.tabs = {}
        for key, label, cls in (
            ("inicio", "🏠 Inicio", InicioTab), ("entrenar", "🏋 Entrenar", EntrenarTab),
            ("rutinas", "📋 Rutinas", RutinasTab), ("aprendizaje", "📘 Aprendizaje", AprendizajeTab),
            ("historial", "🗂 Historial", HistorialTab), ("progreso", "📈 Progreso", ProgresoTab),
            ("cuerpo", "📏 Cuerpo", CuerpoTab), ("objetivos", "🎯 Objetivos", ObjetivosTab),
            ("ajustes", "⚙ Ajustes", AjustesTab),
        ):
            tab = cls(self.nb, self)
            self.nb.add(tab, text=f" {label} ")
            self.tabs[key] = tab
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refresh_current())
        status = ttk.Frame(self, padding=(8, 2))
        status.pack(fill="x")
        ttk.Label(status, text=f"{APP_NAME} v{APP_VERSION} · datos locales en {rutas.data_dir()}",
                  foreground="#6b7280").pack(side="left")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(50, self.refresh_current)

    def refresh_current(self):
        tab = self.nb.nametowidget(self.nb.select())
        tab.refresh()

    def refresh_all(self):
        # Sólo la pestaña visible se redibuja; el resto se refresca al abrirla.
        self.refresh_current()

    def open_technique(self, ex_id):
        tab = self.tabs["aprendizaje"]
        self.nb.select(tab)
        tab.open_exercise(ex_id)

    def show_progress(self, ex_id):
        tab = self.tabs["progreso"]
        self.nb.select(tab)
        tab.select(ex_id)

    def announce_achievements(self, unlocked):
        if unlocked:
            txt = "\n".join(f"{a['icon']}  {a['name']} — {a['description']}" for a in unlocked)
            messagebox.showinfo("¡Logro desbloqueado!", txt, parent=self)

    def on_close(self):
        self.db.close()
        self.destroy()
