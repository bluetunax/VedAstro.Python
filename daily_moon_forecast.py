# File: weekly_forecast_definitive.py

import datetime
from vedastro import Calculate, Time, GeoLocation, PlanetName, Ayanamsa

# Using the Lahiri Ayanamsa, our confirmed standard for accurate transitions.
CHOSEN_AYANAMSA = Ayanamsa.Lahiri

def get_daily_lunar_details(date_obj: datetime.datetime, geo_location: GeoLocation, timezone_offset: str) -> dict:
    """
    Analyzes a single day to get its lunar phase as a float (0.0-2.0)
    and its Nakshatra transition details, using the definitive longitude-difference method.
    """
    date_str = date_obj.strftime("%d/%m/%Y")
    
    noon_time = Time(f"12:00 {date_str} {timezone_offset}", geo_location)

    # --- Calculate the Lunar Phase Float (DEFINITIVE LOGIC) ---
    
    # 1. Get the raw longitudes of the Sun and Moon.
    sun_lon_obj = Calculate.PlanetNirayanaLongitude(PlanetName.Sun, noon_time)
    moon_lon_obj = Calculate.PlanetNirayanaLongitude(PlanetName.Moon, noon_time)
    sun_lon = float(sun_lon_obj['TotalDegrees'])
    moon_lon = float(moon_lon_obj['TotalDegrees'])

    # 2. Calculate the absolute progress of the Moon through its 360-degree cycle relative to the Sun.
    # The '(moon_lon - sun_lon + 360) % 360' formula is a standard astronomical technique.
    cycle_progress_degrees = (moon_lon - sun_lon + 360) % 360
    
    # 3. Map the reliable 0-360 degree progress to our desired 0.0-2.0 float scale.
    lunar_float = (cycle_progress_degrees / 360.0) * 2.0

    # --- Determine Nakshatra Transition ---
    start_time = Time(f"00:01 {date_str} {timezone_offset}", geo_location)
    end_time = Time(f"23:59 {date_str} {timezone_offset}", geo_location)
    start_nakshatra = str(Calculate.PlanetConstellation(PlanetName.Moon, start_time))
    end_nakshatra = str(Calculate.PlanetConstellation(PlanetName.Moon, end_time))
    
    return {
        "lunar_float": lunar_float,
        "start_nakshatra": start_nakshatra,
        "end_nakshatra": end_nakshatra
    }

def run_weekly_forecast_definitive():
    """
    Calculates and prints a 7-day lunar forecast using the definitive,
    mathematically sound float calculation.
    """
    try:
        michigan_location = GeoLocation("Lansing, MI", -84.55, 42.73)
        michigan_timezone_offset = "-04:00" # EDT

        offset = datetime.timedelta(hours=int(michigan_timezone_offset.split(':')[0]))
        local_now = datetime.datetime.utcnow() + offset

        start_date = local_now - datetime.timedelta(days=3)
        end_date = local_now + datetime.timedelta(days=4)

        print(f"\n--- Definitive Weekly Lunar Float Forecast ---")
        print(f"--- (Using {CHOSEN_AYANAMSA.name} Ayanamsa) ---")

        current_date = start_date
        while current_date <= end_date:
            
            is_today = (current_date.date() == local_now.date())
            day_label = f"{current_date.strftime('%A, %b %d')}"
            if is_today: day_label += " (Today)"

            print(f"\n--- {day_label} ---")
            
            lunar_data = get_daily_lunar_details(current_date, michigan_location, michigan_timezone_offset)

            lunar_float = lunar_data['lunar_float']
            if lunar_float < 0.05: interpretation = "New Moon"
            elif lunar_float < 1.0: interpretation = "Growing"
            elif lunar_float < 1.05: interpretation = "Full Moon"
            else: interpretation = "Retreating"

            print(f"  Lunar Float: {lunar_float:.4f} ({interpretation})")
            
            if lunar_data['start_nakshatra'] == lunar_data['end_nakshatra']:
                print(f"  Nakshatra:   The Moon remains in '{lunar_data['start_nakshatra']}' all day.")
            else:
                print(f"  Nakshatra:   Transition from '{lunar_data['start_nakshatra']}' into '{lunar_data['end_nakshatra']}'.")

            current_date += datetime.timedelta(days=1)

    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    Calculate.SetAPIKey('FreeAPIUser')
    Calculate.Ayanamsa = CHOSEN_AYANAMSA
    run_weekly_forecast_definitive()