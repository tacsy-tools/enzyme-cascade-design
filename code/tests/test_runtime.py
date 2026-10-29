"""Reject unsupported Julia before preparing an apparently runnable experiment."""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import reproduce
import scan
import verify
from common import HERE


class RuntimeTests(unittest.TestCase):
    def test_wrong_julia_version_does_not_create_run_outputs(self):
        for version in ["1.10", "1.12", "1.13"]:
            for entry in [scan, reproduce, verify]:
                with self.subTest(version=version, command=entry.__name__):
                    with tempfile.TemporaryDirectory() as directory:
                        output = Path(directory) / "run"
                        arguments = [entry.__name__, "--output", str(output)]
                        if entry is scan:
                            arguments += [
                                str(HERE / "examples/9mec/model.json"),
                                "--run",
                            ]
                        elif entry is reproduce:
                            arguments += ["--kinetics"]
                        result = subprocess.CompletedProcess([], 0, stdout=version)
                        errors = io.StringIO()
                        with (
                            patch.object(sys, "argv", arguments),
                            patch("common.subprocess.run", return_value=result),
                            contextlib.redirect_stderr(errors),
                        ):
                            with self.assertRaises(SystemExit) as raised:
                                entry.main()
                        self.assertEqual(raised.exception.code, 1)
                        self.assertIn("requires Julia 1.11.x", errors.getvalue())
                        self.assertFalse(output.exists())

    def test_preparing_inputs_does_not_require_julia(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            arguments = [
                "scan.py",
                str(HERE / "examples/9mec/model.json"),
                "--single",
                "1",
                "--output",
                str(output),
            ]
            with (
                patch.object(sys, "argv", arguments),
                patch(
                    "common.subprocess.run",
                    side_effect=AssertionError("Julia was started"),
                ),
            ):
                scan.main()
            self.assertTrue((output / "model.json").is_file())
            self.assertIn("require_julia_version()", (output / "model.jl").read_text())


if __name__ == "__main__":
    unittest.main()
