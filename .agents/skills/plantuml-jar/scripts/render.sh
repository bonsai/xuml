#!/usr/bin/env bash
# Render PlantUML file(s) to SVG/PNG using local plantuml.jar

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JAR_PATH="${SKILL_DIR}/plantuml.jar"
ENSURE_JAR="${SKILL_DIR}/scripts/ensure-jar.sh"

# Default format
FORMAT="svg"
INPUT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -tsvg|-tpng|-txt|-tlatex|-teps|-tpdf|-tutxt)
            FORMAT="${1#-t}"
            shift
            ;;
        -t*)
            FORMAT="${1#-t}"
            shift
            ;;
        *)
            INPUT="$1"
            shift
            ;;
    esac
done

if [[ -z "${INPUT}" ]]; then
    echo "Usage: $0 <input.puml|directory> [-tsvg|-tpng|...]"
    exit 1
fi

# Ensure jar exists
if [[ ! -f "${JAR_PATH}" ]]; then
    echo "plantuml.jar not found, downloading..."
    bash "${ENSURE_JAR}"
fi

# Render
if [[ -d "${INPUT}" ]]; then
    # Process all .puml files in directory
    find "${INPUT}" -name "*.puml" -type f | while read -r file; do
        echo "Rendering ${file} -> ${FORMAT}"
        java -jar "${JAR_PATH}" "-t${FORMAT}" "${file}"
    done
else
    # Single file
    echo "Rendering ${INPUT} -> ${FORMAT}"
    java -jar "${JAR_PATH}" "-t${FORMAT}" "${INPUT}"
fi