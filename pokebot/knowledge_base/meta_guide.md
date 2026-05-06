# Pokemon Auto Chess — Item Strategy Meta Guide
# This guide is injected into the LLM system prompt to provide expert-level
# item recommendation knowledge when bot data is missing or low quality.

## CORE ITEM ROLES

### CARRY_AP (Ability Power Carry)
Primary damage comes from abilities (SPECIAL damage). Needs AP, PP regen, and ability amplifiers.

BEST IN SLOT:
- CHOICE_SPECS: +100 AP. Pure AP powerhouse, best raw damage boost.
- SOUL_DEW: +5 AP and +5 PP every second during combat. Best sustained DPS item. Scales harder in long fights.
- REAPER_CLOTH: Abilities can critically strike. Massive damage multiplier with crit chance.
- POKEMONOMICON: Abilities BURN targets and reduce SPE_DEF. Best for AoE ability users.

STRONG ALTERNATIVES:
- AQUA_EGG: +20% max PP refund after casting + 2 PP per cast. Enables fast ability cycling.
- DAWN_STONE: +20 AP + grants PSYCHIC type. Good if team needs PSYCHIC synergy threshold.
- HEAVY_DUTY_BOOTS: +50 AP + 12 DEF + immunity to board effects. Excellent hybrid item.

### CARRY_ATK (Physical Attack Carry)
Primary damage from auto-attacks (PHYSICAL damage). Needs ATK, SPEED, CRIT.

BEST IN SLOT:
- RAZOR_CLAW: +50% crit chance. Core item for any physical carry.
- RAZOR_FANG: +100% crit power + ARMOR_BREAK on crits. Pairs with RAZOR_CLAW.
- RED_ORB: 25% of attack damage dealt as TRUE damage. Ignores all defenses.
- FLAME_ORB: +100% base ATK but self-BURN. Massive damage if BURN doesn't matter.

STRONG ALTERNATIVES:
- SCOPE_LENS: Crits steal 10 PP from target. Shuts down enemy casters.
- DEEP_SEA_TOOTH: Attacks restore 5 PP (+15 on kills). Enables fast ability + strong attacks.
- PUNCHING_GLOVE: Attacks deal 8% target max HP. Tank shredder.

### TANK (Frontline / HP / DEF focused)
Absorbs damage, protects carries. Needs HP, DEF, SPE_DEF, SHIELD.

BEST IN SLOT:
- KINGS_ROCK: +100 HP + 20% max HP as SHIELD at combat start. Best raw tankiness.
- ROCKY_HELMET: +25 DEF + negates critical bonus damage. Anti-crit tank item.
- POKE_DOLL: -30% all incoming damage but makes holder more targeted. Perfect for designated tank.
- ASSAULT_VEST: +40 SPE_DEF + 50% reduced BURN/POISON damage. Best magic defense.

STRONG ALTERNATIVES:
- STICKY_BARB: Melee retaliation damage + WOUND. Punishes melee attackers.
- MAX_REVIVE: Resurrect at full HP on first KO. Second life.
- MUSCLE_BAND: Gains DEF/ATK/SPEED when taking damage. Gets stronger as fight goes on.

### SUPPORT (Utility / PP / Team buffs)
Enables team through buffs, healing, shields. Needs PP, SHIELD, utility effects.

BEST IN SLOT:
- ABILITY_SHIELD: Gives SHIELD + RUNE_PROTECT to holder and row allies at combat start.
- GREEN_ORB: Heals holder and adjacent allies 5% max HP every 2s. Overheal converts to PP.
- GRACIDEA_FLOWER: +20 SPEED to holder and row allies at combat start.
- STAR_DUST: After casting, gain 50% max PP as SHIELD. Makes supports tanky.

## SYNERGY-AWARE RULES

These rules modify item priority based on the Pokemon's synergies:

- DRAGON synergy (5+): Team already gets bonus AP from synergy → reduce priority of CHOICE_SPECS, invest in survivability (KINGS_ROCK) or sustained damage (SOUL_DEW).
- STEEL synergy (4+): Team gets DEF bonus → can afford offensive items on normally-tanky Pokemon.
- FIGHTING synergy: Melee-focused → PROTECTIVE_PADS valuable for shield-breaking, FLAME_ORB for raw ATK.
- PSYCHIC synergy: AP scaling → CHOICE_SPECS and SOUL_DEW are premium.
- GHOST synergy: SPELL_TAG gives GHOST type + CURSE on KO. POKEMONOMICON synergizes with SPECIAL damage.
- ELECTRIC synergy: SPEED-focused → XRAY_VISION (50 speed + can't miss) is premium.
- WATER synergy: PP-focused → AQUA_EGG for fast ability cycling.
- DARK synergy: Crit-focused → RAZOR_CLAW + RAZOR_FANG combo is devastating.
- FAIRY synergy: Wands add 20% additional SPECIAL to attacks. Complements AP items.

## SKILL-BASED RULES

- If Pokemon has low maxPP (<=60): Needs PP items less. Prioritize raw damage (AP or ATK).
- If Pokemon has high maxPP (>=100): Needs PP recovery. AQUA_EGG, SOUL_DEW, DEEP_SEA_TOOTH are critical.
- If Pokemon has range >= 3: Safe backline carry. Can afford full damage build.
- If Pokemon has range 1 (melee): Needs some survivability mixed in. KINGS_ROCK or PROTECTIVE_PADS.
- If Pokemon has high ATK but low range: FLAME_ORB + RAZOR_CLAW is the aggressive melee carry build.

## ANTI-PATTERNS (Items to AVOID)

- Don't recommend CHOICE_SPECS on ATK-based carries (they don't scale with AP).
- Don't recommend FLAME_ORB on tanks (BURN hurts them, they need HP not ATK).
- Don't recommend full glass cannon (3 damage items) on melee Pokemon with HP < 200.
- Don't recommend RAZOR_CLAW on AP carries (their damage is SPECIAL, not PHYSICAL crits).
- Don't stack multiple PP items on Pokemon with low maxPP — diminishing returns.
- WONDER_BOX gives random items — never recommend as a "best" item, it's a gamble.
