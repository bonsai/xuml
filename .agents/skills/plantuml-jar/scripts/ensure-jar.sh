#!/usr/bin/env bash
# Download plantuml.jar to skill directory if missing

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JAR_PATH="${SKILL_DIR}/plantuml.jar"
JAR_URL="https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"

if [[ -f "${JAR_PATH}" ]]; then
    echo "plantuml.jar already exists at ${JAR_PATH}"
    exit 0
fi

echo "Downloading plantuml.jar..."
curl -L -o "${JAR_PATH}" "${JAR_URL}"
echo "Downloaded to ${JAR_PATH}"