#!/usr/bin/env bash
# Descomprime un paquete de documentos en fuentes/, asigna doc_id (D01, D02, …)
# y genera un inventario con páginas y tipo (texto o escaneado).
# Uso: scripts/intake.sh ruta/al/paquete.zip
set -euo pipefail

paquete="${1:?Uso: intake.sh paquete.zip}"
base="$(cd "$(dirname "$0")/.." && pwd)"
fuentes="$base/fuentes"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

case "$paquete" in
  *.zip) unzip -q "$paquete" -d "$tmp" ;;
  *.tar.gz|*.tgz) tar -xzf "$paquete" -C "$tmp" ;;
  *.tar) tar -xf "$paquete" -C "$tmp" ;;
  *) echo "Formato no soportado: $paquete" >&2; exit 1 ;;
esac

# Siguiente número libre según lo que ya hay en fuentes/
n=$(find "$fuentes" -maxdepth 1 -name 'D[0-9][0-9]-*' | wc -l)

printf "| doc_id | archivo | páginas | tipo |\n|---|---|---|---|\n"
find "$tmp" -type f ! -name '.*' ! -path '*/__MACOSX/*' -print0 | sort -z |
while IFS= read -r -d '' f; do
  n=$((n + 1))
  id=$(printf "D%02d" "$n")
  nombre="$(basename "$f")"
  slug="$(echo "$nombre" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9.]+/-/g; s/^-+|-+$//g')"
  destino="$fuentes/$id-$slug"
  cp "$f" "$destino"

  paginas="-"; tipo="otro"
  if [[ "$nombre" =~ \.[pP][dD][fF]$ ]]; then
    paginas=$(pdfinfo "$destino" 2>/dev/null | awk '/^Pages:/ {print $2}')
    # Menos de ~200 caracteres en las primeras 5 páginas → casi seguro escaneado
    chars=$(pdftotext -l 5 "$destino" - 2>/dev/null | tr -d '[:space:]' | wc -c)
    if (( chars > 200 )); then tipo="texto"; else tipo="escaneado"; fi
  fi
  printf "| %s | %s | %s | %s |\n" "$id" "$(basename "$destino")" "$paginas" "$tipo"
done
