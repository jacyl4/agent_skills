import importlib.util
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_skills.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skills", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_skill(root: Path, relative_dir: str, frontmatter: str) -> Path:
    skill_dir = root / relative_dir
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / "SKILL.md"
    path.write_text(f"---\n{frontmatter}\n---\n\n# Skill\n", encoding="utf-8")
    return path


class ValidateSkillsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def assert_validation_error(self, expected_text: str):
        with self.assertRaises(self.validator.SkillValidationError) as caught:
            self.validator.validate_repository(self.root)
        self.assertIn(expected_text, str(caught.exception))

    def test_accepts_skills_in_category_directories(self):
        write_skill(
            self.root,
            "frontend/good-skill",
            "name: good-skill\ndescription: A useful skill.\nmetadata:\n  targets: [codex, claude]",
        )

        manifest = self.validator.validate_repository(self.root)

        self.assertEqual(
            manifest,
            [
                {
                    "name": "good-skill",
                    "path": "frontend/good-skill/SKILL.md",
                    "description": "A useful skill.",
                    "targets": ["codex", "claude"],
                }
            ],
        )

    def test_rejects_name_that_does_not_match_leaf_directory(self):
        write_skill(self.root, "category/actual-name", "name: other-name\ndescription: Valid")
        self.assert_validation_error("must match leaf directory 'actual-name'")

    def test_rejects_duplicate_names(self):
        write_skill(self.root, "one/shared", "name: shared\ndescription: First")
        write_skill(self.root, "two/shared", "name: shared\ndescription: Second")
        self.assert_validation_error("duplicate name 'shared'")

    def test_rejects_invalid_yaml_and_missing_frontmatter(self):
        bad_yaml = self.root / "bad-yaml" / "SKILL.md"
        bad_yaml.parent.mkdir()
        bad_yaml.write_text("---\nname: [broken\n---\n", encoding="utf-8")
        missing = self.root / "missing" / "SKILL.md"
        missing.parent.mkdir()
        missing.write_text("# No frontmatter\n", encoding="utf-8")

        with self.assertRaises(self.validator.SkillValidationError) as caught:
            self.validator.validate_repository(self.root)

        message = str(caught.exception)
        self.assertIn("invalid YAML", message)
        self.assertIn("missing YAML frontmatter", message)

    def test_rejects_invalid_names(self):
        write_skill(self.root, "Bad_Name", "name: Bad_Name\ndescription: Valid")
        self.assert_validation_error("must match [a-z0-9]+(-[a-z0-9]+)*")

    def test_rejects_empty_and_overlong_descriptions(self):
        write_skill(self.root, "empty", "name: empty\ndescription: ''")
        write_skill(
            self.root,
            "long",
            f"name: long\ndescription: {'x' * 1025}",
        )

        with self.assertRaises(self.validator.SkillValidationError) as caught:
            self.validator.validate_repository(self.root)

        message = str(caught.exception)
        self.assertIn("description must be a non-empty string", message)
        self.assertIn("description must be at most 1024 characters", message)

    def test_rejects_non_string_target_lists(self):
        write_skill(
            self.root,
            "not-list",
            "name: not-list\ndescription: Valid\nmetadata:\n  targets: codex",
        )
        write_skill(
            self.root,
            "not-strings",
            "name: not-strings\ndescription: Valid\nmetadata:\n  targets: [codex, 7]",
        )

        with self.assertRaises(self.validator.SkillValidationError) as caught:
            self.validator.validate_repository(self.root)

        self.assertEqual(str(caught.exception).count("metadata.targets must be a list of strings"), 2)

    def test_does_not_follow_first_level_source_symlinks(self):
        external = self.root.parent / f"{self.root.name}-external"
        try:
            write_skill(external, "linked-skill", "name: linked-skill\ndescription: External")
            (self.root / "linked-source").symlink_to(external, target_is_directory=True)
            write_skill(self.root, "local", "name: local\ndescription: Local")

            manifest = self.validator.validate_repository(self.root)

            self.assertEqual([item["name"] for item in manifest], ["local"])
        finally:
            if external.exists():
                for path in sorted(external.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
                external.rmdir()

    def test_ignores_hidden_and_test_directories(self):
        for directory in (".git", ".omx", ".codex", ".agents", ".private", "tests"):
            write_skill(
                self.root,
                f"{directory}/ignored",
                "name: wrong-name\ndescription: This would fail if scanned",
            )
        write_skill(self.root, "kept", "name: kept\ndescription: Kept")

        manifest = self.validator.validate_repository(self.root)

        self.assertEqual([item["name"] for item in manifest], ["kept"])

    def test_metadata_dates_must_be_quoted_for_agent_json_compatibility(self):
        path = write_skill(self.root, "dated", "name: dated\ndescription: Date fixture\nmetadata:\n  date: 2026-02-15")
        self.assert_validation_error("JSON-serializable")
        path.write_text(path.read_text().replace("date: 2026-02-15", 'date: "2026-02-15"'))
        self.assertEqual(self.validator.validate_repository(self.root)[0]["name"], "dated")

    def test_default_cli_uses_only_dedicated_source_from_any_cwd(self):
        # An unrelated cwd must not become Source or leak maintenance fixtures.
        write_skill(self.root, "tooling/fixture", "name: fixture\ndescription: Not a repository skill")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"], cwd=self.root,
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(result.stdout)
        repository = next(parent for parent in SCRIPT.resolve().parents if (parent / ".git").exists())
        source = repository / "skills"
        expected = {str(path.relative_to(source)) for path in source.rglob("SKILL.md")}
        self.assertTrue(expected)
        self.assertEqual({row["path"] for row in manifest}, expected)
        self.assertNotIn("fixture", {row["name"] for row in manifest})

    def _notice_fixture(self):
        write_skill(self.root, "sample", "name: sample\ndescription: Valid")
        notice = self.root / "sample/LICENSE"
        notice.write_text("Original copyright and license text\n")
        record = {"path": "sample/LICENSE",
                  "sha256": hashlib.sha256(notice.read_bytes()).hexdigest()}
        (self.root / ".license-manifest.json").write_text(
            json.dumps({"version": 1, "files": [record]}))
        return notice, record

    def test_verified_notice_is_accepted_and_missing_notice_blocks(self):
        notice, _ = self._notice_fixture()
        self.assertEqual(len(self.validator.validate_repository(self.root)), 1)
        notice.unlink()
        self.assert_validation_error("verified license/notice is missing")

    def test_modified_notice_blocks_without_rewriting_it(self):
        notice, _ = self._notice_fixture()
        notice.write_text("Changed notice")
        self.assert_validation_error("verified license/notice changed")
        self.assertEqual(notice.read_text(), "Changed notice")

    def test_notice_escape_symlink_and_invalid_manifest_block(self):
        notice, record = self._notice_fixture()
        notice.unlink()
        notice.symlink_to(self.root / "external")
        self.assert_validation_error("verified license/notice is missing")
        record["path"] = "../outside/LICENSE"
        (self.root / ".license-manifest.json").write_text(
            json.dumps({"version": 1, "files": [record]}))
        self.assert_validation_error("notice path escapes")
        (self.root / ".license-manifest.json").write_text("{broken")
        self.assert_validation_error(".license-manifest.json")
        (self.root / ".license-manifest.json").unlink()
        (self.root / ".license-manifest.json").symlink_to(self.root / "missing-manifest")
        self.assert_validation_error("notice manifest must be a regular file")

    def test_explicit_license_reference_requires_real_file(self):
        write_skill(self.root, "sample", "name: sample\ndescription: Valid\nlicense: Complete terms in LICENSE.txt")
        self.assert_validation_error("referenced license file is missing")
        notice = self.root / "sample/LICENSE.txt"
        notice.write_text("Verified upstream terms")
        self.assertEqual(len(self.validator.validate_repository(self.root)), 1)
        notice.unlink()
        notice.symlink_to(self.root / "elsewhere")
        self.assert_validation_error("referenced license file is missing or unsafe")

    def test_rejects_repository_without_skills(self):
        self.assert_validation_error("no SKILL.md files found")

    def test_cli_json_output_and_nonzero_error_exit(self):
        write_skill(self.root, "good", "name: good\ndescription: Good")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)[0]["name"], "good")

        empty = self.root / "empty-repository"
        empty.mkdir()
        failed = subprocess.run(
            [sys.executable, str(SCRIPT), str(empty)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("no SKILL.md files found", failed.stderr)


if __name__ == "__main__":
    unittest.main()
