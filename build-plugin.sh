#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
PLUGIN_DIR="${ROOT_DIR}/plugin-src"
OUTPUT_FILE="${DIST_DIR}/BibliomanMetadata.zip"

mkdir -p "${DIST_DIR}"
rm -f "${OUTPUT_FILE}"

cd "${PLUGIN_DIR}"
zip -r "${OUTPUT_FILE}" . >/dev/null

printf 'Built %s\n' "${OUTPUT_FILE}"
