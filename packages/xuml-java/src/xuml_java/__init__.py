"""xuml Java backend wrapper — native Java diagram engine."""

from __future__ import annotations

class JavaDiagramEngine:
    def __init__(self, jar_path: str | None = None):
        self.jar_path = jar_path or ".agents/skills/plantuml-jar/plantuml.jar"

    def render(self, puml_path: str, fmt: str = "svg") -> str:
        import subprocess
        cmd = ["java", "-jar", self.jar_path, f"-t{fmt}", puml_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

def render_java(puml_path: str, fmt: str = "svg") -> str:
    return JavaDiagramEngine().render(puml_path, fmt)