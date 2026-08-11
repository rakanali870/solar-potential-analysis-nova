# Solar Potential Analysis — Northern Virginia

Analyzes rooftop solar energy generation potential for 5 Northern Virginia 
locations using NREL's PVWatts V8 API and EPA emissions data.

## What it does
- Queries NREL PVWatts API for monthly solar output for a 4 kW system
- Compares Centreville, Manassas, Reston, Fairfax, and Arlington
- Calculates annual CO₂ offset per location using EPA eGRID emissions factors
- Generates two professional charts saved as PNG files

## Key findings
- Annual output ranges from approximately 5,185–5,238 kWh across the five locations
- Peak production in June and July, lowest in December and January
- A 4 kW system offsets approximately 4,400–4,460 lbs of CO₂ per year

## How to run it
1. Clone the repository
2. Get a free API key at developer.nlr.gov
3. Create a file called config.py with one line: API_KEY = "your_key_here"
4. Install dependencies: pip install -r requirements.txt
5. Run: python main.py

## Technologies used
Python | requests | pandas | matplotlib | numpy | NREL PVWatts V8 API | EPA eGRID 2022

## Data sources
- NREL PVWatts V8 API: developer.nlr.gov
- EPA eGRID 2022 SRVC subregion emissions factor: 0.386 kg CO₂ per kWh