"""
Compare the OLD vs NEW prompt that the analyst would generate for Crocalor.
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, ".")

from app.tools import recommend_items, get_item_details, POKEMON, ITEMS

# Simulate the tool output
raw_data = recommend_items("CROCALOR")

# ── OLD PROMPT (before changes) ──
item_names_found = set(re.findall(r"([A-Z][A-Z0-9_]{3,})", raw_data))
specs = []
for name in item_names_found:
    details = get_item_details(name)
    if "not found" not in details.lower():
        specs.append(details)
specs_text = "\n".join(specs)

old_prompt = (
    "You are a master Pokemon Auto Chess strategist. Respond ALWAYS in the same language as the user.\n"
    "INSTRUCTION: Bot data exists but from MEDIUM ELO players. "
    "Use bot items as base, you may suggest 1 mathematical complement. "
    "Be transparent that data is not high-ELO validated.\n"
    f"ITEM SPECS (Use to explain reasons): {specs_text}\n\n"
    "RULES:\n"
    "1. ALWAYS keep item names in ENGLISH.\n"
    "2. Use **BOLD** for all items.\n"
    "3. Max 2 short sentences.\n"
    "4. Format: [Build] + [Reason]. STOP."
    "\n\nUser Question: que items le pongo a crocalor?\n"
    f"Bot Meta Data: {raw_data}"
)

# ── NEW PROMPT (after changes) ──
meta_guide = Path("knowledge_base/meta_guide.md").read_text(encoding="utf-8")
pdata = POKEMON.get("CROCALOR", {})
types_str = ", ".join(pdata.get("types", []))
pokemon_context = (
    f"Pokemon: CROCALOR | Types: {types_str} | "
    f"HP:{pdata.get('hp','?')} ATK:{pdata.get('atk','?')} "
    f"DEF:{pdata.get('def','?')} Range:{pdata.get('range','?')} "
    f"MaxPP:{pdata.get('maxPP','?')} Skill:{pdata.get('skill','?')}"
)

instruction = (
    "Bot data exists but from MEDIUM ELO players. "
    "Use bot items as base. Cross-reference with the META GUIDE to validate choices. "
    "You may suggest 1 better alternative if the meta guide clearly recommends something better for this role. "
    "Be transparent that data is not high-ELO validated."
)

new_prompt = (
    "You are a master Pokemon Auto Chess strategist. Respond ALWAYS in the same language as the user.\n\n"
    f"META GUIDE (Expert item strategy knowledge):\n{meta_guide}\n\n"
    f"INSTRUCTION: {instruction}\n\n"
    f"POKEMON CONTEXT: {pokemon_context}\n\n"
    f"ITEM DESCRIPTIONS (Use to explain reasons):\n{specs_text}\n\n"
    "RULES:\n"
    "1. ALWAYS keep item names in ENGLISH.\n"
    "2. Use **BOLD** for all items.\n"
    "3. Max 3 short sentences: [Best 3 items] + [Why they synergize with this Pokemon]. STOP.\n"
    "4. Consider the Pokemon's types, range, maxPP and skill when reasoning about items.\n"
    "\nUser Question: que items le pongo a crocalor?\n"
    f"Bot Meta Data: {raw_data}"
)

print("=" * 60)
print("OLD PROMPT SIZE:", len(old_prompt), "chars")
print("NEW PROMPT SIZE:", len(new_prompt), "chars")
print("=" * 60)

print("\n\n### OLD PROMPT (truncated) ###")
print(old_prompt[:500])
print("...\n")

print("### NEW PROMPT (key sections) ###")
print(f"META GUIDE: {len(meta_guide)} chars of expert knowledge")
print(f"POKEMON CONTEXT: {pokemon_context}")
print(f"INSTRUCTION: {instruction}")
print(f"ITEM DESCRIPTIONS: {len(specs_text)} chars of detailed item effects")
print(f"\nThe LLM now knows:")
print(f"  - Crocalor is FIRE/SOUND/GHOST, Range 3, MaxPP 60")
print(f"  - Bots use REAPER_CLOTH (5x) and RAZOR_FANG (3x)")
print(f"  - Meta guide says CARRY_AP best items: CHOICE_SPECS, SOUL_DEW, REAPER_CLOTH")
print(f"  - Meta guide says REAPER_CLOTH enables ability crits - perfect for AP carry")
print(f"  - Meta guide says Range 3 = safe backline, can afford full damage build")
print(f"  - Meta guide anti-pattern: don't recommend RAZOR_CLAW on AP carry (PHYSICAL crits)")
