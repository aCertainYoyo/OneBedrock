"""
OneBedrock Addon & Pack Management Module.
Imports, organizes, and inspects Bedrock .mcpack, .mcaddon, and .mcworld archives,
managing the com.mojang resource and behavior pack directories.
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_MOJANG_ROOT = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Packages"
    / "Microsoft.MinecraftUWP_8wekyb3d8bbwe"
    / "LocalState"
    / "games"
    / "com.mojang"
)

class BedrockPackManager:
    def __init__(self, mojang_root: Optional[Path] = None):
        self.mojang_root = mojang_root or DEFAULT_MOJANG_ROOT
        self.resource_packs_dir = self.mojang_root / "resource_packs"
        self.behavior_packs_dir = self.mojang_root / "behavior_packs"
        self.worlds_dir = self.mojang_root / "minecraftWorlds"
        self.skin_packs_dir = self.mojang_root / "skin_packs"

        # Ensure directories exist
        for d in [self.resource_packs_dir, self.behavior_packs_dir, self.worlds_dir, self.skin_packs_dir]:
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

    def _read_manifest(self, folder: Path) -> Optional[Dict]:
        manifest_file = folder / "manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def list_resource_packs(self) -> List[Dict]:
        packs = []
        if not self.resource_packs_dir.exists():
            return packs

        for item in self.resource_packs_dir.iterdir():
            if item.is_dir():
                manifest = self._read_manifest(item)
                header = manifest.get("header", {}) if manifest else {}
                pack_name = header.get("name", item.name)
                description = header.get("description", "Bedrock Resource Pack")
                version = ".".join(str(v) for v in header.get("version", [1, 0, 0]))
                
                # Check for pack icon
                icon_path = item / "pack_icon.png"
                packs.append({
                    "id": header.get("uuid", item.name),
                    "folder_name": item.name,
                    "name": pack_name,
                    "description": description,
                    "version": version,
                    "type": "resource",
                    "has_icon": icon_path.exists(),
                    "path": str(item)
                })
        return packs

    def list_behavior_packs(self) -> List[Dict]:
        packs = []
        if not self.behavior_packs_dir.exists():
            return packs

        for item in self.behavior_packs_dir.iterdir():
            if item.is_dir():
                manifest = self._read_manifest(item)
                header = manifest.get("header", {}) if manifest else {}
                packs.append({
                    "id": header.get("uuid", item.name),
                    "folder_name": item.name,
                    "name": header.get("name", item.name),
                    "description": header.get("description", "Bedrock Behavior Pack"),
                    "version": ".".join(str(v) for v in header.get("version", [1, 0, 0])),
                    "type": "behavior",
                    "path": str(item)
                })
        return packs

    def list_worlds(self) -> List[Dict]:
        worlds = []
        if not self.worlds_dir.exists():
            return worlds

        for item in self.worlds_dir.iterdir():
            if item.is_dir():
                world_name = item.name
                level_name_file = item / "levelname.txt"
                if level_name_file.exists():
                    try:
                        with open(level_name_file, "r", encoding="utf-8") as f:
                            world_name = f.read().strip()
                    except Exception:
                        pass
                
                icon_file = item / "world_icon.jpeg"
                worlds.append({
                    "folder_name": item.name,
                    "name": world_name,
                    "has_icon": icon_file.exists(),
                    "path": str(item)
                })
        return worlds

    def import_pack(self, file_path: str) -> Dict:
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": "File not found"}

        suffix = path.suffix.lower()
        if suffix in [".mcpack", ".zip"]:
            # Inspect manifest inside zip
            try:
                with zipfile.ZipFile(path, "r") as z:
                    target_dir = self.resource_packs_dir
                    if "manifest.json" in z.namelist():
                        data = json.loads(z.read("manifest.json").decode("utf-8"))
                        modules = data.get("modules", [])
                        for mod in modules:
                            if mod.get("type") in ["data", "script"]:
                                target_dir = self.behavior_packs_dir
                                break
                    dest = target_dir / path.stem
                    dest.mkdir(parents=True, exist_ok=True)
                    z.extractall(dest)
                return {"success": True, "target": str(dest)}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif suffix == ".mcworld":
            try:
                dest = self.worlds_dir / path.stem
                dest.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(path, "r") as z:
                    z.extractall(dest)
                return {"success": True, "target": str(dest)}
            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "error": f"Unsupported file type: {suffix}"}
