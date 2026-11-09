# OneBedrock 🎮

<div align="center">

![OneBedrock Banner](https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&auto=format&fit=crop&q=80)

**The all-in-one Minecraft Bedrock Edition client and launcher.**  
*Inspired by Polyfrost's OneClient — Reimagined exclusively for Bedrock Edition.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue)](https://microsoft.com)
[![Bedrock Edition](https://img.shields.io/badge/Minecraft-Bedrock%20Edition-green.svg)](https://minecraft.net)
[![Java Not Required](https://img.shields.io/badge/Java%20Account-NOT%20REQUIRED-brightgreen.svg)]()

</div>

---

## ✨ Features

- **PolyGlass Design System**: A 1:1 faithful replica of Polyfrost OneClient's iconic frosted glass dark theme (`#11171C`), animated pills, glowing buttons, and crisp typography.
- **Bedrock-Only Authentication**: **Zero Java Edition account checks**. Sign in directly using your Microsoft / Xbox Live account or create offline Bedrock GamerTag profiles with instant switching.
- **Uncapped FPS & VSync Optimizer**: Direct management of Bedrock's `options.txt` to unlock uncapped framerate, disable VSync, tune render distance, and activate hardware Ray Tracing (RTX).
- **Bedrock Profiles ("Clusters")**: Configure multiple independent Bedrock setups:
  - ⚡ *PvP Competitive* (Uncapped framerate, minimal particle latency for The Hive & NetherGames)
  - ✨ *RTX Shaders & Graphics* (Deferred PBR Ray Tracing, 24+ chunk view distance)
  - 🌿 *Vanilla Survival* (Clean balanced gameplay)
- **3D Interactive Wardrobe**: Real-time 3D character viewer with orbit rotation, walking animation toggle, Steve/Alex models, custom skin upload, and cape customizer.
- **Curated Discover Catalog**: One-click connect to top Bedrock servers (The Hive, NetherGames, CubeCraft, Galaxite, Lifeboat) and browser for Bedrock add-ons, shaders, and UI packs.
- **Live Launch Telemetry**: Real-time launch console monitoring Bedrock stages, options synchronization, and game status.

---

## 🚀 Quick Start

### Prerequisites
- Windows 10 or 11
- Python 3.10+ (Python 3.15 supported)
- Minecraft Bedrock Edition (installed via Microsoft Store / Xbox App)

### Running OneBedrock

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aCertainYoyo/OneBedrock.git
   cd OneBedrock
   ```

2. **Run OneBedrock**:
   - Double-click `run.bat` or `run.ps1`
   - Or run directly from terminal:
     ```bash
     python main.py
     ```

OneBedrock will launch as a sleek native desktop application via Edge WebView2.

---

## 🛠️ Architecture

```
OneBedrock/
├── main.py                    # Application entry point & native desktop window manager
├── run.bat                    # One-click Windows launch batch script
├── run.ps1                    # One-click Windows PowerShell script
├── onebedrock_core/           # Backend core engine
│   ├── auth.py                # Bedrock & Xbox Live account manager (No Java check)
│   ├── launcher.py            # Bedrock UWP protocol & executable launch manager
│   ├── optimizer.py           # options.txt FPS & performance optimizer
│   ├── instances.py           # Bedrock profile & cluster manager
│   ├── packs.py               # .mcpack, .mcaddon, and .mcworld extractor
│   ├── browser_service.py     # Featured servers, addons & Bedrock news
│   └── server.py              # Local REST API server
├── onebedrock_app/            # PolyGlass frontend UI
│   ├── index.html             # Single-page launcher interface
│   ├── css/style.css          # PolyGlass Dark theme & animations
│   ├── js/app.js              # State management & Bedrock controls
│   └── js/wardrobe.js         # Interactive 3D Bedrock skin viewer
└── tests/                     # Automated test suite
    └── test_onebedrock.py     # Core engine tests
```

---

## 🧪 Testing

Run the automated test suite:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📄 License & Credits

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.

Inspired by the design and UX of [Polyfrost OneClient](https://github.com/Polyfrost/OneLauncher). Minecraft is a registered trademark of Mojang Synergies AB / Microsoft. OneBedrock is not affiliated with Mojang or Microsoft.
