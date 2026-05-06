"""
extract_game_data.py
Extracts data from the Pokémon Auto Chess repo and generates a knowledge base in JSON.

Usage:
    python extract_game_data.py --repo-path ./pokemonAutoChess
    python extract_game_data.py --repo-path ./pokemonAutoChess --output-path ./pokebot/knowledge_base
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

PARSE_ERRORS: list[str] = []

# ── Stat enum → output key ────────────────────────────────────────────────────
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

# ── Rarity → gold cost ────────────────────────────────────────────────────────
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

# ── Deprecated item renames (from db-commands/6.7/update-items.ts) ─────────────
ITEM_RENAMES = {
    "CHOICE_SCARF": "LOADED_DICE",
    "LUCKY_EGG":    "HEAVY_DUTY_BOOTS",
    "FLUFFY_TAIL":  "SAFETY_GOGGLES",
    "TOXIC_ORB":    "POKERUS_VIAL",
    "ROTOM_PHONE":  "SPELL_TAG",
    "HARD_STONE":   None,          # removed entirely, no replacement
}

# ── Special items (berries, tools, etc.) that have effects but no stats ────────
# These items don't appear in ItemStats but are used in bot builds.
# Descriptions extracted from core/effects/items.ts.
SPECIAL_ITEM_DESCRIPTIONS = {
    "WONDER_BOX":       "Random item each combat round",
    "GRACIDEA_FLOWER":  "Heals holder and adjacent allies",
    "MAX_REVIVE":       "Resurrect once per combat",
    "CHEF_HAT":         "Cook berries into dishes (Gourmet synergy only)",
    "SPELL_TAG":        "Curses the attacker on death",
    "EXP_SHARE":        "Gives bonus XP to holder",
    "DYNAMAX_BAND":     "Triples holder base HP",
    "POKERUS_VIAL":     "Spreads Pokerus (bonus stats) to adjacent allies",
    "SACRED_ASH":       "Revives all fainted allies once",
    "RUSTED_SWORD":     "Greatly boosts ATK (Zacian only)",
    "SURFBOARD":        "Grants Water type and surf ability",
    "WHITE_FLUTE":      "Attracts wild Pokémon (PvE rounds)",
    "RARE_CANDY":       "Instantly evolves the holder",
    "MAX_ELIXIR":       "Fills PP to max at combat start",
    "TINY_MUSHROOM":    "Cooking ingredient",
    "SALAC_BERRY":      "Boosts speed when HP is low",
    "GANLON_BERRY":     "Boosts defense when HP is low",
    "APICOT_BERRY":     "Boosts special defense when HP is low",
    "LEPPA_BERRY":      "Restores PP during combat",
    "LUM_BERRY":        "Cures status conditions",
}


# ── Utilities ─────────────────────────────────────────────────────────────────

def read_file(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        PARSE_ERRORS.append(f"File not found: {path}")
        return None


def strip_ts_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def extract_block(text: str, keyword: str) -> str | None:
    """Find 'export const KEYWORD = { ... }' by matching braces after '= {'."""
    idx = text.find(keyword)
    if idx == -1:
        PARSE_ERRORS.append(f"Block not found: {keyword}")
        return None

    rest = text[idx:]
    m = re.search(r"=\s*\{", rest)
    if not m:
        PARSE_ERRORS.append(f"No '= {{' found for: {keyword}")
        return None

    start = idx + m.end() - 1
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start: i + 1]

    PARSE_ERRORS.append(f"Unclosed block: {keyword}")
    return None


def _int(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


# ── Parser: pokemons-data.csv ─────────────────────────────────────────────────

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

        types = [
            row[f"Type {i}"].strip()
            for i in range(1, 5)
            if row.get(f"Type {i}", "").strip()
        ]

        rarity    = row.get("Category", "").strip().upper()
        cost      = RARITY_COST.get(rarity)
        tier      = int(row.get("Tier", 1) or 1)
        nb_stages = int(row.get("Nb stages", 1) or 1)

        pokemon[name] = {
            "name":               name,
            "index":              row.get("Index", "").strip(),
            "rarity":             rarity,
            "cost":               cost,
            "hp":                 _int(row.get("HP")),
            "atk":                _int(row.get("Attack")),
            "speed":              _int(row.get("Speed")),
            "def":                _int(row.get("Defense")),
            "speDef":             _int(row.get("Special Defense")),
            "range":              _int(row.get("Attack Range")),
            "maxPP":              _int(row.get("Max PP")),
            "skill":              row.get("Ability", "").strip(),
            "types":              types,
            "stars":              tier,
            "nbStages":           nb_stages,
            "family":             row.get("Family", "").strip(),
            "additional":         row.get("Additional pick", "false").strip().lower() == "true",
            "regional":           row.get("Regional", "false").strip().lower() == "true",
            "variant":            row.get("Variant", "false").strip().lower() == "true",
            "recommended_items":  [],
            "item_frequency":     {},
        }

    # Resolve evolution chains within each family
    family_by_name: dict[str, list] = {}
    for p in pokemon.values():
        family_by_name.setdefault(p["family"], []).append(p)

    for members in family_by_name.values():
        members.sort(key=lambda p: p["stars"])
        for i, p in enumerate(members):
            p["evolution"] = members[i + 1]["name"] if i + 1 < len(members) else None

    return pokemon


# ── Parser: config/game/items.ts → ItemStats ──────────────────────────────────

def parse_items_stats(repo: Path) -> dict:
    path = repo / "app/config/game/items.ts"
    raw  = read_file(path)
    if raw is None:
        return {}

    text  = strip_ts_comments(raw)
    block = extract_block(text, "ItemStats")
    if block is None:
        return {}

    items: dict[str, dict] = {}

    entry_pattern = re.compile(r"\[Item\.(\w+)\]\s*:\s*(\{[^}]*\})", re.DOTALL)
    stat_pattern  = re.compile(r"\[Stat\.(\w+)\]\s*:\s*(-?\d+)")

    for m in entry_pattern.finditer(block):
        item_name   = m.group(1)
        stats_block = m.group(2)

        stats = {v: 0 for v in STAT_MAP.values()}
        for sm in stat_pattern.finditer(stats_block):
            mapped = STAT_MAP.get(sm.group(1))
            if mapped:
                stats[mapped] = int(sm.group(2))
            else:
                PARSE_ERRORS.append(f"Unknown stat in items: {sm.group(1)}")

        items[item_name] = {"name": item_name, "stats": stats}

    return items


# ── Parser: types/enum/Item.ts → ItemRecipe (craftable items without stats) ───

def parse_item_recipes(repo: Path) -> dict:
    """Parse ItemRecipe to discover craftable items and their components.
    Returns items that are NOT already in ItemStats (those are handled above)."""
    path = repo / "app/types/enum/Item.ts"
    raw  = read_file(path)
    if raw is None:
        return {}

    text = strip_ts_comments(raw)
    recipes: dict[str, dict] = {}

    recipe_pattern = re.compile(
        r"\[Item\.(\w+)\]\s*:\s*\[Item\.(\w+),\s*Item\.(\w+)\]"
    )
    for m in recipe_pattern.finditer(text):
        item_name = m.group(1)
        comp1, comp2 = m.group(2), m.group(3)
        zero_stats = {v: 0 for v in STAT_MAP.values()}
        desc = SPECIAL_ITEM_DESCRIPTIONS.get(item_name, "")
        recipes[item_name] = {
            "name":       item_name,
            "stats":      zero_stats,
            "components": [comp1, comp2],
            "description": desc,
        }

    return recipes


# ── Build special items (berries, tools, etc.) ────────────────────────────────

def build_special_items() -> dict:
    """Create entries for known special items (berries, tools, etc.)
    that have effects but no stat entries in ItemStats."""
    items: dict[str, dict] = {}
    zero_stats = {v: 0 for v in STAT_MAP.values()}

    for item_name, desc in SPECIAL_ITEM_DESCRIPTIONS.items():
        items[item_name] = {
            "name":        item_name,
            "stats":       zero_stats,
            "description": desc,
        }

    return items


# ── Parser: models/effects.ts → SynergyEffects ────────────────────────────────

def parse_synergy_effects(repo: Path) -> dict:
    path = repo / "app/models/effects.ts"
    raw  = read_file(path)
    if raw is None:
        return {}

    text  = strip_ts_comments(raw)
    block = extract_block(text, "SynergyEffects")
    if block is None:
        return {}

    effects: dict[str, list[str]] = {}

    entry_pattern  = re.compile(r"\[Synergy\.(\w+)\]\s*:\s*\[([^\]]*)\]", re.DOTALL)
    effect_pattern = re.compile(r"EffectEnum\.(\w+)")

    for m in entry_pattern.finditer(block):
        effects[m.group(1)] = effect_pattern.findall(m.group(2))

    return effects


# ── Parser: config/game/synergies.ts → SynergyTriggers ───────────────────────

def parse_synergy_triggers(repo: Path) -> dict:
    path = repo / "app/config/game/synergies.ts"
    raw  = read_file(path)
    if raw is None:
        return {}

    text  = strip_ts_comments(raw)
    block = extract_block(text, "SynergyTriggers")
    if block is None:
        return {}

    triggers: dict[str, list[int]] = {}

    entry_pattern = re.compile(r"\[Synergy\.(\w+)\]\s*:\s*\[([^\]]*)\]")
    for m in entry_pattern.finditer(block):
        nums = [int(n.strip()) for n in m.group(2).split(",") if n.strip()]
        triggers[m.group(1)] = nums

    return triggers


# ── Parser: db-commands/botv2.json → real item builds ────────────────────────

def _migrate_item(name: str) -> str | None:
    """Apply deprecated item renames. Returns None if the item was removed."""
    if name in ITEM_RENAMES:
        return ITEM_RENAMES[name]   # None means 'removed entirely'
    return name


def parse_bot_builds(repo: Path) -> dict:
    path = repo / "db-commands/botv2.json"
    raw  = read_file(path)
    if raw is None:
        return {}

    bots = json.loads(raw)
    items_by_pokemon: dict[str, dict[str, dict]] = {}
    migrated_count = 0
    removed_count  = 0

    for bot in bots:
        elo = bot.get("elo", 0)
        steps = bot.get("steps", [])
        if not steps:
            continue
        final_step = steps[-1]
        for poke in final_step.get("board", []):
            name  = poke.get("name", "").strip()
            poke_items = poke.get("items", [])
            if not name or not poke_items:
                continue
            if name not in items_by_pokemon:
                items_by_pokemon[name] = {}

            for raw_item in poke_items:
                migrated = _migrate_item(raw_item)
                if migrated is None:
                    removed_count += 1
                    continue
                if migrated != raw_item:
                    migrated_count += 1
                if migrated not in items_by_pokemon[name]:
                    items_by_pokemon[name][migrated] = {"count": 0, "elo_total": 0}
                items_by_pokemon[name][migrated]["count"] += 1
                items_by_pokemon[name][migrated]["elo_total"] += elo

    if migrated_count:
        print(f"   → {migrated_count} deprecated item references migrated")
    if removed_count:
        print(f"   → {removed_count} removed item references dropped")

    builds = {}
    for name, item_data in items_by_pokemon.items():
        builds[name] = {
            "recommended_items": [item for item, d in item_data.items()],
            "item_frequency":  {},
        }
        for item, d in item_data.items():
            builds[name]["item_frequency"][item] = {
                "count": d["count"],
                "elo_total": d["elo_total"],
            }

    return builds


# ── Build synergies with Pokémon list ─────────────────────────────────────────

def build_synergies(triggers: dict, effects: dict, pokemon: dict) -> dict:
    synergies: dict[str, dict] = {}

    for synergy in set(triggers) | set(effects):
        thresholds  = triggers.get(synergy, [])
        effect_list = effects.get(synergy, [])

        effects_per_level = [
            effect_list[i] if i < len(effect_list) else None
            for i in range(len(thresholds))
        ]

        poke_list = sorted(
            [
                p["name"] for p in pokemon.values()
                if synergy in p["types"] and not p["additional"]
            ],
            key=lambda n: (pokemon[n]["cost"] or 99, n),
        )

        synergies[synergy] = {
            "name":              synergy,
            "thresholds":        thresholds,
            "effects_per_level": effects_per_level,
            "all_effects":       effect_list,
            "pokemon":           poke_list,
        }

    return synergies


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract Pokémon Auto Chess game data")
    parser.add_argument(
        "--repo-path",
        default="./pokemonAutoChess",
        help="Path to the cloned repo (default: ./pokemonAutoChess)",
    )
    parser.add_argument(
        "--output-path",
        default="./pokebot/knowledge_base",
        help="Output folder for JSON files (default: ./pokebot/knowledge_base)",
    )
    args = parser.parse_args()

    repo    = Path(args.repo_path).resolve()
    out_dir = Path(args.output_path).resolve()

    if not repo.exists():
        print(f"❌ Repo not found at: {repo}", file=sys.stderr)
        sys.exit(1)

    print(f"📂 Repo:   {repo}")
    print(f"📂 Output: {out_dir}")
    print()

    print("⏳ Parsing Pokémon CSV...")
    pokemon = parse_pokemon_csv(repo)

    print("⏳ Parsing bot builds (botv2.json)...")
    builds   = parse_bot_builds(repo)
    enriched = 0
    for name, build in builds.items():
        if name in pokemon:
            pokemon[name]["recommended_items"] = build["recommended_items"]
            pokemon[name]["item_frequency"]    = build["item_frequency"]
            enriched += 1
    print(f"   → {enriched} Pokémon enriched with real item builds")

    print("⏳ Parsing ItemStats...")
    items = parse_items_stats(repo)

    print("⏳ Parsing ItemRecipe (craftable items without stats)...")
    recipes = parse_item_recipes(repo)
    new_from_recipes = {k: v for k, v in recipes.items() if k not in items}
    items.update(new_from_recipes)
    print(f"   → {len(new_from_recipes)} items added from ItemRecipe")

    print("⏳ Adding special items (berries, tools, etc.)...")
    specials = build_special_items()
    new_from_specials = {k: v for k, v in specials.items() if k not in items}
    items.update(new_from_specials)
    print(f"   → {len(new_from_specials)} special items added")

    print("⏳ Parsing SynergyTriggers...")
    triggers = parse_synergy_triggers(repo)

    print("⏳ Parsing SynergyEffects...")
    effects_map = parse_synergy_effects(repo)

    print("⏳ Building synergies...")
    synergies = build_synergies(triggers, effects_map, pokemon)

    # Write output
    out_dir.mkdir(parents=True, exist_ok=True)

    print()
    _write_json(out_dir / "pokemon.json",   pokemon)
    _write_json(out_dir / "items.json",     items)
    _write_json(out_dir / "synergies.json", synergies)
    _write_json(
        out_dir / "knowledge_base.json",
        {"pokemon": pokemon, "items": items, "synergies": synergies},
    )

    print()
    print(f"✅ Pokémon extracted  : {len(pokemon)}")
    print(f"✅ Items extracted    : {len(items)}")
    print(f"✅ Synergies          : {len(synergies)}")
    print(f"✅ Bot builds         : {enriched} Pokémon with real data")
    print(f"✅ Files written to   : {out_dir}")

    if PARSE_ERRORS:
        print(f"\n⚠️  {len(PARSE_ERRORS)} warning(s):")
        for e in PARSE_ERRORS:
            print(f"   - {e}")


def _write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"   📄 {path.name}")


if __name__ == "__main__":
    main()