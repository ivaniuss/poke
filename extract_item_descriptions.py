"""
Extract item descriptions from pokemonAutoChess translation file
and enrich the pokebot knowledge base.
"""
import json
import re
from pathlib import Path

TRANSLATION_PATH = Path(__file__).parent / "pokemonAutoChess" / "app" / "public" / "dist" / "client" / "locales" / "en" / "translation.json"
KB_PATH = Path(__file__).parent / "pokebot" / "knowledge_base" / "knowledge_base.json"
ITEMS_PATH = Path(__file__).parent / "pokebot" / "knowledge_base" / "items.json"

# Load translation file
with open(TRANSLATION_PATH, encoding="utf-8") as f:
    translations = json.load(f)

item_descriptions = translations.get("item_description", {})

# Load current KB
with open(KB_PATH, encoding="utf-8") as f:
    kb = json.load(f)

# Load current items
with open(ITEMS_PATH, encoding="utf-8") as f:
    items = json.load(f)

# Enrich items with descriptions
enriched_count = 0
for item_key, item_data in items.items():
    desc = item_descriptions.get(item_key)
    if desc:
        # Clean up i18n references like $t(ability.RAGE)
        desc = re.sub(r'\$t\([^)]+\)', '[ref]', desc)
        item_data["description"] = desc
        enriched_count += 1

# Also enrich items in the KB
for item_key in kb.get("items", {}):
    desc = item_descriptions.get(item_key)
    if desc:
        desc = re.sub(r'\$t\([^)]+\)', '[ref]', desc)
        kb["items"][item_key]["description"] = desc

print(f"Enriched {enriched_count}/{len(items)} items with descriptions")

# Save enriched files
with open(ITEMS_PATH, "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

with open(KB_PATH, "w", encoding="utf-8") as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print("[SUCCESS] Saved enriched items.json and knowledge_base.json")

# Print a sample of enriched items
print("\n--- Sample enriched items ---")
sample_items = ["SOUL_DEW", "CHOICE_SPECS", "KINGS_ROCK", "POKEMONOMICON", "PROTECTIVE_PADS", "MUSCLE_BAND"]
for name in sample_items:
    if name in items:
        desc = items[name].get("description", "NO DESCRIPTION")
        print(f"  {name}: {desc[:80]}...")
