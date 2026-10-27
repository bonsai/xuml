# xuml Skills Index

This repository uses [Pi Coding Agent](https://github.com/earendil-works/pi-coding-agent) skills for specialized workflows.

## Available Skills

| Skill | Description | Location |
|-------|-------------|----------|
| `plantuml-jar` | Render PlantUML (.puml) to SVG/PNG using local plantuml.jar. Offline, no external API. | `.agents/skills/plantuml-jar/` |

## Usage

Skills are automatically discovered by Pi when placed in `.agents/skills/` or `~/.agents/skills/`.

### plantuml-jar

```bash
# Ensure plantuml.jar is downloaded
bash .agents/skills/plantuml-jar/scripts/ensure-jar.sh

# Render .puml to SVG
bash .agents/skills/plantuml-jar/scripts/render.sh diagram.puml -tsvg

# Render .puml to PNG
bash .agents/skills/plantuml-jar/scripts/render.sh diagram.puml -tpng

# From Python
from xuml_plantuml import render_puml
render_puml("diagram.puml", fmt="svg")
```

### Full Pipeline

```bash
# 1. Generate PlantUML from Python package
xuml -pyu ./mypackage -o diagram.puml

# 2. Render to SVG using skill
bash .agents/skills/plantuml-jar/scripts/render.sh diagram.puml -tsvg
# → diagram.svg
```

## Adding Skills

1. Create directory under `.agents/skills/<skill-name>/`
2. Add `SKILL.md` with frontmatter (name, description)
3. Add scripts, references, assets as needed
4. Run `/reload` in Pi to discover new skills

## Skill Structure

```
.agents/skills/<skill-name>/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Executable scripts
├── references/           # Reference documentation
└── assets/               # Templates, data files
```

See [Pi Skills Documentation](https://github.com/earendil-works/pi-coding-agent/blob/main/docs/skills.md) for details.