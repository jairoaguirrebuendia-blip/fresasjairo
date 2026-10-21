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
│   └── validar_fichas.py  ← valida fichas, IDs, enlaces; regenera índice y cobertura
└── curso-html/     ← Etapa 3: el curso navegable
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
5. **Curso HTML (Etapa 3):** se arma a partir del corpus validado.

## Nota sobre derechos de autor
Los libros originales se quedan en `fuentes/` (ignorado por git). Las fichas son
resúmenes con ejemplos breves y referencias de página, no copias del libro.
