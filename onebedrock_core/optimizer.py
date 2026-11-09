"""
OneBedrock Performance & Config Optimizer.
Manages Minecraft Bedrock Edition's options.txt to unlock uncapped FPS,
disable VSync, customize view distances, and apply performance presets.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_OPTIONS_PATH = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Packages"
    / "Microsoft.MinecraftUWP_8wekyb3d8bbwe"
    / "LocalState"
    / "games"
    / "com.mojang"
    / "minecraftpe"
    / "options.txt"
)

PRESETS = {
    "pvp_fps": {
        "name": "PvP Maximum FPS",
        "description": "Uncapped framerate, disabled VSync, low latency, reduced particle effects for maximum combat performance.",
        "settings": {
            "gfx_vsync": "0",
            "gfx_max_framerate": "0",
            "gfx_viewdistance": "8",
            "gfx_fancyskies": "0",
            "gfx_renderclouds": "0",
            "gfx_smoothlighting": "0",
            "gfx_particles": "0",
            "gfx_msaa": "1",
            "gfx_texel_aa": "0",
            "gfx_raytracing": "0"
        }
    },
    "balanced": {
        "name": "Balanced Performance",
        "description": "Standard optimized gameplay with smooth 120+ FPS, clean graphics, and 16 chunk render distance.",
        "settings": {
            "gfx_vsync": "0",
            "gfx_max_framerate": "165",
            "gfx_viewdistance": "16",
            "gfx_fancyskies": "1",
            "gfx_renderclouds": "1",
            "gfx_smoothlighting": "1",
            "gfx_particles": "1",
            "gfx_msaa": "2",
            "gfx_texel_aa": "0",
            "gfx_raytracing": "0"
        }
    },
    "ultra_rtx": {
        "name": "RTX Ultra Cinematic",
        "description": "Enables hardware Ray Tracing, PBR reflections, 28 chunk render distance, and maximum visual fidelity.",
        "settings": {
            "gfx_vsync": "1",
            "gfx_max_framerate": "144",
            "gfx_viewdistance": "24",
            "gfx_fancyskies": "1",
            "gfx_renderclouds": "1",
            "gfx_smoothlighting": "1",
            "gfx_particles": "2",
            "gfx_msaa": "4",
            "gfx_texel_aa": "1",
            "gfx_raytracing": "1"
        }
    }
}

class BedrockOptimizer:
    def __init__(self, options_file: Optional[Path] = None):
        self.options_file = options_file or DEFAULT_OPTIONS_PATH
        self.cached_options: Dict[str, str] = {}
        self.load_options()

    def load_options(self) -> Dict[str, str]:
        self.cached_options = {}
        if self.options_file.exists():
            try:
                with open(self.options_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if ":" in line:
                            k, v = line.split(":", 1)
                            self.cached_options[k.strip()] = v.strip()
            except Exception:
                pass
        return self.cached_options

    def save_options(self) -> bool:
        try:
            self.options_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.options_file, "w", encoding="utf-8") as f:
                for k, v in sorted(self.cached_options.items()):
                    f.write(f"{k}:{v}\n")
            return True
        except Exception:
            return False

    def get_setting(self, key: str, default: str = "") -> str:
        return self.cached_options.get(key, default)

    def set_setting(self, key: str, value: Any):
        self.cached_options[key] = str(value)
        self.save_options()

    def apply_preset(self, preset_id: str) -> bool:
        if preset_id not in PRESETS:
            return False
        preset = PRESETS[preset_id]
        for k, v in preset["settings"].items():
            self.cached_options[k] = v
        self.save_options()
        return True

    def get_presets(self) -> Dict[str, Any]:
        return PRESETS

    def get_current_metrics(self) -> Dict[str, Any]:
        return {
            "vsync": self.get_setting("gfx_vsync", "1") == "1",
            "max_fps": self.get_setting("gfx_max_framerate", "0"),
            "render_distance": self.get_setting("gfx_viewdistance", "12"),
            "raytracing": self.get_setting("gfx_raytracing", "0") == "1",
            "fancy_skies": self.get_setting("gfx_fancyskies", "1") == "1",
            "smooth_lighting": self.get_setting("gfx_smoothlighting", "1") == "1",
            "msaa": self.get_setting("gfx_msaa", "2"),
            "options_file_exists": self.options_file.exists(),
            "options_path": str(self.options_file)
        }
