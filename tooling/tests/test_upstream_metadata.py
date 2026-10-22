"""Regression checks for native Skillshare source associations (not an updater)."""
import json
from pathlib import Path, PurePosixPath
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'skills'


class UpstreamMetadataTests(unittest.TestCase):
    def setUp(self):
        self.metadata = json.loads((SOURCE / '.metadata.json').read_text())

    def test_native_schema_and_full_source_paths(self):
        self.assertEqual(self.metadata['version'], 1)
        self.assertTrue(self.metadata['entries'])
        # A source may contain only subdirectory installs; each entry must still
        # use the native type appropriate to its own subdir below.
        self.assertLessEqual({e['type'] for e in self.metadata['entries'].values()}, {'github', 'github-subdir'})
        for path, entry in self.metadata['entries'].items():
            with self.subTest(path=path):
                self.assertFalse(PurePosixPath(path).is_absolute())
                self.assertNotIn('..', PurePosixPath(path).parts)
                self.assertTrue((SOURCE / path / 'SKILL.md').is_file())
                self.assertEqual(entry['group'], str(PurePosixPath(path).parent))
                self.assertEqual(entry['type'], 'github-subdir' if entry.get('subdir') else 'github')
                self.assertFalse(entry.get('tracked', False))

    def test_sources_use_exact_github_repository_and_subdir(self):
        for path, entry in self.metadata['entries'].items():
            with self.subTest(path=path):
                self.assertRegex(entry['repo_url'], r'^https://github\.com/[\w.-]+/[\w.-]+$')
                subdir = entry.get('subdir', '')
                self.assertFalse(PurePosixPath(subdir).is_absolute())
                self.assertNotIn('..', PurePosixPath(subdir).parts)
                # Native updates add .git to clone URLs, not to source URLs.
                repository = entry['repo_url'].removesuffix('.git')
                self.assertEqual(entry['source'], repository + ('/' + subdir if subdir else ''))
                # Follow the upstream default branch, not a pinned historical SHA.
                self.assertNotIn('/tree/', entry['source'])

    def test_baseline_hashes_are_skill_relative_sha256(self):
        for entry in self.metadata['entries'].values():
            self.assertIn('SKILL.md', entry['file_hashes'])
            for path, digest in entry['file_hashes'].items():
                self.assertFalse(PurePosixPath(path).is_absolute())
                self.assertNotIn('..', PurePosixPath(path).parts)
                self.assertRegex(digest, r'^sha256:[0-9a-f]{64}$')
            if entry.get('commit'):
                self.assertRegex(entry['commit'], r'^[0-9a-f]{40}$')
                self.assertEqual(entry['version'], entry['commit'][:7])

    def test_officecli_uses_actual_skill_subdir_not_entire_repository(self):
        entry = self.metadata['entries']['documents/officecli']
        self.assertEqual(entry['type'], 'github-subdir')
        self.assertEqual(entry['subdir'], 'skills/officecli')
        self.assertFalse((SOURCE / 'documents/officecli/.git').exists())
        self.assertEqual(
            list((SOURCE / 'documents/officecli').rglob('SKILL.md')),
            [SOURCE / 'documents/officecli/SKILL.md'],
        )

    def test_native_upstream_baselines_include_verified_added_notices(self):
        notices = json.loads((SOURCE / '.license-manifest.json').read_text())['files']
        for notice in notices:
            path = PurePosixPath(notice['path'])
            entry = self.metadata['entries'].get(str(path.parent))
            if entry:
                with self.subTest(path=notice['path']):
                    self.assertEqual(entry['file_hashes'][path.name],
                                     'sha256:' + notice['sha256'])

    def test_local_wrappers_are_not_bound_to_product_repositories(self):
        for path in ('automation/local/graphify', 'writing/talk-normal'):
            self.assertNotIn(path, self.metadata['entries'])

    def test_legacy_taste_has_its_own_upstream_directory(self):
        entries = self.metadata['entries']
        current = entries['frontend/design/design-taste-frontend']
        legacy = entries['frontend/design/design-taste-frontend-v1']
        self.assertEqual(current['subdir'], 'skills/taste-skill')
        self.assertEqual(legacy['subdir'], 'skills/taste-skill-v1')
        self.assertEqual(current['repo_url'].removesuffix('.git'),
                         legacy['repo_url'].removesuffix('.git'))


if __name__ == '__main__':
    unittest.main()
