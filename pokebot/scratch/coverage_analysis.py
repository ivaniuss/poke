import json

with open("knowledge_base/knowledge_base.json", encoding="utf-8") as f:
    kb = json.load(f)

pokemon = kb["pokemon"]
items = kb["items"]
total = len(pokemon)

with_data = sum(1 for p in pokemon.values() if p.get("item_frequency"))
with_high_elo = sum(
    1 for p in pokemon.values()
    if any(
        isinstance(v, dict) and v.get("count", 0) > 0
        and (v.get("elo_total", 0) / v["count"]) >= 1500
        for v in p.get("item_frequency", {}).values()
    )
)
with_rec = sum(1 for p in pokemon.values() if p.get("recommended_items"))
no_data = total - with_data

print(f"Total Pokemon: {total}")
print(f"Total Items: {len(items)}")
print(f"With ANY item_frequency data: {with_data} ({with_data/total*100:.1f}%)")
print(f"With HIGH ELO data (>=1500): {with_high_elo} ({with_high_elo/total*100:.1f}%)")
print(f"With recommended_items list: {with_rec} ({with_rec/total*100:.1f}%)")
print(f"NO data at all: {no_data} ({no_data/total*100:.1f}%)")

# Check avg items per pokemon that HAS data
counts = []
for p in pokemon.values():
    freq = p.get("item_frequency", {})
    if freq:
        counts.append(len(freq))
if counts:
    print(f"\nAmong pokemon WITH data:")
    print(f"  Avg items per pokemon: {sum(counts)/len(counts):.1f}")
    print(f"  Min: {min(counts)}, Max: {max(counts)}")

# Check stages - only final evolutions tend to have data
stage_data = {"stage1": 0, "stage2": 0, "stage3": 0, "stage1_total": 0, "stage2_total": 0, "stage3_total": 0}
for p in pokemon.values():
    stars = p.get("stars", 1)
    key_total = f"stage{stars}_total"
    key_data = f"stage{stars}"
    if key_total in stage_data:
        stage_data[key_total] += 1
        if p.get("item_frequency"):
            stage_data[key_data] += 1

print(f"\nData coverage by evolution stage:")
for stage in [1, 2, 3]:
    t = stage_data[f"stage{stage}_total"]
    d = stage_data[f"stage{stage}"]
    pct = (d/t*100) if t > 0 else 0
    print(f"  Stage {stage}: {d}/{t} ({pct:.1f}%)")

# Items with descriptions
items_with_desc = sum(1 for i in items.values() if i.get("description"))
print(f"\nItems with descriptions: {items_with_desc}/{len(items)}")
items_no_stats = sum(1 for i in items.values() if all(v == 0 for v in i.get("stats", {}).values()))
print(f"Items with NO stats (utility/special): {items_no_stats}/{len(items)}")
