import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_release.ps1"


class ReleasePackagingTests(unittest.TestCase):
    def test_release_zip_contains_version_readme_and_changelog(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "source"
            output = temp / "output"
            source.mkdir()
            output.mkdir()
            (source / "QQFarmCVHelper.exe").write_bytes(b"fixture")
            (source / "\u9879\u76ee\u8bf4\u660e.txt").write_text("fixture", encoding="utf-8")

            completed = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(SCRIPT),
                    "-SourceDir",
                    str(source),
                    "-OutputDir",
                    str(output),
                    "-Version",
                    "9.9.9",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            archive = output / "CV\u519c\u573a\u52a9\u624b-v9.9.9-\u4fbf\u643a\u5b8c\u6574\u7248.zip"
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(archive) as handle:
                names = set(handle.namelist())
                self.assertIn("VERSION", names)
                self.assertIn("README.md", names)
                self.assertIn("\u7248\u672c\u4e0e\u66f4\u65b0\u65e5\u5fd7.md", names)
                self.assertEqual("9.9.9", handle.read("VERSION").decode("utf-8").strip())


if __name__ == "__main__":
    unittest.main()
