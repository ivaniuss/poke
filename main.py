"""
main.py
Extracts data from the Pokémon Auto Chess repo and generates a JSON knowledge base.

Usage:
    python main.py --repo-path ./pokemonAutoChess

Output:
    knowledge_base/pokemon.json
    knowledge_base/items.json
    knowledge_base/synergies.json
    knowledge_base/knowledge_base.json
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

PARSE_ERRORS: list[str] = []

# ─── Stat enum → output name mapping ─────────────────────────────────────────
STAT_MAP = {
    "AP":          "ap",
    "ATK":         "atk",
    "DEF":         "def",
    "SPE_DEF":     "speDef",
    "SPEED":       "speed",
    "PP":          "pp",
    "CRIT_CHANCE": "critChance",
    "CRIT_POWER":  "critPower",
    "SHIELD":      "shield",
    "LUCK":        "luck",
    "HP":          "hp",
    "RANGE":       "range",
}

# ─── Cost by rarity ──────────────────────────────────────────────────────────
RARITY_COST = {
    "COMMON":    1,
    "UNCOMMON":  2,
    "RARE":      3,
    "EPIC":      4,
    "LEGENDARY": 5,
    "UNIQUE":    None,
    "SPECIAL":   None,
    "HATCH":     None,
}

# ─── Utilities ───────────────────────────────────────────────────────────────

def read_file(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        PARSE_ERRORS.append(f"File not found: {path}")
        return None

def strip_ts_comments(text: str) -> str:
    # Remove /* ... */ and // ... comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text

def extract_block(text: str, keyword: str) -> str | None:
    """
    Finds the block of an 'export const KEYWORD = { ... }'
    ignoring the type annotation which may have its own braces.
    """
    # Look for the keyword and then the '= {' that comes AFTER (skipping the type annotation)
    idx = text.find(keyword)
    if idx == -1:
        PARSE_ERRORS.append(f"Block not found: {keyword}")
        return None

    rest = text[idx:]
    m = re.search(r"=\s*\{", rest)
    if not m:
        PARSE_ERRORS.append(f"Could not find '= {{' for: {keyword}")
        return None

    # Absolute position of the value's opening brace
    start = idx + m.end() - 1

    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    PARSE_ERRORS.append(f"Unclosed block: {keyword}")
    return None


# ─── Parser: pokemons-data.csv ────────────────────────────────────────────────

def parse_pokemon_csv(repo: Path) -> dict:
    path = repo / "app/models/precomputed/pokemons-data.csv"
    content = read_file(path)
    if content is None:
        return {}

    pokemon = {}
    reader = csv.DictReader(content.splitlines())

    for row in reader:
        name = row["Name"].strip()
        if not name:
            continue

        # Types: Type 1..4 columns, filter empty ones
        types = [
            row[f"Type {i}"].strip()
            for i in range(1, 5)
            if row.get(f"Type {i}", "").strip()
        ]

        # Rarity and cost
        rarity = row.get("Category", "").strip().upper()
        cost = RARITY_COST.get(rarity)

        # Evolution: if Tier < Nb stages → there is an evolution (we don't have the direct name in the CSV)
        # It can be enriched later by crossing through Family + Tier+1
        tier = int(row.get("Tier", 1) or 1)
        nb_stages = int(row.get("Nb stages", 1) or 1)

        pokemon[name] = {
            "name":       name,
            "index":      row.get("Index", "").strip(),
            "rarity":     rarity,
            "cost":       cost,
            "hp":         _int(row.get("HP")),
            "atk":        _int(row.get("Attack")),
            "speed":      _int(row.get("Speed")),
            "def":        _int(row.get("Defense")),
            "speDef":     _int(row.get("Special Defense")),
            "range":      _int(row.get("Attack Range")),
            "maxPP":      _int(row.get("Max PP")),
            "skill":      row.get("Ability", "").strip(),
            "types":      types,
            "stars":      tier,
            "nbStages":   nb_stages,
            "family":     row.get("Family", "").strip(),
            "additional": row.get("Additional pick", "false").strip().lower() == "true",
            "regional":   row.get("Regional", "false").strip().lower() == "true",
            "variant":    row.get("Variant", "false").strip().lower() == "true",
        }

    # Second pass: resolve evolutions within the same family
    family_by_name: dict[str, list] = {}
    for p in pokemon.values():
        fam = p["family"]
        family_by_name.setdefault(fam, []).append(p)

    for members in family_by_name.values():
        members.sort(key=lambda p: p["stars"])
        for i, p in enumerate(members):
            if i + 1 < len(members):
                p["evolution"] = members[i + 1]["name"]
            else:
                p["evolution"] = None

    return pokemon

def _int(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

# ─── Parser: config/game/items.ts → ItemStats ─────────────────────────────────

def parse_items_stats(repo: Path) -> dict:
    path = repo / "app/config/game/items.ts"
    raw = read_file(path)
    if raw is None:
        return {}

    text = strip_ts_comments(raw)
    block = extract_block(text, "ItemStats")
    if block is None:
        return {}

    items: dict[str, dict] = {}

    # Each entry has the form:
    #   [Item.XXXX]: { [Stat.YYY]: 10, [Stat.ZZZ]: -5 },
    entry_pattern = re.compile(
        r"\[Item\.(\w+)\]\s*:\s*(\{[^}]*\})",
        re.DOTALL,
    )
    stat_pattern = re.compile(r"\[Stat\.(\w+)\]\s*:\s*(-?\d+)")

    for m in entry_pattern.finditer(block):
        item_name = m.group(1)
        stats_block = m.group(2)

        stats = {v: 0 for v in STAT_MAP.values()}  # default to 0
        for sm in stat_pattern.finditer(stats_block):
            stat_key = sm.group(1)
            stat_val = int(sm.group(2))
            mapped = STAT_MAP.get(stat_key)
            if mapped:
                stats[mapped] = stat_val
            else:
                PARSE_ERRORS.append(f"Unknown stat in items: {stat_key}")

        items[item_name] = {"name": item_name, "stats": stats}

    return items


# ─── Parser: models/effects.ts → SynergyEffects ───────────────────────────────

def parse_synergy_effects(repo: Path) -> dict:
    path = repo / "app/models/effects.ts"
    raw = read_file(path)
    if raw is None:
        return {}

    text = strip_ts_comments(raw)
    block = extract_block(text, "SynergyEffects")
    if block is None:
        return {}

    effects: dict[str, list[str]] = {}

    # Each entry: [Synergy.XXXX]: [ EffectEnum.A, EffectEnum.B, ... ]
    entry_pattern = re.compile(
        r"\[Synergy\.(\w+)\]\s*:\s*\[([^\]]*)\]",
        re.DOTALL,
    )
    effect_pattern = re.compile(r"EffectEnum\.(\w+)")

    for m in entry_pattern.finditer(block):
        synergy = m.group(1)
        inner = m.group(2)
        effect_names = effect_pattern.findall(inner)
        effects[synergy] = effect_names

    return effects


# ─── Parser: config/game/synergies.ts → SynergyTriggers ──────────────────────

def parse_synergy_triggers(repo: Path) -> dict:
    path = repo / "app/config/game/synergies.ts"
    raw = read_file(path)
    if raw is None:
        return {}

    text = strip_ts_comments(raw)
    block = extract_block(text, "SynergyTriggers")
    if block is None:
        return {}

    triggers: dict[str, list[int]] = {}

    # Each entry: [Synergy.XXXX]: [2, 4, 6, 8]
    entry_pattern = re.compile(
        r"\[Synergy\.(\w+)\]\s*:\s*\[([^\]]*)\]"
    )
    for m in entry_pattern.finditer(block):
        synergy = m.group(1)
        nums = [int(n.strip()) for n in m.group(2).split(",") if n.strip()]
        triggers[synergy] = nums

    return triggers


# ─── Enrich synergies with Pokémon list ───────────────────────────────────────

def build_synergies(triggers: dict, effects: dict, pokemon: dict) -> dict:
    synergies: dict[str, dict] = {}

    all_synergies = set(triggers.keys()) | set(effects.keys())
    for synergy in all_synergies:
        thresholds = triggers.get(synergy, [])
        effect_list = effects.get(synergy, [])

        # Align effects with thresholds (one effect per threshold)
        effects_per_level = []
        for i, _ in enumerate(thresholds):
            if i < len(effect_list):
                effects_per_level.append(effect_list[i])
            else:
                effects_per_level.append(None)

        # Pokémon that have this type, sorted by cost
        poke_list = sorted(
            [p["name"] for p in pokemon.values() if synergy in p["types"] and not p["additional"]],
            key=lambda n: (pokemon[n]["cost"] or 99, n),
        )

        synergies[synergy] = {
            "name":             synergy,
            "thresholds":       thresholds,
            "effects_per_level": effects_per_level,
            "all_effects":      effect_list,
            "pokemon":          poke_list,
        }

    return synergies


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extracts data from Pokémon Auto Chess")
    print("⏳ Parsing bot builds...")
    builds = parse_bot_builds(repo)

    # Enriquecer pokemon con recommended_items del botv2
    for name, build in builds.items():
        if name in pokemon:
            pokemon[name]["recommended_items"] = build["recommended_items"]
            pokemon[name]["item_frequency"]    = build["item_frequency"]

    print(f"   → {len(builds)} Pokémon with real item builds")
    parser.add_argument(
        "--repo-path",
        default="./pokemonAutoChess",
        help="Path to the cloned repo (default: ./pokemonAutoChess)",
    )
    args = parser.parse_args()

    repo = Path(args.repo_path).resolve()
    if not repo.exists():
        print(f"❌ Repo not found at: {repo}", file=sys.stderr)
        sys.exit(1)

    print(f"📂 Repo: {repo}")

    # Extraction
    print("⏳ Parsing pokemon CSV...")
    pokemon = parse_pokemon_csv(repo)

    print("⏳ Parsing ItemStats...")
    items = parse_items_stats(repo)

    print("⏳ Parsing SynergyTriggers...")
    triggers = parse_synergy_triggers(repo)

    print("⏳ Parsing SynergyEffects...")
    effects_map = parse_synergy_effects(repo)

    print("⏳ Building synergies...")
    synergies = build_synergies(triggers, effects_map, pokemon)

    # Output
    out_dir = Path("pokebot/knowledge_base")
    out_dir.mkdir(exist_ok=True)

    _write_json(out_dir / "pokemon.json",   pokemon)
    _write_json(out_dir / "items.json",     items)
    _write_json(out_dir / "synergies.json", synergies)
    _write_json(
        out_dir / "knowledge_base.json",
        {"pokemon": pokemon, "items": items, "synergies": synergies},
    )

    # Summary
    print()
    print(f"✅ Pokémon extracted : {len(pokemon)}")
    print(f"✅ Items extracted   : {len(items)}")
    print(f"✅ Synergies         : {len(synergies)}")
    print(f"✅ Files in          : {out_dir.resolve()}")

    if PARSE_ERRORS:
        print(f"\n⚠️  {len(PARSE_ERRORS)} warning(s) during parsing:")
        for e in PARSE_ERRORS:
            print(f"   - {e}")


def _write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"   📄 {path.name} written")


if __name__ == "__main__":
    main()