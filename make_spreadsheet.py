#%%
import pandas as pd
import json

# Dictionary to convert faction ranks to numeric values (higher number = better rank)
rank_to_numeric = {
    'Unranked': 0,
    'Bronze': 1,
    'Bronze I': 2,
    'Bronze II': 3,
    'Bronze III': 4,
    'Silver': 5,
    'Silver I': 6,
    'Silver II': 7, 
    'Silver III': 8,
    'Gold': 9,
    'Gold I': 10,
    'Gold II': 11,
    'Gold III': 12,
    'Platinum': 13,
    'Platinum I': 14,
    'Platinum II': 15,
    'Platinum III': 16,
    'Diamond': 17,
    'Diamond I': 18,
    'Diamond II': 19,
    'Diamond III': 20
}

# Example usage:
# faction_df['rank_before_numeric'] = faction_df['rank_before'].map(rank_to_numeric)
# faction_df['rank_after_numeric'] = faction_df['rank_after'].map(rank_to_numeric)

df = pd.read_json("data.json", orient="index")
df.index.name = "war_id"
df = df[df.error.isna()].copy()
df.drop(columns=["error"], inplace=True)

#%% Extract faction data
faction_rows = []

for war_id, war_data in df.iterrows():
    if 'rankedwarreport' not in war_data:
        continue
        
    report = war_data['rankedwarreport']
    winner_id = report.get('winner')
    total_score = sum(faction['score'] for faction in report['factions'])
    
    for faction in report['factions']:
        # Basic faction info
        faction_row = {
            'start_date': pd.to_datetime(report['start'], unit='s'),
            'end_date': pd.to_datetime(report['end'], unit='s'),
            'duration_hours': round((pd.to_datetime(report['end'], unit='s') - pd.to_datetime(report['start'], unit='s')).total_seconds() / 3600, 2),
            'duration_minutes': round((pd.to_datetime(report['end'], unit='s') - pd.to_datetime(report['start'], unit='s')).total_seconds() / 60, 0),
            'war_id': war_id,
            'faction_id': faction['id'],
            'faction_name': faction['name'],
            'won': faction['id'] == winner_id,
            'score': faction['score'],
            'total_war_score': total_score,
            'attacks': faction['attacks'],
            'rank_before': faction['rank']['before'],
            'rank_after': faction['rank']['after'],
            'member_count': len(faction['members']),
            'participating_member_count': sum(1 for member in faction['members'] if member['attacks'] > 0)
        }
        
        # Add rewards
        if 'rewards' in faction:
            rewards = faction['rewards']
            faction_row['reward_respect'] = rewards.get('respect', 0)
            faction_row['reward_points'] = rewards.get('points', 0)
            
            # Process items
            if 'items' in rewards:
                for item in rewards['items']:
                    item_key = f"reward_item_{item['id']}"
                    faction_row[item_key] = item['quantity']
                    
                    # Store item name for later reference
                    item_name_key = f"item_name_{item['id']}"
                    if item_name_key not in faction_row:
                        faction_row[item_name_key] = item['name']
        
        faction_rows.append(faction_row)

# Create faction dataframe
faction_df = pd.DataFrame(faction_rows)

# Add column to indicate if the faction was forfeit
if 'forfeit' in df['rankedwarreport'].iloc[0]:
    faction_df['forfeit'] = faction_df['war_id'].map(
        {war_id: report.get('forfeit', False) 
         for war_id, report in df['rankedwarreport'].items()}
    )

# Clean up item name columns
item_name_cols = [col for col in faction_df.columns if col.startswith('item_name_')]
item_id_mapping = {}

for col in item_name_cols:
    item_id = col.split('_')[-1]
    # Get a non-null name for this item
    names = faction_df[col].dropna().unique()
    if len(names) > 0:
        item_id_mapping[f"reward_item_{item_id}"] = names[0]

# Rename reward_item columns to actual item names
faction_df = faction_df.rename(columns=item_id_mapping)

# Drop the temporary item name columns
faction_df = faction_df.drop(columns=item_name_cols)
faction_df = faction_df.fillna(0)

#add a couple of features 
faction_df['score_pct_of_war_total'] = round(faction_df['score'] / faction_df['total_war_score'], 3)
faction_df['total_wins'] = faction_df.groupby('faction_id')['won'].transform('sum')
faction_df['total_wars'] = faction_df.groupby('faction_id')['war_id'].transform('nunique')
faction_df['rank_number_before'] = faction_df['rank_before'].map(rank_to_numeric)
faction_df['rank_number_after'] = faction_df['rank_after'].map(rank_to_numeric)

# Save to CSV
faction_df.to_csv('war_data.csv', index=False)

print(f"Extracted data for {len(faction_df)} factions from {faction_df['war_id'].nunique()} wars")
print(f"Output saved to war_data.csv")

# %%
#get all unique ranks, including before and after ranks
# unique_ranks = faction_df['rank_before'].unique().tolist() + faction_df['rank_after'].unique().tolist()
# unique_ranks = list(set(unique_ranks))  # Remove duplicates
