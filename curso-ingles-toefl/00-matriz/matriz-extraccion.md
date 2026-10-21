---
proyecto: "Curso autodidacta de inglés → TOEFL ITP 500"
documento: "Matriz de extracción + plantilla de ficha"
version: 1.0
fecha: 2026-10-21
autor_proceso: "Jairo Aguirre Buendía (+ Claude como copiloto)"
---

# 📥 Matriz de extracción — Curso de inglés (meta: TOEFL ITP 500)

Este documento define **cómo se extrae** el contenido de cada libro de texto y
**cómo se compila** en fichas Markdown. Es la base de la Etapa 1. Una vez que
tengamos un corpus de fichas, se usan para armar el curso en HTML (Etapa 3).

---

## 1. Flujo de trabajo (las 3 etapas)

| Etapa | Qué pasa | Entregable |
|-------|----------|------------|
| **1. Extracción** | Subes un libro (PDF de preferencia). Lo proceso contra esta matriz. | 1 ficha `.md` por tema/unidad, con su fuente y página siempre citadas. |
| **2. Compilación** | Me compartes el texto/fichas extraídas ya revisadas por ti. | Corpus organizado por sección TOEFL y nivel. |
| **3. Curso HTML** | Armo el curso navegable en HTML a partir del corpus. | Curso autodidacta con teoría, ejemplos y práctica. |

> **Regla de oro:** ninguna ficha existe sin su fuente. Cada ficha lleva de dónde
> salió (libro, capítulo, página). Eso es lo que hace rastreable y confiable el curso.

---

## 2. Qué significa "TOEFL 500" (define las prioridades)

- **Examen:** TOEFL **ITP / PBT**, escala **310–677**. (El iBT va de 0 a 120, no a 500.)
- **Nivel objetivo:** ~**B1** (MCER). 500 es intermedio sólido.
- **Secciones y peso para nosotros:**
  1. **Structure & Written Expression** (gramática) → **prioridad ALTA**. Es la más "entrenable" y donde más rápido suben los puntos.
  2. **Reading Comprehension** (lectura + vocabulario en contexto) → **prioridad ALTA**.
  3. **Listening Comprehension** → **prioridad MEDIA-ALTA** (idioms, implicación, paráfrasis).
- **No se evalúa:** producción oral ni ensayo. El corpus se concentra en reconocer y corregir, no en producir libre.

Por eso la matriz clasifica cada ficha por su **macro-habilidad TOEFL** y su **prioridad**.

---

## 3. La matriz de extracción (campos)

Cada "unidad extraída" (un tema, una regla, un set de vocabulario) se registra con
estos campos. Las primeras filas son **obligatorias** (trazabilidad); las demás se
llenan según lo que traiga el texto.

### A. Identificación y fuente (obligatorio)

| Campo | Qué es | Ejemplo |
|-------|--------|---------|
| `id` | Clave única. Formato `PREFIJO-###` | `GRAM-012` |
| `fuente` | Título del libro | *Understanding and Using English Grammar* |
| `autor` | Autor(es) | Azar, B. S. |
| `edicion_anio` | Edición y año | 4th ed., 2009 |
| `capitulo` | Capítulo o unidad | Chapter 3 |
| `seccion` | Sección/subtema tal como aparece | 3-2 Present Perfect |
| `paginas` | Página(s) exactas | pp. 88–92 |
| `isbn` | ISBN (si está) | 978-0132333313 |

### B. Clasificación TOEFL (obligatorio)

| Campo | Valores posibles |
|-------|------------------|
| `macrohabilidad_toefl` | `Structure & Written Expression` · `Reading` · `Listening` · `Vocabulario` · `Lenguaje funcional` |
| `categoria` | Tema amplio (ej. "Tiempos verbales", "Cláusulas relativas", "Estrategias de lectura") |
| `subcategoria` | Tema puntual (ej. "Present Perfect", "Subject-verb agreement") |
| `nivel_cefr` | `A2` · `B1` · `B2` |
| `prioridad_toefl` | `Alta` · `Media` · `Baja` |
| `tipo_item_toefl` | Dónde aparece en el examen (ej. "Written Expression — error ID", "Structure — completion", "Reading — inference") |

### C. Contenido extraído (según el texto)

| Campo | Qué capturar |
|-------|--------------|
| `objetivo` | En 1 línea: qué debe poder hacer el estudiante |
| `regla` | La regla/concepto central, redactado claro |
| `estructura` | Patrón o fórmula (ej. `have/has + past participle`) |
| `ejemplos` | Ejemplos **del libro** (en inglés) |
| `errores_comunes` | Errores típicos (oro puro para la sección Structure) |
| `vocabulario` | Palabras/colocaciones clave asociadas |
| `excepciones` | Notas, casos especiales, matices |
| `practica` | Ejercicios del libro, con referencia de página |
| `relacionado` | Enlaces `[[...]]` a otras fichas (prerrequisitos/relación) |

### D. Convenciones

- **Idioma:** metadatos y explicaciones en **español**; ejemplos, reglas y vocabulario en **inglés** (como vienen del libro).
- **IDs / prefijos:**
  - `GRAM-###` → gramática (Structure & Written Expression)
  - `READ-###` → lectura / estrategias de reading
  - `LIST-###` → listening
  - `VOCAB-###` → vocabulario temático
  - `FUNC-###` → lenguaje funcional / expresiones e idioms
- **Tags:** en minúsculas, con guion. Ej. `#toefl-structure #tenses #present-perfect`
- **Una ficha = una idea extraíble.** Si una sección del libro trae 3 reglas distintas, se abren 3 fichas enlazadas.

---

## 4. Plantilla de ficha (copiar/pegar)

```markdown
---
id: GRAM-000
fuente: ""
autor: ""
edicion_anio: ""
capitulo: ""
seccion: ""
paginas: ""
isbn: ""
macrohabilidad_toefl: ""
categoria: ""
subcategoria: ""
nivel_cefr: ""
prioridad_toefl: ""
tipo_item_toefl: ""
tags: []
fecha_extraccion: 2026-10-21
---

# {{subcategoria}} ({{id}})

> **Fuente:** {{fuente}} — {{autor}}, {{capitulo}}, {{seccion}}, {{paginas}}.

## 🎯 Objetivo
_(Qué debe poder hacer el estudiante tras esta ficha.)_

## 📘 Regla / Concepto
_(La idea central, clara y en tus palabras.)_

## 🧩 Estructura / Fórmula
`patrón`

## 💬 Ejemplos (del texto)
- _(ejemplo 1)_
- _(ejemplo 2)_

## ⚠️ Errores comunes (clave TOEFL)
- ❌ _(error)_ → ✅ _(correcto)_

## 🔤 Vocabulario clave
| Palabra/colocación | Significado | Nota |
|---|---|---|

## 📝 Práctica
- Ref. libro: _(pág. / ejercicio)_

## 🔗 Relacionado
- [[GRAM-000 tema relacionado]]

## 🗒️ Notas / Excepciones
_(Casos especiales.)_
```

---

## 5. Ejemplo de ficha rellenada (ilustrativo)

> ⚠️ **Contenido de muestra.** La fuente y las páginas son un placeholder; se
> reemplazan por tu libro real cuando lo proceses. Sirve solo para ver el formato.

```markdown
---
id: GRAM-012
fuente: "[EJEMPLO — reemplazar con tu libro]"
autor: "[EJEMPLO]"
edicion_anio: ""
capitulo: "Unit X"
seccion: "Present Perfect"
paginas: "pp. 00–00"
isbn: ""
macrohabilidad_toefl: "Structure & Written Expression"
categoria: "Tiempos verbales"
subcategoria: "Present Perfect"
nivel_cefr: "B1"
prioridad_toefl: "Alta"
tipo_item_toefl: "Structure — completion / Written Expression — error ID"
tags: [toefl-structure, tenses, present-perfect]
fecha_extraccion: 2026-10-21
---

# Present Perfect (GRAM-012)

> **Fuente:** [EJEMPLO — reemplazar con tu libro], Unit X, pp. 00–00.

## 🎯 Objetivo
Usar y reconocer el present perfect para acciones pasadas con relevancia en el presente o duración hasta ahora.

## 📘 Regla / Concepto
Conecta pasado y presente: acción terminada en tiempo no específico, o que inició en el pasado y continúa.

## 🧩 Estructura / Fórmula
`subject + have/has + past participle`

## 💬 Ejemplos (del texto)
- She **has lived** here for ten years.
- I **have** already **seen** that movie.
- They **haven't finished** yet.

## ⚠️ Errores comunes (clave TOEFL)
- ❌ *I have seen him yesterday.* → ✅ *I saw him yesterday.* (tiempo específico → past simple)
- ❌ *She has went.* → ✅ *She has gone.* (participio incorrecto)
- ❌ *for / since* mal usados → `for` + periodo, `since` + punto de inicio.

## 🔤 Vocabulario clave
| Palabra/colocación | Significado | Nota |
|---|---|---|
| already | ya | normalmente antes del participio |
| yet | todavía/aún | en negativas y preguntas, al final |
| since / for | desde / durante | marcadores de duración |

## 📝 Práctica
- Ref. libro: pág. 00, ejercicios 1–3.

## 🔗 Relacionado
- [[GRAM-010 Past Simple]]
- [[GRAM-013 Present Perfect vs Past Simple]]

## 🗒️ Notas / Excepciones
En inglés americano (TOEFL) se acepta *Did you eat yet?*; en formal se prefiere present perfect.
```

---

## 6. Mapa de cobertura TOEFL (checklist + tracker)

Úsalo para marcar `[x]` conforme se generen fichas. Así sabemos cuándo el corpus
"abarca lo suficiente" para 500. Las de **prioridad Alta** son las que más mueven el puntaje.

### Structure & Written Expression (gramática) — PRIORIDAD ALTA
- [ ] Subject–verb agreement
- [ ] Verb tenses & forms (present/past/perfect/continuous)
- [ ] Gerunds & infinitives
- [ ] Modals
- [ ] Conditionals (0–3)
- [ ] Passive voice
- [ ] Articles & determiners (a/an/the/Ø)
- [ ] Nouns: count/noncount, singular/plural
- [ ] Pronouns: agreement & case
- [ ] Prepositions
- [ ] Adjectives vs adverbs; comparativos/superlativos
- [ ] Parallel structure (paralelismo)
- [ ] Relative clauses
- [ ] Conjunctions / connectors (coord. y subord.)
- [ ] Word order & inversion
- [ ] Reduced / participial clauses
- [ ] Sentence structure: fragments, run-ons, cláusulas
- [ ] Redundancy & word choice (error ID típico)

### Reading Comprehension — PRIORIDAD ALTA
- [ ] Main idea / topic
- [ ] Supporting details (scanning)
- [ ] Vocabulary in context
- [ ] Pronoun reference
- [ ] Inference
- [ ] Author's purpose / tone
- [ ] Text organization / cohesion

### Listening Comprehension — PRIORIDAD MEDIA-ALTA
- [ ] Short dialogues: idioms & implied meaning
- [ ] Paraphrase / restatement
- [ ] Longer conversations: main idea & detail
- [ ] Mini-talks / lectures

### Vocabulario y lenguaje funcional — PRIORIDAD MEDIA
- [ ] Academic word list (núcleo)
- [ ] Phrasal verbs frecuentes
- [ ] Colocaciones comunes
- [ ] Conectores de discurso (however, therefore, moreover…)

---

## 7. Siguiente paso

Sube el **primer libro** (PDF de preferencia; si es escaneado, igual lo manejo con
OCR). Yo:
1. Reviso índice y estructura.
2. Te propongo el **plan de troceo** (qué unidades → qué IDs).
3. Genero las primeras fichas `.md` según esta plantilla, cada una con su fuente y página.

Tú revisas, ajustamos la matriz si hace falta, y seguimos con el resto del corpus.
