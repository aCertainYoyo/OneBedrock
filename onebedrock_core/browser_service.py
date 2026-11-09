"""
OneBedrock Discover & Browser Catalog.
Provides curated Bedrock Add-ons, Texture Packs, Shaders, UI Overhauls,
and Featured Multiplayer Bedrock Servers with live connect capabilities.
"""

from typing import List, Dict

FEATURED_SERVERS = [
    {
        "id": "hive",
        "name": "The Hive",
        "ip": "geo.hivebedrock.network",
        "port": 19132,
        "description": "The largest Bedrock server! BedWars, SkyWars, Hide and Seek, Survival Games, and Murder Mystery.",
        "players": "28,490 online",
        "tag": "Featured",
        "icon": "https://api.dicebear.com/7.x/identicon/svg?seed=TheHive"
    },
    {
        "id": "nethergames",
        "name": "NetherGames Network",
        "ip": "play.nethergames.org",
        "port": 19132,
        "description": "Premier competitive Bedrock network with fast matchmaking, Duels, Bedwars, Conquest, and Factions.",
        "players": "4,120 online",
        "tag": "Competitive PvP",
        "icon": "https://api.dicebear.com/7.x/identicon/svg?seed=NetherGames"
    },
    {
        "id": "cubecraft",
        "name": "CubeCraft Games",
        "ip": "play.cubecraft.net",
        "port": 19132,
        "description": "Official Bedrock featured server with EggWars, Lucky Islands, Parkour, and Tower Defence.",
        "players": "12,850 online",
        "tag": "Featured",
        "icon": "https://api.dicebear.com/7.x/identicon/svg?seed=CubeCraft"
    },
    {
        "id": "galaxite",
        "name": "Galaxite",
        "ip": "play.galaxite.net",
        "port": 19132,
        "description": "Futuristic alien parkour, Hyper Racers, Core Wars, and Chronos custom game modes.",
        "players": "3,400 online",
        "tag": "Unique Games",
        "icon": "https://api.dicebear.com/7.x/identicon/svg?seed=Galaxite"
    },
    {
        "id": "lifeboat",
        "name": "Lifeboat Network",
        "ip": "play.lbsg.net",
        "port": 19132,
        "description": "Classic Bedrock multiplayer with Prison, Skyblock, City Life roleplay, and Survival.",
        "players": "5,620 online",
        "tag": "RPG & Survival",
        "icon": "https://api.dicebear.com/7.x/identicon/svg?seed=Lifeboat"
    }
]

FEATURED_PACKS = [
    {
        "id": "pack-fps-boost",
        "name": "Bedrock FPS Optimizer HUD",
        "category": "Performance",
        "author": "Polyfrost & BedrockDev",
        "downloads": "420K",
        "rating": "4.9",
        "description": "Optimizes Bedrock particle rendering, disables unused particle emitters, and displays dynamic FPS + ping counter.",
        "type": "Resource Pack",
        "version": "1.21+",
        "installed": True
    },
    {
        "id": "pack-tyel-ui",
        "name": "Ty-el PolyGlass UI for Bedrock",
        "category": "Interface",
        "author": "Ty-el & Polyfrost Team",
        "downloads": "890K",
        "rating": "5.0",
        "description": "Overhauls Bedrock's default interface to match OneClient's sleek PolyGlass frosted glass design with dark inventory.",
        "type": "UI Pack",
        "version": "1.21+",
        "installed": True
    },
    {
        "id": "pack-java-aspects",
        "name": "Java Aspects 1.21",
        "category": "Parity",
        "author": "AgentMindStorm",
        "downloads": "1.2M",
        "rating": "4.8",
        "description": "Brings authentic Java Edition combat sounds, death animations, block hit particles, and GUI details to Bedrock.",
        "type": "Resource Pack",
        "version": "1.21+",
        "installed": False
    },
    {
        "id": "pack-kellys-rtx",
        "name": "Kelly's RTX Vanilla Conversion",
        "category": "Shaders",
        "author": "Kelly",
        "downloads": "650K",
        "rating": "4.9",
        "description": "Pure vanilla-accurate PBR normal maps and height maps for Bedrock hardware Ray Tracing and Deferred Lighting.",
        "type": "PBR Shaders",
        "version": "1.21+",
        "installed": False
    },
    {
        "id": "pack-faithful-32",
        "name": "Faithful 32x Bedrock",
        "category": "Textures",
        "author": "Faithful Team",
        "downloads": "3.4M",
        "rating": "4.9",
        "description": "The quintessential doubled-resolution Minecraft texture pack, keeping vanilla style in crisp 32x32.",
        "type": "Texture Pack",
        "version": "1.21+",
        "installed": False
    },
    {
        "id": "pack-actions-stuff",
        "name": "Actions & Stuff Animations",
        "category": "Animations",
        "author": "AnimationWorks",
        "downloads": "2.1M",
        "rating": "5.0",
        "description": "Incredible dynamic player animations: running, sprinting, swimming, sword combat, and bow aiming animations.",
        "type": "Resource Pack",
        "version": "1.21+",
        "installed": False
    }
]

BEDROCK_NEWS = [
    {
        "id": "news-1",
        "title": "Minecraft Bedrock 1.21.60 Update Released",
        "date": "Today",
        "category": "Changelog",
        "summary": "Fixes for render distance crashing on Windows 11, improvements to Deferred Technical Preview lighting, and new experimental bundles."
    },
    {
        "id": "news-2",
        "title": "OneBedrock v1.0.0 Public Launch",
        "date": "Yesterday",
        "category": "OneBedrock",
        "summary": "Welcome to OneBedrock! The open-source launcher designed exclusively for Bedrock Edition players. No Java account required."
    },
    {
        "id": "news-3",
        "title": "Deferred Lighting & PBR Shaders on Bedrock",
        "date": "3 days ago",
        "category": "Guide",
        "summary": "How to enable high-end shaders on Windows 10/11 using OneBedrock's RTX preset and sub-chunk optimizations."
    }
]

def get_servers() -> List[Dict]:
    return FEATURED_SERVERS

def get_packs() -> List[Dict]:
    return FEATURED_PACKS

def get_news() -> List[Dict]:
    return BEDROCK_NEWS
