---
name: plantuml-jar
description: Render PlantUML (.puml) files to SVG/PNG using local plantuml.jar. Use when you need offline diagram generation without external API calls.
---

# plantuml-jar skill

This skill provides a local PlantUML renderer using `plantuml.jar` + Java. It avoids the public PlantUML server and works fully offline.

## Prerequisites

- Java JRE/JDK installed and on `PATH`
- `plantuml.jar` downloaded (script handles this automatically)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/ensure-jar.sh` | Download `plantuml.jar` to skill directory if missing |
| `scripts/render.sh` | Render `.puml` file to SVG/PNG |

## Usage

```bash
# Ensure jar exists (runs automatically)
.c/.agents/skills/plantuml-jar/scripts/ensure-jar.sh

# Render to SVG
.c/.agents/skills/plantuml-jar/scripts/render.sh diagram.puml -tsvg

# Render to PNG
.c/.agents/skills/plantuml-jar/scripts/render.sh diagram.puml -tpng

# Render all .puml files in directory
.c/.agents/skills/plantuml-jar/scripts/render.sh ./diagrams/ -tsvg
```

## Python helper

```python
from pathlib import Path
import subprocess

SKILL_DIR = Path(__file__).parent / ".agents" / "skills" / "plantuml-jar"
JAR = SKILL_DIR / "plantuml.jar"

def render_puml(puml_path: str, fmt: str = "svg") -> Path:
    """Render .puml file to SVG or PNG using local plantuml.jar."""
    puml_path = Path(puml_path)
    if not JAR.exists():
        subprocess.run(["bash", str(SKILL_DIR / "scripts" / "ensure-jar.sh")], check=True)
    
    output = puml_path.with_suffix(f".{fmt}")
    subprocess.run(["java", "-jar", str(JAR), f"-t{fmt}", str(puml_path)], check=True)
    return output
```

## Integration with xuml

```bash
# Generate PlantUML from Python package
xuml -pyu ./mypackage -o diagram.puml

# Render to SVG using local jar
.agents/skills/plantuml-jar/scripts/render.sh diagram.puml -tsvg
# → diagram.svg created
```

## Notes

- The jar is cached in the skill directory (~15 MB)
- Supports all PlantUML output formats: `-tsvg`, `-tpng`, `-txt`, `-tlatex`, etc.
- For headless servers, ensure Java has `-Djava.awt.headless=true` if rendering fails