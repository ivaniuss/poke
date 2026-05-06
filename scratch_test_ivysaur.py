"""
Test the agent with IVYSAUR (no bot data).
"""
import sys
import json
from pathlib import Path

# 1. Check KB data for IVYSAUR
kb_path = Path("pokebot/knowledge_base/knowledge_base.json")
with open(kb_path, encoding="utf-8") as f:
    kb = json.load(f)

p = kb["pokemon"].get("IVYSAUR")
if not p:
    print("IVYSAUR not found in KB")
    sys.exit(1)

print(f"--- IVYSAUR ---")
print(f"Types: {', '.join(p['types'])}")
print(f"Stats: HP={p['hp']} ATK={p['atk']} DEF={p['def']} Range={p['range']} MaxPP={p['maxPP']}")
print(f"Skill: {p['skill']}")
print(f"HAS BOT DATA: {'YES' if p.get('item_frequency') else 'NO'}")

# 2. Simulate the tools flow
sys.path.insert(0, "./pokebot")
from app.tools import recommend_items

result = recommend_items("IVYSAUR")
print("\n=== Tool Output (Fallthrough to Heuristics) ===")
print(result)
