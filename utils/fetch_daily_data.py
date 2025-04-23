from pybaseball import statcast
import pandas as pd
from datetime import date, timedelta

# Get yesterday's data
yesterday = (date.today() - timedelta(days=1)).isoformat()
data = statcast(start_dt=yesterday, end_dt=yesterday)

# Save data
data.to_csv('data/mlb_data_latest.csv', index=False)
print(f"Updated data for {yesterday}")
