# Entrenador Personal: calistenia y pesas

Programa de escritorio para Windows que funciona **sin internet**. Sirve para planificar, registrar y aprender
calistenia y entrenamiento con pesas. Está escrito en Python, usa solo la biblioteca estándar
(tkinter + SQLite) y guarda todo en un solo archivo de base de datos.

Se basa en los libros de referencia:
*Guía Completa de Calistenia y Street Workout*, Schoenfeld (*Ciencia y desarrollo de la hipertrofia muscular*),
W. Martínez (*La ciencia de la hipertrofia*), Peña Fernández et al. (*Levantamiento de pesas*) y
Sosa Chavez (*Cuerpos de calistenia*).

## Cómo abrirlo

1. Instala **Python 3.9 o posterior** desde [python.org](https://www.python.org/downloads/) (marca "Add Python to PATH").
2. Haz doble clic en **`iniciar.bat`** (o ejecuta `python run.py`).

**¿Prefieres un `.exe`?** Ejecuta `crear_exe.bat` una vez. Así se genera `dist\EntrenadorPersonal.exe`, que funciona
sin tener Python instalado.

Tus datos se guardan en `%APPDATA%\PersonalTrainer\`:

```
PersonalTrainer/
├── db.sqlite          ← base principal
├── media/photos/      ← fotos de progreso
├── media/exports/     ← JSON/CSV exportados
└── backups/           ← copias automáticas (se guardan las 10 más recientes)
```

## Secciones

| Pestaña | Qué hace |
|---|---|
| 🏠 **Inicio** | Racha, cumplimiento semanal y planificador de la semana. Muestra las series por músculo frente al rango 10-20 y la frecuencia 2, avisos de descarga, récords y logros recientes, y qué conviene aprender después. |
| 🏋 **Entrenar** | Carga el plan de una rutina o haz una sesión libre. Registra cada serie (reps o segundos, kg, RIR, tempo, calentamiento, fallo) y usa el temporizador de descanso. Te enseña lo que hiciste la última vez y te sugiere cómo progresar. Al guardar, calcula el tonelaje, el 1RM, los récords y los logros. |
| 📋 **Rutinas** | Crea y edita rutinas con sus días, ejercicios, series, rango de repeticiones, RIR, descanso y tempo. Estima las series semanales por músculo. Trae 4 plantillas: Nivel 0, Full Body 6×4, Frecuencia 2 torso/pierna y Objetivo muscle up. |
| 📘 **Aprendizaje** | Ver más abajo. |
| 🗂 **Historial** | Lista de sesiones con su detalle (tonelaje, 1RM estimado, IMR y zona de intensidad) y cronología de récords. |
| 📈 **Progreso** | Gráficos por ejercicio (1RM, reps, segundos, peso, tonelaje), tonelaje semanal, calendario de cumplimiento, peso corporal y series por zona de intensidad. |
| 📏 **Cuerpo** | Peso, % de grasa, masa muscular y 10 medidas con su gráfico. Fotos de progreso con comparador lado a lado (necesita `pillow`; sin él las abre con el visor del sistema). |
| 🎯 **Objetivos** | Objetivos con hitos y barra de progreso. Los hitos se pueden generar solos a partir de la cadena de progresión. Incluye 18 logros desbloqueables. |
| ⚙ **Ajustes** | Perfil, descanso por defecto, días por semana y copias de seguridad. Exporta en **JSON completo** o **CSV por tabla** (`sessions`, `sets`, `body_measurements`, `personal_records`, `weekly_volume`), restaura desde JSON y permite crear ejercicios propios. |

## 📘 Sección de Aprendizaje (técnica)

1. **Biblioteca de técnica**: 83 ejercicios repartidos en los bloques de la guía (flexiones, fondos, dominadas, pierna,
   core, muscle up, pino, planchas, flags/levers) más pesas y halterofilia. Cada ficha incluye:
   - descripción, dificultad 💪 (1-5), tipo y si se mide en repeticiones o segundos;
   - músculos principales y secundarios, y el material necesario;
   - **cómo hacerlo, paso a paso**;
   - **claves técnicas** (✓) y **errores comunes** (✗);
   - respiración, avisos de seguridad y **cuándo avanzar** al siguiente ejercicio;
   - la **cadena de progresión** completa, en la que puedes pulsar cada ejercicio anterior o siguiente;
   - tu registro personal: la última vez que lo hiciste y tus récords;
   - un estado (Pendiente / Aprendiendo / Dominado) y un botón para crear un objetivo con esa cadena.
2. **Lecciones y quiz**: 13 lecciones con quiz y explicación de cada respuesta. Temas: calentamiento,
   progresiones, tensión mecánica frente a estrés metabólico, volumen 10-20, frecuencia 2 y periodización de
   8 semanas, RIR, zonas de intensidad, tonelaje e IMR, métodos de entrenamiento, cómo diseñar una rutina,
   prevención de lesiones, cuidado de las manos, submodalidades y descarga.
3. **Ruta de habilidades**: un mapa por bloque y dificultad, coloreado según tu estado, con recomendaciones de
   qué aprender después a partir de lo que ya dominas.

## Fórmulas

| Métrica | Fórmula |
|---|---|
| Tonelaje | Σ (reps × peso), sin contar el calentamiento |
| 1RM estimado | Epley: peso × (1 + reps/30), con 1 a 12 repeticiones |
| Peso medio / IMR | tonelaje / reps; IMR = PM × 100 / 1RM |
| Zonas de intensidad | <60 mínima · 60-70 pequeña · 70-80 media · 80-90 grande · >90 submáxima/máxima |
| Volumen semanal | series efectivas por músculo **primario** (rango 10-20) |
| Racha | días seguidos entrenando, con un máximo de 2 días de descanso entre sesiones |
| Descarga sugerida | 6 semanas seguidas cumpliendo el objetivo, más de 20 series en un músculo o RIR medio ≤ 0,75 |

## Pruebas

```
python -m unittest discover -s tests
```

## Estructura del código

```
entrenador/
├── db.py            ← esquema SQLite, sesiones, récords, logros, aprendizaje
├── metricas.py      ← fórmulas (funciones puras)
├── catalogo.py      ← músculos, equipamiento y 83 ejercicios con técnica
├── lecciones.py     ← lecciones y quiz
├── plantillas.py    ← rutinas de ejemplo
├── exportar.py      ← JSON / CSV / restauración / copias
├── graficos.py      ← gráficos dibujados con tk.Canvas
└── ui_*.py          ← interfaz (tkinter)
```

> Aviso: este programa es informativo y no sustituye a un médico, fisioterapeuta ni entrenador. Ante dolor o lesión,
> consulta a un profesional.
