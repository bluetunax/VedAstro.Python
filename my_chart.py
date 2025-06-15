# File: my_chart.py (Final Application with Complete Nakshatra Map)

import json
import os
import sys
from vedastro import *
import time as py_time

# --- CONFIGURATION ---
KNOWN_CITIES_FILE = "known_cities.json"
SAVED_PROFILES_FILE = "saved_profiles.json"

#-----------------------------------------------------
# --- COMPLETE NAKSHATRA NAME TRANSLATION MAP ---
#-----------------------------------------------------
NAKSHATRA_MAP = {
    "Aswini": "Ashwini", "Krithika": "Krittika", "Mrigasira": "Mrigashira", "Aridra": "Ardra",
    "Pushyami": "Pushya", "Aslesha": "Ashlesha", "Makha": "Magha", "Pubba": "Purva Phalguni",
    "Uttara": "Uttara Phalguni", "Chitta": "Chitra", "Swathi": "Swati", "Vishhaka": "Vishakha",
    "Jyesta": "Jyeshtha", "Moola": "Mula", "Poorvashada": "Purva Ashadha", "Uttarashada": "Uttara Ashadha",
    "Sravana": "Shravana", "Dhanishta": "Dhanishtha", "Satabhisha": "Shatabhisha",
    "Poorvabhadra": "Purva Bhadrapada", "Uttarabhadra": "Uttara Bhadrapada", "Revathi": "Revati"
}

# --- HELPER FUNCTIONS for FILE I/O ---

def load_from_json(filename):
    if not os.path.exists(filename): return {}
    try:
        with open(filename, "r") as f: return json.load(f)
    except json.JSONDecodeError: return {}

def save_to_json(data, filename):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

def select_item_from_list(item_list, prompt_message, display_key):
    if not item_list:
        print("No items to display.")
        return None
    print(prompt_message)
    for i, item in enumerate(item_list): print(f"  {i + 1}: {item[display_key]}")
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(item_list): return item_list[choice - 1]
            else: print("Invalid number. Please try again.")
        except ValueError: print("Invalid input. Please enter a number.")
            
# --- THE MAIN CALCULATION FUNCTION ---

def run_divisional_chart_calculations(person_name, birth_date_str, birth_time_str, birth_timezone_str, selected_location):
    start_time = py_time.time()
    print(f"\n--> Generating all divisional charts for {person_name}...")
    print("--> This is an advanced report and will take a few minutes to complete.")
    
    zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    DIVISIONAL_CHARTS = [
        {"name": "Rasi", "d_number": "D1", "description": "Body, Physical & General Matters", "lagna_func": Calculate.HouseRasiSign, "planet_func": Calculate.PlanetRasiD1Sign},
        {"name": "Hora", "d_number": "D2", "description": "Wealth, Family", "lagna_func": Calculate.HouseHoraD2Sign, "planet_func": Calculate.PlanetHoraD2Signs},
        {"name": "Drekkana", "d_number": "D3", "description": "Siblings, Nature", "lagna_func": Calculate.HouseDrekkanaD3Sign, "planet_func": Calculate.PlanetDrekkanaD3Sign},
        {"name": "Chaturthamsa", "d_number": "D4", "description": "Fortune and Property", "lagna_func": Calculate.HouseChaturthamshaD4Sign, "planet_func": Calculate.PlanetChaturthamshaD4Sign},
        {"name": "Saptamsa", "d_number": "D7", "description": "Children/Progeny", "lagna_func": Calculate.HouseSaptamshaD7Sign, "planet_func": Calculate.PlanetSaptamshaD7Sign},
        {"name": "Navamsa", "d_number": "D9", "description": "Spouse, Dharma and Relationships", "lagna_func": Calculate.HouseNavamshaD9Sign, "planet_func": Calculate.PlanetNavamshaD9Sign},
        {"name": "Dasamsa", "d_number": "D10", "description": "Actions in Society, Profession", "lagna_func": Calculate.HouseDashamamshaD10Sign, "planet_func": Calculate.PlanetDashamamshaD10Sign},
        {"name": "Dwadasamsa", "d_number": "D12", "description": "Parents (Paternal Legacies)", "lagna_func": Calculate.HouseDwadashamshaD12Sign, "planet_func": Calculate.PlanetDwadashamshaD12Sign},
        {"name": "Shodasamsa", "d_number": "D16", "description": "Vehicles, Travelling and Comforts", "lagna_func": Calculate.HouseShodashamshaD16Sign, "planet_func": Calculate.PlanetShodashamshaD16Sign},
        {"name": "Vimsamsa", "d_number": "D20", "description": "Spiritual Pursuits", "lagna_func": Calculate.HouseVimshamshaD20Sign, "planet_func": Calculate.PlanetVimshamshaD20Sign},
        {"name": "ChaturVimsamsa", "d_number": "D24", "description": "Education, Learning, Knowledge", "lagna_func": Calculate.HouseChaturvimshamshaD24Sign, "planet_func": Calculate.PlanetChaturvimshamshaD24Sign},
        {"name": "SaptaVimsamsa", "d_number": "D27", "description": "Strengths and Weakness", "lagna_func": Calculate.HouseBhamshaD27Sign, "planet_func": Calculate.PlanetBhamshaD27Sign},
        {"name": "Trimsamsa", "d_number": "D30", "description": "Evils, Misfortunes", "lagna_func": Calculate.HouseTrimshamshaD30Sign, "planet_func": Calculate.PlanetTrimshamshaD30Sign},
        {"name": "KhaVedamsa", "d_number": "D40", "description": "Auspicious/Inauspicious Effects", "lagna_func": Calculate.HouseKhavedamshaD40Sign, "planet_func": Calculate.PlanetKhavedamshaD40Sign},
        {"name": "AkshaVedamsa", "d_number": "D45", "description": "General Indications (Character)", "lagna_func": Calculate.HouseAkshavedamshaD45Sign, "planet_func": Calculate.PlanetAkshavedamshaD45Sign},
        {"name": "Shastiamsa", "d_number": "D60", "description": "General Indications (Past Karma)", "lagna_func": Calculate.HouseShashtyamshaD60Sign, "planet_func": Calculate.PlanetShashtyamshaD60Sign},
    ]

    try:
        birth_location = GeoLocation(selected_location['LocationName'], selected_location['Longitude'], selected_location['Latitude'])
        full_time_string = f"{birth_time_str} {birth_date_str} {birth_timezone_str}"
        birth_details = Time(full_time_string, birth_location)

        planets_to_analyze = [PlanetName.Sun, PlanetName.Moon, PlanetName.Mars, PlanetName.Mercury, PlanetName.Jupiter, PlanetName.Venus, PlanetName.Saturn, PlanetName.Rahu, PlanetName.Ketu]
        
        print("--> Pre-calculating all Nakshatras...")
        nakshatra_cache = {}
        for planet_enum in planets_to_analyze:
            raw_nakshatra_string = str(Calculate.PlanetConstellation(planet_enum, birth_details))
            nakshatra_cache[planet_enum.value] = raw_nakshatra_string

        for chart in DIVISIONAL_CHARTS:
            print("\n" + "="*95)
            print(f"  {chart['d_number']} {chart['name'].upper()}: {chart['description']}")
            print("="*95)
            divisional_lagna_obj = chart["lagna_func"](HouseName.House1, birth_details)
            divisional_lagna_sign = divisional_lagna_obj.get('Name', 'N/A')
            lagna_degree_obj = divisional_lagna_obj.get('DegreesIn', {})
            lagna_degree_str = lagna_degree_obj.get('DegreeMinuteSecond', '')
            print(f"Divisional Lagna: {divisional_lagna_sign} : {lagna_degree_str}\n")

            chart_table_data = []
            for planet_enum in planets_to_analyze:
                planet_name = planet_enum.value
                raw_nakshatra_string = nakshatra_cache[planet_name]
                nakshatra_name_from_api, nakshatra_pada = raw_nakshatra_string, ''
                if " - " in raw_nakshatra_string:
                    parts = raw_nakshatra_string.split(" - ")
                    nakshatra_name_from_api, nakshatra_pada = parts[0].strip(), parts[1].strip()
                translated_name = NAKSHATRA_MAP.get(nakshatra_name_from_api, nakshatra_name_from_api)
                nakshatra_formatted = f"{translated_name} (Pada {nakshatra_pada})" if nakshatra_pada else translated_name
                planet_divisional_sign_obj = chart["planet_func"](planet_enum, birth_details)
                planet_divisional_sign = planet_divisional_sign_obj.get('Name', 'N/A')
                degree_obj = planet_divisional_sign_obj.get('DegreesIn', {})
                degree_str = degree_obj.get('DegreeMinuteSecond', '')
                house_number = 'N/A'
                if divisional_lagna_sign in zodiac_signs and planet_divisional_sign in zodiac_signs:
                    lagna_index, planet_index = zodiac_signs.index(divisional_lagna_sign), zodiac_signs.index(planet_divisional_sign)
                    house_number = (planet_index - lagna_index + 12) % 12 + 1
                chart_table_data.append({"Planet": planet_name, "Sign": planet_divisional_sign, "Degree": degree_str, "Nakshatra": nakshatra_formatted, "House": f"House{house_number}" if house_number != 'N/A' else 'N/A'})
            print(f"{'Planet':<12} | {'Divisional Sign':<15} | {'Degree':<13} | {'Nakshatra (from D1)':<32} | {'House':<10}")
            print("-" * 95)
            for row in chart_table_data: print(f"{row['Planet']:<12} | {row['Sign']:<15} | {row['Degree']:<13} | {row['Nakshatra']:<32} | {row['House']:<10}")
        
        print("\n" + "="*95)
        print(f"Report complete! Total time: {py_time.time() - start_time:.2f} seconds.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred during calculation: {e}")

# --- MAIN APPLICATION LOGIC ---
def main():
    Calculate.SetAPIKey('FreeAPIUser')
    
    while True:
        print("\n" + "="*40)
        print("  Vedic Astrology Chart Generator")
        print("="*40)
        print("1: Load a Saved Profile")
        print("2: Create a New Chart")
        print("3: Exit")
        
        main_choice = input("Select an option: ")

        if main_choice == '1':
            saved_profiles = load_from_json(SAVED_PROFILES_FILE)
            if not saved_profiles:
                print("\nNo profiles saved yet. Please create a new chart first.")
                continue
            profiles_list = [{"person_name": name, **data} for name, data in saved_profiles.items()]
            chosen_profile = select_item_from_list(profiles_list, "\n--- Your Saved Profiles ---", "person_name")
            if chosen_profile:
                run_divisional_chart_calculations(chosen_profile['person_name'], chosen_profile['birth_date_str'], chosen_profile['birth_time_str'], chosen_profile['birth_timezone_str'], chosen_profile['location'])

        elif main_choice == '2':
            known_cities = load_from_json(KNOWN_CITIES_FILE)
            selected_location = None
            
            while True:
                print("\n--- Create New Chart: Location Step ---")
                print("1: Use a saved location")
                print("2: Add a new location by coordinates")
                print("3: Back to Main Menu")
                loc_choice = input("Select an option: ")

                if loc_choice == '1':
                    if not known_cities:
                        print("\nNo locations saved yet. Please add a location first.")
                        continue
                    saved_cities_list = [{"LocationName": name, **data} for name, data in known_cities.items()]
                    selected_location = select_item_from_list(saved_cities_list, "\n--- Your Saved Locations ---", "LocationName")
                    if selected_location: break
                
                elif loc_choice == '2':
                    print("\n--- Add a New Location by Coordinates ---")
                    location_name = input("Enter a name for this location (e.g., 'Lansing, MI'): ")
                    while True:
                        try: latitude = float(input(f"Enter Latitude for {location_name}: ")); break
                        except ValueError: print("Invalid input. Please enter a number.")
                    while True:
                        try: longitude = float(input(f"Enter Longitude for {location_name}: ")); break
                        except ValueError: print("Invalid input. Please enter a number.")
                    known_cities[location_name] = {"Longitude": longitude, "Latitude": latitude}
                    save_to_json(known_cities, KNOWN_CITIES_FILE)
                    print(f"'{location_name}' has been saved.")
                    selected_location = {"LocationName": location_name, "Longitude": longitude, "Latitude": latitude}
                    break
                
                elif loc_choice == '3': break
                else: print("Invalid option.")
            
            if not selected_location: continue

            print("\n--- Please provide the birth details ---")
            person_name = input("Enter a name for this profile: ")
            birth_date_str = input("Enter birth date (DD/MM/YYYY): ")
            birth_time_str = input("Enter birth time (HH:MM, 24-hour format): ")
            birth_timezone_str = input("Enter timezone offset from UTC (e.g., -04:00): ")

            save_choice = input("Save this profile for future use? (y/n): ").lower()
            if save_choice == 'y':
                all_profiles = load_from_json(SAVED_PROFILES_FILE)
                all_profiles[person_name] = {"person_name": person_name, "birth_date_str": birth_date_str, "birth_time_str": birth_time_str, "birth_timezone_str": birth_timezone_str, "location": selected_location}
                save_to_json(all_profiles, SAVED_PROFILES_FILE)
                print(f"Profile '{person_name}' saved!")
            
            run_divisional_chart_calculations(person_name, birth_date_str, birth_time_str, birth_timezone_str, selected_location)

        elif main_choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
