# File: my_chart_v3.py (All-in-One Natal Chart & Transit Generator)

import json
import os
import sys
from datetime import datetime, timedelta
import calendar
from vedastro import * 
from tqdm import tqdm
import concurrent.futures

# --- CONFIGURATION (Matches generate_animation_data_v5.py for v4 data export) ---
MAX_WORKERS = 16
KNOWN_CITIES_FILE = "known_cities.json"
SAVED_PROFILES_FILE = "saved_profiles.json"
CHOSEN_AYANAMSA = Ayanamsa.Lahiri
PLANETS_TO_ANALYZE = [PlanetName.Sun, PlanetName.Moon, PlanetName.Mars, PlanetName.Mercury, PlanetName.Jupiter, PlanetName.Venus, PlanetName.Saturn, PlanetName.Rahu, PlanetName.Ketu]
ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

NAKSHATRA_MAP = {
    "Aswini": "Ashwini", "Krithika": "Krittika", "Mrigasira": "Mrigashira", "Aridra": "Ardra",
    "Pushyami": "Pushya", "Aslesha": "Ashlesha", "Makha": "Magha", "Pubba": "Purva Phalguni",
    "Uttara": "Uttara Phalguni", "Chitta": "Chitra", "Swathi": "Swati", "Vishhaka": "Vishakha",
    "Jyesta": "Jyeshtha", "Moola": "Mula", "Poorvashada": "Purva Ashadha", "Uttarashada": "Uttara Ashadha",
    "Sravana": "Shravana", "Dhanishta": "Dhanishtha", "Satabhisha": "Shatabhisha",
    "Poorvabhadra": "Purva Bhadrapada", "Uttarabhadra": "Uttara Bhadrapada", "Revathi": "Revati"
}
DIVISIONAL_CHARTS_CONFIG = [
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

# --- HELPER FUNCTIONS ---
def load_from_json(filename):
    if not os.path.exists(filename): return {}
    try:
        with open(filename, "r") as f: return json.load(f)
    except Exception: return {}

def save_to_json(data, filename):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

def select_item_from_list(item_list, prompt_message, display_key):
    if not item_list:
        print("No items to display."); return None
    print(prompt_message)
    for i, item in enumerate(item_list): print(f"  {i + 1}: {item[display_key]}")
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(item_list): return item_list[choice - 1]
        except ValueError: print("Invalid input.")

# --- DISPLAY FUNCTION (from my_chartv2.py) ---
def display_full_chart_report(chart_data):
    """Takes loaded chart data and prints the NATAL portion to the console."""
    person_name = chart_data.get("profile_name", "Unknown")
    natal_chart = chart_data.get("natal_chart", {})
    
    print("\n" + "="*95)
    print(f"  Displaying Saved Full Natal Chart for: {person_name}")
    print("="*95)

    for d_number, chart in natal_chart.get("divisional_charts", {}).items():
        print("\n" + "="*95)
        print(f"  {d_number} {chart['name'].upper()}: {chart['description']}")
        print("="*95)
        print(f"Divisional Lagna: {chart['lagna_sign']} : {chart['lagna_degree_str']}\n")
        print(f"{'Planet':<12} | {'Divisional Sign':<15} | {'Degree':<13} | {'Nakshatra (from D1)':<32} | {'House':<10}")
        print("-" * 95)
        for row in chart['planets']:
             print(f"{row['Planet']:<12} | {row['Sign']:<15} | {row['Degree']:<13} | {row['Nakshatra']:<32} | {row['House']:<10}")
    print("\n" + "="*95)
    print("Report complete.")

# --- DATA CALCULATION FUNCTIONS (from generate_animation_data_v5.py) ---
def process_daily_snapshot(task_data):
    current_date, geo_location, timezone_offset, natal_lagna_sign_index = task_data
    try:
        date_str = current_date.strftime('%d/%m/%Y')
        noon_time_obj = Time(f"12:00 {date_str} {timezone_offset}", geo_location)
        start_time_obj = Time(f"00:01 {date_str} {timezone_offset}", geo_location)
        end_time_obj = Time(f"23:59 {date_str} {timezone_offset}", geo_location)
        moon_start_nak = str(Calculate.PlanetConstellation(PlanetName.Moon, start_time_obj))
        moon_end_nak = str(Calculate.PlanetConstellation(PlanetName.Moon, end_time_obj))
        sun_lon_obj = Calculate.PlanetNirayanaLongitude(PlanetName.Sun, noon_time_obj)
        moon_lon_obj = Calculate.PlanetNirayanaLongitude(PlanetName.Moon, noon_time_obj)
        sun_lon = float(sun_lon_obj['TotalDegrees']); moon_lon = float(moon_lon_obj['TotalDegrees'])
        lunar_float = ((moon_lon - sun_lon + 360) % 360 / 360.0) * 2.0
        planets_data = []
        for p_enum in PLANETS_TO_ANALYZE:
            planet_sign_obj = Calculate.PlanetRasiD1Sign(p_enum, noon_time_obj)
            planet_sign_name = planet_sign_obj.get('Name', 'N/A')
            house_number = None
            if planet_sign_name in ZODIAC_SIGNS:
                planet_sign_index = ZODIAC_SIGNS.index(planet_sign_name)
                house_number = (planet_sign_index - natal_lagna_sign_index + 12) % 12 + 1
            planet_lon_obj = Calculate.PlanetNirayanaLongitude(p_enum, noon_time_obj)
            nakshatra_obj = Calculate.PlanetConstellation(p_enum, noon_time_obj)
            planets_data.append({"name": p_enum.value, "absolute_longitude": round(float(planet_lon_obj.get('TotalDegrees', 0.0)), 4), "house": house_number, "nakshatra": str(nakshatra_obj)})
        return {"timestamp": current_date.strftime("%Y-%m-%d 12:00:00"), "lunar_phase_float": round(lunar_float, 4), "moon_start_nakshatra": moon_start_nak, "moon_end_nakshatra": moon_end_nak, "planets": planets_data}
    except Exception as e:
        print(f"Error processing {current_date.strftime('%d/%m/%Y')}: {e}")
        return None

def generate_and_save_all_data(profile_data):
    person_name = profile_data['person_name']; location_info = profile_data['location']
    natal_location = GeoLocation(location_info['LocationName'], location_info['Longitude'], location_info['Latitude'])
    full_time_string = f"{profile_data['birth_time_str']} {profile_data['birth_date_str']} {profile_data['birth_timezone_str']}"
    natal_birth_time = Time(full_time_string, natal_location)
    
    print(f"\n--> Preparing to generate comprehensive data for: {person_name}")
    try:
        natal_lagna_sign_name = str(Calculate.LagnaSignName(natal_birth_time))
        natal_lagna_sign_index = ZODIAC_SIGNS.index(natal_lagna_sign_name)
        print(f"Natal Lagna Sign confirmed: {natal_lagna_sign_name}")
    except Exception as e:
        print(f"[FATAL ERROR] Could not calculate Natal Lagna. Cannot proceed. Error: {e}"); return None

    # --- 1. CALCULATE DETAILED NATAL CHART DATA ---
    print("--> Calculating full natal chart with all 16 divisional charts...")
    detailed_natal_planets = []
    nakshatra_cache = {}
    for planet in PLANETS_TO_ANALYZE:
        planet_sign_obj = Calculate.PlanetRasiD1Sign(planet, natal_birth_time)
        house_obj = Calculate.HousePlanetOccupiesBasedOnSign(planet, natal_birth_time)
        lon_obj = Calculate.PlanetNirayanaLongitude(planet, natal_birth_time)
        nakshatra_str = str(Calculate.PlanetConstellation(planet, natal_birth_time))
        nakshatra_cache[planet.value] = nakshatra_str
        detailed_natal_planets.append({
            "name": planet.value, "house": int(str(house_obj).replace("House","")),
            "absolute_longitude": float(lon_obj['TotalDegrees']), "sign": planet_sign_obj.get('Name', 'N/A'),
            "degree_str": planet_sign_obj.get('DegreesIn', {}).get('DegreeMinuteSecond', ''), "nakshatra": nakshatra_str
        })
    angles_data = {
        "AC": float(Calculate.HouseRasiSign(HouseName.House1, natal_birth_time).get('DegreesIn', {}).get('TotalDegrees', 0.0)),
        "MC": float(Calculate.HouseRasiSign(HouseName.House10, natal_birth_time).get('DegreesIn', {}).get('TotalDegrees', 0.0)),
        "DC": float(Calculate.HouseRasiSign(HouseName.House7, natal_birth_time).get('DegreesIn', {}).get('TotalDegrees', 0.0)),
        "IC": float(Calculate.HouseRasiSign(HouseName.House4, natal_birth_time).get('DegreesIn', {}).get('TotalDegrees', 0.0)),
    }
    all_divisional_charts_data = {}
    for chart_config in tqdm(DIVISIONAL_CHARTS_CONFIG, desc="Calculating Vargas"):
        d_number = chart_config['d_number']
        div_lagna_obj = chart_config["lagna_func"](HouseName.House1, natal_birth_time)
        div_lagna_sign = div_lagna_obj.get('Name', 'N/A')
        planets_in_chart = []
        for p_enum in PLANETS_TO_ANALYZE:
            planet_div_sign_obj = chart_config["planet_func"](p_enum, natal_birth_time)
            planet_div_sign = planet_div_sign_obj.get('Name', 'N/A')
            house_num = (ZODIAC_SIGNS.index(planet_div_sign) - ZODIAC_SIGNS.index(div_lagna_sign) + 12) % 12 + 1 if div_lagna_sign in ZODIAC_SIGNS and planet_div_sign in ZODIAC_SIGNS else 'N/A'
            planets_in_chart.append({
                "Planet": p_enum.value, "Sign": planet_div_sign,
                "Degree": planet_div_sign_obj.get('DegreesIn', {}).get('DegreeMinuteSecond', ''),
                "Nakshatra": nakshatra_cache[p_enum.value],
                "House": f"House {house_num}" if house_num != 'N/A' else 'N/A'
            })
        all_divisional_charts_data[d_number] = {
            "name": chart_config['name'], "description": chart_config['description'],
            "lagna_sign": div_lagna_sign, "lagna_degree_str": div_lagna_obj.get('DegreesIn', {}).get('DegreeMinuteSecond', ''),
            "planets": planets_in_chart
        }
    print("--> Full natal chart calculation complete.")

    # --- 2. CALCULATE DAILY TRANSIT DATA ---
    month_year_str = input("\nEnter the month and year for the transit forecast (e.g., 07/2025): "); month, year = map(int, month_year_str.split('/'))
    start_date = datetime(year, month, 1)
    days_to_process = calendar.monthrange(year, month)[1]
    print(f"\nGenerating daily transit data for {days_to_process} days using up to {MAX_WORKERS} threads...")
    dates_to_process = [start_date + timedelta(days=i) for i in range(days_to_process)]
    tasks = [(day, natal_location, profile_data['birth_timezone_str'], natal_lagna_sign_index) for day in dates_to_process]
    all_keyframes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(tqdm(executor.map(process_daily_snapshot, tasks), total=len(tasks), desc="Processing Days"))
        all_keyframes = [r for r in results if r is not None]

    # --- 3. ASSEMBLE AND SAVE THE FINAL v4 JSON ---
    natal_chart_data = {
        "planets": detailed_natal_planets,
        "angles": angles_data,
        "lagna_sign": natal_lagna_sign_name,
        "divisional_charts": all_divisional_charts_data
    }
    final_output = {
        "profile_name": person_name, 
        "natal_chart": natal_chart_data, 
        "keyframes": sorted(all_keyframes, key=lambda x: x['timestamp'])
    }
    output_suffix = start_date.strftime("%B_%Y")
    output_filename = f"daily_forecast_data_v4_{person_name.replace(' ','_')}_{output_suffix}.json"
    save_to_json(final_output, output_filename)
    
    print(f"\n--- SUCCESS ---")
    print(f"Comprehensive forecast data (v4) saved to '{output_filename}'.")
    return final_output

# --- MAIN APPLICATION LOGIC ---
def create_new_profile():
    print("\n--- Create a New Profile ---")
    known_cities = load_from_json(KNOWN_CITIES_FILE)
    selected_location = None
    while not selected_location:
        print("\nLocation Step:")
        print("1: Use a saved location")
        print("2: Add a new location")
        loc_choice = input("Select an option: ")
        if loc_choice == '1':
            if not known_cities: print("\nNo locations saved yet."); continue
            saved_cities_list = [{"LocationName": name, **data} for name, data in known_cities.items()]
            selected_location = select_item_from_list(saved_cities_list, "\n--- Your Saved Locations ---", "LocationName")
        elif loc_choice == '2':
            location_name = input("Enter a name for this location (e.g., 'Lansing, MI'): ")
            while True:
                try: latitude = float(input(f"Enter Latitude for {location_name}: ")); break
                except ValueError: print("Invalid input.")
            while True:
                try: longitude = float(input(f"Enter Longitude for {location_name}: ")); break
                except ValueError: print("Invalid input.")
            known_cities[location_name] = {"Longitude": longitude, "Latitude": latitude}
            save_to_json(known_cities, KNOWN_CITIES_FILE)
            selected_location = {"LocationName": location_name, "Longitude": longitude, "Latitude": latitude}
    
    print("\n--- Please provide the birth details ---")
    person_name = input("Enter a name for this profile: ")
    birth_date_str = input("Enter birth date (DD/MM/YYYY): ")
    birth_time_str = input("Enter birth time (HH:MM, 24-hour format): ")
    birth_timezone_str = input("Enter timezone offset (e.g., -04:00): ")
    
    new_profile = {
        "person_name": person_name, 
        "birth_date_str": birth_date_str, 
        "birth_time_str": birth_time_str, 
        "birth_timezone_str": birth_timezone_str, 
        "location": selected_location
    }
    
    all_profiles = load_from_json(SAVED_PROFILES_FILE)
    all_profiles[person_name] = new_profile
    save_to_json(all_profiles, SAVED_PROFILES_FILE)
    print(f"\nProfile for '{person_name}' has been saved successfully!")
    return new_profile

def main():
    print("\n" + "="*50); print("  Comprehensive Data Generator (v3.0)"); print("="*50)
    
    while True:
        print("\n--- Main Menu ---")
        print("1: Generate Data for a Saved Profile")
        print("2: Create a New Profile & Generate Data")
        print("3: Exit")
        
        main_choice = input("Select an option: ")
        
        if main_choice == '1':
            saved_profiles = load_from_json(SAVED_PROFILES_FILE)
            if not saved_profiles:
                print("\nNo profiles saved yet. Please create one first.")
                continue
            profiles_list = [{"person_name": name, **data} for name, data in saved_profiles.items()]
            chosen_profile = select_item_from_list(profiles_list, "\n--- Select a Profile ---", "person_name")
            if chosen_profile:
                generated_data = generate_and_save_all_data(chosen_profile)
                if generated_data:
                    display_choice = input("\nDisplay the generated natal chart report now? (y/n): ").lower()
                    if display_choice == 'y':
                        display_full_chart_report(generated_data)

        elif main_choice == '2':
            new_profile = create_new_profile()
            generated_data = generate_and_save_all_data(new_profile)
            if generated_data:
                display_choice = input("\nDisplay the generated natal chart report now? (y/n): ").lower()
                if display_choice == 'y':
                    display_full_chart_report(generated_data)
        
        elif main_choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    Calculate.SetAPIKey('FreeAPIUser')
    Calculate.Ayanamsa = CHOSEN_AYANAMSA
    main()