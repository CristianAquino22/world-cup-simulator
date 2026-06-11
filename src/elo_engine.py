import pandas as pd
import math

CONFEDERATION_WEIGHTS = {
    "UEFA": 1.00,
    "CONMEBOL": 0.98,
    "AFC": 0.85,
    "CONCACAF": 0.78,
    "CAF": 0.83,
    "OFC": 0.70,
}

TEAM_CONFEDERATION = {
    #CONMEBOL
    "Argentina": "CONMEBOL", "Bolivia": "CONMEBOL", "Brazil": "CONMEBOL", 
    "Chile": "CONMEBOL", "Colombia": "CONMEBOL", "Ecuador": "CONMEBOL", 
    "Paraguay": "CONMEBOL", "Peru": "CONMEBOL", "Uruguay": "CONMEBOL", 
    "Venezuela": "CONMEBOL", "Aymara": "CONMEBOL", "Falkland Islands": "CONMEBOL", "Mapuche": "CONMEBOL", 
    "Maule Sur": "CONMEBOL",

    #UEFA
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
    "Ynys Môn": "UEFA", "Yorkshire": "UEFA", "Åland Islands": "UEFA", "Czechoslovakia": "UEFA",

    #CONCACAF
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

    #CAF
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

    #AFC
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

    #OFC
    "American Samoa": "OFC", "Cook Islands": "OFC", "Fiji": "OFC", "New Caledonia": "OFC", 
    "New Zealand": "OFC", "Papua New Guinea": "OFC", "Samoa": "OFC", "Solomon Islands": "OFC", 
    "Tahiti": "OFC", "Tonga": "OFC", "Vanuatu": "OFC", "Kiribati": "OFC", "Marshall Islands": "OFC", "Micronesia": "OFC", 
    "Northern Mariana Islands": "OFC", "Tuvalu": "OFC", "Wallis Islands and Futuna": "OFC"
}

TOURNAMENT_K = {
    "FIFA World Cup":                         60,
    "FIFA World Cup qualification":           35,
    "Confederations Cup":                     50,
 
    "UEFA Euro":                              50,
    "Copa América":                           47,
    "AFC Asian Cup":                          40,
    "African Cup of Nations":                 40,
    "Gold Cup":                               38,
    "Oceania Nations Cup":                    34,
 
    "UEFA Euro qualification":                30,
    "Copa América qualification":             30,
    "Africa Cup of Nations qualification":    28,
    "AFC Asian Cup qualification":            28,
    "CONCACAF Gold Cup qualification":        25,
    "OFC Nations Cup qualification":          22,
 
    "UEFA Nations League":                    32,
    "CONCACAF Nations League":                28,
    "AFC Challenge Cup":                      25,

     "Friendly":                               13,
}

def get_k_factor(tournament):
    #Looks up the exact tournament in the dictionary. 
    return TOURNAMENT_K.get(tournament, 15)

def margin_of_victory_multiplier(goal_diff, elo_diff):
    """
    Scales the Elo exchange based on margin of victory.
    Formula (based on 538's international football model):
    MOV = ln(|goal_diff| + 1) × (2.2 / (Δelo × 0.001 + 2.2))
 
    The second term is the autocorrelation correction:
        - When the favorite wins big (high Δelo, large GD), it's expected
          → the multiplier shrinks toward 1.0 (less extra reward)
        - When an underdog wins big (low/negative Δelo, large GD),
          → the multiplier grows (more reward for the upset)
    Capped at 1.75 to prevent one match from causing catastrophic
    Elo swings (e.g., a 9–0 result).
 
    Args:
        goal_diff: absolute goal difference (always positive)
        elo_diff:  winner's Elo minus loser's Elo at match time
    """
    if goal_diff == 0:
        #Draw: no MOV multiplier — treat as neutral 1.0
        return 1.0
 
    log_component = math.log(abs(goal_diff) + 1)
    autocorr_correction = 2.2 / (elo_diff * 0.001 + 2.2)
 
    multiplier = log_component * autocorr_correction
    return min(multiplier, 1.75)

#Loads data
print("Loading cleaned data...")
df = pd.read_csv('data/processed/cleaned_matches.csv')

df['date'] = pd.to_datetime(df["date"])

elo_ratings = {} #elo dictionary

#Calculates Elo ratings
print("Calculating  Elo ratings... this might take a second.")

for index, row in df.iterrows():
    home = row['home_team']
    away = row['away_team'] 
    home_score = row["home_score"]
    away_score = row["away_score"]
    goal_diff = home_score - away_score

    if home not in elo_ratings:
        elo_ratings[home] = 1500
    if away not in elo_ratings:
        elo_ratings[away] = 1500

    hfa = 0 if row['neutral'] else 65
    k = get_k_factor(row['tournament'])

    if row['date'].year < 2000:
        k = k * 0.5

    home_confederation = TEAM_CONFEDERATION.get(home)
    away_confederation = TEAM_CONFEDERATION.get(away)

    weight_home = CONFEDERATION_WEIGHTS.get(home_confederation)
    weight_away = CONFEDERATION_WEIGHTS.get(away_confederation)

    conf_weight = (weight_home + weight_away) / 2 

    home_expected = 1 / (1 + 10 ** ((elo_ratings[away] - (elo_ratings[home] + hfa)) / 400))
    away_expected = 1 / (1 + 10 ** ((elo_ratings[home] - (elo_ratings[away] - hfa)) / 400))

    if goal_diff > 0:
        elo_diff_at_kickoff = elo_ratings[home] - elo_ratings[away]
    elif goal_diff < 0:
        elo_diff_at_kickoff = elo_ratings[away] - elo_ratings[home]
    else:
        elo_diff_at_kickoff = 0 
        
    mov = margin_of_victory_multiplier(abs(goal_diff), elo_diff_at_kickoff)

    #Determine Actual Results (1 for win, 0.5 for draw, 0 for loss) ---
    if goal_diff > 0:
        home_result, away_result = 1.0, 0.0
    elif goal_diff < 0:
        home_result, away_result = 0.0, 1.0
    else:
        home_result, away_result = 0.5, 0.5

    #Final Equation
    effective_k = k * conf_weight * mov
    elo_ratings[home] = elo_ratings[home] + effective_k * (home_result - home_expected)
    elo_ratings[away] = elo_ratings[away] + effective_k * (away_result - away_expected)        

#Saves results in new dataframe
final_ratings = pd.DataFrame(list(elo_ratings.items()), columns=['Team', 'Elo_Rating'])
final_ratings = final_ratings.sort_values(by='Elo_Rating', ascending=False).reset_index(drop=True)
final_ratings.to_csv('data/processed/current_elos.csv', index=False)

print("Success! Elo engine complete. Here are the Top 10 teams in the world:")
print(final_ratings.head(20))