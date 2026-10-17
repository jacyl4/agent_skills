import importlib.util
import json
import tempfile
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'sync_skills.py'
spec = importlib.util.spec_from_file_location('sync_skills', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyncPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'source'
        self.skill = self.root / 'group' / 'safe'
        self.skill.mkdir(parents=True)
        self.target = self.base / 'target'
        self.target.mkdir()
        self.config = {'sources': {'skills': str(self.root)}, 'mode': 'merge', 'target_naming': 'standard', 'targets': {'codex': {'skills': {'path': str(self.target)}}}}
        self.manifest = [{'name': 'safe', 'path': 'group/safe/SKILL.md'}]

    def test_absent_or_correct_link_passes(self):
        module.check_targets(self.config, self.root, self.manifest)
        (self.target / 'safe').symlink_to(self.skill)
        module.check_targets(self.config, self.root, self.manifest)

    def test_local_directory_blocks(self):
        (self.target / 'safe').mkdir()
        with self.assertRaisesRegex(ValueError, 'collision'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_foreign_link_blocks(self):
        (self.target / 'safe').symlink_to(self.base)
        with self.assertRaisesRegex(ValueError, 'collision'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_broken_unmanaged_link_blocks(self):
        (self.target / 'orphan').symlink_to(self.base / 'missing')
        with self.assertRaisesRegex(ValueError, 'unmanaged broken'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_managed_broken_source_link_can_be_pruned(self):
        (self.target / 'orphan').symlink_to(self.root / 'gone')
        (self.target / '.skillshare-manifest.json').write_text(json.dumps({'managed': {'orphan': 'symlink'}}))
        module.check_targets(self.config, self.root, self.manifest)

    def test_obsolete_managed_external_live_link_blocks(self):
        (self.target / 'obsolete').symlink_to(self.base)
        (self.target / '.skillshare-manifest.json').write_text(json.dumps({'managed': {'obsolete': 'symlink'}}))
        with self.assertRaisesRegex(ValueError, 'obsolete managed'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_obsolete_managed_real_directory_blocks(self):
        (self.target / 'obsolete').mkdir()
        (self.target / '.skillshare-manifest.json').write_text(json.dumps({'managed': {'obsolete': 'copy'}}))
        with self.assertRaisesRegex(ValueError, 'obsolete managed'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_pinned_binary_and_version(self):
        binary = self.base / 'pinned'
        binary.touch()
        entry = self.base / 'entry'
        entry.symlink_to(binary)
        with patch.object(module.subprocess, 'check_output', return_value='skillshare v0.25.13\n'):
            self.assertEqual(module.check_binary(entry, binary), binary)
        with patch.object(module.subprocess, 'check_output', return_value='skillshare v9.0.0\n'):
            with self.assertRaisesRegex(ValueError, 'version'):
                module.check_binary(entry, binary)

    def test_unexpected_binary_path_blocks_before_execution(self):
        binary = self.base / 'wrong'
        binary.touch()
        with patch.object(module.subprocess, 'check_output') as execute:
            with self.assertRaisesRegex(ValueError, 'binary'):
                module.check_binary(binary, self.base / 'expected')
            execute.assert_not_called()

    def test_sync_uses_dedicated_skills_source(self):
        repository = next(parent for parent in SCRIPT.resolve().parents if (parent / '.git').exists())
        self.assertEqual(module.SOURCE_ROOT, repository / 'skills')
        self.assertTrue(module.SOURCE_ROOT.is_dir())

    def _assert_skills_only_command(self, apply):
        # The global config now also owns MCP/hooks/plugins. Ordinary skill
        # maintenance must never silently publish those resource changes.
        self.config.update(mcp={'servers': {}}, hooks={'entries': {}}, plugins={'packages': {}})
        config_dir = self.base / 'config' / 'skillshare'
        config_dir.mkdir(parents=True)
        (config_dir / 'config.yaml').write_text(module.yaml.safe_dump(self.config))
        validator = SimpleNamespace(validate_repository=lambda root: self.manifest,
                                    SkillValidationError=type('FixtureValidationError', (Exception,), {}))
        binary = Path('/reviewed/skillshare')
        argv = ['sync_skills.py'] + (['--apply'] if apply else [])
        with patch.dict(sys.modules, {'validate_skills': validator}), \
             patch.dict(module.os.environ, {'XDG_CONFIG_HOME': str(self.base / 'config')}), \
             patch.object(module, 'SOURCE_ROOT', self.root), \
             patch.object(module, 'check_binary', return_value=binary), \
             patch.object(sys, 'argv', argv), \
             patch.object(module.subprocess, 'run', return_value=SimpleNamespace(returncode=0)) as run:
            self.assertEqual(module.main(), 0)
        expected = [str(binary), 'sync', '-g'] + ([] if apply else ['--dry-run'])
        run.assert_called_once_with(expected, cwd=Path.home(), check=False)
        self.assertNotIn('--all', expected)
        self.assertNotIn('--force', expected)

    def test_default_sync_remains_skills_only_with_other_resource_sources(self):
        self._assert_skills_only_command(apply=False)

    def test_apply_sync_remains_skills_only_with_other_resource_sources(self):
        self._assert_skills_only_command(apply=True)

    def test_wrong_source_blocks(self):
        self.config['sources']['skills'] = str(self.base)
        with self.assertRaisesRegex(ValueError, 'source'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_overlap_and_wrong_mode_block(self):
        self.config['targets']['codex']['skills']['path'] = str(self.root / 'target')
        with self.assertRaisesRegex(ValueError, 'overlap'):
            module.check_targets(self.config, self.root, self.manifest)
        self.config['targets']['codex']['skills']['path'] = str(self.target)
        self.config['mode'] = 'symlink'
        with self.assertRaisesRegex(ValueError, 'merge'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_exact_shared_target_path_aliases_pass(self):
        self.config['targets'].update({
            'universal': {'skills': {'path': str(self.target)}},
            'zed': {'skills': {
                'path': str(self.target),
                'mode': 'merge',
                'target_naming': 'standard',
            }},
        })

        module.check_targets(self.config, self.root, self.manifest)

    def test_shared_target_alias_with_incompatible_settings_blocks(self):
        self.config['targets']['universal'] = {
            'skills': {'path': str(self.target), 'mode': 'copy'},
        }

        with self.assertRaisesRegex(ValueError, 'universal: only reviewed merge mode'):
            module.check_targets(self.config, self.root, self.manifest)

        self.config['targets']['universal']['skills'] = {
            'path': str(self.target),
            'target_naming': 'flat',
        }
        with self.assertRaisesRegex(ValueError, 'universal: this repository requires standard naming'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_disabled_readers_do_not_write_or_check_local_collisions(self):
        # Readers keep their registrations/native resources but use universal's
        # directory. A disabled per-tool path is not a second writer.
        local = self.base / 'reader'
        local.mkdir()
        (local / 'safe').mkdir()
        self.config['targets']['cursor'] = {
            'skills': {'path': str(local), 'enabled': False},
            'agents': {'path': str(self.base / 'agents')},
        }
        module.check_targets(self.config, self.root, self.manifest)
        self.assertFalse(self.config['targets']['cursor']['skills']['enabled'])
        self.assertEqual(self.config['targets']['cursor']['agents']['path'],
                         str(self.base / 'agents'))

    def test_all_writers_disabled_still_blocks(self):
        self.config['targets']['codex']['skills']['enabled'] = False
        with self.assertRaisesRegex(ValueError, 'no enabled targets'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_nested_target_path_still_blocks(self):
        nested = self.target / 'nested'
        nested.mkdir()
        self.config['targets']['universal'] = {'skills': {'path': str(nested)}}

        with self.assertRaisesRegex(ValueError, 'universal: source/target or target/target overlap'):
            module.check_targets(self.config, self.root, self.manifest)

    def test_unmanaged_collision_blocks_with_shared_target_aliases(self):
        self.config['targets']['universal'] = {'skills': {'path': str(self.target)}}
        (self.target / 'safe').mkdir()

        with self.assertRaisesRegex(ValueError, 'unmanaged source-name collision'):
            module.check_targets(self.config, self.root, self.manifest)


if __name__ == '__main__':
    unittest.main()
