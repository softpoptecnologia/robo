#!/usr/bin/env bash
# Popula arquivos/tectonic-cache/ compilando o template IEEE oficial.
# Rode numa máquina Linux x86_64 com internet; depois envie a pasta ao servidor cPanel.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE_DIR="${TECTONIC_CACHE_DIR:-$ROOT/arquivos/tectonic-cache}"
BIN_DIR="${TECTONIC_BIN_DIR:-$ROOT/bin}"
TEMPLATE_DIR="$ROOT/arquivos/ieee-template"
TEX="conference_101719.tex"

mkdir -p "$CACHE_DIR"
export TECTONIC_CACHE_DIR="$CACHE_DIR"

if [[ ! -x "$BIN_DIR/tectonic" ]]; then
  echo "Tectonic não encontrado em $BIN_DIR/tectonic" >&2
  echo "Instale o build musl — veja DEPLOY.md" >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE_DIR/$TEX" ]]; then
  echo "Template IEEE ausente: $TEMPLATE_DIR/$TEX" >&2
  echo "Confirme arquivos/IEEE_Conference_Template.zip e acesse o portal uma vez para extrair." >&2
  exit 1
fi

echo "Compilando $TEX (cache em $CACHE_DIR)..."
cd "$TEMPLATE_DIR"
"$BIN_DIR/tectonic" -X compile --outdir "$TEMPLATE_DIR" "$TEX"

echo
echo "Cache pronto:"
du -sh "$CACHE_DIR"
echo "Envie ao servidor: tar -czf tectonic-cache.tgz -C arquivos tectonic-cache"
