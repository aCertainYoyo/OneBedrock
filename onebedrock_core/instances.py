"""
OneBedrock Instance ("Cluster") Management Module.
Manages isolated Bedrock profiles, performance presets, active addons, and playtime.
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

CONFIG_DIR = Path.home() / ".onebedrock"
INSTANCES_FILE = CONFIG_DIR / "instances.json"

DEFAULT_INSTANCES = [
    {
        "id": "bedrock-pvp-perf",
        "name": "PvP Competitive",
        "version": "Bedrock 1.21.60",
        "tag": "Max FPS",
        "icon": "swords",
        "preset": "pvp_fps",
        "playtime_minutes": 142,
        "last_played": time.time() - 3600 * 2,
        "is_default": True,
        "description": "Uncapped FPS, disabled VSync, low latency, tuned for The Hive and NetherGames."
    },
    {
        "id": "bedrock-rtx-ultra",
        "name": "RTX Shaders & Graphics",
        "version": "Bedrock 1.21.60",
        "tag": "Ray Tracing",
        "icon": "sparkles",
        "preset": "ultra_rtx",
        "playtime_minutes": 85,
        "last_played": time.time() - 3600 * 24,
        "is_default": False,
        "description": "Full hardware Ray Tracing, PBR textures, 24-chunk distance, cinematic lighting."
    },
    {
        "id": "bedrock-vanilla",
        "name": "Vanilla Survival",
        "version": "Bedrock 1.21.60",
        "tag": "Clean",
        "icon": "compass",
        "preset": "balanced",
        "playtime_minutes": 310,
        "last_played": time.time() - 3600 * 48,
        "is_default": False,
        "description": "Balanced vanilla settings with smooth 120 FPS and standard resource packs."
    }
]

class InstanceManager:
    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or INSTANCES_FILE
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.instances: List[Dict] = []
        self.active_instance_id: Optional[str] = None
        self._load()

    def _load(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.instances = data.get("instances", [])
                    self.active_instance_id = data.get("active_instance_id")
            except Exception:
                self.instances = []
                self.active_instance_id = None

        if not self.instances:
            self.instances = list(DEFAULT_INSTANCES)
            self.active_instance_id = self.instances[0]["id"]
            self._save()

    def _save(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump({
                "instances": self.instances,
                "active_instance_id": self.active_instance_id
            }, f, indent=2)

    def get_instances(self) -> List[Dict]:
        return self.instances

    def get_active_instance(self) -> Optional[Dict]:
        for inst in self.instances:
            if inst["id"] == self.active_instance_id:
                return inst
        return self.instances[0] if self.instances else None

    def set_active_instance(self, instance_id: str) -> bool:
        for inst in self.instances:
            if inst["id"] == instance_id:
                self.active_instance_id = instance_id
                self._save()
                return True
        return False

    def create_instance(self, name: str, version: str = "Bedrock 1.21.60", preset: str = "balanced", tag: str = "Custom") -> Dict:
        new_inst = {
            "id": f"inst-{uuid.uuid4().hex[:8]}",
            "name": name,
            "version": version,
            "tag": tag,
            "icon": "box",
            "preset": preset,
            "playtime_minutes": 0,
            "last_played": time.time(),
            "is_default": False,
            "description": f"Custom Bedrock profile configured with {preset} performance preset."
        }
        self.instances.append(new_inst)
        self.active_instance_id = new_inst["id"]
        self._save()
        return new_inst

    def update_instance(self, instance_id: str, updates: Dict) -> Optional[Dict]:
        for inst in self.instances:
            if inst["id"] == instance_id:
                inst.update(updates)
                self._save()
                return inst
        return None

    def delete_instance(self, instance_id: str) -> bool:
        orig = len(self.instances)
        self.instances = [i for i in self.instances if i["id"] != instance_id]
        if self.active_instance_id == instance_id:
            self.active_instance_id = self.instances[0]["id"] if self.instances else None
        self._save()
        return len(self.instances) < orig
