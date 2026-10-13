"""Gráficos simples dibujados en tk.Canvas (sin dependencias externas)."""
from datetime import date, timedelta

COLORS = {
    "bg": "#ffffff", "grid": "#e6e8eb", "axis": "#8a9099", "text": "#2b2f36",
    "line": "#2f6fdb", "bar": "#2f6fdb", "ok": "#2e9e5b", "low": "#d9a400", "high": "#d24b4b",
}


def _clear(canvas):
    canvas.delete("all")
    canvas.update_idletasks()
    w = max(canvas.winfo_width(), int(canvas.cget("width")))
    h = max(canvas.winfo_height(), int(canvas.cget("height")))
    canvas.create_rectangle(0, 0, w, h, fill=COLORS["bg"], outline="")
    return w, h


def _nice_max(v):
    if v <= 0:
        return 1
    for step in (1, 2, 2.5, 5):
        mag = 10 ** (len(str(int(v))) - 1)
        if step * mag >= v:
            return step * mag
    return 10 ** len(str(int(v)))


def line_chart(canvas, labels, values, title="", unit="", color=None):
    w, h = _clear(canvas)
    pad_l, pad_r, pad_t, pad_b = 52, 16, 30, 34
    canvas.create_text(pad_l, 14, text=title, anchor="w", font=("Segoe UI", 10, "bold"), fill=COLORS["text"])
    pts = [(l, v) for l, v in zip(labels, values) if v is not None]
    if not pts:
        canvas.create_text(w / 2, h / 2, text="Sin datos todavía", fill=COLORS["axis"])
        return
    vmin = min(v for _, v in pts)
    vmax = max(v for _, v in pts)
    lo = 0 if vmin >= 0 and vmin < vmax * 0.5 else vmin * 0.9
    hi = _nice_max(vmax * 1.05) if lo == 0 else vmax * 1.05
    if hi == lo:
        hi = lo + 1
    pw, ph = w - pad_l - pad_r, h - pad_t - pad_b
    for i in range(5):
        y = pad_t + ph * i / 4
        val = hi - (hi - lo) * i / 4
        canvas.create_line(pad_l, y, w - pad_r, y, fill=COLORS["grid"])
        canvas.create_text(pad_l - 6, y, text=f"{val:.0f}", anchor="e", fill=COLORS["axis"], font=("Segoe UI", 8))
    n = len(pts)
    xy = []
    for i, (l, v) in enumerate(pts):
        x = pad_l + (pw * i / (n - 1) if n > 1 else pw / 2)
        y = pad_t + ph * (1 - (v - lo) / (hi - lo))
        xy.append((x, y, l, v))
    if len(xy) > 1:
        canvas.create_line(*[c for x, y, _, _ in xy for c in (x, y)], fill=color or COLORS["line"], width=2)
    step = max(1, n // 6)
    for i, (x, y, l, v) in enumerate(xy):
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color or COLORS["line"], outline="")
        if i % step == 0 or i == n - 1:
            canvas.create_text(x, h - pad_b + 12, text=str(l)[5:] if len(str(l)) == 10 else str(l),
                               fill=COLORS["axis"], font=("Segoe UI", 8))
    x, y, _, v = xy[-1]
    canvas.create_text(x - 4, y - 10, text=f"{v:g} {unit}", anchor="e", fill=COLORS["text"],
                       font=("Segoe UI", 8, "bold"))


def bar_chart(canvas, labels, values, title="", unit="", colors=None):
    w, h = _clear(canvas)
    pad_l, pad_r, pad_t, pad_b = 52, 16, 30, 34
    canvas.create_text(pad_l, 14, text=title, anchor="w", font=("Segoe UI", 10, "bold"), fill=COLORS["text"])
    if not values or max(values) <= 0:
        canvas.create_text(w / 2, h / 2, text="Sin datos todavía", fill=COLORS["axis"])
        return
    hi = _nice_max(max(values))
    pw, ph = w - pad_l - pad_r, h - pad_t - pad_b
    for i in range(5):
        y = pad_t + ph * i / 4
        canvas.create_line(pad_l, y, w - pad_r, y, fill=COLORS["grid"])
        canvas.create_text(pad_l - 6, y, text=f"{hi - hi * i / 4:.0f}", anchor="e",
                           fill=COLORS["axis"], font=("Segoe UI", 8))
    n = len(values)
    bw = pw / n
    step = max(1, n // 8)
    for i, (l, v) in enumerate(zip(labels, values)):
        x0 = pad_l + bw * i + bw * 0.15
        x1 = pad_l + bw * (i + 1) - bw * 0.15
        y = pad_t + ph * (1 - v / hi)
        canvas.create_rectangle(x0, y, x1, pad_t + ph, fill=(colors[i] if colors else COLORS["bar"]), outline="")
        if i % step == 0:
            canvas.create_text((x0 + x1) / 2, h - pad_b + 12, text=str(l), fill=COLORS["axis"], font=("Segoe UI", 8))


def volume_bars(canvas, rows, vmin=10, vmax=20, title="Series semanales por músculo (10-20)"):
    """rows: [(nombre, series)]. Barras horizontales con la franja óptima sombreada."""
    w, h = _clear(canvas)
    canvas.create_text(10, 12, text=title, anchor="w", font=("Segoe UI", 10, "bold"), fill=COLORS["text"])
    if not rows:
        canvas.create_text(w / 2, h / 2, text="Registra una sesión para ver tu volumen.", fill=COLORS["axis"])
        return
    pad_l, pad_r, top = 150, 40, 34
    scale_max = max(26, max(v for _, v in rows) + 2)
    pw = w - pad_l - pad_r
    row_h = max(14, min(24, (h - top - 10) / len(rows)))
    x_min = pad_l + pw * vmin / scale_max
    x_max = pad_l + pw * vmax / scale_max
    canvas.create_rectangle(x_min, top, x_max, top + row_h * len(rows), fill="#e9f6ee", outline="")
    canvas.create_text((x_min + x_max) / 2, top - 6, text=f"zona óptima {vmin}-{vmax}",
                       fill=COLORS["ok"], font=("Segoe UI", 8))
    for i, (name, v) in enumerate(rows):
        y = top + i * row_h
        color = COLORS["ok"] if vmin <= v <= vmax else (COLORS["low"] if v < vmin else COLORS["high"])
        canvas.create_text(pad_l - 8, y + row_h / 2, text=name, anchor="e", fill=COLORS["text"], font=("Segoe UI", 9))
        canvas.create_rectangle(pad_l, y + 3, pad_l + pw * v / scale_max, y + row_h - 3, fill=color, outline="")
        canvas.create_text(pad_l + pw * v / scale_max + 6, y + row_h / 2, text=f"{v:g}", anchor="w",
                           fill=COLORS["text"], font=("Segoe UI", 8, "bold"))


def heatmap(canvas, counts, weeks=26, title="Calendario de cumplimiento"):
    """Mapa de calor tipo GitHub: columnas = semanas, filas = días (L-D)."""
    w, h = _clear(canvas)
    canvas.create_text(10, 12, text=title, anchor="w", font=("Segoe UI", 10, "bold"), fill=COLORS["text"])
    today = date.today()
    start = today - timedelta(days=today.weekday()) - timedelta(weeks=weeks - 1)
    cell = min(16, (w - 40) / weeks - 2, (h - 40) / 7 - 2)
    for i, d in enumerate("LMXJVSD"):
        canvas.create_text(14, 30 + i * (cell + 2) + cell / 2, text=d, fill=COLORS["axis"], font=("Segoe UI", 7))
    for wk in range(weeks):
        for dw in range(7):
            d = start + timedelta(weeks=wk, days=dw)
            if d > today:
                continue
            n = counts.get(d.isoformat(), 0)
            fill = "#ebedf0" if n == 0 else ("#7bc96f" if n == 1 else "#196127")
            x = 26 + wk * (cell + 2)
            y = 30 + dw * (cell + 2)
            canvas.create_rectangle(x, y, x + cell, y + cell, fill=fill, outline="")
