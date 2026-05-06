"""
Test the full agent flow with Crocalor.
"""
import sys
import json
from pathlib import Path

# 1. Check KB data for Crocalor
kb_path = Path("knowledge_base/knowledge_base.json")
with open(kb_path, encoding="utf-8") as f:
    kb = json.load(f)

# Search for crocalor (case insensitive)
matches = [k for k in kb["pokemon"] if "CROCALOR" in k.upper()]
print("=== KB SEARCH ===")
if not matches:
    # Try fuzzy
    import difflib
    matches = difflib.get_close_matches("CROCALOR", list(kb["pokemon"].keys()), n=3, cutoff=0.5)
    print(f"Fuzzy matches: {matches}")

for name in matches:
    p = kb["pokemon"][name]
    print(f"\n--- {name} ---")
    print(f"  Rarity: {p['rarity']} | Cost: {p['cost']}g | Stars: {p['stars']}/{p['nbStages']}")
    print(f"  Types: {', '.join(p['types'])}")
    print(f"  Stats: HP={p['hp']} ATK={p['atk']} DEF={p['def']} SpeDef={p['speDef']} Speed={p['speed']} Range={p['range']} MaxPP={p['maxPP']}")
    print(f"  Skill: {p['skill']}")
    print(f"  Evolution: {p.get('evolution', 'None')}")
    print(f"  Recommended items: {p.get('recommended_items', [])}")
    print(f"  Item frequency: {p.get('item_frequency', {})}")
    has_data = bool(p.get('item_frequency'))
    print(f"  HAS BOT DATA: {'YES' if has_data else 'NO'}")

# 2. Simulate the tools flow
print("\n\n=== SIMULATING recommend_items() ===")
sys.path.insert(0, ".")
from app.tools import recommend_items, get_item_details

result = recommend_items("CROCALOR")
print(result)

print("\n\n=== SAMPLE ITEM DETAILS (now with descriptions) ===")
# Show details for items that would be recommended
for item in ["CHOICE_SPECS", "SOUL_DEW", "POKEMONOMICON", "FLAME_ORB"]:
    print(get_item_details(item))
    print()
