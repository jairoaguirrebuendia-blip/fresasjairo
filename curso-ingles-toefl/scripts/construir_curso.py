#!/usr/bin/env python3
"""Construye el curso HTML a partir de las fichas validadas.

Uso:
  python3 scripts/construir_curso.py
Genera:
  curso-html/index.html       documento completo (se abre directo en el navegador)
  curso-html/fragmento.html   mismo curso sin <!doctype>/<html>, para publicarlo como Artifact
"""
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validar_fichas import (  # noqa: E402
    COBERTURA, FICHAS, QUIZ_RE, TEMAS, leer_ficha, leer_quiz, normalizar,
)

BASE = Path(__file__).resolve().parent.parent
PLANTILLA = BASE / "scripts" / "curso_plantilla.html"
SALIDA = BASE / "curso-html"

# Orden y nombre visible de las secciones del curso
SECCIONES = [
    ("structure", "Structure & Written Expression", "Structure & Written Expression"),
    ("reading", "Reading Comprehension", "Reading"),
    ("listening", "Listening Comprehension", "Listening"),
    ("vocabulario", "Vocabulario y lenguaje funcional", "Vocabulario y lenguaje funcional"),
    ("meto", "Aprender a aprender", "Aprendizaje autónomo"),
]
# Macrohabilidad → sección, para fichas con tema "Otro" o sin tema
MACRO_A_SECCION = {
    "Structure & Written Expression": "structure",
    "Reading": "reading",
    "Listening": "listening",
    "Vocabulario": "vocabulario",
    "Lenguaje funcional": "vocabulario",
    "Aprendizaje autónomo": "meto",
}

# Plan de 12 semanas: temas en orden de prioridad TOEFL (sección 2 de la matriz)
PLAN = [
    ("Arranque y diagnóstico", ["Motivación y metas", "Exámenes: cómo funcionan y cómo prepararse",
                                "Sentence structure", "Subject–verb agreement"],
     "Haz el mini simulacro una vez, sin estudiar antes: es tu punto de partida."),
    ("Tiempos verbales I", ["Verb tenses & forms", "Cómo se adquiere un idioma"],
     "Una ficha por día y su práctica. Anota en tu cuaderno los errores que repites."),
    ("Tiempos verbales II, pasiva y modales", ["Passive voice", "Modals", "Verb tenses & forms"],
     "Repasa el banco de errores antes de cada sesión nueva."),
    ("Verbales y condicionales", ["Gerunds & infinitives", "Conditionals (0–3)",
                                  "Estrategias y hábitos de estudio"],
     "Empieza a leer 15 minutos diarios en inglés de un tema que te guste."),
    ("Sustantivos, artículos y pronombres", ["Nouns: count/noncount", "Articles & determiners",
                                             "Pronouns", "Vocabulary in context"],
     "En tus lecturas, adivina el significado por contexto antes de ir al diccionario."),
    ("Modificadores y preposiciones", ["Adjectives vs adverbs; comparisons", "Prepositions",
                                       "Formación de palabras", "Main idea / topic"],
     "Al terminar cada lectura, escribe en una línea su idea principal."),
    ("Cláusulas", ["Relative clauses", "Reduced / participial clauses", "Supporting details",
                   "Práctica, repaso y memoria"],
     "Segundo mini simulacro. Compara por sección con el de la semana 1."),
    ("Conectores y paralelismo", ["Conjunctions / connectors", "Parallel structure",
                                  "Conectores de discurso", "Inference"],
     "Subraya los conectores de tus lecturas y clasifícalos (contraste, causa, adición)."),
    ("Orden, inversión y precisión", ["Word order & inversion", "Redundancy & word choice",
                                      "Pronoun reference", "Author's purpose / tone"],
     "Written Expression: busca primero errores de concordancia, forma de palabra y paralelismo."),
    ("Listening: diálogos cortos", ["Short dialogues: idioms & implied meaning", "Phrasal verbs",
                                    "Paraphrase / restatement", "Colocaciones"],
     "Escucha audio real a diario (pódcast o material oficial). Aquí solo hay transcripciones."),
    ("Listening largo y lectura académica", ["Longer conversations", "Mini-talks / lectures",
                                             "Text organization / cohesion", "Academic word list",
                                             "Sinónimos y palabras confusas"],
     "Lee un texto académico corto al día y resume su estructura."),
    ("Simulacros y cierre", ["Exámenes: cómo funcionan y cómo prepararse"],
     "Dos mini simulacros y vacía el banco de errores. Considera un examen de práctica oficial."),
]


def slug(texto):
    texto = normalizar(texto)
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        texto = texto.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def cuerpo_html(cuerpo, titulos):
    cuerpo = QUIZ_RE.sub("", cuerpo)
    # Quitar la sección de práctica TOEFL (se muestra como ejercicio interactivo)
    cuerpo = re.sub(r"^##[^\n]*Práctica estilo TOEFL[^\n]*\n(?:(?!^## ).*\n?)*", "", cuerpo, flags=re.M)
    # El H1 se muestra en la cabecera de la tarjeta
    cuerpo = re.sub(r"^# .*\n", "", cuerpo, count=1, flags=re.M)

    def enlace(m):
        fid = m.group(1)
        if fid in titulos:
            return f"[{fid} · {titulos[fid]}](#f-{fid})"
        return f"{fid}"

    cuerpo = re.sub(r"\[\[((?:GRAM|READ|LIST|VOCAB|FUNC|METO)-\d{3})[^\]]*\]\]", enlace, cuerpo)
    html = markdown.markdown(cuerpo, extensions=["tables", "fenced_code", "sane_lists"])
    return html.replace("<table>", '<div class="tabla"><table>').replace("</table>", "</table></div>")


def main():
    crudas = {}
    for ruta in sorted(FICHAS.glob("*/*.md")):
        meta, cuerpo = leer_ficha(ruta)
        if not meta or not meta.get("id"):
            continue
        crudas[str(meta["id"])] = (meta, cuerpo)

    titulos = {fid: str(m.get("subcategoria") or fid) for fid, (m, _) in crudas.items()}
    fichas = {}
    temas = defaultdict(list)  # (seccion_id, nombre_tema) → [ids]
    nombre_seccion = {macro: sid for sid, _, macro in SECCIONES}
    fuentes = defaultdict(lambda: {"n": 0})

    for fid, (m, cuerpo) in crudas.items():
        tema = normalizar(m.get("tema_cobertura"))
        if tema in TEMAS:
            seccion_mapa, nombre_tema = TEMAS[tema]
            sid = nombre_seccion[seccion_mapa]
        else:
            sid = MACRO_A_SECCION.get(str(m.get("macrohabilidad_toefl")), "structure")
            nombre_tema = "Otros temas"
        try:
            quiz = [q for q in leer_quiz(cuerpo) if isinstance(q, dict)]
        except Exception:
            quiz = []
        fichas[fid] = {
            "id": fid,
            "titulo": titulos[fid],
            "categoria": str(m.get("categoria") or ""),
            "tema": nombre_tema,
            "seccion": sid,
            "nivel": str(m.get("nivel_cefr") or ""),
            "prioridad": str(m.get("prioridad_toefl") or ""),
            "tipo": str(m.get("tipo_item_toefl") or ""),
            "fuente": str(m.get("fuente") or ""),
            "autor": str(m.get("autor") or ""),
            "edicion": str(m.get("edicion_anio") or ""),
            "capitulo": str(m.get("capitulo") or ""),
            "seccion_libro": str(m.get("seccion") or ""),
            "paginas": str(m.get("paginas") or ""),
            "html": cuerpo_html(cuerpo, titulos),
            "quiz": [{k: q.get(k) for k in ("tipo", "pregunta", "opciones", "respuesta", "explicacion")}
                     for q in quiz],
        }
        temas[(sid, nombre_tema)].append(fid)
        f = fuentes[fichas[fid]["fuente"]]
        f["n"] += 1
        f["autor"] = fichas[fid]["autor"]
        f["edicion"] = fichas[fid]["edicion"]

    orden_nivel = {"A2": 0, "B1": 1, "B2": 2, "Todos": 1}
    orden_prio = {"Alta": 0, "Media": 1, "Baja": 2}

    def clave(fid):
        f = fichas[fid]
        return (orden_prio.get(f["prioridad"], 3), orden_nivel.get(f["nivel"], 3), fid)

    secciones = []
    faltantes = []
    for sid, nombre, macro in SECCIONES:
        lista = []
        for nombre_tema in COBERTURA[macro]:
            ids = sorted(temas.get((sid, nombre_tema), []), key=clave)
            if not ids:
                faltantes.append(nombre_tema)
            lista.append({"slug": slug(nombre_tema), "nombre": nombre_tema, "fichas": ids})
        if temas.get((sid, "Otros temas")):
            lista.append({"slug": f"{sid}-otros", "nombre": "Otros temas",
                          "fichas": sorted(temas[(sid, "Otros temas")], key=clave)})
        secciones.append({"id": sid, "nombre": nombre, "temas": lista})

    # Vocabulario: los temas del mapa viven en la sección "Vocabulario y lenguaje funcional"
    slug_de = {t["nombre"]: t["slug"] for s in secciones for t in s["temas"]}
    plan = [{"semana": i, "foco": foco, "temas": [slug_de[t] for t in ts if t in slug_de], "nota": nota}
            for i, (foco, ts, nota) in enumerate(PLAN, 1)]

    datos = {
        "generado": date.today().isoformat(),
        "secciones": secciones,
        "fichas": fichas,
        "fuentes": sorted(({"titulo": k, **v} for k, v in fuentes.items()), key=lambda x: -x["n"]),
        "plan": plan,
        "faltantes": faltantes,
    }
    json_datos = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    fragmento = PLANTILLA.read_text(encoding="utf-8").replace("/*__DATOS__*/null", json_datos)

    SALIDA.mkdir(exist_ok=True)
    (SALIDA / "fragmento.html").write_text(fragmento, encoding="utf-8")
    completo = ('<!doctype html>\n<html lang="es">\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + fragmento + "\n</html>\n")
    (SALIDA / "index.html").write_text(completo, encoding="utf-8")
    n_quiz = sum(len(f["quiz"]) for f in fichas.values())
    print(f"Curso generado: {len(fichas)} fichas, {n_quiz} preguntas, {len(faltantes)} temas sin fichas.")
    print(f"  {SALIDA / 'index.html'}  ({(SALIDA / 'index.html').stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
