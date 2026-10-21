# 🤖 Instrucciones para el agente extractor (1 agente = 1 documento)

Este es el "contrato" que recibe **cada agente** cuando se procesa un documento.
Varios agentes trabajan en paralelo, uno por documento; por eso cada uno recibe
un **bloque de IDs reservado** y nunca escribe fuera de él.

## Entradas que recibe el agente
| Entrada | Ejemplo |
|---|---|
| `doc_id` | `D03` |
| `ruta_documento` | `fuentes/D03-azar-understanding-grammar.pdf` |
| `bloques_id` | `GRAM-300..399`, `VOCAB-200..299` (solo los prefijos que le tocan) |
| `alcance` | Qué extraer y cuántas fichas, aprox. |
| `matriz` | `00-matriz/matriz-extraccion.md` |
| `plantilla` | `00-matriz/plantilla-ficha.md` |

> Regla de bloques: cada documento recibe rangos de 100 IDs **solo de los prefijos que le tocan**,
> asignados en `registro/documentos.md`. Los IDs se usan en orden desde el inicio del bloque.

## Pasos
1. **Leer la matriz completa** (`00-matriz/matriz-extraccion.md`) y la plantilla.
2. **Identificar la fuente**: título, autor, edición/año, ISBN (portada, página legal).
   Si algo no aparece, dejar el campo como `""` y anotarlo en el reporte; **nunca inventar**.
3. **Revisar el índice** y proponer el *plan de troceo*: qué secciones → qué IDs.
   Regla: **una ficha = una idea extraíble**.
4. **Leer cada sección** y llenar la ficha con la plantilla:
   - Metadatos y explicaciones en **español**; ejemplos, reglas y vocabulario en **inglés**.
   - `paginas` = páginas **impresas del libro** (las que ve el lector), no las del visor PDF.
     Si solo se conoce la página del PDF, escribir `"PDF p. 45"`.
     En documentos convertidos a Markdown, la página sale de marcas como `PAGE 46`, números
     sueltos en una línea, o del índice del libro. Si el libro numera secciones, citarlas también
     (`"§41, p. 46"`). Si de verdad no hay página, usar `"s/p — Unit 5, sección 'Questions'"`.
   - `ejemplos`: copiar ejemplos **del libro** (cortos, 2–5 por ficha). No transcribir
     ejercicios ni páginas completas: se citan por página en `## 📝 Práctica`.
   - `errores_comunes`: priorizar los que sirven para *Written Expression — error ID*.
   - Clasificar `macrohabilidad_toefl`, `nivel_cefr`, `prioridad_toefl` según la sección 2
     y el mapa de cobertura (sección 6) de la matriz.
   - **Práctica estilo TOEFL:** al final de cada ficha, un bloque ```` ```quiz ```` (formato en la
     sección 3.E de la matriz) con preguntas **originales** estilo TOEFL ITP: mín. 2 en `GRAM`,
     1 en `VOCAB`/`FUNC`/`READ`/`LIST`. Explicaciones en español. Las 4 opciones deben ser
     plausibles y solo una correcta. En `error-id` exactamente un segmento es el error.
   - **Fichas `METO`** (libros de teoría/didáctica): no se extrae teoría para profesores, sino
     lo que **un estudiante autodidacta puede aplicar**. Secciones: `🎯 Objetivo`,
     `📘 Idea clave` (con cita breve del libro), `🛠️ Cómo aplicarlo como autodidacta`
     (pasos concretos), `⚠️ Errores comunes del autodidacta`, `📝 Acción para esta semana`,
     `🔗 Relacionado`. `nivel_cefr: "Todos"`, `tipo_item_toefl: "No aplica — método de estudio"`.
5. **Guardar** cada ficha en `fichas/<PREFIJO>/<ID>-<slug>.md`
   (ej. `fichas/GRAM/GRAM-312-present-perfect.md`). Slug en minúsculas con guiones.
6. **Enlazar** fichas relacionadas con `[[ID Título]]`. Solo enlazar IDs que existan
   (propios, o ya listados en `registro/indice-fichas.md`).
7. **Reportar** al orquestador (texto, no archivo):
   - Datos de la fuente detectados y los que faltan.
   - Plan de troceo aplicado (tabla sección → ID).
   - Temas del mapa de cobertura que el documento cubre.
   - Dudas o partes ilegibles (páginas escaneadas borrosas, etc.).

## Lo que el agente NO hace
- No edita `registro/` ni fichas de otros documentos (eso lo consolida el orquestador).
- No usa IDs fuera de su bloque.
- No inventa páginas, ejemplos ni datos bibliográficos.

## Validación antes de entregar
Correr `python3 scripts/validar_fichas.py` y corregir **todos** los errores de las fichas
propias (los avisos de enlaces hacia fichas de otros documentos se pueden dejar).

## Documentos escaneados
Si `pdftotext` devuelve poco o nada de texto, el PDF es escaneado: leer las páginas
como imagen (por rangos de ≤20 páginas) y transcribir solo lo necesario para la ficha.
