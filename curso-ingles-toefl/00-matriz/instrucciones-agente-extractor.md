# 🤖 Instrucciones para el agente extractor (1 agente = 1 documento)

Este es el "contrato" que recibe **cada agente** cuando se procesa un documento.
Varios agentes trabajan en paralelo, uno por documento; por eso cada uno recibe
un **bloque de IDs reservado** y nunca escribe fuera de él.

## Entradas que recibe el agente
| Entrada | Ejemplo |
|---|---|
| `doc_id` | `D03` |
| `ruta_documento` | `fuentes/D03-azar-understanding-grammar.pdf` |
| `bloques_id` | `GRAM-300..399`, `READ-300..399`, `LIST-300..399`, `VOCAB-300..399`, `FUNC-300..399` |
| `matriz` | `00-matriz/matriz-extraccion.md` |
| `plantilla` | `00-matriz/plantilla-ficha.md` |

> Regla de bloques: el documento `Dnn` usa los IDs `nn00–nn99` de cada prefijo
> (D01 → `GRAM-100..199`, D02 → `GRAM-200..299`, …). Si un documento necesita
> más de 100 fichas de un prefijo, se le asigna un segundo bloque en `registro/documentos.md`.

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
   - `ejemplos`: copiar ejemplos **del libro** (cortos, 2–5 por ficha). No transcribir
     ejercicios ni páginas completas: se citan por página en `## 📝 Práctica`.
   - `errores_comunes`: priorizar los que sirven para *Written Expression — error ID*.
   - Clasificar `macrohabilidad_toefl`, `nivel_cefr`, `prioridad_toefl` según la sección 2
     y el mapa de cobertura (sección 6) de la matriz.
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

## Documentos escaneados
Si `pdftotext` devuelve poco o nada de texto, el PDF es escaneado: leer las páginas
como imagen (por rangos de ≤20 páginas) y transcribir solo lo necesario para la ficha.
