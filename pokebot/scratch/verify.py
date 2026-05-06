import json
with open("knowledge_base/items.json", encoding="utf-8") as f:
    items = json.load(f)
for k in ["SOUL_DEW","CHOICE_SPECS","KINGS_ROCK","POKEMONOMICON","MUSCLE_BAND","PROTECTIVE_PADS"]:
    desc = items[k].get("description", "NONE")
    print(f"{k}: {desc[:120]}")
