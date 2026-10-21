# 📚 Registro de documentos

Cada documento recibido obtiene un `doc_id` y un bloque de IDs. Lo llena el orquestador
al descomprimir el paquete (`scripts/intake.sh`) y al cerrar cada extracción.

| doc_id | Archivo | Título | Autor | Edición/año | Páginas | Tipo (texto/escaneado) | Bloque IDs | Estado | Fichas |
|---|---|---|---|---|---|---|---|---|---|
| _(vacío — esperando el primer paquete)_ | | | | | | | | | |

**Estados:** `recibido` → `en extracción` → `extraído` → `revisado por Jairo` → `compilado`
