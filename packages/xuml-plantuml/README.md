# xuml-plantuml

PlantUML rendering integration for xuml using local plantuml.jar.

## Features

- Offline PlantUML rendering (no external API calls)
- Automatic plantuml.jar download and caching
- SVG, PNG, and other format support
- Python API and CLI integration

## Installation

```bash
pip install -e packages/xuml-plantuml
```

Requires Java JRE/JDK on PATH.

## Usage

```python
from xuml_plantuml import render_puml

# Render .puml file to SVG
svg_path = render_puml("diagram.puml", fmt="svg")
print(f"Generated: {svg_path}")

# Or use the renderer class for more control
from xuml_plantuml import PlantUMLRenderer

renderer = PlantUMLRenderer()
svg_path = renderer.render("diagram.puml", fmt="svg")
```

## Integration with xuml

```bash
# Generate PlantUML from Python package
xuml -pyu ./mypackage -o diagram.puml

# Render to SVG
python -c "from xuml_plantuml import render_puml; render_puml('diagram.puml', 'svg')"
```