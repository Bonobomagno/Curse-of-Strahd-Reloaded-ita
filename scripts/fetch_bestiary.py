"""
Fetch D&D 5e monster stat blocks from open5e API, download images,
and generate Italian bestiary entries for Curse of Strahd Reloaded.
"""

import requests
import os
import time
import json
import re
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
IMG_DIR = PROJECT_ROOT / "it" / "images" / "bestiary"
BESTIARY_OUTPUT = PROJECT_ROOT / "scripts" / "bestiary_output.md"
CACHE_DIR = PROJECT_ROOT / "scripts" / "cache"

IMG_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# --- CREATURE LIST ---
# All creatures referenced in the campaign arcs that need stat blocks
# Format: (api_slug, italian_name, english_name)
CREATURES = [
    # Undead
    ("ghoul", "Ghoul", "Ghoul"),
    ("ghast", "Ghast", "Ghast"),
    ("vampire-spawn", "Progenie Vampirica", "Vampire Spawn"),
    ("specter", "Spettro", "Specter"),
    ("wraith", "Presenza", "Wraith"),
    ("ghost", "Fantasma", "Ghost"),
    ("shadow", "Ombra", "Shadow"),
    ("wight", "Wight", "Wight"),
    ("skeleton", "Scheletro", "Skeleton"),
    ("revenant", "Revenant", "Revenant"),
    ("mummy", "Mummia", "Mummy"),
    ("flameskull", "Teschio Fiammeggiante", "Flameskull"),

    # Beasts
    ("dire-wolf", "Lupo Crudele", "Dire Wolf"),
    ("wolf", "Lupo", "Wolf"),
    ("bat", "Pipistrello", "Bat"),
    ("giant-spider", "Ragno Gigante", "Giant Spider"),
    ("giant-wolf-spider", "Ragno Lupo Gigante", "Giant Wolf Spider"),
    ("giant-poisonous-snake", "Serpente Velenoso Gigante", "Giant Poisonous Snake"),
    ("giant-hyena", "Iena Gigante", "Giant Hyena"),
    ("giant-elk", "Alce Gigante", "Giant Elk"),
    ("giant-goat", "Capra Gigante", "Giant Goat"),
    ("giant-eagle", "Aquila Gigante", "Giant Eagle"),
    ("raven", "Corvo", "Raven"),

    # Swarms
    ("swarm-of-bats", "Sciame di Pipistrelli", "Swarm of Bats"),
    ("swarm-of-ravens", "Sciame di Corvi", "Swarm of Ravens"),
    ("swarm-of-rats", "Sciame di Ratti", "Swarm of Rats"),
    ("swarm-of-insects", "Sciame di Insetti", "Swarm of Insects"),

    # Humanoids
    ("guard", "Guardia", "Guard"),
    ("knight", "Cavaliere", "Knight"),
    ("cultist", "Cultista", "Cultist"),
    ("cult-fanatic", "Fanatico del Culto", "Cult Fanatic"),
    ("bandit", "Bandito", "Bandit"),
    ("bandit-captain", "Capitano dei Banditi", "Bandit Captain"),
    ("scout", "Esploratore", "Scout"),
    ("berserker", "Berserker", "Berserker"),
    ("veteran", "Veterano", "Veteran"),
    ("druid", "Druido", "Druid"),
    ("gladiator", "Gladiatore", "Gladiator"),
    ("spy", "Spia", "Spy"),
    ("noble", "Nobile", "Noble"),
    ("commoner", "Popolano", "Commoner"),
    ("priest", "Sacerdote", "Priest"),
    ("acolyte", "Accolito", "Acolyte"),
    ("mage", "Mago", "Mage"),

    # Constructs & Elementals
    ("flesh-golem", "Golem di Carne", "Flesh Golem"),
    ("iron-golem", "Golem di Ferro", "Iron Golem"),
    ("animated-armor", "Armatura Animata", "Animated Armor"),
    ("shambling-mound", "Cumulo Strisciante", "Shambling Mound"),

    # Fiends
    ("shadow-demon", "Demone dell'Ombra", "Shadow Demon"),
    ("bone-devil", "Diavolo delle Ossa", "Bone Devil"),
    ("nightmare", "Incubo", "Nightmare"),

    # Hags
    ("night-hag", "Strega Notturna", "Night Hag"),

    # Dragons
    ("pseudodragon", "Pseudodrago", "Pseudodragon"),
    ("young-red-shadow-dragon", "Giovane Drago Rosso d'Ombra", "Young Red Shadow Dragon"),

    # Aberrations
    ("gibbering-mouther", "Borbottio Farneticante", "Gibbering Mouther"),

    # Misc
    ("mimic", "Mimic", "Mimic"),
    ("rug-of-smothering", "Tappeto Soffocante", "Rug of Smothering"),
    ("flying-sword", "Spada Volante", "Flying Sword"),
    ("will-o-wisp", "Fuoco Fatuo", "Will-o'-Wisp"),
]

# Italian translations for stat block fields
TRANSLATIONS = {
    # Size
    "Tiny": "Minuscolo",
    "Small": "Piccolo",
    "Medium": "Medio",
    "Large": "Grande",
    "Huge": "Enorme",
    "Gargantuan": "Colossale",
    # Type
    "aberration": "aberrazione",
    "beast": "bestia",
    "celestial": "celestiale",
    "construct": "costrutto",
    "dragon": "drago",
    "elemental": "elementale",
    "fey": "folletto",
    "fiend": "immondo",
    "giant": "gigante",
    "humanoid": "umanoide",
    "monstrosity": "mostruosità",
    "ooze": "melma",
    "plant": "pianta",
    "undead": "non morto",
    "swarm of Tiny beasts": "sciame di bestie Minuscole",
    # Alignment
    "unaligned": "senza allineamento",
    "lawful evil": "legale malvagio",
    "lawful good": "legale buono",
    "lawful neutral": "legale neutrale",
    "neutral evil": "neutrale malvagio",
    "neutral good": "neutrale buono",
    "neutral": "neutrale",
    "chaotic evil": "caotico malvagio",
    "chaotic good": "caotico buono",
    "chaotic neutral": "caotico neutrale",
    "any alignment": "qualsiasi allineamento",
    "any non-good alignment": "qualsiasi allineamento non buono",
    "any non-lawful alignment": "qualsiasi allineamento non legale",
    "any chaotic alignment": "qualsiasi allineamento caotico",
    "typically neutral evil": "tipicamente neutrale malvagio",
    "typically chaotic evil": "tipicamente caotico malvagio",
    "any evil alignment": "qualsiasi allineamento malvagio",
    # Damage types
    "acid": "acido",
    "bludgeoning": "contundente",
    "cold": "freddo",
    "fire": "fuoco",
    "force": "forza",
    "lightning": "fulmine",
    "necrotic": "necrotico",
    "piercing": "perforante",
    "poison": "veleno",
    "psychic": "psichico",
    "radiant": "radioso",
    "slashing": "tagliente",
    "thunder": "tuono",
    # Conditions
    "blinded": "accecato",
    "charmed": "affascinato",
    "deafened": "assordato",
    "exhaustion": "sfinimento",
    "frightened": "spaventato",
    "grappled": "afferrato",
    "incapacitated": "incapacitato",
    "invisible": "invisibile",
    "paralyzed": "paralizzato",
    "petrified": "pietrificato",
    "poisoned": "avvelenato",
    "prone": "prono",
    "restrained": "trattenuto",
    "stunned": "stordito",
    "unconscious": "privo di sensi",
    # Senses
    "blindsight": "vista cieca",
    "darkvision": "scurovisione",
    "tremorsense": "percezione tellurica",
    "truesight": "vista pura",
    "passive Perception": "Percezione passiva",
    # Misc
    "Armor Class": "Classe Armatura",
    "Hit Points": "Punti Ferita",
    "Speed": "Velocità",
    "Saving Throws": "Tiri Salvezza",
    "Skills": "Abilità",
    "Damage Resistances": "Resistenze ai Danni",
    "Damage Immunities": "Immunità ai Danni",
    "Damage Vulnerabilities": "Vulnerabilità ai Danni",
    "Condition Immunities": "Immunità alle Condizioni",
    "Senses": "Sensi",
    "Languages": "Linguaggi",
    "Challenge": "Grado di Sfida",
    "Proficiency Bonus": "Bonus di Competenza",
    # Skills
    "Perception": "Percezione",
    "Stealth": "Furtività",
    "Athletics": "Atletica",
    "Acrobatics": "Acrobazia",
    "Deception": "Inganno",
    "Insight": "Intuizione",
    "Intimidation": "Intimidire",
    "Investigation": "Indagare",
    "Arcana": "Arcano",
    "History": "Storia",
    "Nature": "Natura",
    "Religion": "Religione",
    "Persuasion": "Persuasione",
    "Performance": "Intrattenere",
    "Survival": "Sopravvivenza",
    "Medicine": "Medicina",
    "Animal Handling": "Addestrare Animali",
    "Sleight of Hand": "Rapidità di Mano",
    # Actions header
    "Actions": "Azioni",
    "Reactions": "Reazioni",
    "Legendary Actions": "Azioni Leggendarie",
    # Common action names
    "Multiattack": "Multiattacco",
    "Bite": "Morso",
    "Claw": "Artiglio",
    "Claws": "Artigli",
    "Slam": "Schianto",
    "Longsword": "Spada Lunga",
    "Shortsword": "Spada Corta",
    "Shortbow": "Arco Corto",
    "Longbow": "Arco Lungo",
    "Dagger": "Pugnale",
    "Javelin": "Giavellotto",
    "Greataxe": "Ascia Bipenne",
    "Greatsword": "Spadone",
    "Scimitar": "Scimitarra",
    "Spear": "Lancia",
    "Mace": "Mazza",
    "Pike": "Picca",
    "Crossbow": "Balestra",
    "Light Crossbow": "Balestra Leggera",
    "Heavy Crossbow": "Balestra Pesante",
    "Hand Crossbow": "Balestra a Mano",
    "Shield Bash": "Colpo di Scudo",
    "Quarterstaff": "Bastone Ferrato",
    "War Pick": "Piccone da Guerra",
}

# Ability score names
ABILITY_EN = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
ABILITY_IT = ["FOR", "DES", "COS", "INT", "SAG", "CAR"]

# CR to proficiency bonus
CR_TO_PROF = {
    "0": "+2", "1/8": "+2", "1/4": "+2", "1/2": "+2",
    "1": "+2", "2": "+2", "3": "+2", "4": "+2",
    "5": "+3", "6": "+3", "7": "+3", "8": "+3",
    "9": "+4", "10": "+4", "11": "+4", "12": "+4",
    "13": "+5", "14": "+5", "15": "+5", "16": "+5",
    "17": "+6", "18": "+6", "19": "+6", "20": "+6",
    "21": "+7", "22": "+7", "23": "+7", "24": "+7",
    "25": "+8", "26": "+8", "27": "+8", "28": "+8",
    "29": "+9", "30": "+9",
}


def fetch_monster(slug):
    """Fetch monster data from dnd5eapi.co"""
    cache_file = CACHE_DIR / f"{slug}.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f"https://www.dnd5eapi.co/api/monsters/{slug}"
    print(f"  Fetching {slug} from API...")
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            time.sleep(0.3)  # be polite
            return data
        else:
            print(f"    WARN: {slug} returned {resp.status_code}")
            return None
    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def fetch_open5e_monster(slug):
    """Fallback: fetch from open5e API"""
    cache_file = CACHE_DIR / f"{slug}_open5e.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f"https://api.open5e.com/v1/monsters/{slug}/"
    print(f"  Fetching {slug} from Open5e...")
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            time.sleep(0.3)
            return data
        else:
            print(f"    WARN: open5e {slug} returned {resp.status_code}")
            return None
    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def download_image(creature_name_en, slug):
    """Try to download creature image from open5e or other sources"""
    safe_name = slug.replace("-", "_")
    img_path = IMG_DIR / f"{safe_name}.png"

    if img_path.exists():
        print(f"    Image already exists: {safe_name}.png")
        return img_path.name

    # Try Open5e API for image URL
    try:
        resp = requests.get(f"https://api.open5e.com/v1/monsters/{slug}/", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            img_url = data.get("img_main")
            if img_url:
                print(f"    Downloading image from Open5e: {img_url}")
                img_resp = requests.get(img_url, timeout=15)
                if img_resp.status_code == 200:
                    with open(img_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"    Saved: {safe_name}.png")
                    return img_path.name
    except Exception as e:
        print(f"    Image fetch error: {e}")

    # Try 5e.tools token images (public CDN)
    formatted = creature_name_en.replace(" ", "%20")
    token_urls = [
        f"https://5e.tools/img/bestiary/tokens/MM/{formatted}.webp",
        f"https://5e.tools/img/MM/{formatted}.webp",
    ]
    for url in token_urls:
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 1000:
                webp_path = IMG_DIR / f"{safe_name}.webp"
                with open(webp_path, "wb") as f:
                    f.write(resp.content)
                print(f"    Saved token: {safe_name}.webp")
                return webp_path.name
        except:
            pass

    print(f"    No image found for {creature_name_en}")
    return None


def translate_text(text):
    """Comprehensive translation for stat block text"""
    if not text:
        return ""
    result = text

    # Long phrases first (order matters - longer matches before shorter)
    replacements = [
        # Full sentence patterns
        ("If the target is a creature other than an elf or undead, it must succeed on a",
         "Se il bersaglio è una creatura diversa da un elfo o un non morto, deve superare un"),
        ("If the target is a creature other than an undead, it must succeed on a",
         "Se il bersaglio è una creatura diversa da un non morto, deve superare un"),
        ("If the target is a creature, it must succeed on a",
         "Se il bersaglio è una creatura, deve superare un"),
        ("The target must succeed on a", "Il bersaglio deve superare un"),
        ("the target must succeed on a", "il bersaglio deve superare un"),
        ("Each creature in that area must make a", "Ogni creatura nell'area deve effettuare un"),
        ("Each creature within", "Ogni creatura entro"),
        ("must make a", "deve effettuare un"),
        ("or be paralyzed for 1 minute", "o essere paralizzato per 1 minuto"),
        ("or be poisoned for", "o essere avvelenato per"),
        ("or be frightened for", "o essere spaventato per"),
        ("or be restrained", "o essere trattenuto"),
        ("or be knocked prone", "o cadere prono"),
        ("or be grappled", "o essere afferrato"),
        ("or be stunned", "o essere stordito"),
        ("or be blinded", "o essere accecato"),
        ("or be charmed", "o essere affascinato"),
        ("or be petrified", "o essere pietrificato"),
        ("or take half damage", "o subire la metà dei danni"),
        ("The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.",
         "Il bersaglio può ripetere il tiro salvezza alla fine di ciascuno dei suoi turni, terminando l'effetto su di sé con un successo."),
        ("The target can repeat the saving throw at the end of each of its turns",
         "Il bersaglio può ripetere il tiro salvezza alla fine di ciascuno dei suoi turni"),
        ("ending the effect on itself on a success", "terminando l'effetto su di sé con un successo"),
        ("ending the effect on a success", "terminando l'effetto con un successo"),
        ("on a failed save", "con un tiro fallito"),
        ("on a successful one", "con un tiro riuscito"),
        ("on a success", "con un successo"),
        ("half as much damage on a successful one", "la metà dei danni con un tiro riuscito"),
        ("half as much damage", "la metà dei danni"),
        ("at the start of each of its turns", "all'inizio di ciascuno dei suoi turni"),
        ("at the end of each of its turns", "alla fine di ciascuno dei suoi turni"),
        ("at the start of its turn", "all'inizio del suo turno"),
        ("at the end of its turn", "alla fine del suo turno"),
        ("at the start of its next turn", "all'inizio del suo turno successivo"),
        ("can repeat the saving throw", "può ripetere il tiro salvezza"),
        ("for 1 minute", "per 1 minuto"),
        ("for 24 hours", "per 24 ore"),
        ("for 1 hour", "per 1 ora"),
        ("until the start of", "fino all'inizio di"),
        ("until the end of", "fino alla fine di"),
        ("its next turn", "il suo turno successivo"),
        ("the creature's next turn", "il turno successivo della creatura"),

        # Attack patterns
        ("Melee or Ranged Weapon Attack:", "Attacco con Arma da Mischia o a Distanza:"),
        ("Melee Weapon Attack:", "Attacco con Arma da Mischia:"),
        ("Ranged Weapon Attack:", "Attacco con Arma a Distanza:"),
        ("Melee Spell Attack:", "Attacco con Incantesimo da Mischia:"),
        ("Ranged Spell Attack:", "Attacco con Incantesimo a Distanza:"),
        (" to hit, reach ", " al tiro per colpire, portata "),
        (" to hit, range ", " al tiro per colpire, gittata "),
        (" to hit,", " al tiro per colpire,"),
        (", one target.", ", un bersaglio."),
        (", one target,", ", un bersaglio,"),
        (", one target", ", un bersaglio"),
        (", one creature.", ", una creatura."),
        (", one creature,", ", una creatura,"),
        (", one creature", ", una creatura"),
        (", two targets", ", due bersagli"),
        ("Hit: ", "Colpito: "),

        # Damage types - careful ordering to avoid partial matches
        ("bludgeoning damage", "danni contundenti"),
        ("piercing damage", "danni perforanti"),
        ("slashing damage", "danni taglienti"),
        ("necrotic damage", "danni necrotici"),
        ("radiant damage", "danni radiosi"),
        ("fire damage", "danni da fuoco"),
        ("cold damage", "danni da freddo"),
        ("lightning damage", "danni da fulmine"),
        ("thunder damage", "danni da tuono"),
        ("acid damage", "danni da acido"),
        ("poison damage", "danni da veleno"),
        ("psychic damage", "danni psichici"),
        ("force damage", "danni di forza"),
        (" damage.", " danni."),
        (" damage,", " danni,"),
        (" damage ", " danni "),

        # Saving throws
        ("DC ", "CD "),
        ("saving throw", "tiro salvezza"),
        ("Strength", "Forza"),
        ("Dexterity", "Destrezza"),
        ("Constitution", "Costituzione"),
        ("Intelligence", "Intelligenza"),
        ("Wisdom", "Saggezza"),
        ("Charisma", "Carisma"),

        # Conditions
        (" poisoned", " avvelenato"),
        (" paralyzed", " paralizzato"),
        (" frightened", " spaventato"),
        (" restrained", " trattenuto"),
        (" grappled", " afferrato"),
        (" stunned", " stordito"),
        (" blinded", " accecato"),
        (" prone", " prono"),
        (" charmed", " affascinato"),
        (" petrified", " pietrificato"),
        (" incapacitated", " incapacitato"),
        (" invisible", " invisibile"),
        (" unconscious", " privo di sensi"),
        (" deafened", " assordato"),

        # Creature types
        ("undead", "non morto"),
        ("humanoid", "umanoide"),

        # Common phrases
        ("escape DC", "CD di fuga"),
        ("escape dc", "CD di fuga"),
        ("The creature", "La creatura"),
        ("the creature", "la creatura"),
        ("the target", "il bersaglio"),
        ("The target", "Il bersaglio"),
        ("a creature", "una creatura"),
        ("the attack", "l'attacco"),
        ("an attack", "un attacco"),
        ("opportunity attack", "attacco d'opportunità"),
        ("opportunity attacks", "attacchi d'opportunità"),
        ("attack roll", "tiro per colpire"),
        ("attack rolls", "tiri per colpire"),
        ("ability check", "prova di caratteristica"),
        ("ability checks", "prove di caratteristica"),
        ("melee attack", "attacco da mischia"),
        ("melee attacks", "attacchi da mischia"),
        ("ranged attack", "attacco a distanza"),
        ("has advantage on", "ha vantaggio a"),
        ("has disadvantage on", "ha svantaggio a"),
        ("with advantage", "con vantaggio"),
        ("with disadvantage", "con svantaggio"),
        ("doesn't provoke", "non provoca"),
        ("does not provoke", "non provoca"),

        # Movement/positioning
        ("within 5 feet of", "entro 5 piedi da"),
        ("within 10 feet of", "entro 10 piedi da"),
        ("within 30 feet of", "entro 30 piedi da"),
        ("within 60 feet of", "entro 60 piedi da"),
        ("within 120 feet of", "entro 120 piedi da"),
        ("within 5 feet", "entro 5 piedi"),
        ("within 10 feet", "entro 10 piedi"),
        ("within 30 feet", "entro 30 piedi"),
        ("within 60 feet", "entro 60 piedi"),
        ("can see", "può vedere"),
        ("can hear", "può sentire"),
        ("line of sight", "linea di vista"),

        # Spellcasting
        ("Spellcasting", "Lancio di Incantesimi"),
        ("spellcasting ability", "caratteristica da incantatore"),
        ("spell save DC", "CD del tiro salvezza degli incantesimi"),
        ("spell attack", "attacco con incantesimo"),
        ("spell slots", "slot incantesimo"),
        ("spell slot", "slot incantesimo"),
        ("cantrips", "trucchetti"),
        ("Cantrips", "Trucchetti"),
        ("at will", "a volontà"),
        ("At will", "A volontà"),
        ("1/day each", "1/giorno ciascuno"),
        ("2/day each", "2/giorno ciascuno"),
        ("3/day each", "3/giorno ciascuno"),
        ("1/day", "1/giorno"),
        ("2/day", "2/giorno"),
        ("3/day", "3/giorno"),
        ("1st level", "1° livello"),
        ("2nd level", "2° livello"),
        ("3rd level", "3° livello"),
        ("4th level", "4° livello"),
        ("5th level", "5° livello"),
        ("6th level", "6° livello"),
        ("7th level", "7° livello"),
        ("8th level", "8° livello"),
        ("9th level", "9° livello"),

        # Special abilities text
        ("as a bonus action", "come azione bonus"),
        ("as an action", "come azione"),
        ("as a reaction", "come reazione"),
        ("bonus action", "azione bonus"),
        # ("If the" and "if the" skipped - too generic, causes gibberish)
        ("regains", "recupera"),
        ("hit points", "punti ferita"),
        ("hit point", "punto ferita"),
        ("doesn't have all its hit points", "non ha tutti i suoi punti ferita"),
        ("has at least 1", "ha almeno 1"),
        (" turn", " turno"),
        (" turns", " turni"),
        ("running water", "acqua corrente"),
        ("sunlight", "luce solare"),
        ("in dim light or darkness", "in luce fioca o nell'oscurità"),
        ("dim light", "luce fioca"),
        ("bright light", "luce intensa"),
        ("difficult terrain", "terreno difficile"),
        ("nonmagical", "non magiche"),
        ("magical", "magiche"),

        # Keep untranslated text in English rather than creating gibberish
        # Full-sentence special abilities require manual translation
    ]
    for en, it in replacements:
        result = result.replace(en, it)
    return result


def format_speed(speed_data):
    """Format speed from API data"""
    if isinstance(speed_data, str):
        return speed_data
    parts = []
    if isinstance(speed_data, dict):
        if "walk" in speed_data:
            parts.append(speed_data["walk"])
        for key in ["fly", "swim", "climb", "burrow"]:
            if key in speed_data:
                hover = " (fluttuare)" if speed_data.get("hover") else ""
                it_key = {"fly": "volare", "swim": "nuotare", "climb": "arrampicarsi", "burrow": "scavare"}[key]
                parts.append(f"{it_key} {speed_data[key]}{hover}")
    return ", ".join(parts) if parts else "30 ft."


def format_cr(cr):
    """Format challenge rating"""
    if isinstance(cr, (int, float)):
        if cr == 0.125:
            return "1/8"
        elif cr == 0.25:
            return "1/4"
        elif cr == 0.5:
            return "1/2"
        return str(int(cr))
    return str(cr)


def get_modifier(score):
    """Calculate ability modifier"""
    mod = (score - 10) // 2
    return f"+{mod}" if mod >= 0 else str(mod)


def translate_list(items, translation_dict):
    """Translate a comma-separated list"""
    if not items:
        return ""
    if isinstance(items, list):
        translated = []
        for item in items:
            if isinstance(item, dict):
                item = item.get("name", str(item))
            item_lower = item.lower().strip()
            translated.append(translation_dict.get(item_lower, item))
        return ", ".join(translated)
    return str(items)


def build_statblock_dnd5eapi(data, it_name, img_file=None):
    """Build Italian statblock HTML from dnd5eapi.co data"""
    # Type and alignment
    size = TRANSLATIONS.get(data.get("size", "Medium"), data.get("size", "Medio"))
    creature_type = data.get("type", "")
    if isinstance(creature_type, dict):
        creature_type = creature_type.get("type", "unknown")
    type_it = TRANSLATIONS.get(creature_type.lower(), creature_type)

    alignment = data.get("alignment", "unaligned")
    align_it = TRANSLATIONS.get(alignment.lower(), alignment)

    subtitle = f"{type_it.capitalize()} {size}, {align_it}"

    # AC
    ac_data = data.get("armor_class", [])
    if isinstance(ac_data, list) and ac_data:
        ac_entry = ac_data[0]
        if isinstance(ac_entry, dict):
            ac_val = ac_entry.get("value", 10)
            ac_type = ac_entry.get("type", "")
            ac_armor = ac_entry.get("armor", [])
            if ac_armor:
                armor_names = [a.get("name", "") if isinstance(a, dict) else str(a) for a in ac_armor]
                ac_str = f"{ac_val} ({', '.join(armor_names)})"
            elif ac_type and ac_type != "dex" and ac_type != "natural":
                ac_str = f"{ac_val} ({ac_type})"
            elif ac_type == "natural":
                ac_str = f"{ac_val} (armatura naturale)"
            else:
                ac_str = str(ac_val)
        else:
            ac_str = str(ac_entry)
    else:
        ac_str = str(ac_data)

    # HP
    hp = data.get("hit_points", 0)
    hp_dice = data.get("hit_points_roll", data.get("hit_dice", ""))
    hp_str = f"{hp} ({hp_dice})" if hp_dice else str(hp)

    # Speed
    speed_str = format_speed(data.get("speed", {}))

    # Ability scores
    abilities = {
        "strength": data.get("strength", 10),
        "dexterity": data.get("dexterity", 10),
        "constitution": data.get("constitution", 10),
        "intelligence": data.get("intelligence", 10),
        "wisdom": data.get("wisdom", 10),
        "charisma": data.get("charisma", 10),
    }

    # CR
    cr_val = data.get("challenge_rating", 0)
    cr_str = format_cr(cr_val)
    prof_bonus = CR_TO_PROF.get(cr_str, "+2")

    # Build properties section
    props = []

    # Saving throws
    proficiencies = data.get("proficiencies", [])
    saves = []
    skills = []
    for p in proficiencies:
        prof_info = p.get("proficiency", {})
        name = prof_info.get("name", "") if isinstance(prof_info, dict) else str(prof_info)
        val = p.get("value", 0)
        if "Saving Throw:" in name:
            save_name = name.replace("Saving Throw: ", "")
            save_it = {"STR": "For", "DEX": "Des", "CON": "Cos", "INT": "Int", "WIS": "Sag", "CHA": "Car"}.get(save_name, save_name)
            saves.append(f"{save_it} +{val}")
        elif "Skill:" in name:
            skill_name = name.replace("Skill: ", "")
            skill_it = TRANSLATIONS.get(skill_name, skill_name)
            skills.append(f"{skill_it} +{val}")

    if saves:
        props.append(f"<strong>Tiri Salvezza</strong> {', '.join(saves)}")
    if skills:
        props.append(f"<strong>Abilità</strong> {', '.join(skills)}")

    # Damage vulnerabilities, resistances, immunities
    vuln = data.get("damage_vulnerabilities", [])
    if vuln:
        vuln_it = translate_list(vuln, TRANSLATIONS)
        props.append(f"<strong>Vulnerabilità ai Danni</strong> {vuln_it}")

    resist = data.get("damage_resistances", [])
    if resist:
        resist_it = translate_list(resist, TRANSLATIONS)
        props.append(f"<strong>Resistenze ai Danni</strong> {resist_it}")

    immune = data.get("damage_immunities", [])
    if immune:
        immune_it = translate_list(immune, TRANSLATIONS)
        props.append(f"<strong>Immunità ai Danni</strong> {immune_it}")

    cond_immune = data.get("condition_immunities", [])
    if cond_immune:
        ci_it = translate_list(cond_immune, TRANSLATIONS)
        props.append(f"<strong>Immunità alle Condizioni</strong> {ci_it}")

    # Senses
    senses = data.get("senses", {})
    sense_key_map = {
        "blindsight": "vista cieca",
        "darkvision": "scurovisione",
        "tremorsense": "percezione tellurica",
        "truesight": "vista pura",
        "passive_perception": "Percezione passiva",
    }
    if isinstance(senses, dict):
        sense_parts = []
        for key, val in senses.items():
            key_it = sense_key_map.get(key, TRANSLATIONS.get(key, key))
            sense_parts.append(f"{key_it} {val}")
        senses_str = ", ".join(sense_parts)
    else:
        senses_str = str(senses)
    props.append(f"<strong>Sensi</strong> {senses_str}")

    # Languages
    langs = data.get("languages", "—")
    if not langs:
        langs = "—"
    lang_translations = {
        "Common": "Comune",
        "Elvish": "Elfico",
        "Dwarvish": "Nanico",
        "Abyssal": "Abissale",
        "Infernal": "Infernale",
        "Celestial": "Celestiale",
        "Draconic": "Draconico",
        "Deep Speech": "Linguaggio Profondo",
        "Giant": "Gigante",
        "Goblin": "Goblin",
        "Gnomish": "Gnomesco",
        "Halfling": "Halfling",
        "Orc": "Orchesco",
        "Primordial": "Primordiale",
        "Sylvan": "Silvano",
        "Undercommon": "Sottocomune",
        "Terran": "Terran",
        "Auran": "Auran",
        "Ignan": "Ignan",
        "Aquan": "Aquan",
        "telepathy": "telepatia",
        "all": "tutti",
        "any one language": "un linguaggio qualsiasi",
        "any two languages": "due linguaggi qualsiasi",
        "any four languages": "quattro linguaggi qualsiasi",
        "any languages it knew in life": "qualsiasi linguaggio conoscesse in vita",
        "the languages it knew in life": "i linguaggi che conosceva in vita",
        "understands all languages it spoke in life but can't speak": "comprende tutti i linguaggi che parlava in vita ma non può parlare",
        "understands the languages it knew in life but can't speak": "comprende i linguaggi che conosceva in vita ma non può parlare",
        "understands Common and Elvish but can't speak": "comprende Comune ed Elfico ma non può parlare",
        "but can't speak": "ma non può parlare",
    }
    for en, it in lang_translations.items():
        langs = langs.replace(en, it)
    props.append(f"<strong>Linguaggi</strong> {langs}")

    # CR
    xp = data.get("xp", 0)
    props.append(f"<strong>Grado di Sfida</strong> {cr_str} ({xp:,} PE)" if xp else f"<strong>Grado di Sfida</strong> {cr_str}")
    props.append(f"<strong>Bonus di Competenza</strong> {prof_bonus}")

    # Image reference
    img_html = ""
    if img_file:
        img_html = f'\n\n![[bestiary/{img_file}]]\n'

    # Special abilities
    special_html = ""
    special_abilities = data.get("special_abilities", [])
    if special_abilities:
        for sa in special_abilities:
            name = sa.get("name", "")
            desc = translate_text(sa.get("desc", ""))
            special_html += f'\n<p><strong><em>{name}.</em></strong> {desc}</p>'

    # Actions
    actions_html = ""
    actions = data.get("actions", [])
    if actions:
        actions_html = "\n<h3>Azioni</h3>"
        for act in actions:
            name = act.get("name", "")
            name_it = TRANSLATIONS.get(name, name)
            desc = translate_text(act.get("desc", ""))
            actions_html += f'\n<p><strong><em>{name_it}.</em></strong> {desc}</p>'

    # Reactions
    reactions_html = ""
    reactions = data.get("reactions", [])
    if reactions:
        reactions_html = "\n<h3>Reazioni</h3>"
        for r in reactions:
            name = r.get("name", "")
            desc = translate_text(r.get("desc", ""))
            reactions_html += f'\n<p><strong><em>{name}.</em></strong> {desc}</p>'

    # Legendary actions
    legendary_html = ""
    legendary = data.get("legendary_actions", [])
    if legendary:
        legendary_html = "\n<h3>Azioni Leggendarie</h3>"
        for la in legendary:
            name = la.get("name", "")
            desc = translate_text(la.get("desc", ""))
            legendary_html += f'\n<p><strong><em>{name}.</em></strong> {desc}</p>'

    # Build final HTML
    html = f"""### {it_name}
{img_html}
<div style="clear: both; padding-top: 0.8rem;"></div>

<div class="statblock">
<h2>{it_name}</h2>
<em>{subtitle}</em>
<hr>
<strong>Classe Armatura</strong> {ac_str}
<br>
<strong>Punti Ferita</strong> {hp_str}
<br>
<strong>Velocità</strong> {speed_str}
<hr>
<table class="ability-table">
  <thead>
    <tr>
      <th>FOR</th>
      <th>DES</th>
      <th>COS</th>
      <th>INT</th>
      <th>SAG</th>
      <th>CAR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>{abilities['strength']} ({get_modifier(abilities['strength'])})</td>
      <td>{abilities['dexterity']} ({get_modifier(abilities['dexterity'])})</td>
      <td>{abilities['constitution']} ({get_modifier(abilities['constitution'])})</td>
      <td>{abilities['intelligence']} ({get_modifier(abilities['intelligence'])})</td>
      <td>{abilities['wisdom']} ({get_modifier(abilities['wisdom'])})</td>
      <td>{abilities['charisma']} ({get_modifier(abilities['charisma'])})</td>
    </tr>
  </tbody>
</table>
<hr>
{"<br>".join(props)}{special_html}{actions_html}{reactions_html}{legendary_html}
</div>
"""
    return html


def main():
    print("=== Fetching D&D 5e Bestiary ===\n")

    all_entries = []
    failed = []

    for slug, it_name, en_name in CREATURES:
        print(f"Processing: {en_name} → {it_name}")

        # Fetch stat block
        data = fetch_monster(slug)
        if not data:
            data = fetch_open5e_monster(slug)

        if not data:
            print(f"  SKIPPED: no data found for {slug}")
            failed.append((slug, it_name, en_name))
            continue

        # Download image
        img_file = download_image(en_name, slug)

        # Build statblock
        try:
            entry = build_statblock_dnd5eapi(data, it_name, img_file)
            all_entries.append(entry)
            print(f"  OK: {it_name}")
        except Exception as e:
            print(f"  ERROR building statblock: {e}")
            failed.append((slug, it_name, en_name))

    # Write output
    output = "\n---\n\n".join(all_entries)
    with open(BESTIARY_OUTPUT, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"\n=== Done ===")
    print(f"Generated: {len(all_entries)} entries")
    print(f"Failed: {len(failed)}")
    if failed:
        print("Failed creatures:")
        for slug, it_name, en_name in failed:
            print(f"  - {en_name} ({slug})")
    print(f"\nOutput: {BESTIARY_OUTPUT}")
    print(f"Images: {IMG_DIR}")


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    main()
