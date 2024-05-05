import pandas as pd

data_file_path = 'comments/2024-03-26-wsb-comments.csv'
output_file_path = 'comments/2024-03-27-wsb-comments.csv'

# Read the data into a DataFrame
df = pd.read_csv(data_file_path)

# Convert the 'Datetime' column to datetime objects
df['Datetime'] = pd.to_datetime(df['Datetime'])

# Convert all datetime objects in the 'Datetime' column to UTC
df['Datetime'] = df['Datetime'].dt.tz_convert('UTC')

# Optional: If you want the 'Datetime' column to be in a naive datetime format without timezone information
# df['Datetime'] = df['Datetime'].dt.tz_localize(None)

# Save the updated DataFrame to a new file
df.to_csv(output_file_path, index=False)

print(f"Data converted to UTC and saved to '{output_file_path}'.")