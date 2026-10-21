#!/usr/bin/env python3
"""Valida las fichas contra la matriz y regenera los registros.

Uso:
  python3 scripts/validar_fichas.py              # solo valida
  python3 scripts/validar_fichas.py --cobertura  # valida y regenera registro/indice-fichas.md y registro/cobertura.md
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent.parent
FICHAS = BASE / "fichas"

OBLIGATORIOS = [
    "id", "fuente", "autor", "capitulo", "seccion", "paginas",
    "macrohabilidad_toefl", "categoria", "subcategoria",
    "nivel_cefr", "prioridad_toefl", "tipo_item_toefl",
]
VALORES = {
    "macrohabilidad_toefl": {"Structure & Written Expression", "Reading", "Listening",
                             "Vocabulario", "Lenguaje funcional"},
    "nivel_cefr": {"A2", "B1", "B2"},
    "prioridad_toefl": {"Alta", "Media", "Baja"},
}
ID_RE = re.compile(r"^(GRAM|READ|LIST|VOCAB|FUNC)-\d{3}$")
LINK_RE = re.compile(r"\[\[((?:GRAM|READ|LIST|VOCAB|FUNC)-\d{3})[^\]]*\]\]")

# Mapa de cobertura (sección 6 de la matriz): tema → palabras clave buscadas en
# categoria, subcategoria y tags de cada ficha.
COBERTURA = {
    "Structure & Written Expression": {
        "Subject–verb agreement": ["agreement", "concordancia sujeto"],
        "Verb tenses & forms": ["tense", "tiempos verbales", "present", "past", "perfect", "continuous", "progressive"],
        "Gerunds & infinitives": ["gerund", "infinitive"],
        "Modals": ["modal"],
        "Conditionals (0–3)": ["conditional", "condicional"],
        "Passive voice": ["passive", "pasiva"],
        "Articles & determiners": ["article", "determiner", "artículo"],
        "Nouns: count/noncount": ["noun", "count", "plural", "sustantivo"],
        "Pronouns": ["pronoun", "pronombre"],
        "Prepositions": ["preposition", "preposicion", "preposición"],
        "Adjectives vs adverbs; comparisons": ["adjective", "adverb", "comparative", "superlative", "comparativo"],
        "Parallel structure": ["parallel", "paralelismo"],
        "Relative clauses": ["relative", "adjective clause", "relativa"],
        "Conjunctions / connectors": ["conjunction", "connector", "conector", "adverb clause"],
        "Word order & inversion": ["word order", "inversion", "inversión", "orden"],
        "Reduced / participial clauses": ["reduced", "participial", "participle phrase"],
        "Sentence structure": ["fragment", "run-on", "sentence structure", "independent clause"],
        "Redundancy & word choice": ["redundan", "word choice", "word form"],
    },
    "Reading": {
        "Main idea / topic": ["main idea", "topic", "idea principal"],
        "Supporting details": ["detail", "scanning", "detalle"],
        "Vocabulary in context": ["vocabulary in context", "contexto"],
        "Pronoun reference": ["reference", "referencia"],
        "Inference": ["inference", "inferencia"],
        "Author's purpose / tone": ["purpose", "tone", "propósito"],
        "Text organization / cohesion": ["organization", "cohesion", "organización"],
    },
    "Listening": {
        "Short dialogues: idioms & implied meaning": ["idiom", "implied", "short dialogue"],
        "Paraphrase / restatement": ["paraphrase", "restatement", "paráfrasis"],
        "Longer conversations": ["conversation", "conversación"],
        "Mini-talks / lectures": ["talk", "lecture"],
    },
    "Vocabulario y lenguaje funcional": {
        "Academic word list": ["academic", "awl"],
        "Phrasal verbs": ["phrasal"],
        "Colocaciones": ["collocation", "colocación"],
        "Conectores de discurso": ["discourse", "transition", "discurso"],
    },
}


def leer_ficha(ruta):
    texto = ruta.read_text(encoding="utf-8")
    if not texto.startswith("---"):
        return None, texto
    partes = texto.split("---", 2)
    if len(partes) < 3:
        return None, texto
    return yaml.safe_load(partes[1]) or {}, partes[2]


def main():
    regenerar = "--cobertura" in sys.argv
    errores, avisos = [], []
    fichas = {}
    cuerpos = {}

    for ruta in sorted(FICHAS.glob("*/*.md")):
        rel = ruta.relative_to(BASE)
        meta, cuerpo = leer_ficha(ruta)
        if meta is None:
            errores.append(f"{rel}: sin front matter YAML")
            continue
        fid = str(meta.get("id", ""))
        if not ID_RE.match(fid):
            errores.append(f"{rel}: id inválido '{fid}'")
            continue
        if fid.split("-")[0] != ruta.parent.name:
            errores.append(f"{rel}: id {fid} no corresponde a la carpeta {ruta.parent.name}/")
        if not ruta.name.startswith(fid):
            errores.append(f"{rel}: el nombre del archivo debe empezar con {fid}")
        if fid in fichas:
            errores.append(f"{rel}: id duplicado {fid} (también en {fichas[fid][0]})")
        for campo in OBLIGATORIOS:
            if not str(meta.get(campo) or "").strip():
                errores.append(f"{rel}: campo obligatorio vacío '{campo}'")
        for campo, permitidos in VALORES.items():
            valor = meta.get(campo)
            if valor and valor not in permitidos:
                errores.append(f"{rel}: '{campo}' = '{valor}' no es un valor permitido")
        if "EJEMPLO" in str(meta.get("fuente", "")):
            errores.append(f"{rel}: la fuente sigue siendo un placeholder")
        fichas[fid] = (rel, meta)
        cuerpos[fid] = cuerpo

    for fid, cuerpo in cuerpos.items():
        for destino in LINK_RE.findall(cuerpo):
            if destino not in fichas:
                avisos.append(f"{fichas[fid][0]}: enlace a ficha inexistente [[{destino}]]")

    for e in errores:
        print(f"❌ {e}")
    for a in avisos:
        print(f"⚠️  {a}")
    print(f"\n{len(fichas)} fichas · {len(errores)} errores · {len(avisos)} avisos")

    if regenerar:
        escribir_indice(fichas)
        escribir_cobertura(fichas)
        print("Registros regenerados en registro/.")

    return 1 if errores else 0


def escribir_indice(fichas):
    filas = ["# 🗂️ Índice de fichas", "",
             "_Generado por `scripts/validar_fichas.py --cobertura`. No editar a mano._", "",
             "| ID | Subcategoría | Macrohabilidad | Nivel | Prioridad | Fuente | Páginas | Archivo |",
             "|---|---|---|---|---|---|---|---|"]
    for fid in sorted(fichas):
        rel, m = fichas[fid]
        filas.append(f"| {fid} | {m.get('subcategoria','')} | {m.get('macrohabilidad_toefl','')} | "
                     f"{m.get('nivel_cefr','')} | {m.get('prioridad_toefl','')} | {m.get('fuente','')} | "
                     f"{m.get('paginas','')} | [{rel.name}](../{rel.as_posix()}) |")
    (BASE / "registro" / "indice-fichas.md").write_text("\n".join(filas) + "\n", encoding="utf-8")


def escribir_cobertura(fichas):
    hits = defaultdict(list)
    for fid, (_, m) in fichas.items():
        texto = " ".join([str(m.get("categoria", "")), str(m.get("subcategoria", "")),
                          " ".join(map(str, m.get("tags") or []))]).lower()
        for seccion, temas in COBERTURA.items():
            for tema, claves in temas.items():
                if any(c in texto for c in claves):
                    hits[(seccion, tema)].append((fid, m.get("fuente", "")))

    lineas = ["# 🗺️ Cobertura TOEFL (meta ITP 500)", "",
              "_Generado por `scripts/validar_fichas.py --cobertura`. "
              "`[x]` = ≥1 ficha · ⭐ = sólido (≥2 fuentes distintas)._", ""]
    for seccion, temas in COBERTURA.items():
        cubiertos = sum(1 for t in temas if hits[(seccion, t)])
        lineas += [f"## {seccion} — {cubiertos}/{len(temas)}", ""]
        for tema in temas:
            h = hits[(seccion, tema)]
            marca = "x" if h else " "
            solido = " ⭐" if len({f for _, f in h}) >= 2 else ""
            ids = ", ".join(sorted(fid for fid, _ in h))
            lineas.append(f"- [{marca}] {tema}{solido}" + (f" — {ids}" if ids else ""))
        lineas.append("")
    (BASE / "registro" / "cobertura.md").write_text("\n".join(lineas), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
