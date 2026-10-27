from __future__ import annotations

import tempfile
import unittest
from unittest.mock import patch, Mock
from pathlib import Path
from io import BytesIO

from xuml.analyze import analyze_python
from xuml.cli import main
from xuml.render import render_svg, write_svg_atomic
from xuml.source import MAX_SOURCE_BYTES, SourceError, _github_blob_to_raw, _read_limited, load_source


class SourceTests(unittest.TestCase):
    def test_github_blob_url_maps_to_raw(self):
        raw, name, origin = _github_blob_to_raw(
            "https://github.com/bonsai/comfy-gen-lora/blob/master/kaggle/interpolate_rife.py"
        )
        self.assertEqual(
            raw,
            "https://raw.githubusercontent.com/bonsai/comfy-gen-lora/master/kaggle/interpolate_rife.py",
        )
        self.assertEqual(name, "interpolate_rife.py")
        self.assertTrue(origin.startswith("https://github.com/"))

    def test_rejects_non_github_host_and_non_https(self):
        for url in (
            "http://github.com/a/b/blob/main/x.py",
            "https://example.com/a/b/blob/main/x.py",
            "https://github.com/a/b/blob/main/x.txt",
        ):
            with self.subTest(url=url), self.assertRaises(SourceError):
                _github_blob_to_raw(url)

    def test_local_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.py"
            path.write_text("class Example:\n    pass\n", encoding="utf-8")
            source = load_source(str(path))
            self.assertEqual(source.name, "sample.py")
            self.assertIn("class Example", source.text)

    def test_remote_retrieval_is_size_limited(self):
        class Response(BytesIO):
            headers = {"Content-Length": str(MAX_SOURCE_BYTES + 1)}

        with self.assertRaisesRegex(SourceError, "byte limit"):
            _read_limited(Response(b"x" * (MAX_SOURCE_BYTES + 1)))


class AnalysisAndRenderTests(unittest.TestCase):
    def test_semantic_ir_has_class_and_method(self):
        ir = analyze_python("class Example:\n    def run(self):\n        pass\n", "sample.py", "sample.py")
        self.assertEqual(ir["ir_version"], "1.0")
        self.assertEqual([node["kind"] for node in ir["nodes"]], ["module", "class", "function"])
        self.assertEqual(ir["nodes"][2]["parent"], "sample.Example")

    def test_syntax_error_is_actionable(self):
        with self.assertRaisesRegex(ValueError, "line 1"):
            analyze_python("class :\n", "bad.py", "bad.py")

    def test_svg_escapes_untrusted_text(self):
        ir = analyze_python("class A_B:\n    pass\n", "x&y.py", "x&y.py")
        svg = render_svg(ir)
        self.assertIn("x&amp;y.py", svg)
        self.assertIn("<svg", svg)
        self.assertTrue(svg.endswith("</svg>\n"))

    def test_atomic_write_preserves_existing_file_before_replace(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "out.svg"
            target.write_text("previous", encoding="utf-8")
            write_svg_atomic(target, "<svg/>\n")
            self.assertEqual(target.read_text(encoding="utf-8"), "<svg/>\n")


class CliTests(unittest.TestCase):
    def test_cli_generates_svg_for_local_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.py"
            output = Path(directory) / "out.svg"
            source.write_text("class Example:\n    pass\n", encoding="utf-8")
            result = main(["-svg", str(source), "-o", str(output)])
            self.assertEqual(result, 0)
            self.assertIn("<svg", output.read_text(encoding="utf-8"))

    def test_cli_failure_does_not_overwrite_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.py"
            output = Path(directory) / "out.svg"
            source.write_text("class :\n", encoding="utf-8")
            output.write_text("known-good", encoding="utf-8")
            result = main(["-svg", str(source), "-o", str(output)])
            self.assertEqual(result, 1)
            self.assertEqual(output.read_text(encoding="utf-8"), "known-good")

    def test_pyu_uses_py2puml_through_uvx(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.py"
            source.write_text("class Example:\\n    pass\\n", encoding="utf-8")
            completed = Mock(returncode=0)
            with patch("xuml.cli.shutil.which", return_value="uvx"), patch(
                "xuml.cli.subprocess.run", return_value=completed
            ) as run:
                result = main(["-pyu", str(source), "-o", str(Path(directory) / "out.puml")])
            self.assertEqual(result, 0)
            command = run.call_args.args[0]
            self.assertEqual(command[:4], ["uvx", "--from", "py2puml", "py2puml"])
            self.assertIn("--path", command)
            self.assertIn("--output-file", command)

    def test_pyu_rejects_remote_url(self):
        with patch("xuml.cli.shutil.which", return_value="uvx"), patch("xuml.cli.subprocess.run") as run:
            result = main(["-pyu", "https://github.com/owner/repo/blob/main/module.py"])
        self.assertEqual(result, 1)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
