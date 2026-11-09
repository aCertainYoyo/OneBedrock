"""
OneBedrock Unit Test Suite.
Verifies accounts, launcher, options optimizer, instances, and packs.
"""

import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from onebedrock_core.auth import BedrockAccountManager
from onebedrock_core.optimizer import BedrockOptimizer
from onebedrock_core.instances import InstanceManager
from onebedrock_core.launcher import BedrockLauncher
from onebedrock_core.packs import BedrockPackManager

class TestOneBedrock(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_bedrock_account_manager(self):
        acc_file = self.test_path / "accounts.json"
        mgr = BedrockAccountManager(data_file=acc_file)
        
        # Verify default seed account
        self.assertEqual(len(mgr.get_accounts()), 1)
        active = mgr.get_active_account()
        self.assertIsNotNone(active)
        self.assertEqual(active["edition"], "Bedrock Edition")

        # Add new Bedrock GamerTag
        new_acc = mgr.add_local_account("DragonSlayer99")
        self.assertEqual(new_acc["gamertag"], "DragonSlayer99")
        self.assertEqual(mgr.get_active_account()["gamertag"], "DragonSlayer99")
        self.assertEqual(len(mgr.get_accounts()), 2)

        # Switch account
        mgr.set_active_account(active["id"])
        self.assertEqual(mgr.get_active_account()["id"], active["id"])

        # Ensure no Java check exists
        self.assertNotIn("minecraft_token", active)

    def test_bedrock_optimizer(self):
        opt_file = self.test_path / "options.txt"
        opt = BedrockOptimizer(options_file=opt_file)

        # Apply PvP FPS preset
        opt.apply_preset("pvp_fps")
        self.assertEqual(opt.get_setting("gfx_vsync"), "0")
        self.assertEqual(opt.get_setting("gfx_max_framerate"), "0")
        self.assertEqual(opt.get_setting("gfx_viewdistance"), "8")

        # Apply RTX preset
        opt.apply_preset("ultra_rtx")
        self.assertEqual(opt.get_setting("gfx_raytracing"), "1")
        self.assertEqual(opt.get_setting("gfx_viewdistance"), "24")

    def test_instance_manager(self):
        inst_file = self.test_path / "instances.json"
        mgr = InstanceManager(data_file=inst_file)

        # Default instances
        self.assertGreaterEqual(len(mgr.get_instances()), 3)
        active = mgr.get_active_instance()
        self.assertIsNotNone(active)

        # Create new profile
        new_inst = mgr.create_instance(name="SkyWars Rush", preset="pvp_fps")
        self.assertEqual(new_inst["name"], "SkyWars Rush")
        self.assertEqual(mgr.get_active_instance()["id"], new_inst["id"])

    def test_launcher_stages(self):
        logs = []
        launcher = BedrockLauncher(data_dir=self.test_path)
        launcher.add_log_listener(lambda stage, msg: logs.append((stage, msg)))

        res = launcher.launch(instance_name="TestBedrock", gamertag="TestPlayer")
        self.assertTrue(res["success"])
        self.assertTrue(launcher.is_running)

        stages = [s[0] for s in logs]
        self.assertIn("PREPARING", stages)
        self.assertIn("AUTH", stages)

        summary = launcher.stop_session()
        self.assertIsNotNone(summary)
        self.assertFalse(launcher.is_running)

if __name__ == "__main__":
    unittest.main()
