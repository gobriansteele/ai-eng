from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "factory_verify", ROOT / "plugins/factory/scripts/factory_verify.py"
)
assert spec and spec.loader
verify = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = verify
spec.loader.exec_module(verify)


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "source"
        self.repo.mkdir()
        self.source = self.repo / "sample.py"
        self.source.write_text("print('sample')\n")
        self.output = self.root / "evidence"

    def metadata(self):
        return json.loads((self.output / "command.json").read_text())

    def test_records_actual_command_outputs_clock_and_failure(self):
        command = [
            sys.executable,
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr); sys.exit(7)",
        ]
        self.assertEqual(
            verify.record(self.repo, self.output, [self.source], command), 7
        )
        saved = self.metadata()
        self.assertEqual(saved["command"], command)
        self.assertEqual(saved["cwd"], str(self.repo))
        self.assertEqual(saved["exit_code"], 7)
        self.assertIsNone(saved["launch_error"])
        self.assertEqual(Path(saved["stdout_path"]).read_text(), "out\n")
        self.assertEqual(Path(saved["stderr_path"]).read_text(), "err\n")
        self.assertLessEqual(
            datetime.fromisoformat(saved["started_at"]),
            datetime.fromisoformat(saved["ended_at"]),
        )
        self.assertGreaterEqual(saved["elapsed_seconds"], 0)
        self.assertEqual(saved["before"]["files"], saved["after"]["files"])

    def test_captures_changed_or_missing_input_after_execution(self):
        command = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('sample.py').unlink()",
        ]
        self.assertEqual(
            verify.record(self.repo, self.output, [Path("sample.py")], command), 0
        )
        saved = self.metadata()
        self.assertIsNotNone(saved["before"]["files"][0]["sha256"])
        self.assertIsNone(saved["after"]["files"][0]["sha256"])
        self.assertIsNotNone(saved["after"]["files"][0]["error"])

    def test_missing_executable_is_not_an_executed_check(self):
        self.assertEqual(
            verify.record(
                self.repo, self.output, [self.source], ["/no-such-factory-check"]
            ),
            1,
        )
        saved = self.metadata()
        self.assertIsNone(saved["exit_code"])
        self.assertIsNotNone(saved["launch_error"])

    def test_missing_input_and_existing_output_do_not_run_command(self):
        command = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('ran').touch()",
        ]
        with self.assertRaisesRegex(ValueError, "readable"):
            verify.record(self.repo, self.output, [Path("missing.py")], command)
        self.assertFalse((self.repo / "ran").exists())
        self.output.mkdir()
        marker = self.output / "original"
        marker.write_text("keep")
        with self.assertRaises(FileExistsError):
            verify.record(self.repo, self.output, [self.source], command)
        self.assertEqual(marker.read_text(), "keep")
        self.assertFalse((self.repo / "ran").exists())

    def test_evidence_inside_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            verify.record(
                self.repo,
                self.repo / "evidence",
                [self.source],
                [sys.executable, "-c", "pass"],
            )
        self.assertFalse((self.repo / "evidence").exists())

    def test_git_observations_allow_honest_precommit_byte_reuse(self):
        def git(*args):
            return subprocess.check_output(
                ["git", *args], cwd=self.repo, text=True
            ).strip()

        git("init", "-q")
        git("add", "sample.py")
        git(
            "-c",
            "user.name=Synthetic",
            "-c",
            "user.email=synthetic@example.invalid",
            "commit",
            "-qm",
            "baseline",
        )
        original = git("rev-parse", "HEAD")
        self.source.write_text("print('changed')\n")
        self.assertEqual(
            verify.record(
                self.repo, self.output, [self.source], [sys.executable, "sample.py"]
            ),
            0,
        )
        saved = self.metadata()
        git("add", "sample.py")
        git(
            "-c",
            "user.name=Synthetic",
            "-c",
            "user.email=synthetic@example.invalid",
            "commit",
            "-qm",
            "change",
        )
        current = verify.snapshot(self.repo, [self.source])
        self.assertEqual(saved["before"]["git"]["head"], original)
        self.assertNotEqual(current["git"]["head"], original)
        self.assertEqual(current["files"], saved["after"]["files"])
        self.assertNotEqual(saved["before"]["git"]["status"], current["git"]["status"])

    def test_parent_traversal_through_symlink_is_rejected_before_execution(self):
        real = self.root / "real"
        (real / "child").mkdir(parents=True)
        (self.repo / "checked.py").write_text("wrong lexical file")
        (real / "checked.py").write_text("actual command input")
        (self.repo / "link").symlink_to(real / "child", target_is_directory=True)
        command = [
            sys.executable,
            "-c",
            "from pathlib import Path; print(Path('link/../checked.py').read_text())",
        ]
        with self.assertRaisesRegex(ValueError, "parent traversal"):
            verify.record(self.repo, self.output, [Path("link/../checked.py")], command)
        self.assertFalse(self.output.exists())

    def test_symlink_input_is_read_again_after_retarget(self):
        first, second, link = self.repo / "a", self.repo / "b", self.repo / "link"
        first.write_text("first")
        second.write_text("second")
        link.symlink_to(first)
        command = [
            sys.executable,
            "-c",
            "from pathlib import Path; p=Path('link'); p.unlink(); p.symlink_to('b')",
        ]
        verify.record(self.repo, self.output, [link], command)
        saved = self.metadata()
        self.assertNotEqual(saved["before"]["files"], saved["after"]["files"])


if __name__ == "__main__":
    unittest.main()
