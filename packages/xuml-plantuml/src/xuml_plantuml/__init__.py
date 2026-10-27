"""xuml PlantUML integration - render PlantUML to SVG/PNG using local plantuml.jar."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Literal

__version__ = "0.1.0"

DEFAULT_JAR_URL = "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
FORMATS = Literal["svg", "png", "txt", "latex", "eps", "pdf", "utxt"]


class PlantUMLError(Exception):
    """Raised when PlantUML rendering fails."""
    pass


class PlantUMLRenderer:
    """Render PlantUML files using local plantuml.jar."""

    def __init__(self, jar_path: Path | None = None, java_cmd: str = "java"):
        self.java_cmd = java_cmd
        if jar_path is None:
            # Default to skill location
            self.jar_path = Path(__file__).parent.parent.parent.parent / ".agents" / "skills" / "plantuml-jar" / "plantuml.jar"
        else:
            self.jar_path = Path(jar_path)

    def ensure_jar(self) -> None:
        """Download plantuml.jar if not present."""
        if self.jar_path.exists():
            return

        self.jar_path.parent.mkdir(parents=True, exist_ok=True)
        import urllib.request
        print(f"Downloading plantuml.jar to {self.jar_path}...")
        urllib.request.urlretrieve(DEFAULT_JAR_URL, self.jar_path)
        print("Download complete.")

    def render(
        self,
        input_path: Path | str,
        fmt: FORMATS = "svg",
        output_path: Path | str | None = None,
    ) -> Path:
        """Render a .puml file to the specified format."""
        input_path = Path(input_path)
        if not input_path.exists():
            raise PlantUMLError(f"Input file not found: {input_path}")

        self.ensure_jar()

        if output_path is None:
            output_path = input_path.with_suffix(f".{fmt}")
        else:
            output_path = Path(output_path)

        cmd = [self.java_cmd, "-jar", str(self.jar_path), f"-t{fmt}", str(input_path)]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
        except subprocess.CalledProcessError as e:
            raise PlantUMLError(f"PlantUML failed: {e.stderr}") from e
        except subprocess.TimeoutExpired:
            raise PlantUMLError("PlantUML timed out after 60 seconds") from None

        if not output_path.exists():
            # PlantUML outputs to the same directory as input by default
            expected = input_path.with_suffix(f".{fmt}")
            if expected.exists():
                expected.rename(output_path)
            else:
                raise PlantUMLError(f"Output not generated at {output_path}")

        return output_path

    def render_string(
        self,
        puml_content: str,
        fmt: FORMATS = "svg",
        output_path: Path | str | None = None,
    ) -> Path:
        """Render PlantUML from string content."""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".puml", delete=False) as f:
            f.write(puml_content)
            temp_path = Path(f.name)
        try:
            return self.render(temp_path, fmt, output_path)
        finally:
            temp_path.unlink(missing_ok=True)


def render_puml(
    input_path: Path | str,
    fmt: FORMATS = "svg",
    output_path: Path | str | None = None,
    jar_path: Path | str | None = None,
) -> Path:
    """Convenience function to render a .puml file."""
    renderer = PlantUMLRenderer(Path(jar_path) if jar_path else None)
    return renderer.render(input_path, fmt, output_path)