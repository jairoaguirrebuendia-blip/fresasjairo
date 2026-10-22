# 🇬🇧 Curso autodidacta de inglés → TOEFL ITP 500

Proyecto para convertir tus libros de inglés en un curso propio, rastreable y orientado
al TOEFL ITP (meta: 500 ≈ B1). Todo nace de la
[matriz de extracción](00-matriz/matriz-extraccion.md).

## Estructura

```
curso-ingles-toefl/
├── 00-matriz/
│   ├── matriz-extraccion.md            ← reglas, campos, mapa de cobertura (la "ley")
│   ├── plantilla-ficha.md              ← plantilla para copiar
│   └── instrucciones-agente-extractor.md ← contrato que sigue cada agente
├── fuentes/        ← libros descomprimidos (D01-..., D02-...). No se suben a git.
├── fichas/
│   ├── GRAM/  READ/  LIST/  VOCAB/  FUNC/   ← 1 ficha .md = 1 idea, siempre con fuente y página
├── registro/
│   ├── documentos.md     ← qué libro es cada D##, su bloque de IDs y su estado
│   ├── indice-fichas.md  ← índice generado de todas las fichas
│   └── cobertura.md      ← checklist TOEFL generado (qué temas ya están cubiertos)
├── scripts/
│   ├── intake.sh          ← descomprime el paquete y hace el inventario
│   ├── validar_fichas.py  ← valida fichas, IDs, enlaces y quizzes; regenera índice y cobertura
│   ├── construir_curso.py ← genera el curso HTML desde las fichas
│   └── curso_plantilla.html
└── curso-html/
    ├── index.html      ← el curso: ábrelo en el navegador (funciona sin servidor)
    └── fragmento.html  ← mismo curso, versión para publicar como Artifact
```

## Cómo se procesa un paquete (multi-agente)

1. **Intake (orquestador):** `scripts/intake.sh paquete.zip` → cada archivo queda como
   `fuentes/Dnn-nombre.pdf`, con páginas y tipo (texto/escaneado). Se registra en
   `registro/documentos.md` con su bloque de IDs (`Dnn` → `XXXX-nn00..nn99`).
2. **Extracción en paralelo:** se lanza **un agente por documento**, cada uno con
   `instrucciones-agente-extractor.md`, su ruta y su bloque de IDs. Así no hay choques de IDs
   y cada ficha queda ligada a su libro y página.
3. **Consolidación (orquestador):** `python3 scripts/validar_fichas.py --cobertura`
   revisa campos obligatorios, valores permitidos, IDs duplicados y enlaces rotos, y
   regenera índice y cobertura. Los temas que se repiten entre libros se enlazan.
4. **Tu revisión (Etapa 2):** revisas las fichas, ajustamos la matriz si hace falta.
5. **Curso HTML (Etapa 3):** `python3 scripts/construir_curso.py` → `curso-html/index.html`.
   Publicado en: https://claude.ai/artifact/7hN2S3auDHqiXnbHBWxG7A

## Estado (paquete 1)
17 de 19 documentos extraídos (2 llegaron vacíos): **347 fichas · 616 preguntas**.
Detalle por libro en `registro/documentos.md`; cobertura TOEFL en `registro/cobertura.md`.

## Nota sobre derechos de autor
Los libros originales se quedan en `fuentes/` (ignorado por git). Las fichas son
resúmenes con ejemplos breves y referencias de página, no copias del libro.
