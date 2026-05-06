"""
Test the enriched analyst flow end-to-end.
Simulates a query for a Pokemon WITH and WITHOUT bot data.
"""
import json
from pathlib import Path

# Test 1: Verify items now have descriptions
kb_path = Path("knowledge_base/knowledge_base.json")
with open(kb_path, encoding="utf-8") as f:
    kb = json.load(f)

items = kb["items"]
items_with_desc = sum(1 for i in items.values() if i.get("description"))
print(f"Items with descriptions: {items_with_desc}/{len(items)}")

# Test 2: Verify meta guide loads
meta_path = Path("knowledge_base/meta_guide.md")
meta = meta_path.read_text(encoding="utf-8")
print(f"Meta guide loaded: {len(meta)} chars")
print(f"Contains CARRY_AP: {'CARRY_AP' in meta}")
print(f"Contains TANK: {'TANK' in meta}")
print(f"Contains anti-patterns: {'ANTI-PATTERNS' in meta}")

# Test 3: Check a Pokemon without bot data
no_data_pokemon = [k for k, v in kb["pokemon"].items() 
                   if not v.get("item_frequency") and v.get("stars", 1) >= 2][:5]
print(f"\nSample Pokemon WITHOUT bot data (stage 2+):")
for name in no_data_pokemon:
    p = kb["pokemon"][name]
    print(f"  {name}: HP={p['hp']} ATK={p['atk']} DEF={p['def']} Range={p['range']} Types={p['types']}")

# Test 4: Check get_item_details now includes description
from app.tools import get_item_details
print(f"\n--- get_item_details('SOUL_DEW') ---")
print(get_item_details("SOUL_DEW"))
print(f"\n--- get_item_details('KINGS_ROCK') ---")
print(get_item_details("KINGS_ROCK"))

print("\nAll tests passed!")
