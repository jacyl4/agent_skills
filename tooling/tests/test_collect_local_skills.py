import importlib.util
from pathlib import Path
import tempfile
import unittest
import yaml

spec = importlib.util.spec_from_file_location("collector", Path(__file__).parents[1] / "scripts/collect_local_skills.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "native/sample"
        self.source.mkdir(parents=True)
        self.text = "---\nname: sample\ndescription: Useful\n---\n\nBody\n"
        (self.source / "SKILL.md").write_text(self.text)
        (self.source / "run.sh").write_text("#!/bin/sh\nexit 0\n")
        (self.source / "run.sh").chmod(0o755)
        self.destination = self.root / "source/group/sample"
        self.expected = collector.fingerprint(self.source)

    def test_preserves_payload_modes_and_original(self):
        collector.copy_reviewed(self.source, self.destination, self.expected)
        self.assertEqual(collector.fingerprint(self.destination), self.expected)
        self.assertEqual(collector.fingerprint(self.source), self.expected)
        self.assertEqual((self.destination / "run.sh").stat().st_mode & 0o777, 0o755)

    def test_never_overwrites_existing_or_broken_destination(self):
        self.destination.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "already exists"):
            collector.copy_reviewed(self.source, self.destination, self.expected)
        self.destination.rmdir()
        self.destination.symlink_to(self.root / "missing")
        with self.assertRaisesRegex(ValueError, "already exists"):
            collector.copy_reviewed(self.source, self.destination, self.expected)

    def test_source_change_blocks_before_copy(self):
        (self.source / "SKILL.md").write_text(self.text + "Changed")
        with self.assertRaisesRegex(ValueError, "source changed"):
            collector.copy_reviewed(self.source, self.destination, self.expected)
        self.assertFalse(self.destination.exists())

    def test_links_require_review_and_do_not_get_dereferenced(self):
        (self.source / "escape").symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, "symlink"):
            collector.fingerprint(self.source)

    def test_target_scope_preserves_body_and_source(self):
        collector.copy_reviewed(self.source, self.destination, self.expected, ("hermes",))
        result = (self.destination / "SKILL.md").read_text().split("---", 2)
        self.assertEqual(yaml.safe_load(result[1])["metadata"]["targets"], ["hermes"])
        self.assertEqual(result[2], self.text.split("---", 2)[2])
        self.assertEqual((self.source / "SKILL.md").read_text(), self.text)

    def test_wrong_canonical_name_and_scope_conflict_block(self):
        with self.assertRaisesRegex(ValueError, "frontmatter name"):
            collector.copy_reviewed(self.source, self.root / "wrong", self.expected)
        (self.source / "SKILL.md").write_text("---\nname: sample\ndescription: Useful\nmetadata:\n  targets: [codex]\n---\nBody")
        with self.assertRaisesRegex(ValueError, "scope conflict"):
            collector.copy_reviewed(self.source, self.destination, collector.fingerprint(self.source), ("hermes",))
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
