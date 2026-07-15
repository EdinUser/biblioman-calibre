#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
PLUGIN_DIR="${ROOT_DIR}/plugin-src"
SOURCE_VERSION="$(
    python3 - "${PLUGIN_DIR}/__init__.py" <<'PY'
import re
import sys

source = open(sys.argv[1], encoding='utf-8').read()
match = re.search(r"^__version__ = ['\"]([^'\"]+)['\"]", source, re.MULTILINE)
if not match:
    raise SystemExit('Could not find __version__ in plugin source')
print(match.group(1))
PY
)"
PLUGIN_VERSION="${1:-${SOURCE_VERSION}}"
PLUGIN_VERSION="${PLUGIN_VERSION#v}"

if [[ "${PLUGIN_VERSION}" != "${SOURCE_VERSION}" ]]; then
    printf 'Version mismatch: plugin source is %s, requested build is %s\n' "${SOURCE_VERSION}" "${PLUGIN_VERSION}" >&2
    exit 1
fi

OUTPUT_FILE="${DIST_DIR}/BibliomanMetadata-${PLUGIN_VERSION}.zip"

mkdir -p "${DIST_DIR}"
rm -f "${OUTPUT_FILE}"

cd "${PLUGIN_DIR}"
zip -r "${OUTPUT_FILE}" . >/dev/null

printf 'Built %s\n' "${OUTPUT_FILE}"
