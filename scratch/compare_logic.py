import sys
import json
from pathlib import Path

# Setup paths
sys.path.insert(0, ".")
from app.tools import recommend_items, POKEMON, _infer_role, _score_item_for_role, ITEMS, _item_label

def compare_pokemon(name):
    name = name.upper()
    if name not in POKEMON:
        print(f"❌ Pokemon {name} no encontrado.")
        return

    p = POKEMON[name]
    role = _infer_role(p)
    
    print(f"\n{'='*60}")
    print(f"🔍 COMPARATIVA: {name}")
    print(f"{'='*60}")
    print(f"Stats: HP {p['hp']} | ATK {p['atk']} | DEF {p['def']} | Range {p['range']}")
    print(f"Role detectado: {role}")
    print(f"{'-'*60}")

    # 1. BOT DATA
    freq = p.get("item_frequency", {})
    if freq:
        print("\n🤖 LO QUE HACEN LOS BOTS (Meta real):")
        # Sort by count for this simple view
        sorted_bot = sorted(freq.items(), key=lambda x: x[1].get('count', 0) if isinstance(x[1], dict) else x[1], reverse=True)
        for i, (item, data) in enumerate(sorted_bot[:5]):
            count = data.get('count', 0) if isinstance(data, dict) else data
            elo = (data.get('elo_total', 0) / count) if isinstance(data, dict) and count > 0 else 0
            print(f"  {i+1}. {item:<18} | Usado {count:>2} veces | ELO Avg: {elo:.0f}")
    else:
        print("\n🤖 BOTS: No hay datos registrados para este Pokémon.")

    # 2. HEURISTIC (MATH)
    print("\n🧮 LO QUE DICEN LAS MATEMÁTICAS (Heurística de Stats):")
    scored = sorted(ITEMS.items(), key=lambda kv: _score_item_for_role(kv[1], p, role), reverse=True)
    for i, (item_name, item_data) in enumerate(scored[:5]):
        print(f"  {i+1}. {item_name:<18} | {_item_label(item_name)}")

    # 3. VERDICT ANALYSIS (Manual simulation of what the new Agent does)
    print("\n🧠 NUEVA LÓGICA DEL AGENTE (Meta Guide Aware):")
    if name == "CROCALOR":
        print("  • Conflicto detectado: Los bots usan CRIT (Reaper Cloth), la matemática pide AP (Choice Specs).")
        print("  • Razonamiento IA: REAPER_CLOTH es superior porque la descripción (ahora disponible) revela")
        print("    que permite critear la habilidad. La heurística fallaba por no leer efectos especiales.")
    elif not freq:
        print("  • Sin datos de bots: La IA usará la Meta Guide.")
        print(f"  • Plan: Como es {role}, recomendará items core de la guía + Eviolite si no ha evolucionado.")
    else:
        print("  • Análisis: Comparando sinergias de tipos con items recomendados...")

compare_pokemon(sys.argv[1] if len(sys.argv) > 1 else "CROCALOR")
