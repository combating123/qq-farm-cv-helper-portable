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
                self.assertIn("\u9879\u76ee\u8bf4\u660e.txt", names)
                self.assertEqual("9.9.9", handle.read("VERSION").decode("utf-8").strip())
                project_info = handle.read("\u9879\u76ee\u8bf4\u660e.txt").decode("utf-8")
                self.assertIn("9.9.9", project_info)
                self.assertIn(
                    "github.com/combating123/qq-farm-cv-helper-portable",
                    project_info,
                )
                self.assertIn("\u4e0d\u4f1a\u5411\u4efb\u4f55\u7528\u6237\u6536\u53d6\u8d39\u7528", project_info)

    def test_release_zip_excludes_local_backups_debug_files_and_parallel_runtime(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "source"
            output = temp / "output"
            source.mkdir()
            output.mkdir()
            (source / "QQFarmCVHelper.exe").write_bytes(b"fixture")
            (source / "friend_help_request_text.png").write_bytes(b"required")
            (source / "desktop-current.png").write_bytes(b"private-screen")
            (source / "_analysis_board_crop.png").write_bytes(b"debug")
            (source / "old-launch.lnk").write_bytes(b"absolute-shortcut")
            (source / "hook.py.backup-20260810").write_text("old", encoding="utf-8")
            for dirname in (
                "UserData", "logs", "backups", "artifacts", "diagnostics",
                "maintenance-backup", "runtime-v2.2.5",
            ):
                folder = source / dirname
                folder.mkdir()
                (folder / "private.txt").write_text("private", encoding="utf-8")

            completed = subprocess.run(
                [
                    "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-File", str(SCRIPT), "-SourceDir", str(source),
                    "-OutputDir", str(output), "-Version", "9.9.8",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            archive = output / "CV\u519c\u573a\u52a9\u624b-v9.9.8-\u4fbf\u643a\u5b8c\u6574\u7248.zip"
            with zipfile.ZipFile(archive) as handle:
                names = set(handle.namelist())
                self.assertIn("friend_help_request_text.png", names)
                forbidden = (
                    "UserData/", "logs/", "backups/", "artifacts/",
                    "diagnostics/", "maintenance-backup/", "runtime-v2.2.5/",
                )
                self.assertFalse(any(name.startswith(forbidden) for name in names))
                self.assertNotIn("desktop-current.png", names)
                self.assertNotIn("_analysis_board_crop.png", names)
                self.assertNotIn("old-launch.lnk", names)
                self.assertNotIn("hook.py.backup-20260810", names)


if __name__ == "__main__":
    unittest.main()
