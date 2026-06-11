import pandas as pd

#Loads raw data
print("Loading raw data...")
df = pd.read_csv('data/raw/results.csv')

#Converts date column so Python understand it as a real date
df['date'] = pd.to_datetime(df['date'])

#Remove future matches (NA scores)
print("Removing future matches (NA scores)...")
df = df.dropna(subset=['home_score', 'away_score'])

#Creates filters, such as competitive matches from 2000 onwards, and friendlies from 2023 onwards
print("Applying hybrid filter for competitive matches and recent friendlies...")
cond_competitive = (df['tournament'] != 'Friendly') & (df['date'] >= '1993-01-01')
cond_recent_friendly = (df['tournament'] == 'Friendly') & (df['date'] >= '2023-01-01')

#Applies filters
df = df[cond_competitive | cond_recent_friendly]

#Sorts matches chronologically
df = df.sort_values(by='date').reset_index(drop=True)

#Save clean data to 'processed' folder
output_path = 'data/processed/cleaned_matches.csv'
df.to_csv(output_path, index=False)

print(f"Success! Clean data saved. We have {len(df)} highly optimized matches left for our model.")