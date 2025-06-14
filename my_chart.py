# File: my_chart.py (Detailed Tables for All Divisional Charts)

from vedastro import *
import time as py_time # Renaming to avoid conflict with vedastro.Time

#-----------------------------------------------------
# --- 1. ENTER YOUR BIRTH DETAILS HERE ---
#-----------------------------------------------------
person_name = "Albert Einstein"
birth_date_str = "14/03/1879"
birth_time_str = "11:30"
birth_timezone_str = "+01:00"
birth_city_str = "Ulm, Germany"
birth_longitude = 9.99
birth_latitude = 48.40
#-----------------------------------------------------

# A list of zodiac signs in their natural order, used for counting houses
zodiac_signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# --- DATA STRUCTURE DEFINING ALL DIVISIONAL CHARTS AND THEIR FUNCTIONS ---
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

def generate_all_detailed_charts():
    """
    Generates detailed tables (Planet, Nakshatra, House) for all major divisional charts.
    """
    start_time = py_time.time()
    print(f"--> Generating all divisional charts for {person_name}...")
    print("--> This is an advanced report and will take a few minutes to complete.")
    try:
        # --- SETUP ---
        Calculate.SetAPIKey('FreeAPIUser')
        birth_location = GeoLocation(birth_city_str, birth_longitude, birth_latitude)
        full_time_string = f"{birth_time_str} {birth_date_str} {birth_timezone_str}"
        birth_details = Time(full_time_string, birth_location)

        planets_to_analyze = [
            PlanetName.Sun, PlanetName.Moon, PlanetName.Mars, PlanetName.Mercury,
            PlanetName.Jupiter, PlanetName.Venus, PlanetName.Saturn,
            PlanetName.Rahu, PlanetName.Ketu
        ]
        
        # Pre-calculate all Nakshatras once to avoid repeated API calls in the loop
        print("--> Pre-calculating all Nakshatras...")
        nakshatra_cache = {}
        for planet_enum in planets_to_analyze:
            raw_nakshatra_string = str(Calculate.PlanetConstellation(planet_enum, birth_details))
            nakshatra_cache[planet_enum.value] = raw_nakshatra_string

        # --- LOOP THROUGH EACH DIVISIONAL CHART DEFINED ABOVE ---
        for chart in DIVISIONAL_CHARTS:
            print("\n" + "="*80)
            print(f"  {chart['d_number']} {chart['name'].upper()}: {chart['description']}")
            print("="*80)

            # --- Calculate the Divisional Ascendant (Lagna) ---
            divisional_lagna_obj = chart["lagna_func"](HouseName.House1, birth_details)
            divisional_lagna_sign = divisional_lagna_obj.get('Name', 'N/A')
            print(f"Divisional Lagna: {divisional_lagna_sign}\n")

            # --- Prepare a list to hold the detailed data for this chart's table ---
            chart_table_data = []

            # --- Calculate placement for each planet in this divisional chart ---
            for planet_enum in planets_to_analyze:
                planet_name = planet_enum.value
                
                # Get Nakshatra from our pre-calculated cache
                raw_nakshatra_string = nakshatra_cache[planet_name]
                if " (Pada " in raw_nakshatra_string:
                    parts = raw_nakshatra_string.split(" (Pada ")
                    nakshatra_formatted = f"{parts[0]} (Pada {parts[1][0]})"
                else:
                    nakshatra_formatted = raw_nakshatra_string
                
                # Calculate the divisional sign for the planet
                planet_divisional_sign_obj = chart["planet_func"](planet_enum, birth_details)
                planet_divisional_sign = planet_divisional_sign_obj.get('Name', 'N/A')
                
                # Calculate House Placement by counting from the Lagna
                house_number = 'N/A'
                if divisional_lagna_sign in zodiac_signs and planet_divisional_sign in zodiac_signs:
                    lagna_index = zodiac_signs.index(divisional_lagna_sign)
                    planet_index = zodiac_signs.index(planet_divisional_sign)
                    house_number = (planet_index - lagna_index + 12) % 12 + 1

                # Add the data for this planet to our table list
                chart_table_data.append({
                    "Planet": planet_name,
                    "Divisional Sign": planet_divisional_sign,
                    "Nakshatra": nakshatra_formatted,
                    "House": f"House{house_number}" if house_number != 'N/A' else 'N/A'
                })

            # --- Print the formatted table for this divisional chart ---
            print(f"{'Planet':<12} | {'Divisional Sign':<15} | {'Nakshatra (from D1)':<28} | {'House':<10}")
            print("-" * 80)
            for row in chart_table_data:
                print(f"{row['Planet']:<12} | {row['Divisional Sign']:<15} | {row['Nakshatra']:<28} | {row['House']:<10}")

        end_time = py_time.time()
        print("\n" + "="*80)
        print(f"Report complete! Total time: {end_time - start_time:.2f} seconds.")

    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    generate_all_detailed_charts()
