#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Pokemon pets for Agent Monster from the 42arch/pokemon-dataset-zh dataset
Extracts first 100 Pokemon with full multilingual support (EN, ZH, JP)
"""

import json
import os
import urllib.request
import urllib.error
import urllib.parse

# Base URLs for the dataset
BASE_URL = "https://raw.githubusercontent.com/42arch/pokemon-dataset-zh/main"
SIMPLE_POKEDEX_URL = f"{BASE_URL}/data/simple_pokedex.json"
POKEMON_DETAIL_URL = f"{BASE_URL}/data/pokemon/"

def fetch_json(url):
    """Fetch and parse JSON from a URL"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return None

def get_pokemon_detail_url(index, name_zh):
    """Generate the correct URL for Pokemon detail data with proper encoding"""
    filename = f"{index}-{name_zh}.json"
    encoded_filename = urllib.parse.quote(filename.encode('utf-8'), safe='-.')
    return f"{POKEMON_DETAIL_URL}{encoded_filename}"

def get_gene_type(types):
    """Determine gene type based on Pokemon type"""
    type_to_gene = {
        "Fire": "creative",
        "Grass": "logic",
        "Electric": "speed",
        "Water": "logic",
        "Fighting": "creative",
        "Bug": "logic",
        "Poison": "lucky",
        "Flying": "speed",
        "Ground": "logic",
        "Rock": "logic",
        "Psychic": "speed",
        "Ghost": "lucky",
        "Ice": "logic",
        "Dragon": "creative",
        "Dark": "lucky",
        "Steel": "logic",
        "Fairy": "creative",
        "Normal": "lucky"
    }
    
    for ptype in types:
        if ptype in type_to_gene:
            return type_to_gene[ptype]
    return "lucky"

def get_types_from_stats(name_en, name_zh):
    """Try to infer types from Pokemon name - this is a fallback"""
    type_hints = {
        "Bulbasaur": ["Grass", "Poison"],
        "Ivysaur": ["Grass", "Poison"],
        "Venusaur": ["Grass", "Poison"],
        "Charmander": ["Fire"],
        "Charmeleon": ["Fire"],
        "Charizard": ["Fire", "Flying"],
        "Squirtle": ["Water"],
        "Wartortle": ["Water"],
        "Blastoise": ["Water"],
        "Caterpie": ["Bug"],
        "Metapod": ["Bug"],
        "Butterfree": ["Bug", "Flying"],
        "Weedle": ["Bug", "Poison"],
        "Kakuna": ["Bug", "Poison"],
        "Beedrill": ["Bug", "Poison"],
        "Pidgey": ["Normal", "Flying"],
        "Pidgeotto": ["Normal", "Flying"],
        "Pidgeot": ["Normal", "Flying"],
        "Rattata": ["Normal"],
        "Raticate": ["Normal"],
        "Spearow": ["Normal", "Flying"],
        "Fearow": ["Normal", "Flying"],
        "Ekans": ["Poison"],
        "Arbok": ["Poison"],
        "Pikachu": ["Electric"],
        "Raichu": ["Electric"],
        "Sandshrew": ["Ground"],
        "Sandslash": ["Ground"],
        "Nidoran♀": ["Poison"],
        "Nidorina": ["Poison"],
        "Nidoqueen": ["Poison", "Ground"],
        "Nidoran♂": ["Poison"],
        "Nidorino": ["Poison"],
        "Nidoking": ["Poison", "Ground"],
        "Clefairy": ["Fairy"],
        "Clefable": ["Fairy"],
        "Vulpix": ["Fire"],
        "Ninetales": ["Fire"],
        "Jigglypuff": ["Normal", "Fairy"],
        "Wigglytuff": ["Normal", "Fairy"],
        "Zubat": ["Poison", "Flying"],
        "Golbat": ["Poison", "Flying"],
        "Oddish": ["Grass", "Poison"],
        "Gloom": ["Grass", "Poison"],
        "Vileplume": ["Grass", "Poison"],
        "Paras": ["Bug", "Grass"],
        "Parasect": ["Bug", "Grass"],
        "Venonat": ["Bug", "Poison"],
        "Venomoth": ["Bug", "Poison"],
        "Diglett": ["Ground"],
        "Dugtrio": ["Ground"],
        "Meowth": ["Normal"],
        "Persian": ["Normal"],
        "Psyduck": ["Water"],
        "Golduck": ["Water"],
        "Mankey": ["Fighting"],
        "Primeape": ["Fighting"],
        "Growlithe": ["Fire"],
        "Arcanine": ["Fire"],
        "Poliwag": ["Water"],
        "Poliwhirl": ["Water"],
        "Poliwrath": ["Water", "Fighting"],
        "Abra": ["Psychic"],
        "Kadabra": ["Psychic"],
        "Alakazam": ["Psychic"],
        "Machop": ["Fighting"],
        "Machoke": ["Fighting"],
        "Machamp": ["Fighting"],
        "Bellsprout": ["Grass", "Poison"],
        "Weepinbell": ["Grass", "Poison"],
        "Victreebel": ["Grass", "Poison"],
        "Tentacool": ["Water", "Poison"],
        "Tentacruel": ["Water", "Poison"],
        "Geodude": ["Rock", "Ground"],
        "Graveler": ["Rock", "Ground"],
        "Golem": ["Rock", "Ground"],
        "Ponyta": ["Fire"],
        "Rapidash": ["Fire"],
        "Slowpoke": ["Water", "Psychic"],
        "Slowbro": ["Water", "Psychic"],
        "Magnemite": ["Electric", "Steel"],
        "Magneton": ["Electric", "Steel"],
        "Farfetch'd": ["Normal", "Flying"],
        "Doduo": ["Normal", "Flying"],
        "Dodrio": ["Normal", "Flying"],
        "Seel": ["Water"],
        "Dewgong": ["Water", "Ice"],
        "Grimer": ["Poison"],
        "Muk": ["Poison"],
        "Shellder": ["Water"],
        "Cloyster": ["Water", "Ice"],
        "Gastly": ["Ghost", "Poison"],
        "Haunter": ["Ghost", "Poison"],
        "Gengar": ["Ghost", "Poison"],
        "Onix": ["Rock", "Ground"],
        "Drowzee": ["Psychic"],
        "Hypno": ["Psychic"],
        "Krabby": ["Water"],
        "Kingler": ["Water"],
        "Voltorb": ["Electric"],
    }
    return type_hints.get(name_en, ["Normal"])

def create_pet(pokemon_data, stats_data, types):
    """Convert Pokemon data to pet format"""
    stats = stats_data
    gene_type = get_gene_type(types)
    
    name_en = pokemon_data["name_en"]
    name_zh = pokemon_data["name_zh"]
    name_jp = pokemon_data["name_jp"]
    
    pet = {
        "metadata": {
            "name": name_en,
            "species": name_en,
            "birth_time": "2026-04-07T00:00:00.000000",
            "owner": "pokedex@agent-monster",
            "generation": 1,
            "evolution_stage": 1,
            "avatar": f"\n  {name_en}\n ╭───╮\n│ ◕‿◕ │\n╰─────╯\n  {name_zh}\n  {name_jp}\n"
        },
        "stats": {
            "hp": {"base": int(stats["hp"]), "iv": 15, "ev": 0, "exp": 0},
            "attack": {"base": int(stats["attack"]), "iv": 15, "ev": 0, "exp": 0},
            "defense": {"base": int(stats["defense"]), "iv": 15, "ev": 0, "exp": 0},
            "speed": {"base": int(stats["speed"]), "iv": 15, "ev": 0, "exp": 0},
            "armor": {"base": int(stats["sp_defense"]), "iv": 15, "ev": 0, "exp": 0},
            "quota": {"base": int(stats["sp_attack"]), "iv": 15, "ev": 0, "exp": 0}
        },
        "genes": {
            gene_type: {"weight": 0.5, "source_commits": []},
            "lucky": {"weight": 0.3, "source_commits": []},
            "logic": {"weight": 0.1, "source_commits": []},
            "speed": {"weight": 0.1, "source_commits": []}
        },
        "battle_history": [],
        "signature": {
            "algorithm": "RSA-SHA256",
            "value": "",
            "keyid": ""
        }
    }
    return pet

def main():
    output_dir = "/root/pet/agent-monster-pet/demos/pokemon"
    os.makedirs(output_dir, exist_ok=True)
    
    # Fetch the simple pokedex to get the first 100 Pokemon
    print("📥 Fetching simple pokedex from 42arch/pokemon-dataset-zh...")
    simple_pokedex = fetch_json(SIMPLE_POKEDEX_URL)
    if not simple_pokedex:
        print("❌ Failed to fetch simple pokedex")
        return
    
    # Take first 100 Pokemon
    pokemon_list = simple_pokedex[:100]
    print(f"✅ Found {len(pokemon_list)} Pokemon to process\n")
    
    all_pokemon = []
    success_count = 0
    
    for i, pokemon_info in enumerate(pokemon_list, 1):
        index = pokemon_info["index"]
        name_zh = pokemon_info["name_zh"]
        name_jp = pokemon_info["name_jp"]
        name_en = pokemon_info["name_en"]
        
        print(f"[{i:3d}/100] {name_en:15} ({name_zh:6} / {name_jp:8})", end="")
        
        # Fetch detailed data for this Pokemon
        detail_url = get_pokemon_detail_url(index, name_zh)
        
        stats_data = None
        types = ["Normal"]
        
        detail_data = fetch_json(detail_url)
        if detail_data:
            # Extract stats from the detailed data
            stats_list = detail_data.get("stats", [])
            if stats_list and len(stats_list) > 0:
                try:
                    stats_dict = stats_list[0].get("data", {})
                    stats_data = {
                        "hp": str(max(1, int(stats_dict.get("hp", 50)))),
                        "attack": str(max(1, int(stats_dict.get("attack", 50)))),
                        "defense": str(max(1, int(stats_dict.get("defense", 50)))),
                        "sp_attack": str(max(1, int(stats_dict.get("sp_attack", 50)))),
                        "sp_defense": str(max(1, int(stats_dict.get("sp_defense", 50)))),
                        "speed": str(max(1, int(stats_dict.get("speed", 50))))
                    }
                except (ValueError, TypeError):
                    stats_data = None
        
        # Use default stats if fetching failed
        if not stats_data:
            stats_data = {"hp": "50", "attack": "50", "defense": "50", "sp_attack": "50", "sp_defense": "50", "speed": "50"}
            types = get_types_from_stats(name_en, name_zh)
            print(" [using fallback stats]")
        else:
            print(" ✓")
        
        # Create the pet
        pokemon_data = {
            "name_en": name_en,
            "name_zh": name_zh,
            "name_jp": name_jp,
            "types": types
        }
        
        pet = create_pet(pokemon_data, stats_data, types)
        
        # Save the pet file
        output_file = os.path.join(output_dir, f"{index}-{name_en}.soul")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(pet, f, indent=2, ensure_ascii=False)
        
        # Add to our index
        total_stats = sum(int(stats_data[key]) for key in ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"])
        all_pokemon.append({
            "id": index,
            "name_en": name_en,
            "name_zh": name_zh,
            "name_jp": name_jp,
            "types": types,
            "total_stats": total_stats
        })
        
        success_count += 1
    
    # Save the index file
    index_file = os.path.join(output_dir, "index.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(all_pokemon, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully created {success_count} Pokemon pets!")
    print(f"   Location: {output_dir}/")
    print(f"   Index: {index_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
