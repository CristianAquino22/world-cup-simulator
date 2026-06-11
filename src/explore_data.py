import pandas as pd

df = pd.read_csv('data/processed/cleaned_matches.csv')

CONFEDERATION_WEIGHTS = {
    "UEFA":      1.00,
    "CONMEBOL":  0.95,
    "AFC":       0.85,
    "CONCACAF":  0.80,
    "CAF":       0.85,
    "OFC":       0.75,
}

# ── Team to Confederation Mapping ────────────────────────────────────────────
TEAM_CONFEDERATION = {
    # 🌍 CONMEBOL (South America) - The complete 10
    "Argentina": "CONMEBOL", "Bolivia": "CONMEBOL", "Brazil": "CONMEBOL", 
    "Chile": "CONMEBOL", "Colombia": "CONMEBOL", "Ecuador": "CONMEBOL", 
    "Paraguay": "CONMEBOL", "Peru": "CONMEBOL", "Uruguay": "CONMEBOL", 
    "Venezuela": "CONMEBOL", "Aymara": "CONMEBOL", "Falkland Islands": "CONMEBOL", "Mapuche": "CONMEBOL", 
    "Maule Sur": "CONMEBOL",

    # 🌍 UEFA (Europe)
    "Albania": "UEFA", "Andorra": "UEFA", "Armenia": "UEFA", "Austria": "UEFA", 
    "Azerbaijan": "UEFA", "Belarus": "UEFA", "Belgium": "UEFA", "Bosnia and Herzegovina": "UEFA", 
    "Bulgaria": "UEFA", "Croatia": "UEFA", "Cyprus": "UEFA", "Czech Republic": "UEFA", 
    "Czechia": "UEFA", "Denmark": "UEFA", "England": "UEFA", "Estonia": "UEFA", 
    "Faroe Islands": "UEFA", "Finland": "UEFA", "France": "UEFA", "Georgia": "UEFA", 
    "Germany": "UEFA", "Gibraltar": "UEFA", "Greece": "UEFA", "Hungary": "UEFA", 
    "Iceland": "UEFA", "Israel": "UEFA", "Italy": "UEFA", "Kazakhstan": "UEFA", 
    "Kosovo": "UEFA", "Latvia": "UEFA", "Liechtenstein": "UEFA", "Lithuania": "UEFA", 
    "Luxembourg": "UEFA", "Malta": "UEFA", "Moldova": "UEFA", "Montenegro": "UEFA", 
    "Netherlands": "UEFA", "North Macedonia": "UEFA", "Macedonia": "UEFA", "Northern Ireland": "UEFA", 
    "Norway": "UEFA", "Poland": "UEFA", "Portugal": "UEFA", "Republic of Ireland": "UEFA", 
    "Romania": "UEFA", "Russia": "UEFA", "San Marino": "UEFA", "Scotland": "UEFA", 
    "Serbia": "UEFA", "Slovakia": "UEFA", "Slovenia": "UEFA", "Spain": "UEFA", 
    "Sweden": "UEFA", "Switzerland": "UEFA", "Turkey": "UEFA", "Ukraine": "UEFA", "Wales": "UEFA", "Abkhazia": "UEFA", "Alderney": "UEFA", "Artsakh": "UEFA", "Basque Country": "UEFA", 
    "Brittany": "UEFA", "Corsica": "UEFA", "County of Nice": "UEFA", "Crimea": "UEFA", 
    "Délvidék": "UEFA", "Ellan Vannin": "UEFA", "Felvidék": "UEFA", "Franconia": "UEFA", 
    "Frøya": "UEFA", "Galicia": "UEFA", "Gotland": "UEFA", "Gozo": "UEFA", 
    "Guernsey": "UEFA", "Găgăuzia": "UEFA", "Hitra": "UEFA", "Isle of Man": "UEFA", 
    "Isle of Wight": "UEFA", "Jersey": "UEFA", "Kernow": "UEFA", "Kárpátalja": "UEFA", 
    "Menorca": "UEFA", "Monaco": "UEFA", "Northern Cyprus": "UEFA", "Occitania": "UEFA", 
    "Orkney": "UEFA", "Padania": "UEFA", "Parishes of Jersey": "UEFA", "Provence": "UEFA", 
    "Raetia": "UEFA", "Republic of St. Pauli": "UEFA", "Rhodes": "UEFA", "Romani people": "UEFA", 
    "Saare County": "UEFA", "Sark": "UEFA", "Sealand": "UEFA", "Shetland": "UEFA", 
    "South Ossetia": "UEFA", "Székely Land": "UEFA", "Sápmi": "UEFA", "Ticino": "UEFA", 
    "Two Sicilies": "UEFA", "Western Armenia": "UEFA", "Western Isles": "UEFA", 
    "Ynys Môn": "UEFA", "Yorkshire": "UEFA", "Åland Islands": "UEFA",

    # 🌍 CONCACAF (North/Central America & Caribbean)
    "Anguilla": "CONCACAF", "Antigua and Barbuda": "CONCACAF", "Aruba": "CONCACAF", 
    "Bahamas": "CONCACAF", "Barbados": "CONCACAF", "Belize": "CONCACAF", "Bermuda": "CONCACAF", 
    "British Virgin Islands": "CONCACAF", "Canada": "CONCACAF", "Cayman Islands": "CONCACAF", 
    "Costa Rica": "CONCACAF", "Cuba": "CONCACAF", "Curaçao": "CONCACAF", "Dominica": "CONCACAF", 
    "Dominican Republic": "CONCACAF", "El Salvador": "CONCACAF", "Grenada": "CONCACAF", 
    "Guadeloupe": "CONCACAF", "Guatemala": "CONCACAF", "Guyana": "CONCACAF", "Haiti": "CONCACAF", 
    "Honduras": "CONCACAF", "Jamaica": "CONCACAF", "Martinique": "CONCACAF", "Mexico": "CONCACAF", 
    "Montserrat": "CONCACAF", "Nicaragua": "CONCACAF", "Panama": "CONCACAF", "Puerto Rico": "CONCACAF", 
    "Saint Kitts and Nevis": "CONCACAF", "Saint Lucia": "CONCACAF", "Saint Vincent and the Grenadines": "CONCACAF", 
    "Suriname": "CONCACAF", "Trinidad and Tobago": "CONCACAF", "Turks and Caicos Islands": "CONCACAF", 
    "United States": "CONCACAF", "USA": "CONCACAF", "US Virgin Islands": "CONCACAF", "Bonaire": "CONCACAF", "Cascadia": "CONCACAF", "French Guiana": "CONCACAF", 
    "Greenland": "CONCACAF", "Quebec": "CONCACAF", "Saint Barthélemy": "CONCACAF", 
    "Saint Martin": "CONCACAF", "Saint Pierre and Miquelon": "CONCACAF", 
    "Sint Maarten": "CONCACAF", "United States Virgin Islands": "CONCACAF",

    # 🌍 CAF (Africa)
    "Algeria": "CAF", "Angola": "CAF", "Benin": "CAF", "Botswana": "CAF", 
    "Burkina Faso": "CAF", "Burundi": "CAF", "Cameroon": "CAF", "Cape Verde": "CAF", 
    "Central African Republic": "CAF", "Chad": "CAF", "Comoros": "CAF", "Congo": "CAF", 
    "Congo DR": "CAF", "DR Congo": "CAF", "Djibouti": "CAF", "Egypt": "CAF", 
    "Equatorial Guinea": "CAF", "Eritrea": "CAF", "Eswatini": "CAF", "Swaziland": "CAF", 
    "Ethiopia": "CAF", "Gabon": "CAF", "Gambia": "CAF", "Ghana": "CAF", "Guinea": "CAF", 
    "Guinea-Bissau": "CAF", "Ivory Coast": "CAF", "Côte d'Ivoire": "CAF", "Kenya": "CAF", 
    "Lesotho": "CAF", "Liberia": "CAF", "Libya": "CAF", "Madagascar": "CAF", "Malawi": "CAF", 
    "Mali": "CAF", "Mauritania": "CAF", "Mauritius": "CAF", "Morocco": "CAF", "Mozambique": "CAF", 
    "Namibia": "CAF", "Niger": "CAF", "Nigeria": "CAF", "Rwanda": "CAF", "São Tomé and Príncipe": "CAF", 
    "Senegal": "CAF", "Seychelles": "CAF", "Sierra Leone": "CAF", "Somalia": "CAF", 
    "South Africa": "CAF", "South Sudan": "CAF", "Sudan": "CAF", "Tanzania": "CAF", 
    "Togo": "CAF", "Tunisia": "CAF", "Uganda": "CAF", "Zambia": "CAF", "Zimbabwe": "CAF","Ambazonia": "CAF", "Barawa": "CAF", "Biafra": "CAF", "Chagos Islands": "CAF", 
    "Darfur": "CAF", "Kabylia": "CAF", "Matabeleland": "CAF", "Mayotte": "CAF", 
    "Réunion": "CAF", "Saint Helena": "CAF", "Somaliland": "CAF", "Western Sahara": "CAF", 
    "Yoruba Nation": "CAF", "Zanzibar": "CAF",

    # 🌍 AFC (Asia)
    "Afghanistan": "AFC", "Australia": "AFC", "Bahrain": "AFC", "Bangladesh": "AFC", 
    "Bhutan": "AFC", "Brunei": "AFC", "Cambodia": "AFC", "China": "AFC", "China PR": "AFC", 
    "Chinese Taipei": "AFC", "Taiwan": "AFC", "Guam": "AFC", "Hong Kong": "AFC", "India": "AFC", 
    "Indonesia": "AFC", "Iran": "AFC", "Iraq": "AFC", "Japan": "AFC", "Jordan": "AFC", 
    "Kuwait": "AFC", "Kyrgyzstan": "AFC", "Laos": "AFC", "Lebanon": "AFC", "Macau": "AFC", 
    "Malaysia": "AFC", "Maldives": "AFC", "Mongolia": "AFC", "Myanmar": "AFC", "Nepal": "AFC", 
    "North Korea": "AFC", "Oman": "AFC", "Pakistan": "AFC", "Palestine": "AFC", "Philippines": "AFC", 
    "Qatar": "AFC", "Saudi Arabia": "AFC", "Singapore": "AFC", "South Korea": "AFC", 
    "Sri Lanka": "AFC", "Syria": "AFC", "Tajikistan": "AFC", "Thailand": "AFC", 
    "Timor-Leste": "AFC", "Turkmenistan": "AFC", "United Arab Emirates": "AFC", "UAE": "AFC", 
    "Uzbekistan": "AFC", "Vietnam": "AFC", "Yemen": "AFC", "Arameans Suryoye": "AFC", "Chameria": "AFC", "East Turkestan": "AFC", "Hmong": "AFC", 
    "Iraqi Kurdistan": "AFC", "Kurdistan": "AFC", "Panjab": "AFC", "Tamil Eelam": "AFC", 
    "Tibet": "AFC", "United Koreans in Japan": "AFC",

    # 🌍 OFC (Oceania)
    "American Samoa": "OFC", "Cook Islands": "OFC", "Fiji": "OFC", "New Caledonia": "OFC", 
    "New Zealand": "OFC", "Papua New Guinea": "OFC", "Samoa": "OFC", "Solomon Islands": "OFC", 
    "Tahiti": "OFC", "Tonga": "OFC", "Vanuatu": "OFC", "Kiribati": "OFC", "Marshall Islands": "OFC", "Micronesia": "OFC", 
    "Northern Mariana Islands": "OFC", "Tuvalu": "OFC"
}

TOURNAMENT_K = {
    "FIFA World Cup":                         60,
    "FIFA World Cup qualification":           32,
    "Confederations Cup":                     50,
 
    # Continental tournaments — tier by prestige
    "UEFA Euro":                              50,
    "Copa América":                           45,
    "Africa Cup of Nations":                  40,
    "AFC Asian Cup":                          40,
    "CONCACAF Gold Cup":                      35,
    "OFC Nations Cup":                        35,
    "African Cup of Nations":                 45,
    "Gold Cup":                               40,
    "Oceania Nations Cup":                    40,
 
    #Continental qualification
    "UEFA Euro qualification":                30,
    "Copa América qualification":             30,
    "Africa Cup of Nations qualification":    28,
    "AFC Asian Cup qualification":            28,
    "CONCACAF Gold Cup qualification":        25,
    "OFC Nations Cup qualification":          22,
 
    #Nations Leagues — competitive but lower stakes
    "UEFA Nations League":                    32,
    "CONCACAF Nations League":                28,
    "AFC Challenge Cup":                      25,
 
    #Friendlies — informative but low weight
    "Friendly":                               10,
}

def get_k_factor(tournament: str) -> int:
    """
    Returns K-factor for a tournament using exact match first,
    then falls back to keyword-based pattern matching.
    """
    if tournament in TOURNAMENT_K:
        return TOURNAMENT_K[tournament]
 
    t_lower = tournament.lower()
 
    # Pattern fallbacks — order matters (more specific first)
    if "world cup" in t_lower and "qualif" in t_lower:
        return 32
    if "world cup" in t_lower:
        return 60
    if "nations league" in t_lower:
        return 30
    if "qualif" in t_lower:
        return 28
    if "friendly" in t_lower or "international" in t_lower:
        return 10
 
    # Catch-all for minor regional cups
    return 20


all_home_teams = set(df['home_team'].unique())
all_away_teams = set(df['away_team'].unique())

# Combine them into one master list of all teams that exist in the CSV
all_teams_in_data = all_home_teams.union(all_away_teams)

# 4. Get all the teams currently in your dictionary
teams_in_dict = set(TEAM_CONFEDERATION.keys())

# 5. The Magic Math: Subtract the dictionary set from the data set
missing_teams = all_teams_in_data - teams_in_dict

# 6. Print the results
print("-" * 50)
print(f"Total unique teams in dataset: {len(all_teams_in_data)}")
print(f"Teams covered by dictionary: {len(teams_in_dict)}")
print(f"Teams MISSING from dictionary: {len(missing_teams)}")
print("-" * 50)

if len(missing_teams) > 0:
    print("🚨 Here are the teams you need to assign a confederation to:")
    # Sorting them alphabetically makes it easier to read
    for team in sorted(missing_teams):
        print(f"  '{team}': '???',")
else:
    print("✅ All teams are perfectly mapped! You are good to go.")
